import os
import psycopg
from dotenv import load_dotenv
from datetime import date

load_dotenv()

connection = psycopg.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = connection.cursor()

# --------------------------------
# Insert Client Change Requests
# --------------------------------

change_requests = [
    (
        "CR001",
        "P001",
        date(2026, 10, 2),
        "Acme Retail",
        "Add OTP-based login in addition to password login.",
        "Medium",
        "Approved"
    ),
    (
        "CR002",
        "P001",
        date(2026, 10, 5),
        "Acme Retail",
        "Add Google login as an additional authentication option.",
        "High",
        "Approved"
    )
]

for change in change_requests:

    cursor.execute("""
        INSERT INTO change_requests
        (
            change_id,
            project_id,
            requested_date,
            requested_by,
            description,
            impact,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)

        ON CONFLICT (change_id)
        DO UPDATE SET
            requested_date = EXCLUDED.requested_date,
            requested_by = EXCLUDED.requested_by,
            description = EXCLUDED.description,
            impact = EXCLUDED.impact,
            status = EXCLUDED.status;
    """, change)

    print(f"Processed change request: {change[0]}")


# --------------------------------
# Insert Project Blockers
# --------------------------------

blockers = [
    (
        "B001",
        "P001",
        "T102",
        "Priya, QA Engineer",
        date(2026, 10, 4),
        "Invalid OTP handling needs verification during OTP testing.",
        "Open"
    ),
    (
        "B002",
        "P001",
        "T102",
        "Priya, QA Engineer",
        date(2026, 10, 7),
        "Invalid OTP defect reproduced. Waiting for backend fix.",
        "Open"
    )
]

for blocker in blockers:

    cursor.execute("""
        INSERT INTO blockers
        (
            blocker_id,
            project_id,
            task_id,
            reported_by,
            reported_date,
            description,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)

        ON CONFLICT (blocker_id)
        DO UPDATE SET
            reported_by = EXCLUDED.reported_by,
            reported_date = EXCLUDED.reported_date,
            description = EXCLUDED.description,
            status = EXCLUDED.status;
    """, blocker)

    print(f"Processed blocker: {blocker[0]}")


connection.commit()

print("\nProject events loaded successfully!")

cursor.close()
connection.close()