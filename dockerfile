# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the initial database (if it exists) and application code
COPY logs/genset_data.db /app/logs/
COPY src/ ./src/
COPY data/ ./data/
COPY models/ ./models/
COPY reports/ ./reports/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8501

# Expose the port Streamlit uses
EXPOSE $PORT

# Command to run the app
CMD ["streamlit", "run", "src/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]