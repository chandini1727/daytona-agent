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

# Pass the OpenRouter token securely at runtime using: docker run -e OPENROUTER_API_KEY="..."

# Set the entrypoint to run Streamlit on port 8080
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]