import sqlite3


# ─── Database Connect ───────────────────────────────────────────
conn = sqlite3.connect("app.db", check_same_thread=False)
cursor = conn.cursor()

# ─── Database Setup ─────────────────────────────────────────────
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    year INTEGER,
    availability BOOLEAN
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS borrowed_books (
    member_id INTEGER,
    book_id INTEGER,
    FOREIGN KEY(member_id) REFERENCES members(id),
    FOREIGN KEY(book_id) REFERENCES books(id)
)
""")

conn.commit()


# ─── CRUD Functions ────────────────────────────────────────────────────────────────
def create_book(id: int, name: str, year: int, availability: bool):
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO books (id, name, year, availability) VALUES (?, ?, ?, ?)",
            (id, name, year, availability)
        )
        conn.commit()
        return {"status": "Book created"}
    except Exception as e:
        return {"error": str(e)}

def read_book_list():
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    return [
        {"id": r[0], "name": r[1], "year": r[2], "availability": r[3]}
        for r in rows
    ]

def update_book(id: int, name: str, year: int, availability: bool):
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE books SET name=?, year=?, availability=? WHERE id=?",
        (name, year, availability, id)
    )
    conn.commit()
    return {"status": "Book updated"}

def delete_book(id: int):
    cursor = conn.cursor()

    cursor.execute("DELETE FROM books WHERE id=?", (id,))
    conn.commit()
    return {"status": "Book deleted"}


def create_member(id: int, name: str, borrowed_books: list[int]):
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO members (id, name) VALUES (?, ?)",
            (id, name)
        )

        for book_id in borrowed_books:
            cursor.execute(
                "INSERT INTO borrowed_books (member_id, book_id) VALUES (?, ?)",
                (id, book_id)
            )

        conn.commit()
        return {"status": "Member created"}
    except Exception as e:
        return {"error": str(e)}

def read_member_list():
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()

    result = []
    for m in members:
        cursor.execute(
            "SELECT book_id FROM borrowed_books WHERE member_id=?",
            (m[0],)
        )
        books = [b[0] for b in cursor.fetchall()]

        result.append({
            "id": m[0],
            "name": m[1],
            "borrowed_books": books
        })

    return result

def update_member(id: int, name: str, borrowed_books: list[int]):
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE members SET name=? WHERE id=?",
        (name, id)
    )

    cursor.execute("DELETE FROM borrowed_books WHERE member_id=?", (id,))

    for book_id in borrowed_books:
        cursor.execute(
            "INSERT INTO borrowed_books (member_id, book_id) VALUES (?, ?)",
            (id, book_id)
        )

    conn.commit()
    return {"status": "Member updated"}

def delete_member(id: int):
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM borrowed_books WHERE member_id=?", (id,))
    cursor.execute("DELETE FROM members WHERE id=?", (id,))
    conn.commit()
    return {"status": "Member deleted"}
