import subprocess
import time
import requests
import os

def main():
    print("🚀 Initializing Modal Deployment...")
    # Modal handles API keys automatically from ~/.modal.toml after running `modal setup`
    
    # We will spawn the modal deployment in a subprocess
    print("🏃 Deploying and starting the Voice Agent Server...")
    # Add PYTHONIOENCODING to prevent Modal from crashing when printing emojis on Windows
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    process = subprocess.Popen(
        ["python", "-m", "modal", "serve", "deploy_voice_modal.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        env=env
    )
    
    public_url = None
    print("🌍 Waiting for public URL...")
    
    # Read the output to find the generated URL
    while True:
        line = process.stdout.readline()
        if not line:
            break
        print(f"[Modal] {line.strip()}")
        if "Created web_server =>" in line:
            # Extract the URL
            parts = line.split("=>")
            if len(parts) > 1:
                public_url = parts[1].strip()
                break
                
    if public_url:
        print(f"\n✅ Server is live at: {public_url}")
        print("👉 You can now test this URL in Hoppscotch!")
        
        try:
            print("⏳ Press Ctrl+C to stop the server...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
            
    print("\n🧹 Cleaning up sandbox...")
    process.terminate()
    print("✅ Done!")

if __name__ == "__main__":
    main()
