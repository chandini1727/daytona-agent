import os
import requests
import time
from dotenv import load_dotenv
from e2b import Sandbox

load_dotenv()

def main():
    api_key = os.environ.get("E2B_API_KEY")
    if not api_key:
        print("❌ Please set E2B_API_KEY environment variable")
        return
        
    print("🚀 Initializing E2B Sandbox...")
    # This requires building a custom E2B template from your Dockerfile first using the E2B CLI.
    # For now, we spin up the default sandbox to demonstrate the flow.
    sandbox = Sandbox.create()
    
    print(f"✅ Sandbox created! ID: {sandbox.sandbox_id}")
    
    # Upload the voice agent code
    print("📤 Uploading pure_voice_agent.py...")
    with open("pure_voice_agent.py", "r") as f:
        sandbox.files.write("/pure_voice_agent.py", f.read())
        
    print("📦 Installing dependencies...")
    sandbox.commands.run("pip install fastapi uvicorn pydantic speechrecognition pypdf")
    sandbox.commands.run("sudo apt-get update && sudo apt-get install -y espeak ffmpeg")
        
    print("🏃 Starting the Voice Agent Server...")
    # Start the server in the background
    server_process = sandbox.commands.run("uvicorn pure_voice_agent:app --host 0.0.0.0 --port 8000", background=True)
    
    time.sleep(5)
    
    # Get the public hostname for port 8000
    public_url = sandbox.get_host(8000)
    print(f"🌍 Server is live at: https://{public_url}")
    
    print("🧹 Cleaning up sandbox...")
    sandbox.kill()
    print("✅ Done!")

if __name__ == "__main__":
    main()
