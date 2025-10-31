
Your JobMate - PostgreSQL converted project
------------------------------------------
Files updated:
- db_config.py        (PostgreSQL using psycopg2; user=postgres password=admin123 database=jobmate)
- database_postgresql.sql  (PostgreSQL schema)
- All .py files: replaced '?' placeholders with '%s', removed sqlite3 imports and switched sqlite3.connect(...) -> get_connection()

How to get started:
1. Install dependencies:
   pip install psycopg2-binary

2. Create the PostgreSQL database and run schema:
   psql -U postgres
   CREATE DATABASE jobmate;
   \c jobmate
   \i database_postgresql.sql

3. Run main.py:
   python main.py

Notes:
- We attempted a best-effort conversion of placeholder styles and connection usage. Review files for any SQL strings that may need manual tweaks.
- Credentials in db_config.py: user=postgres password=admin123 host=localhost port=5432
