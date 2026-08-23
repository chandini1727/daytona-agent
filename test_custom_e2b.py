import os
import time
from dotenv import load_dotenv
from e2b import Sandbox, Template

load_dotenv()

def main():
    api_key = os.environ.get("E2B_API_KEY")
    if not api_key:
        print("Please set E2B_API_KEY environment variable")
        return
        
    print("Initializing E2B Sandbox using YOUR custom template...")
    # E2B v2: Build the template directly in code using your Docker image
    print("Building template from Docker Hub image...")
    print("Building automatic template...")
    # 1. We build the template with strict configurations
    template = (
        Template()
        .from_image("chintalachyandini/my-openrouter-agent:voice4")
        
        # 2. BAKE THE API KEY: We embed the API key directly into the template
        .set_envs({"OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY", "")})
        
        # 3. FIX THE SNAPSHOT: We explicitly tell E2B to wait until port 8000 is open 
        # BEFORE taking the snapshot. This guarantees the port survives!
        .set_start_cmd(
            start_cmd="bash -c 'cd /app && uvicorn pure_voice_agent:app --host 0.0.0.0 --port 8000'",
            ready_cmd="curl -s -f http://localhost:8000/docs > /dev/null"
        )
    )
    
    build_info = Template.build(template, "my-openrouter-agent")
    template_id = build_info.template_id
    
    try:
        # ==========================================
        # NOW YOU CAN RUN IT AUTOMATICALLY FOREVER!
        # ==========================================
        # Because you built the template properly above, the sandbox will now automatically 
        # boot your server and securely expose port 8000 the second it is created!
        sandbox = Sandbox.create(template=template_id)
        print(f"Sandbox created! ID: {sandbox.sandbox_id}")
        
        print("Waiting 5 seconds for the automatic server to finish initializing...")
        time.sleep(5)
        
        # In E2B, ports are accessible via this hostname pattern:
        # https://<port>-<sandbox_id>.e2b.dev
        host_url = f"https://8000-{sandbox.sandbox_id}.e2b.dev"
        
        print("\n" + "="*50)
        print("YOUR AGENT IS DEPLOYED AND LIVE!")
        print(f"Test your API at: {host_url}/docs")
        print("="*50)
        print("\nThe sandbox will remain alive while this script is running.")
        print("Press Ctrl+C to shut it down and exit.")
        
        # Keep the script running to keep the sandbox alive for testing
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down by user request...")
    except Exception as e:
        print(f"Failed to create sandbox: {e}")
        print("Did you remember to build the template and update 'template_id' in this script?")
    
    finally:
        if 'sandbox' in locals():
            print("\nCleaning up sandbox...")
            sandbox.kill()
            print("Done!")

if __name__ == "__main__":
    main()
