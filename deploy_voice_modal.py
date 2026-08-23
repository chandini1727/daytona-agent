import os
import subprocess
import modal

# 1. Initialize the Modal App
app = modal.App("voice-agent-sandbox")

# 2. Use your custom voice agent Docker image tag
# (Make sure to build and push this tag first!)
byoi_image = modal.Image.from_registry("chintalachyandini/my-openrouter-agent:voice3")

# 3. Securely pass the OpenRouter API key
secrets = []
api_key = os.environ.get("OPENROUTER_API_KEY")
if api_key:
    secrets.append(modal.Secret.from_dict({"OPENROUTER_API_KEY": api_key}))

# 4. Create a serverless web server endpoint hosting port 8000
@app.function(image=byoi_image, secrets=secrets)
@modal.web_server(8000)
def web_terminal():
    print("🚀 Starting Pure Backend Voice Agent Server inside the Sandbox...")
    # Run the FastAPI server using uvicorn
    subprocess.run([
        "uvicorn", 
        "pure_voice_agent:app", 
        "--host", 
        "0.0.0.0", 
        "--port", 
        "8000"
    ])
