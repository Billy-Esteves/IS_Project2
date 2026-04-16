"""
MCP Server using FastMCP
Exposes: one tool, one resource, one prompt
Run with: python mcp_server.py
"""

from fastmcp import FastMCP
from fastapi import FastAPI
import sqlite3

app = FastAPI()

mcp = FastMCP(name="SimpleAssistantServer")


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
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    return [
        {"id": r[0], "name": r[1], "year": r[2], "availability": r[3]}
        for r in rows
    ]

def update_book(id: int, name: str, year: int, availability: bool):
    cursor.execute(
        "UPDATE books SET name=?, year=?, availability=? WHERE id=?",
        (name, year, availability, id)
    )
    conn.commit()
    return {"status": "Book updated"}

def delete_book(id: int):
    cursor.execute("DELETE FROM books WHERE id=?", (id,))
    conn.commit()
    return {"status": "Book deleted"}


def create_member(id: int, name: str, borrowed_books: list[int]):
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
    cursor.execute("DELETE FROM borrowed_books WHERE member_id=?", (id,))
    cursor.execute("DELETE FROM members WHERE id=?", (id,))
    conn.commit()
    return {"status": "Member deleted"}


# ─── TOOLS ────────────────────────────────────────────────────────────────────
@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> str:
    """Calculate the Body Mass Index (BMI) given weight in kg and height in meters."""
    if height_m <= 0:
        return "Error: height must be greater than 0."
    bmi = weight_kg / (height_m ** 2)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return f"BMI: {bmi:.2f} — Category: {category}"

@mcp.tool()
def create_book_tool(id: int, name: str, year: int, availability: bool):
    return str(create_book(id, name, year, availability))


@mcp.tool()
def read_book_list_tool():
    return(read_book_list())

@mcp.tool()
def update_book_tool(id: int, name: str, year: int, availability: bool):
    """Update a book's information."""
    return str(update_book(id, name, year, availability))


@mcp.tool()
def delete_book_tool(id: int):
    """Delete a book by ID."""
    return str(delete_book(id))



@mcp.tool()
def create_member_tool(id: int, name: str, borrowed_books: list[int]):
    """Create a new member with optional borrowed books."""
    return str(create_member(id, name, borrowed_books))


@mcp.tool()
def read_member_list_tool():
    """Get all members and their borrowed books."""
    return read_member_list()


@mcp.tool()
def update_member_tool(id: int, name: str, borrowed_books: list[int]):
    """Update a member's name and borrowed books."""
    return str(update_member(id, name, borrowed_books))

@mcp.tool()
def delete_member_tool(id: int):
    """Delete a member by ID."""
    return str(delete_member(id))


# ─── CRUD API ────────────────────────────────────────────────────────────────
@app.post("/books")
def create_book_api(book: dict):
    return create_book(
        book["id"],
        book["name"],
        book["year"],
        book["availability"]
    )

@app.get("/books")
def get_books():
    return read_book_list()

@app.put("/books/{id}")
def update_book_api(id: int, book: dict):
    return update_book(
        id,
        book["name"],
        book["year"],
        book["availability"]
    )

@app.delete("/books/{id}")
def delete_book_api(id: int):
    return delete_book(id)

@app.post("/members")
def create_member_api(member: dict):
    return create_member(
        member["id"],
        member["name"],
        member.get("borrowed_books", [])
    )

@app.get("/members")
def get_members():
    return read_member_list()

@app.put("/members/{id}")
def update_member_api(id: int, member: dict):
    return update_member(
        id,
        member["name"],
        member.get("borrowed_books", [])
    )

@app.delete("/members/{id}")
def delete_member_api(id: int):
    return delete_member(id)


# ─── RESOURCE ────────────────────────────────────────────────────────────────
@mcp.resource("info://app")
def get_app_info() -> str:
    """Returns general information about this MCP server / app."""
    return (
        "SimpleAssistantServer v1.0\n"
        "Purpose: Demo MCP server with a tool, resource, and prompt.\n"
        "Available tool: calculate_bmi\n"
        "Built with: FastMCP + Python\n"
    )


# ─── PROMPT ──────────────────────────────────────────────────────────────────
@mcp.prompt()
def health_advisor_prompt(user_name: str = "User") -> str:
    """A system prompt that turns the LLM into a friendly health advisor."""
    return (
        f"You are a friendly and knowledgeable health advisor. "
        f"You are currently helping {user_name}. "
        "You can calculate BMI using the `calculate_bmi` tool. "
        "Always remind users that your advice is informational only and not a substitute "
        "for professional medical guidance. Keep your tone warm and encouraging."
    )



# ─── ENTRY POINT ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8002)
