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
# Project
# -------------------------

cursor.execute("""
INSERT INTO projects
(project_id, project_name, description, status, start_date, target_end_date, client)
VALUES
(
    'P001',
    'ShopSphere E-commerce Platform',
    'Build a web-based e-commerce platform with authentication, catalog, cart, payment and order management.',
    'In Progress',
    '2026-10-01',
    '2026-10-31',
    'Acme Retail'
)
ON CONFLICT (project_id) DO NOTHING;
""")

# -------------------------
# Team Members
# -------------------------

team_members = [
    ('M001', 'Ananya', 'Project Manager', 'PMO', 'ananya@example.com'),
    ('M002', 'Rahul', 'Backend Developer', 'Backend', 'rahul@example.com'),
    ('M003', 'Sadaf', 'Frontend Developer', 'Frontend', 'sadaf@example.com'),
    ('M004', 'Priya', 'QA Engineer', 'QA', 'priya@example.com'),
    ('M005', 'Arjun', 'DevOps Engineer', 'DevOps', 'arjun@example.com')
]

for member in team_members:
    cursor.execute("""
        INSERT INTO team_members
        (member_id, name, role, team, email)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (member_id) DO NOTHING;
    """, member)

# -------------------------
# Sprints
# -------------------------

sprints = [
    ('S1', 'P001', 'Authentication & Catalog',
     '2026-10-01', '2026-10-10', 'Active'),

    ('S2', 'P001', 'Cart & Payments',
     '2026-10-11', '2026-10-20', 'Planned')
]

for sprint in sprints:
    cursor.execute("""
        INSERT INTO sprints
        (sprint_id, project_id, sprint_name, start_date, end_date, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (sprint_id) DO NOTHING;
    """, sprint)

# -------------------------
# Tasks
# -------------------------

tasks = [
    (
        'T101',
        'P001',
        'Password Login',
        'Implement username/password authentication API',
        'M002',
        'In Progress',
        'High',
        '2026-10-05',
        'S1'
    ),
    (
        'T102',
        'P001',
        'OTP Login',
        'Implement OTP-based authentication',
        'M002',
        'In Progress',
        'High',
        '2026-10-10',
        'S1'
    ),
    (
        'T103',
        'P001',
        'Product Catalog UI',
        'Build product listing and search UI',
        'M003',
        'Not Started',
        'Medium',
        '2026-10-12',
        'S1'
    ),
    (
        'T104',
        'P001',
        'Cart Module',
        'Implement add/remove/update cart functionality',
        'M003',
        'Not Started',
        'Medium',
        '2026-10-15',
        'S2'
    ),
    (
        'T105',
        'P001',
        'Payment API',
        'Integrate payment provider and payment status API',
        'M002',
        'Not Started',
        'High',
        '2026-10-18',
        'S2'
    ),
    (
        'T106',
        'P001',
        'Authentication QA',
        'Test password and OTP authentication',
        'M004',
        'In Progress',
        'High',
        '2026-10-09',
        'S1'
    ),
    (
        'T107',
        'P001',
        'Deployment Pipeline',
        'Set up CI/CD pipeline for staging',
        'M005',
        'Not Started',
        'Medium',
        '2026-10-16',
        'S2'
    )
]

for task in tasks:
    cursor.execute("""
        INSERT INTO tasks
        (
            task_id,
            project_id,
            task_name,
            description,
            assignee,
            status,
            priority,
            deadline,
            sprint_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (task_id) DO NOTHING;
    """, task)

connection.commit()

print("ShopSphere data inserted successfully!")

cursor.close()
connection.close()