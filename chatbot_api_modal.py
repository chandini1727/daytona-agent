import modal
import os
from fastapi import FastAPI
from pydantic import BaseModel

# 1. Initialize the Modal app
app = modal.App("chatbot-api-agent")

# 2. Use your custom BYOI image (and make sure FastAPI is installed)
byoi_image = (
    modal.Image.from_registry("chintalachyandini/my-openrouter-agent:1.0")
    .pip_install("fastapi[standard]")
)

# 3. Create the FastAPI application
web_app = FastAPI(title="Agent Chatbot API")

# Define the structure of incoming messages from your frontend chat widget
class ChatRequest(BaseModel):
    message: str
    user_id: str = "anonymous"

# 4. Define the API Webhook endpoint
@web_app.post("/chat")
def chat_webhook(request: ChatRequest):
    """
    This webhook receives POST requests from your frontend chat widget.
    It securely processes the message inside the sandbox and returns the agent's response.
    """
    user_msg = request.message
    
    # ==========================================
    # 🤖 AGENT LOGIC GOES HERE
    # Here you would normally pass the `user_msg` to OpenRouter or your LLM.
    # We will just do a simple mock response to prove the webhook works!
    # ==========================================
    
    agent_reply = f"Hello {request.user_id}! I am your secure Sandbox Agent. I received your message: '{user_msg}'"
    
    return {
        "status": "success",
        "reply": agent_reply
    }

# 5. Expose the FastAPI app as a public Serverless Webhook on Modal
@app.function(image=byoi_image)
@modal.asgi_app()
def serve_chatbot_api():
    return web_app
