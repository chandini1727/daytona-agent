# E2B BYOI Proof of Concept: No-LLM Rule-Based Agent

This repository contains a deterministic, rule-based agent built entirely using Python's standard library. The purpose of this agent is to validate E2B's "Bring Your Own Image" (BYOI) functionality without needing any API keys, LLMs, or complex frameworks.

## Complete Flow

```text
Custom Docker Image
       ↓
Docker Hub
       ↓
E2B fromImage()
       ↓
E2B Template
       ↓
E2B start command
       ↓
E2B ready command
       ↓
E2B snapshot
       ↓
Sandbox.create()
       ↓
No-LLM Agent
```

This agent does **not** use an LLM. It listens on port `8080` and only responds to specific, pre-programmed endpoints (`/health`, `/`, and `/run` with predefined commands).

## How to Build

Build the Docker image locally:
```bash
docker build -t no-llm-agent:1.0 .
```

## How to Run Locally

Run the image and map port 8080:
```bash
docker run --rm -p 8080:8080 no-llm-agent:1.0
```

## Local Tests

Once the container is running, test the endpoints:

**1. Health Endpoint:**
```bash
curl http://localhost:8080/health
```

**2. Root Endpoint:**
```bash
curl http://localhost:8080/
```

**3. Run Command (System Info):**
```bash
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{"command":"system info"}'
```

**4. Run Command (Workspace Files):**
```bash
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{"command":"workspace files"}'
```

## E2B Usage

Once the image is pushed to Docker Hub (`YOUR_DOCKERHUB_USERNAME/no-llm-agent:1.0`), use it in your E2B template configuration like so:

```python
# e2b_template.py example
from e2b import Template

template = Template.fromImage("YOUR_DOCKERHUB_USERNAME/no-llm-agent:1.0")

template.setStartCmd(
    "python3 /app/agent.py",
    "curl -s http://localhost:8080/health"
)
```

## E2B Verification Checklist
When testing with E2B, verify the following:
1. E2B successfully pulls the custom image.
2. E2B successfully identifies the Ubuntu distribution.
3. The template builds successfully.
4. The start command launches the agent.
5. The ready command (`curl -s http://localhost:8080/health`) succeeds.
6. E2B creates a sandbox from the template.
7. The agent is already running when the sandbox is created.
8. `/health` returns HTTP 200.
9. `/` returns the agent status.
10. `/run` can execute the predefined agent operations.
11. `/workspace` exists.
