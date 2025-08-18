# book-mcp-server

![Python Version](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white) ![License: MIT](https://img.shields.io/badge/License-MIT-green.svg) ![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white) [![Stars](https://img.shields.io/github/stars/ZohaibCodez/book-mcp-server?style=social)](https://github.com/ZohaibCodez/book-mcp-server) ![Last Commit](https://img.shields.io/github/last-commit/ZohaibCodez/book-mcp-server) ![Issues](https://img.shields.io/github/issues/ZohaibCodez/book-mcp-server)

An MCP (Model Context Protocol) server exposing tools, resources, and prompts to browse, search, and recommend books from a local dataset. Built with Python 3.12, FastMCP, and uvicorn.

## Table of Contents
- Overview
- Features
- Data
- Quickstart (Local)
- Docker
- Smithery AI Deployment
- Project Layout
- Development
- License
- Contact

## 📘 Overview
This server provides a clean set of MCP tools and resources for book discovery tasks (listing, search, recommendations, summarization). It’s designed to be easy to run locally, containerize, and deploy, with a professional code structure, type hints, and robust docstrings.

## ✨ Features
- Tools
  - `list_books`: Return all book titles
  - `total_books`: Return total number of books
  - `get_book_detail`: Fetch details for a book by ID
  - `search_books`: Search books by title keyword
  - `recommend_book`: Recommend a random book from a given genre
  - `top_books`: Return Top-N books by rating
  - `random_book`: Pick a random book
- Resources
  - `book://collection`: Entire dataset
  - `book://collection/{book_id}`: Match by ID (exact) or title substring
  - `book://collection/genres`: Unique genres
  - `book://collection/genres/{genre}`: Books by a specific genre
- Prompts
  - `Test_prompt`
  - `summarize_book_prompt`

## 🗂️ Data
- Source: `data/data.json`
- Expected format: a top-level object with a `books` array.

## 🚀 Quickstart (Local)
Prerequisites:
- Python 3.12+
- Optional: `uv` for fast installs

Using uv (recommended):
```bash
uv sync
uv run book-mcp-server
# or
uv run uvicorn server:mcp_server --host 0.0.0.0 --port 8000
```

Using pip (editable install):
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
. .venv/bin/activate

pip install -U pip
pip install -e .

book-mcp-server
# or
uvicorn server:mcp_server --host 0.0.0.0 --port 8000
```

Environment variables:
- `PORT` (default: `8000`)

## 🐳 Docker
Build and run a production image:
```bash
docker build -t book-mcp-server .
docker run --rm -p 8000:8000 --name book-mcp book-mcp-server
```

Developer image with hot reload:
```bash
# Build
docker build -f Dockerfile.dev -t book-mcp-dev .

# Windows (cmd)
docker run --rm -it -p 8000:8000 -v %cd%:/app book-mcp-dev

# Linux/macOS (bash)
docker run --rm -it -p 8000:8000 -v "$(pwd)":/app book-mcp-dev
```

## 🧠 Smithery AI Deployment
Add a `smithery.yaml` next to your `Dockerfile`:
```yaml
version: 1
start:
  command: ["book-mcp-server"]
  port: 8000
```

Alternatively, run uvicorn directly:
```yaml
version: 1
start:
  command: ["uvicorn", "server:mcp_server", "--host", "0.0.0.0", "--port", "8000"]
  port: 8000
```

Guidance: see Smithery docs: [Project Configuration Guide](https://smithery.ai/docs/build/project-config).

## 📁 Project Layout
```
book-mcp-server/
├─ server.py           # MCP app (tools, resources, prompts)
├─ data/data.json      # Local dataset of books
├─ pyproject.toml      # Project metadata and dependencies
├─ Dockerfile          # Production image
├─ Dockerfile.dev      # Dev image (hot reload)
├─ uv.lock             # uv lockfile
└─ LICENSE             # MIT License
```

## 🛠️ Development
- Clean code: type hints, guard clauses, descriptive naming
- Live reload:
```bash
uv run uvicorn server:mcp_server --host 0.0.0.0 --port 8000 --reload
```

## ⚖️ License
MIT — see `LICENSE`.

## 📫 Contact
- Author: Zohaib Khan
- GitHub: [ZohaibCodez](https://github.com/ZohaibCodez)
- Email: itxlevicodez@gmail.com
