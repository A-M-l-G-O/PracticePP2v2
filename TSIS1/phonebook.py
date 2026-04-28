import csv
import json
import sys
from datetime import date, datetime

import psycopg2
from connect import get_connection

def _json_serial(obj):
    """JSON serializer for date objects."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def _print_contacts(rows):
    """Pretty-print a list of contact tuples."""
    if not rows:
        print("  (no results)")
        return
    header = f"{'ID':<5} {'Name':<20} {'Email':<25} {'Birthday':<12} {'Group':<10} {'Phones'}"
    print(header)
    print("-" * len(header))
    for row in rows:
        cid, name, email, birthday, group, phones = row
        print(f"{str(cid):<5} {str(name):<20} {str(email or ''):<25} "
              f"{str(birthday or ''):<12} {str(group or ''):<10} {phones or ''}")


def get_or_create_group(cur, group_name: str) -> int:
    """Return group id, creating the group if needed."""
    cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (group_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
    return cur.fetchone()[0]


def filter_by_group(conn):
    """Show contacts that belong to a chosen group."""
    with conn.cursor() as cur:
        cur.execute("SELECT name FROM groups ORDER BY name")
        groups = [r[0] for r in cur.fetchall()]

    print("\nAvailable groups:")
    for i, g in enumerate(groups, 1):
        print(f"  {i}. {g}")
    choice = input("Enter group name: ").strip()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.name, c.email, c.birthday, g.name AS grp,
                   STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            LEFT JOIN phones p ON p.contact_id = c.id
            WHERE g.name ILIKE %s
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY c.name
        """, (choice,))
        rows = cur.fetchall()

    print(f"\nContacts in group '{choice}':")
    _print_contacts(rows)


def search_by_email(conn):
    """Partial email search."""
    query = input("Enter email fragment to search: ").strip()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.name, c.email, c.birthday, g.name,
                   STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ')
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            LEFT JOIN phones p ON p.contact_id = c.id
            WHERE c.email ILIKE %s
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY c.name
        """, (f"%{query}%",))
        rows = cur.fetchall()
    print(f"\nResults for email fragment '{query}':")
    _print_contacts(rows)


def sort_contacts(conn):
    """List all contacts sorted by a chosen field."""
    print("\nSort by: 1) name  2) birthday  3) date added (id)")
    choice = input("Choose [1/2/3]: ").strip()
    order_map = {"1": "c.name", "2": "c.birthday", "3": "c.id"}
    order = order_map.get(choice, "c.name")

    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT c.id, c.name, c.email, c.birthday, g.name,
                   STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ')
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            LEFT JOIN phones p ON p.contact_id = c.id
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY {order}
        """)
        rows = cur.fetchall()
    _print_contacts(rows)


def paginated_navigation(conn, page_size: int = 5):
    """Navigate contacts page by page using the DB's paginate_contacts function."""
    page = 0
    while True:
        offset = page * page_size
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM paginate_contacts(%s, %s)", (page_size, offset))
            rows = cur.fetchall()

        print(f"\n--- Page {page + 1} ---")
        _print_contacts(rows)

        if not rows:
            print("(end of contacts)")

        cmd = input("\n[n]ext  [p]rev  [q]uit: ").strip().lower()
        if cmd == "n":
            if rows:
                page += 1
            else:
                print("Already at the last page.")
        elif cmd == "p":
            if page > 0:
                page -= 1
            else:
                print("Already on the first page.")
        elif cmd == "q":
            break

def export_to_json(conn, filename: str = "contacts_export.json"):
    """Export all contacts (with phones and group) to a JSON file."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.name, c.email,
                   c.birthday::TEXT,
                   g.name AS group_name,
                   COALESCE(
                       JSON_AGG(
                           JSON_BUILD_OBJECT('phone', p.phone, 'type', p.type)
                       ) FILTER (WHERE p.id IS NOT NULL),
                       '[]'
                   ) AS phones
            FROM contacts c
            LEFT JOIN groups g ON c.group_id = g.id
            LEFT JOIN phones p ON p.contact_id = c.id
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY c.name
        """)
        rows = cur.fetchall()

    data = [
        {
            "id": r[0], "name": r[1], "email": r[2],
            "birthday": r[3], "group": r[4], "phones": r[5]
        }
        for r in rows
    ]
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=_json_serial, ensure_ascii=False)
    print(f"Exported {len(data)} contacts to '{filename}'.")


def import_from_json(conn, filename: str = "contacts_export.json"):
    """Import contacts from a JSON file with duplicate handling."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return

    inserted = skipped = overwritten = 0
    with conn.cursor() as cur:
        for contact in data:
            name = contact.get("name", "").strip()
            if not name:
                continue

            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            existing = cur.fetchone()

            if existing:
                print(f"Duplicate found: '{name}'")
                action = input("  [s]kip / [o]verwrite: ").strip().lower()
                if action != "o":
                    skipped += 1
                    continue
                contact_id = existing[0]
                group_id = get_or_create_group(cur, contact.get("group") or "Other")
                cur.execute("""
                    UPDATE contacts
                    SET email=%s, birthday=%s, group_id=%s
                    WHERE id=%s
                """, (contact.get("email"), contact.get("birthday"), group_id, contact_id))
                cur.execute("DELETE FROM phones WHERE contact_id=%s", (contact_id,))
                overwritten += 1
            else:
                group_id = get_or_create_group(cur, contact.get("group") or "Other")
                cur.execute("""
                    INSERT INTO contacts (name, email, birthday, group_id)
                    VALUES (%s, %s, %s, %s) RETURNING id
                """, (name, contact.get("email"), contact.get("birthday"), group_id))
                contact_id = cur.fetchone()[0]
                inserted += 1

            for ph in contact.get("phones") or []:
                cur.execute("""
                    INSERT INTO phones (contact_id, phone, type)
                    VALUES (%s, %s, %s)
                """, (contact_id, ph.get("phone"), ph.get("type")))

    conn.commit()
    print(f"Import done — inserted: {inserted}, overwritten: {overwritten}, skipped: {skipped}.")


def import_from_csv(conn, filename: str = "contacts.csv"):
    """Extended CSV importer supporting email, birthday, group, and phone type."""
    try:
        with open(filename, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return

    inserted = skipped = 0
    with conn.cursor() as cur:
        for row in rows:
            name = row.get("name", "").strip()
            if not name:
                continue

            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            existing = cur.fetchone()
            if existing:
                print(f"Skipping duplicate from CSV: '{name}'")
                skipped += 1
                continue

            group_id = get_or_create_group(cur, row.get("group") or "Other")
            birthday = row.get("birthday") or None
            cur.execute("""
                INSERT INTO contacts (name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s) RETURNING id
            """, (name, row.get("email") or None, birthday, group_id))
            contact_id = cur.fetchone()[0]

            phone = row.get("phone", "").strip()
            phone_type = row.get("phone_type", "mobile").strip()
            if phone:
                cur.execute("""
                    INSERT INTO phones (contact_id, phone, type)
                    VALUES (%s, %s, %s)
                """, (contact_id, phone, phone_type))
            inserted += 1

    conn.commit()
    print(f"CSV import done — inserted: {inserted}, skipped: {skipped}.")


def call_add_phone(conn):
    name = input("Contact name: ").strip()
    phone = input("Phone number: ").strip()
    ptype = input("Type (home/work/mobile): ").strip()
    with conn.cursor() as cur:
        cur.callproc("add_phone", [name, phone, ptype])
    conn.commit()
    print("Phone added.")


def call_move_to_group(conn):
    name = input("Contact name: ").strip()
    group = input("Target group name: ").strip()
    with conn.cursor() as cur:
        cur.callproc("move_to_group", [name, group])
    conn.commit()
    print("Contact moved.")


def call_search_contacts(conn):
    query = input("Search query (name / email / phone): ").strip()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", (query,))
        rows = cur.fetchall()
    print(f"\nSearch results for '{query}':")
    _print_contacts(rows)


MENU = """
========== PhoneBook Extended ==========
 1.  Filter contacts by group
 2.  Search contacts by email
 3.  Sort and list all contacts
 4.  Paginated navigation
 5.  Export contacts to JSON
 6.  Import contacts from JSON
 7.  Import contacts from CSV
 8.  Add phone number (stored procedure)
 9.  Move contact to group (stored procedure)
10.  Search contacts — all fields (DB function)
 0.  Exit
========================================="""


def main():
    try:
        conn = get_connection()
    except Exception as e:
        print(f"Cannot connect to database: {e}")
        sys.exit(1)

    print("Connected to PhoneBook database.")

    action_map = {
        "1":  filter_by_group,
        "2":  search_by_email,
        "3":  sort_contacts,
        "4":  paginated_navigation,
        "5":  export_to_json,
        "6":  import_from_json,
        "7":  import_from_csv,
        "8":  call_add_phone,
        "9":  call_move_to_group,
        "10": call_search_contacts,
    }

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        handler = action_map.get(choice)
        if handler:
            try:
                handler(conn)
            except psycopg2.Error as db_err:
                conn.rollback()
                print(f"Database error: {db_err.pgerror or db_err}")
            except Exception as err:
                print(f"Error: {err}")
        else:
            print("Invalid option. Please try again.")

    conn.close()


if __name__ == "__main__":
    main()
