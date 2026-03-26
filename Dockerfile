# Use a lightweight Python image
FROM python:3.11-slim

# Copy the local code to the container image
WORKDIR /app
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup
# Using 4 threads to handle more requests
CMD exec gunicorn --bind :$PORT --workers 1 --threads 4 --timeout 0 main:app