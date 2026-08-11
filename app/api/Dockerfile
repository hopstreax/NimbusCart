# Official lightweight Python 3.12 base image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements file first for optimal Docker layer caching
COPY app/api/requirements.txt ./app/api/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r app/api/requirements.txt

# Copy application files (both app/api and app/frontend)
COPY app ./app

# Expose port 5000
EXPOSE 5000

# Ensure Python output is sent straight to terminal/logs without buffering
ENV PYTHONUNBUFFERED=1

# Run Flask application on container startup
CMD ["python", "app/api/app.py"]
