import os
import json
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL_ID = "meta-llama/llama-3.3-70b-instruct"
PORT = int(os.environ.get("PORT", 8000))

conversation_history = [
    {"role": "system", "content": "You are a helpful, extremely concise, and friendly AI voice assistant. Since you are speaking out loud, keep your answers to 1 or 2 short sentences. Do not use markdown, code blocks, or emojis. Speak naturally."}
]

class VoiceAgentHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            try:
                with open('voice_ui.html', 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                user_msg = data.get('message', '')
                print(f"\n User said: {user_msg}")
                
                conversation_history.append({"role": "user", "content": user_msg})
                
                # Call OpenRouter API
                req = urllib.request.Request(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    },
                    data=json.dumps({
                        "model": MODEL_ID,
                        "messages": conversation_history
                    }).encode('utf-8')
                )
                
                print(" Thinking...")
                with urllib.request.urlopen(req) as response:
                    res_body = response.read()
                    res_json = json.loads(res_body.decode('utf-8'))
                    agent_reply = res_json['choices'][0]['message']['content']
                    
            except Exception as e:
                agent_reply = f"Sorry, I had an error talking to my brain. {str(e)}"
            
            print(f" Agent replied: {agent_reply}")
            conversation_history.append({"role": "assistant", "content": agent_reply})
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'reply': agent_reply}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run(server_class=HTTPServer, handler_class=VoiceAgentHandler):
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    print("="*50)
    print(f" VOICE AGENT SERVER STARTED on port {PORT}")
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("[WARNING] OPENROUTER_API_KEY environment variable is not set!")
        print("          Using the default fallback key (which may be depleted and throw HTTP 402).")
    print(f"Open http://localhost:{PORT} in your browser (Chrome/Edge)")
    print("="*50)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Server stopped.")

if __name__ == '__main__':
    run()
