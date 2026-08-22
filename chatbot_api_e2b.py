import os
import time
from e2b import Sandbox

# Using the keys you provided
e2b_api_key = os.environ.get("E2B_API_KEY", "e2b_c05b748432c449950aed6916f7b0c95294878d3d")
openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")

print("🚀 Starting E2B Sandbox with your BYOI Template...")
# We use the template you already built ('my-agent-template')
sandbox = Sandbox.create(
    template="my-agent-template", 
    api_key=e2b_api_key, 
    timeout=3600,
    envs={"OPENROUTER_API_KEY": openrouter_key}
)

print(f"Sandbox created successfully! ID: {sandbox.sandbox_id}")

print("📦 Installing FastAPI & OpenAI inside the Sandbox...")
# Install fastapi and openai inside the container
sandbox.commands.run("pip install fastapi[standard] openai", background=False)

# This is the exact code that will run INSIDE the E2B Sandbox
FASTAPI_CODE = """
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="Agent Chatbot API")

# Initialize OpenRouter Client
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.environ.get("OPENROUTER_API_KEY"),
)

class ChatRequest(BaseModel):
    message: str
    user_id: str = "anonymous"

@app.post("/chat")
def chat_webhook(request: ChatRequest):
    user_msg = request.message
    
    try:
        # Call the actual AI model via OpenRouter!
        completion = client.chat.completions.create(
          model="anthropic/claude-3.5-sonnet",
          messages=[
            {"role": "system", "content": "You are a helpful AI assistant running securely inside a NeevAI E2B sandbox. Keep answers helpful but concise."},
            {"role": "user", "content": user_msg}
          ]
        )
        agent_reply = completion.choices[0].message.content
    except Exception as e:
        agent_reply = f"Error calling AI: {str(e)}"
    
    return {"status": "success", "reply": agent_reply}

@app.get("/")
def home():
    html = '''
    <html>
        <body style="font-family: sans-serif; padding: 20px;">
            <h2>🤖 Sandbox Agent Webhook Tester</h2>
            <div id="chatbox" style="height: 400px; border: 1px solid #ccc; padding: 10px; overflow-y: scroll; margin-bottom: 10px; background: #f9f9f9;"></div>
            <input type="text" id="msg" placeholder="Type a message..." style="width: 70%; padding: 10px;" onkeydown="if(event.key === 'Enter') send()">
            <button onclick="send()" style="padding: 10px; width: 25%;">Send to Real AI</button>

            <script>
                async function send() {
                    const input = document.getElementById('msg');
                    const msg = input.value;
                    if(!msg) return;
                    
                    const chatbox = document.getElementById('chatbox');
                    chatbox.innerHTML += `<div style="margin-bottom: 8px;"><b>You:</b> ${msg}</div>`;
                    input.value = '';
                    chatbox.scrollTop = chatbox.scrollHeight;

                    try {
                        const response = await fetch('/chat', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ message: msg, user_id: 'browser_user' })
                        });
                        const data = await response.json();
                        
                        let replyText = data.reply.replace(/\\n/g, '<br>');
                        chatbox.innerHTML += `<div style="color: #0066cc; margin-bottom: 15px;"><b>Agent:</b> ${replyText}</div>`;
                        chatbox.scrollTop = chatbox.scrollHeight;
                    } catch (err) {
                        chatbox.innerHTML += `<div style="color: red; margin-bottom: 15px;"><b>Error:</b> Could not reach agent.</div>`;
                    }
                }
            </script>
        </body>
    </html>
    '''
    return HTMLResponse(content=html)
"""

print("📝 Writing API code into Sandbox...")
sandbox.files.write("/app/api.py", FASTAPI_CODE)

print("🌐 Starting FastAPI Webhook server on port 8000...")
sandbox.commands.run("fastapi run /app/api.py --port 8000 --host 0.0.0.0", background=True)

webhook_url = f"https://{sandbox.get_host(8000)}/chat"

print("\n" + "="*50)
print("✅ CHATBOT WEBHOOK IS LIVE!")
print("="*50)
print(f"Webhook POST URL: {webhook_url}")
print(f"Visual Tester URL: https://{sandbox.get_host(8000)}/")
print("\nPress Ctrl+C to shut down the Sandbox.")
print("="*50 + "\n")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down the sandbox...")
    sandbox.kill()
    print("Goodbye!")
