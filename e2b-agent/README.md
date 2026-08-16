# E2B Minimal BYOI Agent

This is a minimal Docker image designed to test E2B's custom image / Bring Your Own Image (BYOI) support.

## What the image does
- Uses `ubuntu:22.04` as the base image.
- Installs only `python3` and `curl`.
- Creates a `/workspace` directory as the working directory.
- Copies a simple standard library Python HTTP server to `/app/agent.py`.
- Runs the HTTP server on port 8080, serving `/` and `/health` endpoints.

## How to build it

Run the following command from this directory:

```bash
docker build -t my-e2b-agent:1.0 .
```

## How to run it locally

To run the container locally and map port 8080:

```bash
docker run --rm -p 8080:8080 my-e2b-agent:1.0
```

## How to test `/health` and `/`

With the container running locally, test the health endpoint:

```bash
curl http://localhost:8080/health
```
**Expected Output:**
```json
{"status": "ok"}
```

Test the root endpoint:

```bash
curl http://localhost:8080/
```
**Expected Output:**
```json
{"message": "E2B custom agent is running"}
```

## How to verify image requirements

Verify it is based on Ubuntu:
```bash
docker run --rm my-e2b-agent:1.0 cat /etc/os-release
```

Verify Python 3 is installed:
```bash
docker run --rm my-e2b-agent:1.0 python3 --version
```

Verify `/workspace` exists:
```bash
docker run --rm my-e2b-agent:1.0 ls -ld /workspace
```

## How to push it to Docker Hub

1. **Tag the image** with your Docker Hub username:
   ```bash
   docker tag my-e2b-agent:1.0 YOUR_DOCKERHUB_USERNAME/my-e2b-agent:1.0
   ```

2. **Log in to Docker Hub**:
   ```bash
   docker login
   ```

3. **Push the image**:
   ```bash
   docker push YOUR_DOCKERHUB_USERNAME/my-e2b-agent:1.0
   ```

## Next Step

The next step is to use the image with E2B `Template.fromImage()`.
