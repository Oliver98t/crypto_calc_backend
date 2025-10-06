# Build the image:
# docker build -t crypto-calc-backend .
#
# Run the container:
# docker run -p 8000:8000 crypto-calc-backend
#
# Run with environment variables:
# docker run -p 8000:8000 -e DEBUG=True -e SECRET_KEY=your-secret-key crypto-calc-backend
#
# Run in detached mode:
# docker run -d -p 8000:8000 --name crypto-calc crypto-calc-backend
#
# Open bash shell in container:
# docker run -it --entrypoint bash crypto-calc-backend
#
# Open bash shell in running container:
# docker exec -it <container_id_or_name> bash

# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["bash", "startup.sh"]
