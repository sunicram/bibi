FROM python:3.11-slim

# Install system build dependencies for psycopg2 and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend files
COPY . .

EXPOSE 8000

# Start via start.sh to run migrations and seed data on startup
RUN chmod +x start.sh
CMD ["./start.sh"]
