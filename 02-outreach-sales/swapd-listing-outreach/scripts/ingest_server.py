#!/usr/bin/env python3
"""
ingest_server.py — tiny localhost receiver for the in-browser swapd scanner.

The scanner runs inside the authenticated swapd page (so cookies apply) and POSTs the
listings it scraped to http://127.0.0.1:8748/ingest. This server (CORS-enabled) writes
each batch to data/raw/<category>.json, avoiding any hand-copying of scraped data.

Run in background:  python3 scripts/ingest_server.py
Endpoints:
  GET  /ping             -> {"ok": true}
  POST /ingest           -> body {category, listings:[...]}; writes data/raw/<category>.json
"""
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
PORT = 8748


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/ping"):
            return self._json(200, {"ok": True})
        self._json(404, {"error": "not found"})

    def do_POST(self):
        if not self.path.startswith("/ingest"):
            return self._json(404, {"error": "not found"})
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._json(400, {"error": "bad json"})
        category = re.sub(r"[^a-z0-9_-]+", "-", str(payload.get("category", "batch")).lower())
        listings = payload.get("listings", [])
        out = RAW / f"{category}.json"
        out.write_text(json.dumps(payload, indent=2))
        print(f"ingest: {category} -> {len(listings)} listings ({out})")
        self._json(200, {"ok": True, "category": category, "count": len(listings)})

    def log_message(self, *args):
        pass  # quiet


if __name__ == "__main__":
    print(f"ingest server on http://127.0.0.1:{PORT}  (raw -> {RAW})")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
