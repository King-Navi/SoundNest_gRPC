import os
import asyncio
from http.server import BaseHTTPRequestHandler , HTTPServer
from sqlalchemy import text
from typing_extensions import override
from dotenv import load_dotenv

from config.connection_mysql import engine
load_dotenv()
HELTH_PORT = int(os.getenv("HELTH_PORT", 8088)) # pylint: disable=W1508

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self): # pylint: disable=C0103
        sql_status = False
        sql_error = None

        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                sql_status = True
        except Exception as e: # pylint: disable=W0718
            sql_error = str(e)

        if sql_status:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"SQL: OK")
        else:
            self.send_response(500)
            self.end_headers()
            if not sql_status:
                self.wfile.write(f"SQL: ERROR - {sql_error}\n".encode())


    @override
    def log_message(self, format, *args): # pylint: disable=W0622
        return

def start_http_health_server():
    httpd = HTTPServer(('0.0.0.0', HELTH_PORT), HealthHandler)
    print(f"HTTP health check running on port http://localhost:{HELTH_PORT}...")
    httpd.serve_forever()
