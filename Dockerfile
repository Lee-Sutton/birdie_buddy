# Use the official Python runtime as the base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    DEBUG=False \
    SECRET_KEY=django-insecure-@6y1-ec2mj7k5&whys=-j&*^2*ui*ez*(!%i@k3%pweabg6!(j \
    DB_NAME=birdie_buddy \
    DB_USER=rci_user \
    DB_PASSWORD=rci_password \
    DB_HOST=localhost \
    DB_PORT=5432 \
    OPENAI_API_KEY=build-time-placeholder

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements and install Python dependencies
COPY requirements.lock .

# Copy project files
COPY . .

# Install requirements
RUN pip install --no-cache-dir -r requirements.lock

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Expose the port that the app runs on
EXPOSE $PORT

# Command to run the application (migrations and collectstatic handled during deployment)
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 birdie_buddy.wsgi:application
