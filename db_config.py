
import psycopg2
from psycopg2.extras import RealDictCursor

def create_connection():
    """
    Returns a new psycopg2 connection to the 'jobmate' database.
    Credentials are set for local development:
      user: postgres
      password: admin123
      host: localhost
      port: 5432
    """
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="job",
            user="postgres",
            password="root25"
        )
        return conn
    except Exception as e:
        print("❌ PostgreSQL connection failed:", e)
        return None
