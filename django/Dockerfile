# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory to /app
WORKDIR /app

# Install system dependencies required for mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    libmariadb-dev \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file from the build context. Note: the file is at the root of context.
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the Django project
COPY . /app/

# Change directory to your Django project folder.
# In this example, your WSGI file is in /app/lol, so adjust accordingly if different.
WORKDIR /app

# Expose port 8000 (optional, since we already map ports in docker-compose)
EXPOSE 8000

# Start Gunicorn using the correct WSGI application
CMD ["gunicorn", "lol.wsgi:application", "--bind", "0.0.0.0:8000"]
