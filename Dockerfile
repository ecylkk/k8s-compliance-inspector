# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and fixtures
COPY inspector.py .
COPY bad-deployments.yaml .

# Expose the port Flask will run on
EXPOSE 8080

# Environment variable for the port (Render provides this)
ENV PORT=8080

# Run the inspector to generate the report and then start the web server
CMD ["python", "inspector.py"]
