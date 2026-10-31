"""Shared helpers: .env loading, token storage, Content Snare API calls."""

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
TOKENS_PATH = os.path.join(BASE_DIR, ".tokens.json")

API_BASE = "https://api.contentsnare.com"
REDIRECT_URI = "http://localhost:8484/callback"
SCOPES = "read write"


def load_env():
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


def _http(method, url, payload=None, headers=None, form=False):
    data = None
    hdrs = dict(headers or {})
    if payload is not None:
        if form:
            data = urllib.parse.urlencode(payload).encode()
            hdrs["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            data = json.dumps(payload).encode()
            hdrs["Content-Type"] = "application/json"
    hdrs.setdefault("Accept", "application/json")
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode()
            return resp.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"error": body}


def save_tokens(tokens):
    tokens["obtained_at"] = int(time.time())
    with open(TOKENS_PATH, "w") as f:
        json.dump(tokens, f, indent=2)
    os.chmod(TOKENS_PATH, 0o600)


def load_tokens():
    if not os.path.exists(TOKENS_PATH):
        raise SystemExit(
            "No Content Snare tokens found. Run `python3 cs_auth.py` first."
        )
    with open(TOKENS_PATH) as f:
        return json.load(f)


def exchange_token(grant):
    """grant: {'code': ...} for initial auth or {'refresh_token': ...} to refresh."""
    payload = {
        "client_id": os.environ["CS_CLIENT_ID"],
        "client_secret": os.environ["CS_CLIENT_SECRET"],
        "redirect_uri": REDIRECT_URI,
    }
    if "code" in grant:
        payload.update(grant_type="authorization_code", code=grant["code"])
    else:
        payload.update(grant_type="refresh_token", refresh_token=grant["refresh_token"])
    status, body = _http("POST", f"{API_BASE}/oauth/token", payload, form=True)
    if status != 200:
        raise SystemExit(f"Token request failed ({status}): {body}")
    return body


def get_access_token():
    tokens = load_tokens()
    expires_in = tokens.get("expires_in") or 7200
    if time.time() > tokens.get("obtained_at", 0) + expires_in - 120:
        tokens = exchange_token({"refresh_token": tokens["refresh_token"]})
        save_tokens(tokens)
    return tokens["access_token"]


def cs_api(method, path, payload=None):
    token = get_access_token()
    status, body = _http(
        method,
        f"{API_BASE}/partner_api/v1{path}",
        payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    if status >= 400:
        raise RuntimeError(f"Content Snare API {method} {path} failed ({status}): {body}")
    return body
