FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "Waiting for Ollama to be ready..."\n\
until curl -s http://ollama:11434/api/tags > /dev/null 2>&1; do\n\
    echo "Ollama not ready yet, waiting..."\n\
    sleep 5\n\
done\n\
echo "Ollama is ready!"\n\
\n\
echo "Pulling required models..."\n\
curl -X POST http://ollama:11434/api/pull -d "{\"name\":\"nomic-embed-text\"}" -H "Content-Type: application/json" || echo "Failed to pull nomic-embed-text"\n\
curl -X POST http://ollama:11434/api/pull -d "{\"name\":\"smollm2:360m\"}" -H "Content-Type: application/json" || echo "Failed to pull smollm2:360m"\n\
\n\
echo "Starting the application..."\n\
exec python main.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["/app/start.sh"]