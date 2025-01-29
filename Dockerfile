FROM python:3.10-slim

LABEL authors="jerry george"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory
WORKDIR /shortcast

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create a non-root user (to prevent Celery security warning)
RUN useradd -m celeryuser
USER celeryuser

# Expose port for Flask app
EXPOSE 5000

# Default command (for Flask app)
CMD ["gunicorn", "run:app"]
