import base64
import json
import ssl
import threading
import webbrowser

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class CommandAndControlServer:
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.server = HTTPServer((self.host, self.port), CommandAndControlHandler)
    self.server.server_cert = 'server.crt'
    self.server.server_key = 'server.key'
    self.server.server_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    self.server.server_context.load_cert_chain(certfile=self.server.server_cert, keyfile=self.server.server_key)

  def start(self):
    print(f'Starting C2 server at {self.host}:{self.port}')
    threading.Thread(target=self.server.serve_forever).start()

  def stop(self):
    self.server.shutdown()

class CommandAndControlHandler(BaseHTTPRequestHandler):
  def do_POST(self):
    # Parse the request body
    try:
      content_length = int(self.headers['Content-Length'])
      request_body = self.rfile.read(content_length).decode()
      request_data = json.loads(request_body)
    except (ValueError, KeyError):
      self.send_response(400)
      self.end_headers()
      return

    # Validate the request data
    if 'command' not in request_data:
      self.send_response(400)
      self.end_headers()
      return

    # Decode the base64-encoded command
    try:
      command = base64.b64decode(request_data['command']).decode()
    except (TypeError, ValueError):
      self.send_response(400)
      self.end_headers()
      return

    # Execute the command and get the response
    try:
      response = execute_command(command)
    except Exception as e:
      self.send_response(500)
      self.end_headers()
      return

    # Encode the response in base64
    try:
      encoded_response = base64.b64encode(response.encode()).decode()
    except TypeError:
      self.send_response(500)
      self.end_headers()
      return

    # Send the response back to the controlled device
    self.send_response(200)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps({'response': encoded_response}).encode())

def execute_command(command):
  # TODO: Replace this with your own command execution code
  return f'Executed command: {command}'

def start_web_dashboard():
  webbrowser.open_new_tab(f'https://localhost:8000/dashboard')

def start_cli():
  while True:
    # Wait for a command from the operator
    command = input('Enter a command: ')

    # Send the command to the controlled devices
    send_command(command)

def send_command(command):
  # TODO: Replace this with your own code to send commands to controlled devices via HTTPS
  print(f'Sent command: {command}')

if __name__ == '__main__':
  # Start the C2 server in a separate thread
  c2_server = CommandAndControlServer('localhost', 8000)
  c2_server.start()

  # Start the web dashboard in a separate thread
  threading.Thread(target=start_web_dashboard).start()

  # Start the command-line interface in the main thread
  start_cli()
