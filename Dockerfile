FROM arm32v7/python:3.11-slim-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    vlc-bin \
    libvlc5 \
    vlc-plugin-base \
    python3-vlc \
    alsa-utils \
    # pulseaudio \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV VLC_PLUGIN_PATH=/usr/lib/arm-linux-gnueabihf/vlc/plugins

# Expose port
EXPOSE 8888

# Create startup script
RUN echo '#!/bin/bash\n\
trap "exit" SIGTERM\n\
python app.py &\n\
PID=$!\n\
wait $PID\n\
trap - SIGTERM\n\
wait $PID\n\
EXIT_STATUS=$?\n\
exit $EXIT_STATUS' > /app/start.sh && \
    chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]