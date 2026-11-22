"""Inspect the local public 4DN snapshot and replay the team's recorded assessment."""
from pathlib import Path
import argparse
import hashlib
import xml.etree.ElementTree as ET
import zipfile

from evaluate import ROOT, NAMES, score, inspect_archive

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--all", action="store_true", help="show all historical element decisions")
parser.add_argument("snapshot", type=Path, help="Local 4DN metadata ZIP")
parser.add_argument("--matrix", type=Path, help="Optional historical November evidence workbook")
args = parser.parse_args()
snapshot = args.snapshot
stats = inspect_archive(snapshot, hashlib.sha256(snapshot.read_bytes()).hexdigest())
tables = stats["tables"]
print("4DN public submission | December 15, 2025 | local package inspection")
print(f"{len(tables)} tables, {sum(t['rows'] for t in tables.values()):,} metadata rows")
print("Package SHA-256:", stats["sha256"])
files = tables["file"]
print(f"File table: {files['rows']:,} rows, {files['missing_checksums']:,} missing both MD5 and SHA-256.")
print("Rubric check | Records exist for each subject: ",
      "Pending | Subject records are present; confirming complete coverage requires an independent roster."
      if tables.get("subject", {}).get("rows") else "Pending | No populated subject table found.")
print("Evidence: subject.tsv,", tables.get("subject", {}).get("rows", 0), "rows.")
if not args.matrix:
    raise SystemExit(0)
print("\nHistorical human review | November workbook, Evidence sheet")
matrix = args.matrix
with zipfile.ZipFile(matrix) as book:
    strings = ["".join(t.text or "" for t in si.findall(".//{*}t"))
               for si in ET.fromstring(book.read("xl/sharedStrings.xml"))]
    sheet = ET.fromstring(book.read("xl/worksheets/sheet2.xml"))
scores = {}
for row in sheet.findall(".//{*}row"):
    cells = {}
    for cell in row.findall("{*}c"):
        value = cell.findtext("{*}v")
        if value is not None:
            col = cell.attrib["r"].rstrip("0123456789")
            cells[col] = strings[int(value)] if cell.get("t") == "s" else value
    if cells.get("A") == "4DN" and cells.get("B") in NAMES:
        name = cells["B"]
        scores[name] = int(cells["C"])
        if args.all or name == "Long-term Home":
            print(f"{name}: {scores[name]}/5")
            for col in "EFGHI":
                print(" ", cells[col])
if set(scores) != set(NAMES):
    raise ValueError("Incomplete historical evidence sheet")
total = sum(scores.values())
print(f"Historical total {total}/55 | Long-term Home {scores['Long-term Home']}/5 |",
      score(total, scores["Long-term Home"]))
