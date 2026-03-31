

import csv
import psycopg2
from connect import get_connection, create_table


def insert_contact(name, phone):
    conn = get_connection()
    if not conn: return
    try:
        with conn:
            conn.cursor().execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (name, phone))
        print(f"[OK] Added '{name}'.")
    except psycopg2.errors.UniqueViolation:
        print(f"[WARN] Phone '{phone}' already exists.")
    finally:
        conn.close()


def insert_from_csv(filepath="contacts.csv"):
    conn = get_connection()
    if not conn: return
    inserted = skipped = 0
    try:
        with open(filepath, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    with conn:
                        conn.cursor().execute("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (row["name"].strip(), row["phone"].strip()))
                    inserted += 1
                except psycopg2.errors.UniqueViolation:
                    conn.rollback()
                    skipped += 1
        print(f"[OK] {inserted} inserted, {skipped} skipped.")
    except FileNotFoundError:
        print(f"[ERROR] File '{filepath}' not found.")
    finally:
        conn.close()


def search(name_filter=None, phone_prefix=None):
    conn = get_connection()
    if not conn: return
    try:
        with conn.cursor() as cur:
            if name_filter:
                cur.execute("SELECT id, name, phone FROM phonebook WHERE name ILIKE %s ORDER BY name", (f"%{name_filter}%",))
            elif phone_prefix:
                cur.execute("SELECT id, name, phone FROM phonebook WHERE phone LIKE %s ORDER BY name", (f"{phone_prefix}%",))
            else:
                cur.execute("SELECT id, name, phone FROM phonebook ORDER BY name")
            rows = cur.fetchall()
        if not rows:
            print("  (no contacts found)")
        else:
            print(f"\n  {'ID':<5} {'Name':<25} {'Phone':<20}")
            print("  " + "─" * 50)
            for r in rows:
                print(f"  {r[0]:<5} {r[1]:<25} {r[2]:<20}")
    finally:
        conn.close()


def update(name=None, phone=None, new_value=None, update_phone=True):
    conn = get_connection()
    if not conn: return
    try:
        with conn:
            with conn.cursor() as cur:
                if update_phone:
                    cur.execute("UPDATE phonebook SET phone=%s WHERE name ILIKE %s", (new_value, name))
                else:
                    cur.execute("UPDATE phonebook SET name=%s WHERE phone=%s", (new_value, phone))
                print("[OK] Updated." if cur.rowcount else "[WARN] No contact found.")
    except psycopg2.errors.UniqueViolation:
        print("[WARN] That value already exists.")
    finally:
        conn.close()


def delete(name=None, phone=None):
    conn = get_connection()
    if not conn: return
    try:
        with conn:
            with conn.cursor() as cur:
                if name:
                    cur.execute("DELETE FROM phonebook WHERE name ILIKE %s", (name,))
                else:
                    cur.execute("DELETE FROM phonebook WHERE phone=%s", (phone,))
                print(f"[OK] Deleted {cur.rowcount} contact(s)." if cur.rowcount else "[WARN] No contact found.")
    finally:
        conn.close()


def main():
    create_table()
    menu = """
  1. Add contact
  2. Import from CSV
  3. Show all / Search
  4. Update contact
  5. Delete contact
  0. Exit
"""
    while True:
        print(menu)
        choice = input("  Choice: ").strip()

        if choice == "1":
            name  = input("  Name  : ").strip()
            phone = input("  Phone : ").strip()
            insert_contact(name, phone)

        elif choice == "2":
            path = input("  CSV path [contacts.csv]: ").strip() or "contacts.csv"
            insert_from_csv(path)

        elif choice == "3":
            print("  a) All   b) By name   c) By phone prefix")
            sub = input("  Choose: ").strip().lower()
            if sub == "a":   search()
            elif sub == "b": search(name_filter=input("  Name filter: ").strip())
            elif sub == "c": search(phone_prefix=input("  Phone prefix: ").strip())

        elif choice == "4":
            print("  a) Update phone by name   b) Update name by phone")
            sub = input("  Choose: ").strip().lower()
            if sub == "a":
                update(name=input("  Name: ").strip(), new_value=input("  New phone: ").strip(), update_phone=True)
            elif sub == "b":
                update(phone=input("  Phone: ").strip(), new_value=input("  New name: ").strip(), update_phone=False)

        elif choice == "5":
            print("  a) By name   b) By phone")
            sub = input("  Choose: ").strip().lower()
            if sub == "a":
                name = input("  Name: ").strip()
                if input(f"  Delete '{name}'? (y/n): ").lower() == "y": delete(name=name)
            elif sub == "b":
                phone = input("  Phone: ").strip()
                if input(f"  Delete '{phone}'? (y/n): ").lower() == "y": delete(phone=phone)

        elif choice == "0":
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()