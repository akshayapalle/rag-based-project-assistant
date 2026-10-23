import os

import psycopg
from dotenv import load_dotenv


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


# --------------------------------------------------
# Retrieve ShopSphere project context
# --------------------------------------------------

def get_project_context():

    connection_config = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD")
    }

    with psycopg.connect(**connection_config) as connection:
        with connection.cursor() as cursor:

            print("Connected to ShopSphere database!")

            # ----------------------------------------
            # Get active blockers across the project
            # ----------------------------------------

            cursor.execute("""
                SELECT
                    b.blocker_id,
                    b.description,
                    b.status AS blocker_status,
                    t.task_id,
                    t.task_name,
                    t.status AS task_status,
                    s.sprint_name,
                    s.end_date
                FROM blockers b
                JOIN tasks t
                    ON b.task_id = t.task_id
                JOIN sprints s
                    ON t.sprint_id = s.sprint_id
                WHERE b.project_id = 'P001'
                  AND LOWER(b.status) IN ('open', 'in progress')
                ORDER BY b.reported_date;
            """)

            blockers = cursor.fetchall()

            # ----------------------------------------
            # Get client change requests
            # ----------------------------------------

            cursor.execute("""
                SELECT
                    change_id,
                    requested_date,
                    requested_by,
                    description,
                    impact,
                    status
                FROM change_requests
                WHERE project_id = 'P001'
                ORDER BY requested_date;
            """)

            changes = cursor.fetchall()

            # ----------------------------------------
            # Get project updates
            # ----------------------------------------

            cursor.execute("""
                SELECT
                    update_id,
                    update_date,
                    submitted_by,
                    update_type,
                    content
                FROM updates
                WHERE project_id = 'P001'
                ORDER BY update_date, update_id;
            """)

            updates = cursor.fetchall()

            # ----------------------------------------
            # Get project tasks
            # ----------------------------------------

            cursor.execute("""
                SELECT
                    task_id,
                    task_name,
                    assignee,
                    status,
                    priority,
                    sprint_id
                FROM tasks
                WHERE project_id = 'P001'
                ORDER BY task_id;
            """)

            tasks = cursor.fetchall()

            # ----------------------------------------
            # Get project sprints
            # ----------------------------------------

            cursor.execute("""
                SELECT
                    sprint_id,
                    sprint_name,
                    start_date,
                    end_date,
                    status
                FROM sprints
                WHERE project_id = 'P001'
                ORDER BY start_date;
            """)

            sprints = cursor.fetchall()

            # ----------------------------------------
            # Get project details
            # ----------------------------------------

            cursor.execute("""
                SELECT
                    project_id,
                    project_name,
                    description,
                    status,
                    start_date,
                    target_end_date,
                    client
                FROM projects
                WHERE project_id = 'P001';
            """)

            project = cursor.fetchone()

            # ----------------------------------------
            # Build project context
            # ----------------------------------------

            project_context = {
                "project_id": "P001",
                "project_name": "ShopSphere",
                "project_details": {},
                "blockers": [],
                "change_requests": [],
                "updates": [],
                "tasks": [],
                "sprints": []
            }

            if project:
                project_context["project_details"] = {
                    "project_id": project[0],
                    "project_name": project[1],
                    "description": project[2],
                    "status": project[3],
                    "start_date": str(project[4]),
                    "target_end_date": str(project[5]),
                    "client": project[6]
                }

            # ----------------------------------------
            # Add blockers
            # ----------------------------------------

            for blocker in blockers:
                project_context["blockers"].append({
                    "blocker_id": blocker[0],
                    "description": blocker[1],
                    "blocker_status": blocker[2],
                    "task_id": blocker[3],
                    "task_name": blocker[4],
                    "task_status": blocker[5],
                    "sprint": blocker[6],
                    "deadline": str(blocker[7])
                })

            # ----------------------------------------
            # Add change requests
            # ----------------------------------------

            for change in changes:
                project_context["change_requests"].append({
                    "change_id": change[0],
                    "date": str(change[1]),
                    "requested_by": change[2],
                    "description": change[3],
                    "impact": change[4],
                    "status": change[5]
                })

            # ----------------------------------------
            # Add project updates
            # ----------------------------------------

            for update in updates:
                project_context["updates"].append({
                    "update_id": update[0],
                    "date": str(update[1]),
                    "submitted_by": update[2],
                    "type": update[3],
                    "details": (
                        update[4].split("Update:", 1)[-1].strip()
                        if update[4]
                        else ""
                    )
                })

            # ----------------------------------------
            # Add tasks
            # ----------------------------------------

            for task in tasks:
                project_context["tasks"].append({
                    "task_id": task[0],
                    "task_name": task[1],
                    "assignee": task[2],
                    "status": task[3],
                    "priority": task[4],
                    "sprint_id": task[5]
                })

            # ----------------------------------------
            # Add sprints
            # ----------------------------------------

            for sprint in sprints:
                project_context["sprints"].append({
                    "sprint_id": sprint[0],
                    "sprint_name": sprint[1],
                    "start_date": str(sprint[2]),
                    "end_date": str(sprint[3]),
                    "status": sprint[4]
                })

    return project_context


# --------------------------------------------------
# Test the function
# --------------------------------------------------

if __name__ == "__main__":
    import json

    try:
        context = get_project_context()

        print("\n--- Project Context ---")
        print(
            json.dumps(
                context,
                indent=2,
                ensure_ascii=False
            )
        )

        print("\n--- Blocker Summary ---")

        if context["blockers"]:
            for blocker in context["blockers"]:
                print(
                    f"{blocker['blocker_id']}: "
                    f"{blocker['description']} | "
                    f"Status: {blocker['blocker_status']}"
                )
        else:
            print("No active blockers found in the query results.")

    except Exception as error:
        print(f"Failed to retrieve project context: {error}")
