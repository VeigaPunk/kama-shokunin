#!/usr/bin/env python3
"""Generate round-51 C1 counter mutants (seat M1Ctr) from the pristine bytes.

Each mutant is one exact, uniquely-anchored string replacement in a COPY under
mut/. The pristine source is never touched. Writes manifest.json with the
replacement, before/after sha256, the predicted happy-path (build) outcome and
the decoy prediction.
"""
import hashlib
import json
import os
import sys

SRC = "/fast/scratch/hyaku/kama-r51/M1Ctr/lane/tools/round51-replay-exe-audit.py"
DST = "/fast/scratch/hyaku/kama-r51/M1Ctr/mut"

# (id, old, new, build-expectation, decoy-expectation, note)
MUTANTS = [
    ("mu01",
     "    if got != want:\n",
     "    if False:\n",
     "survive", "killed-by-decoy",
     "own_exe dev/inode comparison dropped"),
    ("mu02",
     "        st = os.fstat(fd)\n",
     '        st = os.stat(f"/proc/{pid}/exe")\n',
     "survive", "survive",
     "fstat of opened /proc/pid/exe replaced by stat of the link"),
    ("mu03",
     "    if h.hexdigest() != SERVER_SHA:\n",
     "    if False:\n",
     "survive", "survive",
     "own_exe running-image sha check dropped (observe() hashes the same bytes in the bind leg)"),
    ("mu04",
     '    member_path = os.path.join(work, "server", member) if isinstance(member, str) else None\n',
     '    member_path = os.path.join(work, "server") if isinstance(member, str) else None\n',
     "killed-at-build", "-",
     "member_path constructed without the member name (points at the directory)"),
    ("mu05",
     'se.get("opened") is True and se.get("sha256") == SERVER_SHA',
     'se.get("opened") is not False and se.get("sha256") == SERVER_SHA',
     "survive", "survive",
     "rerun server_exe opened check weakened to not-False"),
    ("mu06",
     'and se.get("sha256") == SERVER_SHA\n',
     "and True\n",
     "survive", "survive",
     "rerun server_exe sha check dropped"),
    ("mu07",
     'and got is not None and (str(se.get("dev")), str(se.get("inode"))) == got):\n',
     "and got is not None and str(se.get(\"dev\")) == got[0]):\n",
     "survive", "survive",
     "rerun server_exe dev/inode compared on dev only"),
    ("mu08",
     'and os.path.realpath(str(osv.get("path"))) == os.path.realpath(member_path)\n',
     'and osv.get("path") is not None\n',
     "survive", "survive",
     "own_server path identity check dropped (any non-None path passes)"),
    ("mu09",
     'os.path.realpath(str(osv.get("path"))) == os.path.realpath(member_path)',
     'str(osv.get("path")) == str(member_path)',
     "survive", "survive",
     "realpath dropped: literal string comparison"),
    ("mu10",
     'and got is not None and (str(osv.get("dev")), str(osv.get("inode"))) == got):\n',
     "and got is not None):\n",
     "survive", "survive",
     "own_server dev/inode comparison dropped"),
    ("mu11",
     '            oprobs.append("own: no server was announced, so no running image was observed")\n',
     "            pass\n",
     "survive", "survive",
     "oprobs on ready None removed (own leg passes with no observation)"),
    ("mu12",
     "                owned += o\n",
     "                owned += 1\n",
     "survive", "killed-by-decoy",
     "owned counter increments regardless of the own verdict"),
    ("mu13",
     "        met = bool(bl and ol and tl and nl)\n",
     "        met = bool(bl and tl and nl)\n",
     "survive", "killed-by-decoy",
     "own leg removed from the met conjunction"),
    ("mu14",
     "    hit = [ln for ln in new if EXE_URL in ln]\n",
     "    hit = [ln for ln in new if EXE_URL not in ln]\n",
     "killed-at-build", "-",
     "newrow EXE_URL membership inverted"),
    ("mu15",
     '    if a.out:\n        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)\n',
     "    pass  # mutant: --out parent creation removed\n",
     "killed-with-missing-parent", "-",
     "--out mkdir removed; run with a nonexistent --out parent"),
    ("mu16",
     "        ol = owned == len(RECEIPTS)\n",
     "        ol = owned >= 1\n",
     "survive", "survive",
     "own leg passes with a single owned replay"),
    ("mu17",
     '        probs.append(f"own: running image sha256 {h.hexdigest()} is not the frozen server")\n    return got\n',
     '        probs.append(f"own: running image sha256 {h.hexdigest()} is not the frozen server")\n    return want\n',
     "survive", "survive-with-mirror-lie",
     "own_exe returns the member's identity instead of the observed image"),
    ("mu18",
     "            if member_path is None:\n",
     "            if member_path is not None:\n",
     "killed-at-build", "-",
     "member-present branch inverted"),
]


def main():
    with open(SRC, "rb") as fh:
        src = fh.read()
    base_sha = hashlib.sha256(src).hexdigest()
    assert base_sha == "e5753c453c30bd311e4c12fc962d324c7db482233b64b22795658b47b6ee5155", base_sha
    os.makedirs(DST, exist_ok=True)
    manifest = []
    for mid, old, new, build_exp, decoy_exp, note in MUTANTS:
        text = src.decode()
        n = text.count(old)
        assert n == 1, f"{mid}: anchor occurs {n} times, need exactly 1: {old!r}"
        mutated = text.replace(old, new)
        out = os.path.join(DST, f"{mid}.py")
        with open(out, "w") as fh:
            fh.write(mutated)
        manifest.append({
            "id": mid, "file": out,
            "old": old, "new": new,
            "sha256_pristine": base_sha,
            "sha256_mutant": hashlib.sha256(mutated.encode()).hexdigest(),
            "build_expectation": build_exp, "decoy_expectation": decoy_exp, "note": note,
        })
    with open(os.path.join(DST, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=1)
    print(f"{len(manifest)} mutants written to {DST}; pristine sha {base_sha}")


if __name__ == "__main__":
    sys.exit(main())
