# Dockerfile for Schemathesis API Fuzz Testing with LLM Summarizer
#
# Build:
#   docker build -t schemathesis-runner .
#
# Run (with env file):
#   docker run --env-file ../.env -v $(pwd)/allure-results:/app/allure-results schemathesis-runner
#
# Run (with inline env):
#   docker run -e API_URL=https://api.example.com -e EMAIL=user@test.com -e PASSWORD=pass schemathesis-runner

FROM python:3.12-slim

LABEL maintainer="NoteTaker Team"
LABEL description="Schemathesis API fuzz testing with LLM-powered summarization"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install llama-cpp-python (CPU version for portability)
RUN pip install --no-cache-dir llama-cpp-python

# Copy application files
COPY run_schemathesis.py .

# Create directories
RUN mkdir -p allure-results models scripts

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV LLM_MODEL_PATH=/app/models/qwen2.5-0.5b-instruct-q4_0.gguf

# Download model (optional - comment out to reduce image size)
# RUN curl -L -o $LLM_MODEL_PATH \
#     "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_0.gguf"

# Default command
CMD ["python", "run_schemathesis.py"]

# Alternative: Run with summary
# CMD ["sh", "-c", "python run_schemathesis.py && python scripts/summarize_schemathesis_results.py --results allure-results"]
