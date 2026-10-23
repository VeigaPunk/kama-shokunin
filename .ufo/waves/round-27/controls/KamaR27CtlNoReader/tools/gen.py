#!/usr/bin/env python3
"""Control generator for the round-27 no-reader seat.

Writes three things into a sandbox lane tree:
  registry/error-signatures-r27.json
  a SKILL.md section '## Round-27 request-validation signatures'
  corpus/SOURCES.md rows

Input: a spec JSON  {"rows": [{id, sig, file, line, path, marker, trigger,
                               meaning, next, srow}]}
"""
import json
import sys
from pathlib import Path

HEADING = "## Round-27 request-validation signatures"


def build(spec_path, lane, append=True):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    lane = Path(lane)
    rows = spec["rows"]

    entries = []
    skill = ["| id | signature | trigger | meaning | next action | source |",
             "|---|---|---|---|---|---|"]
    srcs = []

    for r in rows:
        entries.append({
            "id": r["id"],
            "profile": "default",
            "signature": r["sig"],
            "request": {"method": "POST", "path": r["path"],
                        "body": {"m": r["marker"]}},
            "control": {"method": "POST", "path": r["path"],
                        "body": {"ctl": True}},
            "source": {"row": r["srow"], "file": r["file"], "line": r["line"]},
            "found_by": "KamaR27CtlNoReader (control, not claim data)",
        })
        skill.append("| {} | `{}` | {} | {} | {} | {} |".format(
            r["id"], r["sig"], r["trigger"], r["meaning"], r["next"], r["srow"]))
        srcs.append("| {} | {}#L{} 704366d | control row, round-27 no-reader probe "
                    "(not claim data) |".format(r["srow"], r["file"], r["line"]))

    reg = lane / "registry/error-signatures-r27.json"
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(json.dumps({
        "schema": "kama-r27-error-signatures/v1",
        "build": "llama-server b11755 (704366d76)",
        "fixture": "stories260K.gguf sha256 270cba1b...256d",
        "note": "CONTROL rows (round-27 no-reader seat). Not claim data.",
        "signatures": entries,
    }, indent=1) + "\n", encoding="utf-8")

    skill_p = lane / "SKILL.md"
    text = skill_p.read_text(encoding="utf-8")
    if append:
        text = text.rstrip("\n") + "\n\n" + HEADING + "\n\n" + "\n".join(skill) + "\n"
    else:
        text = HEADING + "\n\n" + "\n".join(skill) + "\n"
    skill_p.write_text(text, encoding="utf-8")

    src_p = lane / "corpus/SOURCES.md"
    text = src_p.read_text(encoding="utf-8")
    text = text.rstrip("\n") + "\n\n## Round-27 control rows (no-reader seat, not claim data)\n\n"
    text += "| id | source | kind |\n|---|---|---|\n" + "\n".join(srcs) + "\n"
    src_p.write_text(text, encoding="utf-8")

    # marker -> signature map for the fake server
    wanted = {r["marker"]: r["sig"] for r in rows}
    Path("/tmp/kama-r27-noreader/wanted.json").write_text(
        json.dumps(wanted, indent=1) + "\n", encoding="utf-8")
    print("wrote {} rows to {}".format(len(rows), lane))


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
