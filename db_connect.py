"""
db_connect.py - MySQL connection helper for AWS RDS.

Reads credentials from environment variables so nothing sensitive
is ever committed to the repository.

Required environment variables:
    DB_HOST  - RDS endpoint (e.g. mydb.abc123.us-east-1.rds.amazonaws.com)
    DB_USER  - Database username
    DB_PASS  - Database password
    DB_NAME  - Database name (default: appdb)
    DB_PORT  - Port (default: 3306)

Usage:
    from db_connect import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
"""

import os
import sys

try:
    import mysql.connector
except ImportError:
    sys.exit("mysql-connector-python not installed. Run: pip install mysql-connector-python")


def get_connection():
    """Return a live MySQL connection using environment variable credentials."""
    host = os.environ.get("DB_HOST")
    user = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASS")
    database = os.environ.get("DB_NAME", "appdb")
    port = int(os.environ.get("DB_PORT", "3306"))

    missing = [v for v in ["DB_HOST", "DB_USER", "DB_PASS"] if not os.environ.get(v)]
    if missing:
        sys.exit(f"Missing environment variables: {', '.join(missing)}\n"
                 f"See README.md for setup instructions.")

    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            ssl_ca=None,          # set path to AWS RDS CA cert for production
            connection_timeout=10,
        )
        print(f"[OK] Connected to {database} at {host}:{port}")
        return conn
    except mysql.connector.Error as err:
        sys.exit(f"[ERROR] Could not connect to database: {err}")


if __name__ == "__main__":
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"MySQL version: {version[0]}")
    conn.close()
