FROM arm32v7/python:3.11-slim-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    vlc \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8888

# Set environment variable for VLC
ENV VLC_PLUGIN_PATH=/usr/lib/arm-linux-gnueabihf/vlc/plugins

# Run the application
CMD ["python", "app.py"] 