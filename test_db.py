from db_config import create_connection

conn = create_connection()

if conn:
    print("✅ Database connection successful!")
    conn.close()
else:
    print("❌ Failed to connect to database.")