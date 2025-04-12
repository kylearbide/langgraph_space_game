# Use official Python 3.12 slim image
FROM python:3.12-slim-bookworm

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --upgrade "langgraph-cli[inmem]"

# Set working directory
WORKDIR /app

# Copy app files
COPY ./app /app

# Install dependencies
RUN pip install -e .

# Expose port 2024
EXPOSE 2024

# Run langgraph development server
CMD ["langgraph", "dev", "--port", "2024"]