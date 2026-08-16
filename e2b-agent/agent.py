import http.server
import json
import socketserver

PORT = 8080

class AgentHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": "E2B custom agent is running"}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    # Ensure stdout is unbuffered or flushed so print statements appear in docker logs
    print(f"Starting server on port {PORT}...", flush=True)
    with socketserver.TCPServer(("0.0.0.0", PORT), AgentHandler) as httpd:
        print(f"Serving at port {PORT}", flush=True)
        httpd.serve_forever()
