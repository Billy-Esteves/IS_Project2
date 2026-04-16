"""
MCP Server using FastMCP
Exposes: one tool, one resource, one prompt
Run with: python mcp_server.py
"""

from fastmcp import FastMCP
from crud_service import (
    create_book, read_book_list, update_book, delete_book, create_member, read_member_list, update_member, delete_member, borrow_book
)

mcp = FastMCP(name="SimpleAssistantServer")


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
    return(create_book(id, name, year, availability))


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

@mcp.tool()
def delete_all_members_tool(confirm: bool) -> str:
    """Delete all members and their borrowed books."""
    if confirm:
        raise PermissionError(
            "CRITICAL EXCEPTION: Mass deletion of all members and books is strictly forbidden! "
            "Operation aborted to prevent data loss."
        )
    
    return "Operation cancelled safely. The data is untouched."

@mcp.tool()
def borrow_book_tool(member_id: int, book_id: int) -> str:
    return borrow_book(member_id, book_id)


@mcp.tool()
def calculate_late_fee_tool(days_late: int) -> int:
    """
    Calculate the late fee in CENTS. 
    Accepts INT (full days) and returns INT (cents). Cost is 50 cents per day.
    """
    return days_late * 50

@mcp.tool()
def calculate_late_fee_float(days_late: float) -> str:
    """Calculate the late fee based on the number of days late (accepting float)."""
    if days_late < 0:
        return "Error: days_late cannot be negative."
    fee_per_day = 0.50
    total_fee = days_late * fee_per_day
    return f"Total late fee for {days_late:.2f} days late is ${total_fee:.2f}."


# ─── RESOURCE ────────────────────────────────────────────────────────────────
@mcp.resource("info://app")
def get_app_info() -> str:
    """Returns general information about this MCP server / app."""
    return (
        "SimpleLibraryAssistant v1.0\n"
        "Purpose: A MCP server with tools, resources, and prompt.\n"
        "Available tools: create_book_tool, read_book_list_tool, update_book_tool, delete_book_tool, create_member_tool, read_member_list_tool, update_member_tool, delete_member_tool\n"
        "Built with: FastMCP + Python\n"
    )


@mcp.resource("info://library_rules")
def get_library_rules() -> str:
    """Returns the library rules."""
    return (
        "Library Rules:\n"
        "1. Books can be borrowed for a maximum of 2 weeks.\n"
        "2. Late returns incur a fine of $0.50 per day.\n"
        "3. Please handle books with care and return them in good condition."
    )


# ─── PROMPT ──────────────────────────────────────────────────────────────────
@mcp.prompt()
def library_assistant_prompt(user_name: str = "User") -> str:
    """A system prompt that turns the LLM into a friendly library assistant."""
    return (
        f"You are a friendly and knowledgeable library assistant. "
        f"You are currently helping {user_name}. "
        "You can manage books and members using the available tools. "
        "You can also calculate late fees if needed."
        "Keep your tone warm, encouraging, and helpful."
    )



# ─── ENTRY POINT ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8002)

