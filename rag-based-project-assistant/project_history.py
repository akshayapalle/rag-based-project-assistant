import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

connection = psycopg.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = connection.cursor()

# -------------------------
# Project Updates
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS updates (
    update_id VARCHAR(20) PRIMARY KEY,
    project_id VARCHAR(20) REFERENCES projects(project_id),
    submitted_by VARCHAR(100),
    update_date DATE,
    update_type VARCHAR(50),
    source VARCHAR(30),
    content TEXT NOT NULL
);
""")

# -------------------------
# Client Change Requests
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS change_requests (
    change_id VARCHAR(20) PRIMARY KEY,
    project_id VARCHAR(20) REFERENCES projects(project_id),
    requested_date DATE,
    requested_by VARCHAR(100),
    description TEXT NOT NULL,
    impact VARCHAR(30),
    status VARCHAR(30)
);
""")

# -------------------------
# Project Blockers
# -------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS blockers (
    blocker_id VARCHAR(20) PRIMARY KEY,
    project_id VARCHAR(20) REFERENCES projects(project_id),
    task_id VARCHAR(20) REFERENCES tasks(task_id),
    reported_by VARCHAR(100),
    reported_date DATE,
    description TEXT NOT NULL,
    status VARCHAR(30)
);
""")

connection.commit()

print("Project history tables created successfully!")

cursor.close()
connection.close()