
from datetime import date

from project_intelligence import get_project_context
from rag_chat import retrieve_documents


def run_evaluation():
    print("\n=== SHOPSPHERE COPILOT EVALUATION ===")
    print(f"Evaluation date: {date.today().isoformat()}")

    # Read the structured project records
    context = get_project_context()

    # Test 1: Approved change requests
    approved = [
        cr["change_id"]
        for cr in context["change_requests"]
        if cr["status"].lower() == "approved"
    ]

    print("\nTEST 1: Approved change requests")
    print("Expected: CR001 and CR002")
    print("Actual:", approved)
    print("PASS" if {"CR001", "CR002"}.issubset(set(approved))
          else "CHECK")

    # Test 2: OTP blocker
    otp_blockers = [
        blocker for blocker in context["blockers"]
        if blocker["task_id"] == "T102"
    ]

    print("\nTEST 2: OTP login blockers")
    print("Expected: B001 and B002")
    print("Actual:", [b["blocker_id"] for b in otp_blockers])
    print("PASS" if {"B001", "B002"}.issubset(
        {b["blocker_id"] for b in otp_blockers}
    ) else "CHECK")

    # Test 3: Overdue sprint deadline
    overdue_sprints = [
        sprint for sprint in context["sprints"]
        if sprint["end_date"] < date.today().isoformat()
    ]

    print("\nTEST 3: Overdue sprints")
    print("Actual:", [
        (s["sprint_name"], s["end_date"], s["status"])
        for s in overdue_sprints
    ])
    print("PASS" if any(
        s["sprint_id"] == "S1" for s in overdue_sprints
    ) else "CHECK")

    # Test 4: T101 status versus project history
    t101 = next(
        (task for task in context["tasks"]
         if task["task_id"] == "T101"),
        None
    )

    print("\nTEST 4: Password Login status")
    print("Database status:", t101["status"] if t101 else "Not found")
    print("Expected finding: compare with Oct 3-4 history")
    print("CHECK: a human or explicit rule must reconcile the status")

    # Test 5: Document retrieval
    question = "What is the latest update about the invalid OTP defect?"
    sources = retrieve_documents(question, top_k=3)

    print("\nTEST 5: Document retrieval")
    print("Question:", question)
    print("Retrieved sources:", [
        source["file_name"] for source in sources
    ])
    print("PASS" if sources else "CHECK")

    print("\n=== EVALUATION COMPLETE ===")
    print("PASS means the basic condition was met, not that every AI answer is correct.")


if __name__ == "__main__":
    run_evaluation()
