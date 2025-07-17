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
COPY api_server.py ./
COPY start_api_server.py ./
COPY data/ ./data/
COPY models/ ./models/
COPY reports/ ./reports/
COPY supervisord.conf ./

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8501
ENV PYTHONPATH=/app/src

# Expose the ports for Streamlit and API server
EXPOSE 8501
EXPOSE 5000

# Start both Streamlit and API server using supervisor
CMD ["supervisord", "-c", "supervisord.conf"]