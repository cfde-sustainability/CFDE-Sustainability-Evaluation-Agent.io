"""Start the local CFDE scoring dashboard."""
import json
import os
import re
import sqlite3
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import evaluate as engine

lock = threading.RLock()
state = {"running": False, "events": [], "run": 0, "program": ""}
groups = engine.rubric()


def emit(message, **details):
    with lock:
        state["events"].append(dict(time=datetime.now().strftime("%H:%M:%S"),
                                    message=message, **details))


def run(program, key):
    token = engine.run_key.set(key)
    engine.event_sink.set(emit)
    try:
        assets = engine.releases(program)
        if not assets:
            emit("Not evaluated · no current approved C2M2 submission", outcome=True)
        with sqlite3.connect(engine.ROOT / "reviews.sqlite") as db:
            db.execute("create table if not exists results(id text primary key,program text,body text)")
            for index, asset in enumerate(assets, 1):
                emit(f"Release {index} of {len(assets)} · {asset['lastmodified']}", release=True)
                with db:
                    report = engine.evaluate(db, asset, groups,
                        os.getenv("ANTHROPIC_MODEL","claude-sonnet-4-6"), False)
                emit(f"{report['status']} · {report['reason']}", outcome=True)
    except Exception as error:
        emit("Evaluation stopped · " + engine.error_summary(error), outcome=True)
    finally:
        engine.run_key.reset(token)
        with lock:
            state["running"] = False


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, body, media="application/json", status=200):
        raw = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", media)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/":
            self.send((engine.ROOT/"dashboard.html").read_bytes(),"text/html; charset=utf-8")
        elif self.path == "/rubric":
            self.send(groups)
        elif self.path == "/programs":
            try:
                self.send(engine.programs())
            except Exception:
                self.send([], status=503)
        elif self.path == "/state":
            with lock:
                snapshot = dict(state, events=state["events"].copy())
            self.send(snapshot)
        else:
            self.send({}, status=404)

    def do_POST(self):
        allowed = f"127.0.0.1:{self.server.server_port}"
        if (self.path != "/run" or self.headers.get("Host") != allowed
                or self.headers.get("Origin") != "http://" + allowed):
            return self.send({}, status=403)
        try:
            length = int(self.headers["Content-Length"])
            if not 0 < length <= 4096:
                raise ValueError
            data = json.loads(self.rfile.read(length))
            key = data["key"]
            if not isinstance(key, str) or not key.strip() or not key.isascii() or not key.strip().isprintable():
                raise ValueError
            program = data["program"]
            if not re.fullmatch(r"[\w ()+.-]{1,80}", program):
                raise ValueError
        except (TypeError,ValueError,KeyError):
            return self.send({}, status=400)
        with lock:
            if state["running"]:
                return self.send({}, status=409)
            state.update(running=True, events=[], program=program, run=state["run"]+1)
            threading.Thread(target=run,args=(program,key.strip()),daemon=True).start()
        self.send({}, status=202)


if __name__ == "__main__":
    os.umask(0o077)
    server = ThreadingHTTPServer(("127.0.0.1",8765),Handler)
    print("CFDE evaluation dashboard · http://127.0.0.1:8765",flush=True)
    server.serve_forever()
