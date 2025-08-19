FROM python:3.12-slim

LABEL maintainer="itxlevicodez@gmail.com"

WORKDIR /app

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --upgrade pip && pip install uv

# Copy dependency files
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock

# Copy source code
COPY . /app

# Install dependencies
RUN uv sync --frozen

# Expose port
EXPOSE 8000

# Run the server - Smithery expects the app to be available at root
CMD ["uv", "run", "uvicorn", "server:mcp_server", "--host", "0.0.0.0", "--port", "8000"]