import os
import subprocess
import modal

# 1. Initialize the Modal app
app = modal.App("byoi-web-agent")

# 2. Point Modal directly to your existing Docker Hub image!
byoi_image = modal.Image.from_registry("chintalachyandini/my-openrouter-agent:1.0")

# 3. Securely pass the OpenRouter API key if it's set in your terminal
secrets = []
api_key = os.environ.get("OPENROUTER_API_KEY")
if api_key:
    secrets.append(modal.Secret.from_dict({"OPENROUTER_API_KEY": api_key}))

# 4. Create a web endpoint that hosts port 8000 (the port the voice agent uses)
@app.function(image=byoi_image, secrets=secrets)
@modal.web_server(8000)
def web_terminal():
    print("🚀 Starting Voice Agent Server from BYOI image...")
    # Modal ignores Dockerfile CMDs, so we explicitly run the server command here
    subprocess.run([
        "python", 
        "-m", 
        "uvicorn", 
        "pure_voice_agent:app", 
        "--host", 
        "0.0.0.0", 
        "--port", 
        "8000"
    ])
