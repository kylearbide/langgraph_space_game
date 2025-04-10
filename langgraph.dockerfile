# Use official Python 3.12 slim image
FROM python:3.12-slim

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --upgrade "langgraph-cli[inmem]"

# Set working directory
WORKDIR /app

# Copy app files
COPY ./app /app

# Expose port 2024
EXPOSE 2024

# Run langgraph development server
CMD ["langgraph", "dev", "--host", "0.0.0.0", "--port", "2024"]