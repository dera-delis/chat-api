FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make entrypoint script executable
RUN chmod +x scripts/entrypoint.sh

# Expose port (Cloud Run uses PORT env var, defaults to 8000)
EXPOSE 8000

# Run migrations and start the application
ENTRYPOINT ["scripts/entrypoint.sh"]

