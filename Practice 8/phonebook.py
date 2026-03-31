import psycopg2
from connect import get_connection

def setup(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phonebook (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name  VARCHAR(50) NOT NULL,
                phone      VARCHAR(20) NOT NULL
            );
        """)
        for f in ("functions.sql", "procedures.sql"):
            cur.execute(open(f).read())
    conn.commit()

def search(conn, pattern):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts(%s);", (pattern,))
        return cur.fetchall()

def upsert(conn, fn, ln, ph):
    with conn.cursor() as cur:
        cur.execute("CALL upsert_contact(%s, %s, %s);", (fn, ln, ph))
    conn.commit()

def bulk_insert(conn, contacts):
    arr = "ARRAY[" + ",".join(
        f"ARRAY[{psycopg2.extensions.adapt(f).getquoted().decode()},"
        f"{psycopg2.extensions.adapt(l).getquoted().decode()},"
        f"{psycopg2.extensions.adapt(p).getquoted().decode()}]"
        for f, l, p in contacts
    ) + "]"
    with conn.cursor() as cur:
        cur.execute(f"CALL bulk_insert_contacts({arr}::TEXT[][]);")
        cur.execute("SELECT * FROM invalid_contacts;")
        invalid = cur.fetchall()
    conn.commit()
    return invalid

def get_page(conn, limit=5, offset=0):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM get_contacts_paginated(%s, %s);", (limit, offset))
        return cur.fetchall()

def delete(conn, fn=None, ln=None, ph=None):
    with conn.cursor() as cur:
        cur.execute("CALL delete_contact(%s, %s, %s);", (fn, ln, ph))
    conn.commit()

def main():
    conn = get_connection()
    setup(conn)

    upsert(conn, "Alice", "Smith", "+77771112233")
    upsert(conn, "Bob",   "Jones", "+77772223344")
    upsert(conn, "Alice", "Smith", "+70000000000")  # updates Alice

    invalid = bulk_insert(conn, [
        ("Carol", "White",  "+77773334455"),
        ("Dave",  "Brown",  "bad-phone"),       # invalid
        ("Eve",   "Davis",  "+77774445566"),
    ])
    print("Invalid entries:", invalid)

    print("Search 'ali':", search(conn, "ali"))
    print("Page 1:", get_page(conn, limit=3, offset=0))
    print("Page 2:", get_page(conn, limit=3, offset=3))

    delete(conn, ph="+77772223344")
    delete(conn, fn="Carol", ln="White")

    conn.close()

if __name__ == "__main__":
    main()