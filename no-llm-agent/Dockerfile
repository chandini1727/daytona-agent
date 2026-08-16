FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y python3 curl && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /app

WORKDIR /workspace

COPY agent.py /app/agent.py

CMD ["python3", "/app/agent.py"]
