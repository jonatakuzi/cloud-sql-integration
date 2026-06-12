# Cloud & SQL Integration

A Python project demonstrating cloud database connectivity and automated data operations using AWS RDS (MySQL). Covers the full stack: provisioning an RDS instance, configuring EC2 and IAM with least-privilege access, connecting securely via Python, and running CRUD + analytics queries.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.x-blue?logo=mysql&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-RDS%20%2B%20EC2-orange?logo=amazonaws&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Secure RDS connection** — credentials loaded from environment variables, never hardcoded
- **Table setup** — create `users` and `events` tables via Python
- **Bulk inserts** — seed sample data with `executemany` for efficient batch writes
- **Analytics report** — role distribution, active/inactive counts, top users by activity
- **CSV export** — dump the users table to a CSV file for reporting
- Follows AWS least-privilege: IAM role scoped to RDS access only; EC2 security group allows only port 3306 from app server

## Architecture

```
EC2 Instance (app server)
  └── Python scripts
        └── mysql-connector-python
              └── AWS RDS MySQL (private subnet)
```

IAM role on EC2 grants RDS connect permission. Security group restricts port 3306 to the EC2 security group only — not open to the internet.

## Requirements

- Python 3.8+
- `pip install -r requirements.txt`
- AWS account with an RDS MySQL instance running

## Setup

### 1. Provision AWS RDS (one-time)

- Create an RDS MySQL 8.x instance (Free Tier eligible: `db.t3.micro`)
- Set the master username and password
- Configure the security group to allow port 3306 **only** from your EC2 security group (not `0.0.0.0/0`)
- Note the RDS endpoint hostname

### 2. Configure IAM

- Attach an IAM role to your EC2 instance with `rds-db:connect` permission
- Policy: restrict to your specific RDS ARN (least-privilege)

### 3. Set environment variables

```bash
export DB_HOST=mydb.abc123.us-east-1.rds.amazonaws.com
export DB_USER=admin
export DB_PASS=your_password
export DB_NAME=appdb
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run

```bash
# Test connection only
python db_connect.py

# Full workflow: create tables → seed data → report → export
python data_operations.py --all

# Or run steps individually
python data_operations.py --setup
python data_operations.py --seed
python data_operations.py --report
python data_operations.py --export
```

## Example Output

```
[OK] Connected to appdb at mydb.abc123.us-east-1.rds.amazonaws.com:3306
[OK] Tables created (or already exist): users, events
[OK] Inserted 5 user rows
[OK] Inserted 15 event rows

==================================================
  DATABASE REPORT — 2024-11-15 14:32
==================================================

Users by role:
  viewer      2
  editor      2
  admin       1

Top 5 users by event count:
  alice           3 events
  bob             3 events
  carol           3 events

[OK] Exported 5 users to users_export.csv
[OK] Connection closed.
```

## Tech Stack

- Python 3.8+
- MySQL Connector/Python (`mysql-connector-python`)
- AWS RDS (MySQL 8.x)
- AWS EC2 (app host)
- AWS IAM (least-privilege access control)
