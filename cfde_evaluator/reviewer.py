"""Local human review of completed assessments."""
import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs
from evaluate import ROOT, score

DB = ROOT / "reviews.sqlite"


def read(db, run):
    row = db.execute("select body from results where id=?", (run,)).fetchone()
    if not row:
        raise ValueError("Choose a completed assessment")
    report = json.loads(row[0])
    changes = db.execute("select criterion,idx,mark,reason,source from human_marks where run=? order by id", (run,))
    for name, idx, mark, reason, source in changes:
        report["criteria"][name]["elements"][idx]["human"] = dict(mark=mark,reason=reason,source=source)
    total = 0
    pending = 0
    for criterion in report["criteria"].values():
        marks = [x.get("human",x)["mark"] for x in criterion["elements"]]
        pending += marks.count(None)
        total += sum(m for m in marks if m is not None)
        criterion["score"] = sum(marks) if None not in marks else None
    report["status"] = "Review required" if pending else score(total,report["criteria"]["Long-term Home"]["score"])
    report["points"], report["pending"] = total,pending
    report["verified"] = bool(db.execute("select 1 from human_verified where run=?", (run,)).fetchone())
    return report


def save(db, data):
    run = data["run"]
    report = read(db,run)
    if data.get("verify") is True:
        if report["pending"]:
            raise ValueError("Resolve remaining elements before verification")
        db.execute("insert or replace into human_verified values(?,CURRENT_TIMESTAMP)",(run,))
        return
    name,idx,mark = data["criterion"],data["index"],data["mark"]
    if name not in report["criteria"] or type(idx) is not int or not 0<=idx<5:
        raise ValueError("Unknown element")
    if type(mark) is not int or mark not in (0,1):
        raise ValueError("Choose Yes or No")
    reason,source = data["reason"].strip(),data["source"].strip()
    if not reason or not source:
        raise ValueError("Enter a rationale and evidence reference")
    db.execute("insert into human_marks(run,criterion,idx,mark,reason,source) values(?,?,?,?,?,?)",
               (run,name,idx,mark,reason,source))
    db.execute("delete from human_verified where run=?",(run,))


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):
        pass

    def reply(self,obj,status=200):
        html=isinstance(obj,bytes)
        body=obj if html else json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type","text/html; charset=utf-8" if html else "application/json")
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url=urlsplit(self.path)
        with sqlite3.connect(DB) as db:
            if url.path=="/":
                return self.reply((ROOT/"reviewer.html").read_bytes())
            if url.path=="/runs":
                return self.reply(db.execute("select id,program,json_extract(body,'$.retrieved'),rowid from results order by rowid desc").fetchall())
            if url.path=="/report":
                try:
                    return self.reply(read(db,parse_qs(url.query).get("run",[""])[0]))
                except ValueError:
                    pass
        self.reply({},404)

    def do_POST(self):
        addr=f"127.0.0.1:{self.server.server_port}"
        if self.path!="/decision" or self.headers.get("Host")!=addr or self.headers.get("Origin")!="http://"+addr:
            return self.reply({},403)
        try:
            size=int(self.headers.get("Content-Length",0))
            if not 0<size<16000:
                raise ValueError("Invalid request size")
            data=json.loads(self.rfile.read(size))
            with sqlite3.connect(DB) as db:
                db.execute("begin immediate")
                save(db,data)
            self.reply({"saved":True})
        except (ValueError,KeyError,TypeError,AttributeError) as exc:
            self.reply({"error":str(exc)},400)


if __name__=="__main__":
    os.umask(0o077)
    with sqlite3.connect(DB) as db:
        db.execute("create table if not exists results(id text primary key,program text,body text)")
        db.execute("create table if not exists human_marks(id integer primary key,run text,criterion text,idx integer,mark integer,reason text,source text,saved text default CURRENT_TIMESTAMP)")
        db.execute("create table if not exists human_verified(run text primary key,saved text)")
    ThreadingHTTPServer(("127.0.0.1",8766),Handler).serve_forever()
