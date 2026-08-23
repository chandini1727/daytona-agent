import os
import requests
import time
from dotenv import load_dotenv
from daytona import Daytona, DaytonaConfig, CreateSandboxFromImageParams

load_dotenv()

def main():
    # Daytona API key is loaded automatically from environment variables
    # or you can pass it to DaytonaConfig explicitly.
    api_key = os.environ.get("DAYTONA_API_KEY")
    if not api_key:
        print("❌ Please set DAYTONA_API_KEY environment variable")
        return
        
    print("🚀 Initializing Daytona Client...")
    daytona = Daytona(DaytonaConfig(api_key=api_key))
    
    # Define parameters (pointing to your existing custom image or repo)
    params = CreateSandboxFromImageParams(
        language="python",
        image="chintalachyandini/my-openrouter-agent:voice3"
    )
    
    print("🏗️ Creating Daytona Sandbox...")
    sandbox = daytona.create(params)
    print(f"✅ Sandbox created! ID: {sandbox.id}")
    
    print("🏃 Starting the Voice Agent Server...")
    # Run the uvicorn command statelessly in the background
    sandbox.process.code_run('''
import subprocess
subprocess.Popen(["uvicorn", "pure_voice_agent:app", "--host", "0.0.0.0", "--port", "8000"])
''')
    
    # Wait for server to start
    time.sleep(5)
    
    print("🌍 Getting public preview URL...")
    # The Daytona Python SDK currently primarily supports processing code execution.
    # To get the preview URL programmatically, you would usually query the Daytona API 
    # for the sandbox details, but this is handled automatically via the Daytona CLI.
    print(f"👉 To test, expose the port: daytona preview-url {sandbox.id} --port 8000")
    try:
        print("🧹 Cleaning up sandbox...")
        daytona.delete(sandbox.id)
    except Exception as e:
        print(f"⚠️ Note: Auto-cleanup failed or requires manual deletion via 'daytona delete {sandbox.id}'")
    print("✅ Done!")

if __name__ == "__main__":
    main()
