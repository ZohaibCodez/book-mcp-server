import json
import random
from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp_app = FastMCP(name="book-mcp-server", stateless_http=True)

with open("data/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    books_data = data["books"]

print(f"Loaded {len(books_data)} books")

# **********TOOLS**********


@mcp_app.tool(
    name="list_books",
    description="List all books",
)
def list_books() -> list[str]:
    """
    List all books
    """
    return [book["title"] for book in books_data]


@mcp_app.tool(
    name="total_books",
    description="Get total number of books",
)
def total_books() -> int:
    """
    Get total number of books
    """
    return len(books_data)


@mcp_app.tool(
    name="get_book_detail",
    description="Get book detail",
)
def get_book_detail(
    book_id: int,
) -> dict:
    """
    Get book detail
    Args:
        book_id: The id of the book
    Returns:
        A book dictionary
    """
    result = [
        book
        for book in books_data
        if str(book.get("book_id", "")).lower() == str(book_id).lower()
    ]

    if not result:
        raise ValueError(f"No book found with id: {book_id}")

    return result[0]


@mcp_app.tool(
    name="search_books",
    description="Search books by title",
)
def search_books(
    query: str = Field(description="A keyword to search in title"),
) -> list[dict]:
    """
    Search books by title
    Args:
        query: A keyword to search in title
    Returns:
        A list of books
    """
    result = [book for book in books_data if query.lower() in book["title"].lower()]

    if not result:
        raise ValueError(f"No book found with query: {query}")

    return result


@mcp_app.tool(
    name="recommend_book",
    description="Recommend a book based on the genre",
)
def recommend_book(genre: str = Field(description="The genre of the book")) -> dict:
    """
    Recommend a book based on the genre
    """
    candidates = [book for book in books_data if book["genre"].lower() == genre.lower()]
    if not candidates:
        raise ValueError(f"No books found in genre '{genre}'")
    return random.choice(candidates)


@mcp_app.tool(
    name="top_books",
    description="Get the top n books",
)
def top_books(n: int = Field(description="The number of books to get")) -> list[dict]:
    """
    Get the top n books
    """
    return sorted(books_data, key=lambda x: x["rating"], reverse=True)[:n]


@mcp_app.tool(
    name="random_book",
    description="Get a random book from the collection",
)
def random_book() -> dict:
    return random.choice(books_data)


# **********************8RESOURCES*********************


@mcp_app.resource(
    "book://collection",
    name="books_resource",
)
def books_resource() -> dict:
    """
    Get a book from the collection
    """
    return books_data


@mcp_app.resource(
    "book://collection/{book_id}",
    name="book_resource",
)
def book_resource(book_id: str) -> dict:
    """
    Get a book from the collection
    """
    result = [book for book in books_data if book_id.lower() in book["title"].lower()]

    if not result:
        raise ValueError(f"No book found with book_id: {book_id}")
    return result


@mcp_app.resource(
    "book://collection/genres",
    name="genres_resource",
)
def genres_resource() -> dict:
    """
    Get a book from the collection
    """
    return list(set([book.get("genre", "") for book in books_data]))


@mcp_app.resource(
    "book://collection/genres/{genre}",
    name="genre_books_resource",
)
def genre_books_resource(genre: str) -> dict:
    """
    Get a book from the collection
    """
    result = [
        book for book in books_data if book.get("genre", "").lower() == genre.lower()
    ]
    if not result:
        raise ValueError(f"No book found with genre: {genre}")
    return result


# **********PROMPTS**********


@mcp_app.prompt(
    name="Test_prompt",
    description="Test prompt",
)
def test_prompt(book_id: str = Field(description="Book ID or title")) -> str:
    return f"Test prompt: {book_id}"


@mcp_app.prompt(
    name="summarize_book_prompt",
    description="Summarize book details for a user-friendly response",
)
def summarize_book_prompt(
    book_id: str = Field(description="Book ID or title"),
) -> str:
    try:
        # Search for the book by ID or title
        result = [
            book
            for book in books_data
            if str(book.get("book_id", "")).lower() == str(book_id).lower()
            or book_id.lower() in book["title"].lower()
        ]

        if not result:
            return f"No book found with ID or title: {book_id}"

        book = result[0]
        return (
            f"📖 '{book['title']}' is a {book.get('genre', 'Unknown genre')} book "
            f"rated {book.get('rating', 'N/A')}/5, priced at ${book.get('price', 'N/A')}. "
            f"Availability: {'In stock' if book.get('in_stock_availability') == 'True' else 'Out of stock'}."
        )
    except Exception as e:
        return f"Error processing book: {str(e)}"


mcp_server = mcp_app.streamable_http_app()
