# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY backend /app/backend

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=7860

# Expose the port (7860 is the default for Hugging Face)
EXPOSE 7860

# Start gunicorn
CMD ["gunicorn", "-c", "backend/gunicorn_conf.py", "backend.app.main:app"]
