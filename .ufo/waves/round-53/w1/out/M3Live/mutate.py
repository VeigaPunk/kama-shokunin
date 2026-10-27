#!/usr/bin/env python3
"""M3Live round-53 mutation driver for tools/kama-llamacpp-live.py.

Applies exact-count textual mutations to the pristine copy and writes one
mutant file per entry plus a manifest. Each (old, new) pair must occur exactly
`count` times (default 1) in the pristine text, or the driver aborts.
"""
import hashlib
import json
import pathlib
import sys

PRISTINE = pathlib.Path(__file__).resolve().parent / "live" / "tools" / "kama-llamacpp-live.py"
OUTDIR = pathlib.Path(__file__).resolve().parent / "mutants"

MUTANTS = {
    # --- code_mappings() filter stage -------------------------------------
    "M01-perm-filter-drop": [
        ("if (len(f) < 6 or 'x' not in f[1] or not f[5].startswith('/')",
         "if (len(f) < 6 or not f[5].startswith('/')"),
    ],
    "M02-slash-prefix-drop": [
        ("'x' not in f[1] or not f[5].startswith('/')",
         "'x' not in f[1]"),
    ],
    "M03-memfd-skip-drop": [
        ("or f[5].startswith('/memfd:') or (f[5], f[3], f[4]) in seen",
         "or (f[5], f[3], f[4]) in seen"),
    ],
    "M04-dedupe-key-path-only": [
        ("(f[5], f[3], f[4]) in seen", "f[5] in seen"),
        ("seen.add((f[5], f[3], f[4]))", "seen.add(f[5])"),
    ],
    # --- code_mappings() guard stage ---------------------------------------
    "M05-deleted-guard-drop": [
        ("""        if path.endswith(' (deleted)'):
            # the mapped file has no directory entry any more (rename-over or unlink): the
            # name is not opened, so a file that happens to carry that name is never hashed
            out.append({**ent, 'opened': False, 'reason': 'mapped-file-deleted'})
            continue
""", ""),
    ],
    "M06-inode-compare-drop": [
        ("if (not stat.S_ISREG(st.st_mode) or str(st.st_ino) != ino",
         "if (not stat.S_ISREG(st.st_mode)"),
    ],
    "M07-dev-compare-drop-all-uid": [
        ("or (sdev != dev and st.st_uid != 0)):", "):"),
    ],
    # --- code_mappings() hash stage ----------------------------------------
    "M08-read-loop-while-false": [
        ("st_size\n            while left > 0:", "st_size\n            while False:"),
    ],
    "M09-shrink-check-dead": [
        ("            if left != 0:", "            if left < 0:"),
    ],
    "M10-opened-flag-drop": [
        ("out.append({**ent, 'opened': True, 'size': st.st_size, 'uid': st.st_uid,",
         "out.append({**ent, 'size': st.st_size, 'uid': st.st_uid,"),
    ],
    "M13-chunk-break-drop": [
        ("""                chunk = os.read(fd, min(1 << 20, left))
                if not chunk:
                    break
                h.update(chunk)
""", """                chunk = os.read(fd, min(1 << 20, left))
                h.update(chunk)
"""),
    ],
    # --- receipt wiring -----------------------------------------------------
    "M11-wiring-empty-mappings": [
        ("receipt['code_mappings'] = code_mappings(proc.pid)",
         "receipt['code_mappings'] = {'read': True, 'mappings': []}"),
    ],
    "M12-wiring-key-rename": [
        ("receipt['code_mappings']", "receipt['code_map']", 2),
    ],
}


def main() -> int:
    text = PRISTINE.read_text(encoding="utf-8")
    pristine_sha = hashlib.sha256(text.encode()).hexdigest()
    OUTDIR.mkdir(exist_ok=True)
    manifest = {"pristine_sha256": pristine_sha, "pristine": str(PRISTINE), "mutants": {}}
    for name, pairs in MUTANTS.items():
        cur = text
        applied = []
        for pair in pairs:
            old, new = pair[0], pair[1]
            want = pair[2] if len(pair) > 2 else 1
            got = cur.count(old)
            if got != want:
                print(f"{name}: anchor occurs {got}x, expected {want}: {old[:70]!r}",
                      file=sys.stderr)
                return 2
            cur = cur.replace(old, new)
            applied.append({"old": old[:80], "new": new[:80], "count": want})
        out = OUTDIR / f"{name}.py"
        out.write_text(cur, encoding="utf-8")
        manifest["mutants"][name] = {
            "file": str(out),
            "sha256": hashlib.sha256(cur.encode()).hexdigest(),
            "edits": applied,
        }
        print(f"{name}: ok -> {out}")
    (OUTDIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"pristine sha256 {pristine_sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
