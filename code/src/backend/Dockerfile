# Use official Python image
FROM python:3.11.5

# Set working directory
WORKDIR /app

# Install system dependencies for psycopg2 and other libraries
RUN apt-get update && apt-get install -y libpq-dev gcc

# Copy requirements first to leverage Docker cache
COPY requirements.txt .env ./

# Create a virtual environment and install dependencies
RUN pip install -r requirements.txt

# Copy the entire backend code
COPY . .

# Note: Run pytest outside the Docker build process to avoid build failures

# Expose FastAPI port
EXPOSE 8000

# Run the FastAPI application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]