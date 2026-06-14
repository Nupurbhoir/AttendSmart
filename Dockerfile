# Use official Python lightweight image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy the entire project directory into the container
COPY . /app

# Expose port 8000 for the API Gateway and Web UI
EXPOSE 8000

# Start the native Python server
CMD ["python3", "server.py"]
