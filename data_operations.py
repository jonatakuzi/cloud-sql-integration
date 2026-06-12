"""
data_operations.py - Automated data operations against the RDS MySQL database.

Demonstrates CRUD operations, bulk inserts, and reporting queries
using the connection helper from db_connect.py.

Usage:
    python data_operations.py --setup    # create tables
    python data_operations.py --seed     # insert sample data
    python data_operations.py --report   # print analytics report
    python data_operations.py --export   # export users to CSV
"""

import argparse
import csv
import datetime
import os
from db_connect import get_connection


# ---------------------------------------------------------------------------
# Schema setup
# ---------------------------------------------------------------------------
CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    user_id    INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(50)  NOT NULL UNIQUE,
    email      VARCHAR(100) NOT NULL UNIQUE,
    role       ENUM('admin', 'editor', 'viewer') NOT NULL DEFAULT 'viewer',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    active     BOOLEAN NOT NULL DEFAULT TRUE
)
"""

CREATE_EVENTS = """
CREATE TABLE IF NOT EXISTS events (
    event_id   INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    action     VARCHAR(100) NOT NULL,
    payload    TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
)
"""

def setup_tables(conn):
    """Create tables if they do not already exist."""
    cursor = conn.cursor()
    cursor.execute(CREATE_USERS)
    cursor.execute(CREATE_EVENTS)
    conn.commit()
    print("[OK] Tables created (or already exist): users, events")
    cursor.close()


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------
SAMPLE_USERS = [
    ("alice",   "alice@example.com",  "admin"),
    ("bob",     "bob@example.com",    "editor"),
    ("carol",   "carol@example.com",  "viewer"),
    ("dave",    "dave@example.com",   "editor"),
    ("eve",     "eve@example.com",    "viewer"),
]

def seed_data(conn):
    """Insert sample users and activity events."""
    cursor = conn.cursor()

    # Bulk insert users (skip duplicates)
    user_sql = "INSERT IGNORE INTO users (username, email, role) VALUES (%s, %s, %s)"
    cursor.executemany(user_sql, SAMPLE_USERS)
    conn.commit()
    print(f"[OK] Inserted/skipped {cursor.rowcount} user rows")

    # Insert events for each user
    cursor.execute("SELECT user_id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]
    events = []
    actions = ["login", "view_dashboard", "export_report", "edit_record", "logout"]
    for uid in user_ids:
        for action in actions[:3]:
            events.append((uid, action, f'{{"source": "seed_script"}}'))
    event_sql = "INSERT INTO events (user_id, action, payload) VALUES (%s, %s, %s)"
    cursor.executemany(event_sql, events)
    conn.commit()
    print(f"[OK] Inserted {len(events)} event rows")
    cursor.close()


# ---------------------------------------------------------------------------
# Analytics report
# ---------------------------------------------------------------------------
def print_report(conn):
    """Print summary analytics from the database."""
    cursor = conn.cursor(dictionary=True)

    print("\n" + "=" * 50)
    print(f"  DATABASE REPORT — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    # User counts by role
    cursor.execute("SELECT role, COUNT(*) AS cnt FROM users GROUP BY role ORDER BY cnt DESC")
    rows = cursor.fetchall()
    print("\nUsers by role:")
    for r in rows:
        print(f"  {r['role']:<10} {r['cnt']}")

    # Active vs inactive
    cursor.execute("SELECT active, COUNT(*) AS cnt FROM users GROUP BY active")
    rows = cursor.fetchall()
    print("\nActive status:")
    for r in rows:
        label = "Active" if r['active'] else "Inactive"
        print(f"  {label:<10} {r['cnt']}")

    # Top 5 most active users
    cursor.execute("""
        SELECT u.username, COUNT(e.event_id) AS event_count
        FROM users u
        LEFT JOIN events e ON u.user_id = e.user_id
        GROUP BY u.user_id, u.username
        ORDER BY event_count DESC
        LIMIT 5
    """)
    rows = cursor.fetchall()
    print("\nTop 5 users by event count:")
    for r in rows:
        print(f"  {r['username']:<15} {r['event_count']} events")

    # Most common actions
    cursor.execute("SELECT action, COUNT(*) AS cnt FROM events GROUP BY action ORDER BY cnt DESC LIMIT 5")
    rows = cursor.fetchall()
    print("\nMost common actions:")
    for r in rows:
        print(f"  {r['action']:<20} {r['cnt']}")

    print("=" * 50)
    cursor.close()


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------
def export_users(conn, filename="users_export.csv"):
    """Export the users table to a CSV file."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, username, email, role, created_at, active FROM users ORDER BY user_id")
    rows = cursor.fetchall()
    if not rows:
        print("[WARN] No users to export.")
        return
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] Exported {len(rows)} users to {filename}")
    cursor.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="AWS RDS data operations demo")
    parser.add_argument("--setup",  action="store_true", help="Create tables")
    parser.add_argument("--seed",   action="store_true", help="Insert sample data")
    parser.add_argument("--report", action="store_true", help="Print analytics report")
    parser.add_argument("--export", action="store_true", help="Export users to CSV")
    parser.add_argument("--all",    action="store_true", help="Run all steps in order")
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        return

    conn = get_connection()
    try:
        if args.all or args.setup:  setup_tables(conn)
        if args.all or args.seed:   seed_data(conn)
        if args.all or args.report: print_report(conn)
        if args.all or args.export: export_users(conn)
    finally:
        conn.close()
        print("\n[OK] Connection closed.")


if __name__ == "__main__":
    main()
