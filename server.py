"""Book MCP Server

This module exposes tools, resources, and prompts for interacting with a
collection of books via the Model Context Protocol (MCP).

Refactors include:
- Clearer function and variable names
- Consistent and informative docstrings
- Type hints for better editor and static analysis support
- Centralized data loading and helper utilities
- Basic logging instead of print statements
"""

import json
import os
import logging
import random
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP
from pydantic import Field
import uvicorn


# Configure basic logging for visibility in server environments
logging.basicConfig(level=logging.INFO)


# Create the MCP application
mcp_app = FastMCP(name="book-mcp-server", stateless_http=True)


# -------------------------
# Data loading and helpers
# -------------------------

DATA_FILE_PATH: str = "data/data.json"


def _load_books_data(file_path: str) -> List[Dict[str, Any]]:
    """Load books data from a JSON file.

    Args:
        file_path: Relative or absolute path to the JSON file containing a
            top-level object with a "books" array.

    Returns:
        A list of book dictionaries as loaded from the file.
    """
    with open(file_path, "r", encoding="utf-8") as json_file:
        raw_data = json.load(json_file)
    return list(raw_data.get("books", []))


BOOKS_DATA: List[Dict[str, Any]] = _load_books_data(DATA_FILE_PATH)
logging.info("Loaded %d books", len(BOOKS_DATA))


def _to_lower(value: Any) -> str:
    """Safely convert a value to lowercase string for case-insensitive compares."""
    return str(value).lower()


def _find_books_by_id_or_title(identifier: str) -> List[Dict[str, Any]]:
    """Find books whose `book_id` matches (case-insensitive) or whose title contains the identifier.

    Args:
        identifier: A string that can be a `book_id` or a substring of the title.

    Returns:
        A list of matching book dicts. May be empty if no match.
    """
    identifier_l = _to_lower(identifier)
    return [
        book
        for book in BOOKS_DATA
        if _to_lower(book.get("book_id", "")) == identifier_l
        or identifier_l in _to_lower(book.get("title", ""))
    ]


def _filter_books_by_genre(genre: str) -> List[Dict[str, Any]]:
    """Return books that exactly match the provided genre (case-insensitive)."""
    genre_l = _to_lower(genre)
    return [book for book in BOOKS_DATA if _to_lower(book.get("genre", "")) == genre_l]


def _rating_as_float(book: Dict[str, Any]) -> float:
    """Retrieve the rating as a float, defaulting safely to 0.0 if missing/invalid."""
    value = book.get("rating", 0)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


# -----
# TOOLS
# -----


@mcp_app.tool(name="list_books", description="List the titles of all books")
def list_books() -> List[str]:
    """Return the list of all book titles in the catalog."""
    return [book.get("title", "") for book in BOOKS_DATA]


@mcp_app.tool(name="total_books", description="Get total number of books")
def total_books() -> int:
    """Return the number of books available in the catalog."""
    return len(BOOKS_DATA)


@mcp_app.tool(name="get_book_detail", description="Get details for a book by ID")
def get_book_detail(book_id: int) -> Dict[str, Any]:
    """Fetch a single book by numeric ID.

    Args:
        book_id: The integer ID of the target book.

    Returns:
        The first matching book dictionary.

    Raises:
        ValueError: If no book with the given ID exists.
    """
    book_id_l = _to_lower(book_id)
    result = [
        book for book in BOOKS_DATA if _to_lower(book.get("book_id", "")) == book_id_l
    ]

    if not result:
        raise ValueError(f"No book found with id: {book_id}")

    return result[0]


@mcp_app.tool(name="search_books", description="Search books by title keyword")
def search_books(
    query: str = Field(description="A keyword to search within the book title"),
) -> List[Dict[str, Any]]:
    """Search for books whose titles contain the provided query.

    Args:
        query: Keyword to match within titles (case-insensitive substring match).

    Returns:
        List of matching books.

    Raises:
        ValueError: If no matching books are found.
    """
    query_l = _to_lower(query)
    result = [
        book for book in BOOKS_DATA if query_l in _to_lower(book.get("title", ""))
    ]

    if not result:
        raise ValueError(f"No books found for query: {query}")

    return result


@mcp_app.tool(
    name="recommend_book",
    description="Recommend a random book from the requested genre",
)
def recommend_book(
    genre: str = Field(description="Genre to filter by, e.g., 'Fiction'"),
) -> Dict[str, Any]:
    """Recommend a random book for the specified genre.

    Raises:
        ValueError: If there are no books in the genre.
    """
    candidates = _filter_books_by_genre(genre)
    if not candidates:
        raise ValueError(f"No books found in genre '{genre}'")
    return random.choice(candidates)


@mcp_app.tool(name="top_books", description="Get the top N books by rating")
def top_books(
    n: int = Field(description="Number of books to return, sorted by rating desc"),
) -> List[Dict[str, Any]]:
    """Return the top N rated books.

    Args:
        n: Positive integer count of books to return.

    Raises:
        ValueError: If `n` is less than 1.
    """
    if n < 1:
        raise ValueError("n must be at least 1")
    return sorted(BOOKS_DATA, key=_rating_as_float, reverse=True)[:n]


@mcp_app.tool(
    name="random_book",
    description="Get a random book from the collection",
)
def random_book() -> Dict[str, Any]:
    """Return a single random book from the catalog."""
    return random.choice(BOOKS_DATA)


# ---------
# RESOURCES
# ---------


@mcp_app.resource("book://collection", name="books_resource")
def books_resource() -> List[Dict[str, Any]]:
    """Return the entire book collection."""
    return BOOKS_DATA


@mcp_app.resource("book://collection/{book_id}", name="book_resource")
def book_resource(book_id: str) -> List[Dict[str, Any]]:
    """Find books by ID (exact) or by title substring.

    Args:
        book_id: An ID or a fragment of the title to search for.

    Returns:
        A list of matching books.

    Raises:
        ValueError: If no matching book is found.
    """
    result = _find_books_by_id_or_title(book_id)
    if not result:
        raise ValueError(f"No book found for: {book_id}")
    return result


@mcp_app.resource("book://collection/genres", name="genres_resource")
def genres_resource() -> List[str]:
    """Return the unique list of genres in the collection."""
    return sorted({str(book.get("genre", "")) for book in BOOKS_DATA})


@mcp_app.resource("book://collection/genres/{genre}", name="genre_books_resource")
def genre_books_resource(genre: str) -> List[Dict[str, Any]]:
    """Return all books belonging to the specified genre.

    Raises:
        ValueError: If there are no books in the genre.
    """
    result = _filter_books_by_genre(genre)
    if not result:
        raise ValueError(f"No book found with genre: {genre}")
    return result


# -------
# PROMPTS
# -------


@mcp_app.prompt(name="Test_prompt", description="Test prompt")
def test_prompt(book_id: str = Field(description="Book ID or title")) -> str:
    """Basic echo prompt for quick connectivity checks."""
    return f"Test prompt: {book_id}"


@mcp_app.prompt(
    name="summarize_book_prompt",
    description="Summarize book details for a user-friendly response",
)
def summarize_book_prompt(
    book_id: str = Field(description="Book ID or title"),
) -> str:
    """Return a short natural-language summary of a book.

    The identifier can be either the exact `book_id` or a substring of the
    title. The first match will be summarized.
    """
    try:
        matches = _find_books_by_id_or_title(book_id)
        if not matches:
            return f"No book found with ID or title: {book_id}"

        book = matches[0]

        def _as_bool(value: Any) -> bool:
            text = _to_lower(value)
            return text in {"true", "1", "yes", "y"}

        availability = (
            "In stock"
            if _as_bool(book.get("in_stock_availability", False))
            else "Out of stock"
        )

        title = book.get("title", "Unknown title")
        genre = book.get("genre", "Unknown genre")
        rating = book.get("rating", "N/A")
        price = book.get("price", "N/A")

        return (
            f"'{title}' is a {genre} book rated {rating}/5, priced at ${price}. "
            f"Availability: {availability}."
        )
    except Exception as exc:  # Defensive: ensure prompt never raises
        return f"Error processing book: {exc}"


mcp_server = mcp_app.streamable_http_app()


def main() -> None:
    """Run the MCP server using uvicorn.

    Honors the PORT environment variable (defaults to 8000).
    """
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("server:mcp_server", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
