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

cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    project_id VARCHAR(20) PRIMARY KEY,
    project_name VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(30),
    start_date DATE,
    target_end_date DATE,
    client VARCHAR(100)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS team_members (
    member_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(100),
    team VARCHAR(100),
    email VARCHAR(150)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sprints (
    sprint_id VARCHAR(20) PRIMARY KEY,
    project_id VARCHAR(20) REFERENCES projects(project_id),
    sprint_name VARCHAR(100),
    start_date DATE,
    end_date DATE,
    status VARCHAR(30)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    task_id VARCHAR(20) PRIMARY KEY,
    project_id VARCHAR(20) REFERENCES projects(project_id),
    task_name VARCHAR(150) NOT NULL,
    description TEXT,
    assignee VARCHAR(20) REFERENCES team_members(member_id),
    status VARCHAR(30),
    priority VARCHAR(30),
    deadline DATE,
    sprint_id VARCHAR(20) REFERENCES sprints(sprint_id)
);
""")

connection.commit()

print("Tables created successfully!")

cursor.close()
connection.close()