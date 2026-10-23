import threading
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from document_loader import DATASET_DIR
from build_vector_store import build_vector_store
from sync_excel_to_postgres import sync_data
from ingest_updates import ingest_updates

DOCUMENT_EXTENSIONS = {".txt", ".docx"}
EXCEL_EXTENSIONS = {".xlsx"}
DEBOUNCE_SECONDS = 5
RETRY_ATTEMPTS = 4
RETRY_DELAY_SECONDS = 2


class DatasetChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.condition = threading.Condition()
        self.pending_documents = False
        self.pending_excel = False
        self.pending_update_files = set()
        self.last_event_time = 0
        self.stopping = False

    def on_any_event(self, event):
        if event.is_directory:
            return

        if event.event_type not in {
            "created", "modified", "deleted", "moved"
        }:
            return

        paths = [event.src_path]

        if event.event_type == "moved":
            paths.append(event.dest_path)

        extensions = {
            Path(path).suffix.lower() for path in paths
        }

        if not extensions.intersection(
            DOCUMENT_EXTENSIONS | EXCEL_EXTENSIONS
        ):
            return

        updates_dir = (Path(DATASET_DIR) / "updates").resolve()

        with self.condition:
            self.pending_documents |= bool(
                extensions & DOCUMENT_EXTENSIONS
            )
            self.pending_excel |= bool(
                extensions & EXCEL_EXTENSIONS
            )

            for path in paths:
                file_path = Path(path).resolve()

                if (
                    file_path.suffix.lower() == ".txt"
                    and file_path.parent == updates_dir
                    and file_path.exists()
                ):
                    self.pending_update_files.add(str(file_path))

            self.last_event_time = time.monotonic()
            self.condition.notify()

    def run_with_retry(self, operation, label):
        for attempt in range(1, RETRY_ATTEMPTS + 1):
            try:
                operation()
                print(f"{label} completed successfully.")
                return True

            except PermissionError as error:
                print(
                    f"{label}: file locked "
                    f"(attempt {attempt}/{RETRY_ATTEMPTS})."
                )

                if attempt < RETRY_ATTEMPTS:
                    time.sleep(RETRY_DELAY_SECONDS)
                else:
                    print(f"{label} failed: {error}")

            except Exception as error:
                print(f"{label} failed: {error}")
                return False

        return False

    def worker(self):
        while True:
            with self.condition:
                while not (
                    self.pending_documents
                    or self.pending_excel
                    or self.pending_update_files
                    or self.stopping
                ):
                    self.condition.wait()

                if self.stopping:
                    return

                while not self.stopping:
                    remaining = (
                        self.last_event_time
                        + DEBOUNCE_SECONDS
                        - time.monotonic()
                    )

                    if remaining <= 0:
                        break

                    self.condition.wait(timeout=remaining)

                if self.stopping:
                    return

                documents = self.pending_documents
                excel = self.pending_excel
                update_files = set(self.pending_update_files)

                self.pending_documents = False
                self.pending_excel = False
                self.pending_update_files.clear()

            # Synchronize Excel workbooks with PostgreSQL.
            if excel:
                print("\nExcel changes detected. Syncing PostgreSQL...")
                self.run_with_retry(sync_data, "Excel sync")

            # Ingest only the changed update files.
            if update_files:
                print(
                    f"\nChanged update files: {len(update_files)}. "
                    "Syncing PostgreSQL..."
                )
                self.run_with_retry(
                    lambda: ingest_updates(update_files),
                    "Update ingestion"
                )

            # Update the document index for changed or removed documents.
            if documents:
                print("\nDocument changes detected. Updating ChromaDB...")
                self.run_with_retry(
                    build_vector_store,
                    "Document indexing"
                )

    def stop(self):
        with self.condition:
            self.stopping = True
            self.condition.notify_all()


if __name__ == "__main__":
    dataset_path = Path(DATASET_DIR)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset folder not found: {dataset_path}"
        )

    handler = DatasetChangeHandler()
    worker = threading.Thread(
        target=handler.worker,
        daemon=True
    )
    observer = Observer()

    observer.schedule(
        handler,
        str(dataset_path),
        recursive=True
    )

    worker.start()
    observer.start()

    print(f"Watching dataset folder: {dataset_path}")
    print("Excel files → PostgreSQL")
    print("Changed update TXT files → PostgreSQL")
    print("TXT/DOCX changes → ChromaDB")
    print(f"Waiting {DEBOUNCE_SECONDS} seconds after changes settle.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()
        handler.stop()
        print("Stopping dataset watcher...")

    observer.join()
    worker.join()
