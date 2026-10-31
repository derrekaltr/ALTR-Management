#!/usr/bin/env python3
"""Clean screenshots of public Instagram (or any) pages via headless Chrome + CDP.

Dismisses Instagram's logged-out signup modal / dim overlay before capturing,
so evidence shots are clean and full-brightness.

Usage:
  python3 scripts/igshot.py <url> <out.png> [--full] [--scroll N] [--width W --height H]

  --full      capture full scrollable page (up to ~6000px)
  --scroll N  scroll down N pixels before capture (viewport mode)
"""
import base64
import json
import subprocess
import sys
import time

try:
    import websocket
except ModuleNotFoundError:  # system python changed (PEP 668): re-exec via repo venv
    import os
    _venv = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         ".venv", "bin", "python")
    if os.path.exists(_venv) and os.environ.get("IGSHOT_REEXEC") != "1":
        os.environ["IGSHOT_REEXEC"] = "1"
        os.execv(_venv, [_venv] + __import__("sys").argv)
    raise

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

KILL_MODAL_JS = """
(() => {
  let removed = 0;
  // Instagram's signup modal + backdrop live in role=dialog / presentation layers
  document.querySelectorAll('div[role="dialog"]').forEach(d => {
    // climb toward body, but never remove a node that contains the page <main>
    let layer = d;
    while (layer.parentElement && layer.parentElement !== document.body &&
           !layer.parentElement.contains(document.querySelector('main'))) {
      layer = layer.parentElement;
    }
    if (!layer.contains(document.querySelector('main'))) { layer.remove(); removed++; }
    else { d.remove(); removed++; }
  });
  // dim overlays: full-viewport fixed divs with opacity/backdrop styling
  document.querySelectorAll('body > div').forEach(d => {
    const s = getComputedStyle(d);
    if (s.position === 'fixed' && parseInt(s.zIndex || 0) > 0 &&
        d.offsetWidth >= innerWidth * 0.9 && d.offsetHeight >= innerHeight * 0.9 &&
        !d.querySelector('main')) { d.remove(); removed++; }
  });
  document.body.style.overflow = 'auto';
  document.documentElement.style.overflow = 'auto';
  return removed;
})()
"""


class CDP:
    def __init__(self, port):
        for _ in range(60):
            try:
                targets = json.loads(subprocess.run(
                    ["curl", "-s", f"http://127.0.0.1:{port}/json"],
                    capture_output=True, text=True, check=True).stdout)
                page = next(t for t in targets if t["type"] == "page")
                break
            except Exception:
                time.sleep(0.25)
        else:
            raise RuntimeError("Chrome CDP not reachable")
        self.ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=30)
        self.mid = 0

    def cmd(self, method, **params):
        self.mid += 1
        self.ws.send(json.dumps({"id": self.mid, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.mid:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})

    def js(self, expr):
        r = self.cmd("Runtime.evaluate", expression=expr, returnByValue=True)
        return r.get("result", {}).get("value")


def main():
    args = sys.argv[1:]
    url, out = args[0], args[1]
    full = "--full" in args
    scroll = int(args[args.index("--scroll") + 1]) if "--scroll" in args else 0
    width = int(args[args.index("--width") + 1]) if "--width" in args else 1400
    height = int(args[args.index("--height") + 1]) if "--height" in args else 1000

    port = 9333
    proc = subprocess.Popen(
        [CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={port}",
         "--remote-allow-origins=*",
         f"--window-size={width},{height}", f"--user-agent={UA}",
         "--no-first-run", "--user-data-dir=/tmp/igshot-profile"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        c = CDP(port)
        c.cmd("Page.enable")
        c.cmd("Page.navigate", url=url)
        time.sleep(6)
        # dismiss modal twice (it can re-mount once)
        for _ in range(3):
            removed = c.js(KILL_MODAL_JS)
            time.sleep(1)
            if not removed:
                break
        if scroll:
            for _ in range(4):  # IG re-resets scroll during hydration; insist
                c.js(f"window.scrollTo(0, {scroll})")
                time.sleep(1.2)
                c.js(KILL_MODAL_JS)
                if (c.js("window.scrollY") or 0) >= scroll * 0.9:
                    break
        shot_args = {"format": "png"}
        if full:
            h = min(int(c.js(
                "Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)") or height), 6000)
            c.cmd("Emulation.setDeviceMetricsOverride", width=width, height=h,
                  deviceScaleFactor=1, mobile=False)
            time.sleep(1)
            c.js(KILL_MODAL_JS)
        data = c.cmd("Page.captureScreenshot", **shot_args)["data"]
        with open(out, "wb") as f:
            f.write(base64.b64decode(data))
        print(out)
    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
