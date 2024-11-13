# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Update package list and install required dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev gcc netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file and install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["./entrypoint.sh"]
