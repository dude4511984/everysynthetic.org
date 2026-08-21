#!/usr/bin/env python3
"""
Static homepage server. Serves the pages that live here; everything else is a
301 to app.everysynthetic.org.

The root domain used to serve the whole app. When the homepage and the app were
split (2026-08-20), paths like /install and /install.sh started 404ing on the
root domain -- including the install command printed on the install page itself,
which was live and broken for every visitor.

That was first fixed with a hand-maintained MOVED list, which promptly failed
the same way: /uninstall.ps1 was left out, so the uninstall command printed in
uninstall.ps1's own header returned 404 for a month while the install command
beside it worked. Nobody finds that until a user tries to leave, and a user who
cannot uninstall does not file a bug, they just stop using it.

So the rule is inverted. A file that exists here is served. Anything else went
to the app, whether or not someone remembered to write it down. New app routes
work on the root domain by default, and the failure mode of forgetting is a
redirect to a real page instead of a silent 404.
"""
import http.server
import os
import socketserver

PORT = 8091
APP = "https://app.everysynthetic.org"


class Handler(http.server.SimpleHTTPRequestHandler):

    def _served_locally(self) -> bool:
        """True when this request maps to a file that actually exists here."""
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        if path in ("", "/"):
            path = "/index.html"
        # translate_path handles URL-decoding and blocks .. traversal.
        return os.path.isfile(self.translate_path(path))

    def _redirected(self) -> bool:
        if self._served_locally():
            return False
        self.send_response(301)
        self.send_header("Location", APP + self.path)
        self.end_headers()
        return True

    def do_GET(self):
        if self._redirected():
            return
        return super().do_GET()

    def do_HEAD(self):
        if self._redirected():
            return
        return super().do_HEAD()


if __name__ == "__main__":
    os.chdir(os.path.expanduser("~/es-homepage"))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"homepage + redirects on :{PORT}", flush=True)
        httpd.serve_forever()
