#!/usr/bin/env python3
"""cdp.py - a zero-dependency Chrome DevTools Protocol client.

Why hand-rolled: the useful operations are three (navigate, evaluate, read text), and every
Python CDP wrapper pulls a websocket dependency for them. This speaks the few frames it needs
over stdlib sockets.

Start Chrome with a debugging port first:

    google-chrome --remote-debugging-port=9333 --user-data-dir=/tmp/agent-profile &

CLI:
    python3 cdp.py tabs
    python3 cdp.py nav   <url> [settle_seconds]
    python3 cdp.py js    '<expression>'
    python3 cdp.py text  [chars]

Module:
    from cdp import CDP
    cdp = CDP(port=9333, match="example.com")   # match selects the tab by URL substring
    cdp.js("document.title")
    cdp.call("DOM.getDocument", {"depth": -1, "pierce": True})
"""

import base64
import json
import os
import socket
import struct
import sys
import time
import urllib.request
from urllib.parse import urlparse

DEFAULT_PORT = int(os.environ.get("CDP_PORT", "9333"))


class CDPError(RuntimeError):
    pass


class CDP:
    def __init__(self, port=DEFAULT_PORT, match=None, new_tab=False, url=None):
        self.port = port
        self._mid = 0
        if new_tab and url:
            self._target = self._create_target(url)
        else:
            self._target = self._pick(match)
        self._sock = self._connect(self._target["webSocketDebuggerUrl"])
        for domain in ("Page.enable", "Runtime.enable", "DOM.enable", "Network.enable"):
            try:
                self.call(domain)
            except CDPError:
                pass

    # ---------- target management ----------

    def _http(self, path, method="GET"):
        req = urllib.request.Request("http://127.0.0.1:%d%s" % (self.port, path), method=method)
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())

    def tabs(self):
        return [t for t in self._http("/json/list")
                if t.get("type") == "page" and t.get("webSocketDebuggerUrl")]

    def _pick(self, match):
        pages = self.tabs()
        if match:
            pages = [t for t in pages if match in (t.get("url") or "")]
        if not pages:
            raise CDPError("no page target%s; open a tab or pass new_tab=True, url=..."
                           % (" matching %r" % match if match else ""))
        # prefer a real page over about:blank
        pages.sort(key=lambda t: 1 if (t.get("url") or "").startswith("about:") else 0)
        return pages[0]

    def _create_target(self, url):
        req = urllib.request.Request(
            "http://127.0.0.1:%d/json/new?%s" % (self.port, url), method="PUT")
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())

    # ---------- transport ----------

    def _connect(self, ws_url):
        u = urlparse(ws_url)
        s = socket.create_connection((u.hostname, u.port), timeout=40)
        key = base64.b64encode(os.urandom(16)).decode()
        req = ("GET %s HTTP/1.1\r\nHost: %s:%d\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
               "Sec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n"
               % (u.path, u.hostname, u.port, key))
        s.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += s.recv(4096)
        return s

    def _send(self, obj):
        data = json.dumps(obj).encode()
        mask = os.urandom(4)
        payload = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
        n = len(data)
        if n < 126:
            header = struct.pack("!BB", 0x81, 0x80 | n)
        elif n < 65536:
            header = struct.pack("!BBH", 0x81, 0x80 | 126, n)
        else:
            header = struct.pack("!BBQ", 0x81, 0x80 | 127, n)
        self._sock.sendall(header + mask + payload)

    def _recv(self):
        b = self._sock.recv(2)
        if not b:
            return None
        ln = b[1] & 0x7F
        if ln == 126:
            ln = struct.unpack("!H", self._sock.recv(2))[0]
        elif ln == 127:
            ln = struct.unpack("!Q", self._sock.recv(8))[0]
        buf = b""
        while len(buf) < ln:
            buf += self._sock.recv(ln - len(buf))
        try:
            return json.loads(buf)
        except ValueError:
            return None

    def call(self, method, params=None):
        self._mid += 1
        mid = self._mid
        self._send({"id": mid, "method": method, "params": params or {}})
        for _ in range(400):
            msg = self._recv()
            if msg is None:
                raise CDPError("connection closed during %s" % method)
            if msg.get("id") != mid:
                continue
            if "error" in msg:
                raise CDPError("%s: %s" % (method, msg["error"]))
            return msg.get("result", {})
        raise CDPError("timeout waiting for %s" % method)

    # ---------- convenience ----------

    def js(self, expression):
        r = self.call("Runtime.evaluate", {
            "expression": expression, "returnByValue": True, "awaitPromise": True})
        if "exceptionDetails" in r:
            raise CDPError(r["exceptionDetails"].get("text", "evaluate failed"))
        return r.get("result", {}).get("value")

    def navigate(self, url, settle=4.0):
        self.call("Page.navigate", {"url": url})
        time.sleep(settle)
        return self.js("location.href")

    def text(self, limit=4000):
        return (self.js("document.body.innerText") or "")[:limit]

    def backend_node_ids(self, node_name="INPUT", attrs=None):
        """Walk the pierced DOM for matching nodes. Needed for file inputs and shadow roots."""
        doc = self.call("DOM.getDocument", {"depth": -1, "pierce": True})
        found = []

        def walk(node, depth=0):
            if not node or depth > 40:
                return
            if node.get("nodeName") == node_name:
                a = dict(zip((node.get("attributes") or [])[::2],
                             (node.get("attributes") or [])[1::2]))
                if all(a.get(k) == v for k, v in (attrs or {}).items()):
                    found.append((a, node["backendNodeId"]))
            for child in (node.get("children") or []) + (node.get("shadowRoots") or []):
                walk(child, depth + 1)

        walk(doc.get("root"))
        return found

    def attach(self, path, attrs=None):
        """Attach a file to the first file input matching attrs. Returns the attribute dict."""
        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise CDPError("no such file: %s" % path)
        targets = self.backend_node_ids("INPUT", attrs or {"type": "file"})
        if not targets:
            raise CDPError("no file input found")
        attrs_found, backend_node_id = targets[0]
        self.call("DOM.setFileInputFiles", {"files": [path], "backendNodeId": backend_node_id})
        return attrs_found


def list_tabs(port=DEFAULT_PORT):
    """Page targets on the given debugging port."""
    req = urllib.request.Request("http://127.0.0.1:%d/json/list" % port)
    with urllib.request.urlopen(req, timeout=30) as r:
        tabs = json.loads(r.read())
    return [t for t in tabs if t.get("type") == "page" and t.get("webSocketDebuggerUrl")]


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd = argv[1]
    match = os.environ.get("CDP_TAB_MATCH")
    if cmd == "tabs":
        for t in list_tabs():
            print(t.get("url"))
        return 0
    cdp = CDP(match=match)
    if cmd == "nav":
        print(cdp.navigate(argv[2], float(argv[3]) if len(argv) > 3 else 4.0))
        print("title:", cdp.js("document.title"))
    elif cmd == "js":
        print(cdp.js(argv[2]))
    elif cmd == "text":
        print(cdp.text(int(argv[2]) if len(argv) > 2 else 4000))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
