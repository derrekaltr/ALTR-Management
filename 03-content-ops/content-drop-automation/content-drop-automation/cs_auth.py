"""One-time Content Snare OAuth setup.

Opens the authorization page in your browser, catches the redirect on
localhost:8484, exchanges the code for tokens, and stores them in .tokens.json.
Run once; monthly_drop.py refreshes tokens automatically afterwards.
"""

import http.server
import threading
import urllib.parse
import webbrowser

from cs_common import API_BASE, REDIRECT_URI, SCOPES, exchange_token, load_env, save_tokens

load_env()

import os

if not os.environ.get("CS_CLIENT_ID") or not os.environ.get("CS_CLIENT_SECRET"):
    raise SystemExit(
        "Set CS_CLIENT_ID and CS_CLIENT_SECRET in content-drop-automation/.env first.\n"
        "Create the app in Content Snare: avatar menu > Integrations > API > New application,\n"
        f"with redirect URL {REDIRECT_URI}"
    )

auth_code = {}


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        auth_code["code"] = query.get("code", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h2>Authorized. You can close this tab.</h2>")

    def log_message(self, *args):
        pass


server = http.server.HTTPServer(("localhost", 8484), Handler)
threading.Thread(target=server.handle_request, daemon=True).start()

auth_url = f"{API_BASE}/oauth/authorization?" + urllib.parse.urlencode({
    "client_id": os.environ["CS_CLIENT_ID"],
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": SCOPES,
})
print("Opening browser for Content Snare authorization...")
print(f"If it doesn't open, visit:\n{auth_url}\n")
webbrowser.open(auth_url)

print("Waiting for authorization (approve in the browser)...")
while "code" not in auth_code:
    pass

if not auth_code["code"]:
    raise SystemExit("No authorization code received — try again.")

tokens = exchange_token({"code": auth_code["code"]})
save_tokens(tokens)
print("Success — tokens saved to .tokens.json. You can now run monthly_drop.py.")
