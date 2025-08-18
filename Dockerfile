FROM python:3.12-slim

LABEL maintainer="itxlevicodez@gmail.com"

WORKDIR /app

# Install uv (Python package manager)
RUN pip install --upgrade pip && pip install uv 

# Leverage build cache for dependencies
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock

# Copy metadata and module files required for editable build
COPY README.md /app/README.md
COPY LICENSE /app/LICENSE
COPY server.py /app/server.py
COPY data/ /app/data/

# Create and sync virtual environment from lockfile
RUN uv sync --frozen

## uvicorn is already declared in pyproject dependencies and installed by `uv sync`

# Copy application code
COPY . /app

EXPOSE 8000

# Start directly with uvicorn from the built virtualenv, honoring PORT if provided
CMD ["sh", "-c", "/app/.venv/bin/uvicorn server:mcp_server --host 0.0.0.0 --port ${PORT:-8000}"]