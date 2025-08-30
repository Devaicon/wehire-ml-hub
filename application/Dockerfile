# Base image
FROM python:3.11-slim

# Set work directory inside container
WORKDIR /app

# Install dependencies
COPY application/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port (example: FastAPI/Flask on 8000)
EXPOSE 8000

# Start command (replace with your app’s entry point)
CMD ["python", "app.py"]
