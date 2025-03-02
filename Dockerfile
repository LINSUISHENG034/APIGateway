# Base image
FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy supervisord configuration
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy project files
COPY . .

# Create necessary directories for logs
RUN mkdir -p /var/log && touch /var/log/ai-proxy.err.log /var/log/ai-proxy.out.log

# Ensure data directory exists
RUN mkdir -p /app/data

# Expose port
EXPOSE 5000

# Run supervisord
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]