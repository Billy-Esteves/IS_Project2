"""
MCP Server using FastMCP
Exposes: one tool, one resource, one prompt
Run with: python mcp_server.py
"""

from fastmcp import FastMCP
from crud_service import (
    create_book, read_book_list, update_book, delete_book, create_member, read_member_list, update_member, delete_member
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

