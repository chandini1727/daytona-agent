import http.server
import json
import socketserver
import os
import sys

PORT = 8080

class AgentHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "agent": "no-llm-agent"
            }).encode('utf-8'))
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "agent": "no-llm-agent",
                "status": "running",
                "message": "Agent is running successfully"
            }).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/run':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.end_headers()
                return

            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                command = data.get('command', '')
                
                result = ""
                
                if command == 'list files' or command == 'workspace files':
                    try:
                        result = str(os.listdir('/workspace'))
                    except Exception as e:
                        result = str(e)
                elif command == 'current directory':
                    result = os.getcwd()
                elif command == 'system info':
                    try:
                        with open('/etc/os-release', 'r') as f:
                            result = f.read()
                    except Exception as e:
                        result = str(e)
                elif command == 'python version':
                    result = sys.version
                else:
                    result = f"Unknown command: {command}"
                    
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"result": result}).encode('utf-8'))
                
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print(f"Starting server on port {PORT}...", flush=True)
    with socketserver.TCPServer(("0.0.0.0", PORT), AgentHandler) as httpd:
        print(f"Serving at port {PORT}", flush=True)
        httpd.serve_forever()
