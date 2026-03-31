
import psycopg2
from config import DB_CONFIG


def get_connection():
    """Create and return a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.OperationalError as e:
        print(f"[ERROR] Could not connect to the database: {e}")
        print("Make sure PostgreSQL is running and your config.py credentials are correct.")
        return None


def create_table():
    """Create the phonebook table if it does not already exist."""
    conn = get_connection()
    if conn is None:
        return

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS phonebook (
                        id      SERIAL PRIMARY KEY,
                        name    VARCHAR(100) NOT NULL,
                        phone   VARCHAR(20)  NOT NULL UNIQUE
                    );
                """)
        print("[OK] Table 'phonebook' is ready.")
    except Exception as e:
        print(f"[ERROR] Failed to create table: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("[OK] Connection successful!")
        conn.close()
        create_table()