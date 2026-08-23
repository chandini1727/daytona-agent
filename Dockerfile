# Platform-version: v0.1.2
# Custom Chatbot Agent powered by OpenRouter
# Uses a robust base with essential system utilities like the Claude Code template.

FROM python:3.12-slim

# UTF-8 locale so a tmux client started in the sandbox comes up in UTF-8 mode
ENV LANG=C.UTF-8
ENV IS_SANDBOX=1

# Common dev toolset Claude Code shells out to; Python comes from the base image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git openssh-client ca-certificates sudo \
        curl wget jq \
        ripgrep fd-find tree \
        zip unzip tar \
        less vim nano \
        tmux ncurses-term \
        build-essential cmake pkg-config \
        ffmpeg \
        espeak \
    && ln -s "$(command -v fdfind)" /usr/local/bin/fd \
    && rm -rf /var/lib/apt/lists/*

# Preconfigure tmux with 256-color terminfo and RGB passthrough
RUN printf '%s\n' \
        'set -g default-terminal "tmux-256color"' \
        'set -as terminal-features ",xterm-256color:RGB"' \
        'set -g history-limit 50000' \
        > /etc/tmux.conf

# Setup working directories
RUN mkdir -p /workspace /app
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the agent application code
COPY app.py .
COPY terminal_agent.py .
COPY voice_agent_server.py .
COPY voice_ui.html .
COPY pure_voice_agent.py .

# Pass the OpenRouter token securely at runtime using: docker run -e OPENROUTER_API_KEY="..."

# Expose the voice agent server port
EXPOSE 8000

# Set the entrypoint to run the FastAPI voice agent server
CMD ["bash", "-c", "cd /app && uvicorn pure_voice_agent:app --host 0.0.0.0 --port 8000"]