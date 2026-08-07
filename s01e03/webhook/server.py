import json
import asyncio
import logging
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

from ..agent import run_agent
from ..config import WEBHOOK_PORT
from ..mcp_agent.client import MCPClient

logging.getLogger("httpx").setLevel(logging.WARNING)

class SimpleRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'Server is alive')
    
    def do_POST(self):
        content_length_str = self.headers.get('Content-Length')
        if content_length_str is None:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Content-Length header is missing')
            return
        try:
            content_length = int(content_length_str)
            raw_body = self.rfile.read(content_length)
            data = json.loads(raw_body)
        except (ValueError) as e:
            self.send_response(400)
            self.end_headers()
            return

        session_id = data["sessionID"]
        msg = data["msg"]
        logging.info(f"<- {session_id}: {msg}")

        if "FLG:" in msg:
            self.server.shutdown()
            self.server.loop.call_soon_threadsafe(self.server.shutdown_event.set)
        else:
            try:
                future = asyncio.run_coroutine_threadsafe(run_agent(session_id, msg, self.server.mcp_client), self.server.loop)
                ai_response = future.result(timeout=30)
            except Exception as e:
                logging.exception("Agent failed")
                self.send_response(500)
                self.end_headers()
                return
            body = json.dumps({"msg": ai_response}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

def run(loop:asyncio.AbstractEventLoop, client:MCPClient, shutdown_event:asyncio.Event, server_class=ThreadingHTTPServer, handler_class=SimpleRequestHandler):
    server_address = ("127.0.0.1", WEBHOOK_PORT)
    httpd = server_class(server_address, handler_class)
    logging.info(f"Listening on http://localhost:{server_address[1]}")

    httpd.loop = loop
    httpd.mcp_client = client
    httpd.shutdown_event = shutdown_event
    httpd.serve_forever()
    httpd.server_close()
    logging.info(f"Shutting down http://localhost:{server_address[1]} server...")