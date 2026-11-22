"""Build the public aggregate evidence used by the hosted browser evaluator."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "cfde_evaluator"))
import evaluate

evaluate.event_sink.set(lambda *args, **kwargs: None)
catalog = {}
for name in evaluate.programs():
    entries = []
    try:
        for release in evaluate.releases(name):
            entry = {k: release[k] for k in ("link", "drs", "lastmodified")}
            try:
                entry["quality"] = evaluate.package(release)
            except Exception as exc:
                entry["error"] = type(exc).__name__
            entries.append(entry)
        catalog[name] = {"releases": entries}
    except Exception as exc:
        catalog[name] = {"error": type(exc).__name__}
    print(name, len(entries), flush=True)
if not any(entry.get("quality") for p in catalog.values() for entry in p.get("releases", [])):
    raise SystemExit("No usable package measurements")
(root / "docs/evidence.json").write_text(json.dumps({
    "checked": datetime.now(timezone.utc).isoformat(), "programs": catalog
}, separators=(",", ":"))+"\n")
