#!/usr/bin/env python3
"""build-survivors.py — round-74 pre-freeze control fixtures (KQ118(a)).

Builds the fixtures the round's three frozen claims must kill, so the control that
skips the claimed work can be scored before any seat runs:

  c1_invisible  a SCORECARD whose demonstrated-capabilities tables (rounds 73/74) are
                newer than the newest BOLD canonical heading (round 71) — the r42
                canon() resolves round 71 and the demonstrated names are invisible
  c1_clean      the same record plus a bold `**Capabilities — canonical list as of
                round 74**` covering every name (the honest record shape)
  c2_wrapped    a tip claim whose token is split across hard line breaks, citation in
                the same paragraph, receipt header rev=X != tip (r73 line-scoped pass
                uncounts it)
  c2_offset     a tip claim on line 1, its citation on line 2 of one paragraph,
                receipt header rev=X != tip (r73 pairs citations on the token line only)
  c2_mixed_honest  a record that binds its receipt by naming the receipt's revision in
                upper-case hex (header lower-case) — a case-sensitive v2 false-flags it
  c2_clean_realizable  a record naming the receipt's own revision (the realizable clean
                rule replacing the impossible committed-header-equals-tip clause)
  c3_edited     a host block recording the live triple at rev A with a `recorded at A`
                token, then a commit editing the block's date byte (r73 stays green)
  c3_clean      the same block, unchanged after A

Every git fixture is a throwaway repository under $KAMA_R74_SCRATCH (default
/fast/scratch/hyaku/kama-r74/controls-work). No git mutation runs outside a fixture
dir, every git call names -C <fixture>, and the toplevel is asserted before the first
commit.

Usage:
    python3 build-survivors.py [--work DIR] [--meta OUT.json]
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

GITID = ["-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
         "-c", "commit.gpgsign=false"]

LIVE_TRIPLE = ("Linux", "x86_64", "arch")  # this host; the r73 counter compares live


def sh(argv, cwd=None, check=True):
    r = subprocess.run(argv, cwd=None if cwd is None else str(cwd),
                       capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError("{} -> {}\n{}\n{}".format(" ".join(argv), r.returncode,
                                                     r.stdout, r.stderr))
    return r


def git(d: Path, *args, check=True):
    return sh(["git", "-C", str(d), *GITID, *args], check=check)


def rev(d: Path) -> str:
    return git(d, "rev-parse", "HEAD").stdout.strip()


def init(d: Path) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    git(d, "init", "-q", "-b", "master")
    top = Path(git(d, "rev-parse", "--show-toplevel").stdout.strip()).resolve()
    assert top == d.resolve(), "toplevel {} != fixture {}".format(top, d)
    return d


def put(d: Path, rel: str, text: str) -> None:
    p = d / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def commit(d: Path, msg: str) -> str:
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", msg)
    return rev(d)


# ----------------------------------------------------------------------------- C1

BOLD71 = """**Capabilities — canonical list as of round 71**

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curates where kama learns | `corpus/SOURCES.md` | 10 |
| pin-watch | Lists upstream release tags per pinned engine | `tools/pin-watch.py` | 41 |
| digest-ledger | Classifies every cited full SHA-256 | `tools/digest-ledger.py` | 42 |
"""

DEMO73 = """### Capabilities demonstrated in round 73

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| round-scope-cases | Grades linked-worktree and submodule scope cases | `tools/round73-round-scope-cases.py` | 73 |
| receipt-claim-binding | Rejects a three-token tip claim naming another revision | `tools/round73-receipt-claim-binding.py` | 73 |
"""

DEMO74 = """### Capabilities demonstrated in round 74

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| province-host-drift | Compares the recorded host triple with the live triple | `tools/round73-province-host-drift.py` | 73 |
| live-ollama-lifecycle | Starts the pinned Ollama binary on a loopback port | `tools/kama-ollama-live.py` | 61 |
"""

BOLD74 = """**Capabilities — canonical list as of round 74**

Same four columns; supersedes the round-71 list.

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curates where kama learns | `corpus/SOURCES.md` | 10 |
| pin-watch | Lists upstream release tags per pinned engine | `tools/pin-watch.py` | 41 |
| digest-ledger | Classifies every cited full SHA-256 | `tools/digest-ledger.py` | 42 |
| round-scope-cases | Grades linked-worktree and submodule scope cases | `tools/round73-round-scope-cases.py` | 73 |
| receipt-claim-binding | Rejects a three-token tip claim naming another revision | `tools/round73-receipt-claim-binding.py` | 73 |
| province-host-drift | Compares the recorded host triple with the live triple | `tools/round73-province-host-drift.py` | 73 |
| live-ollama-lifecycle | Starts the pinned Ollama binary on a loopback port | `tools/kama-ollama-live.py` | 61 |
"""

C1_HEAD = "# kama-shokunin — SCORECARD\n\nfixture record\n\n## Capabilities\n\nmirror\n\n"


def build_c1(root: Path, meta: dict) -> None:
    inv = root / "fixtures/c1_invisible"
    inv.mkdir(parents=True)
    (inv / "SCORECARD.md").write_text(C1_HEAD + BOLD71 + "\n" + DEMO73 + "\n" + DEMO74)
    meta["c1_invisible"] = {"fixture": str(inv)}

    clean = root / "fixtures/c1_clean"
    clean.mkdir(parents=True)
    (clean / "SCORECARD.md").write_text(
        C1_HEAD + BOLD71 + "\n" + DEMO73 + "\n" + DEMO74 + "\n" + BOLD74)
    meta["c1_clean"] = {"fixture": str(clean)}


# ----------------------------------------------------------------------------- C2

RECEIPT_PATH = ".ufo/waves/round-74/measured/a.out"

C2_SEED = {
    "LOG.md": "# kama fixture LOG\n",
    "plans/round-74-claims.md": "# kama round 74 — frozen claims\n\nfixture\n",
    "corpus/lessons/round-74.md": "# kama round 74 — fixture lesson\n",
}

ROUND_HEAD = "# kama fixture SCORECARD\n\n## Round 74 — fixture\n\n"


def build_c2_repo(root: Path, name: str, record_paragraph: str, meta: dict,
                  extra_record: str = "") -> None:
    d = init(root / "fixtures" / name)
    for rel, text in C2_SEED.items():
        put(d, rel, text)
    commit(d, "seed")
    put(d, RECEIPT_PATH, "# rev=PLACEHOLDER\nverdict: green\n")
    x = commit(d, "receipt at X")
    put(d, RECEIPT_PATH, "# rev={}\nverdict: green\n".format(x))
    commit(d, "receipt header names X")
    put(d, "SCORECARD.md", ROUND_HEAD + record_paragraph.format(receipt=RECEIPT_PATH) + "\n"
        + extra_record)
    tip = commit(d, "round-74 record")
    meta[name] = {"fixture": str(d), "round": 74, "receipt_rev": x, "tip": tip,
                  "receipt": RECEIPT_PATH}


def build_c2(root: Path, meta: dict) -> None:
    build_c2_repo(
        root, "c2_wrapped",
        "- C2 evidence: `{receipt}` — measured\n"
        "  at the\n"
        "  report tip.\n", meta)
    build_c2_repo(
        root, "c2_offset",
        "- C2 evidence: measured at the report tip.\n"
        "  Receipt: `{receipt}`.\n", meta)
    build_c2_repo(
        root, "c2_mixed_honest",
        "- C2 evidence: re-run at revision "
        "2E3CA86788C0EF041B34B329D58DB6D7953513FC naming `{receipt}`.\n",
        meta, extra_record="")
    # c2_mixed_honest names the REAL r73 revision to prove the hex source is immaterial;
    # its fixture receipt header carries the fixture's own commit instead — rewrite the
    # record to name the fixture receipt's revision in upper case.
    d = Path(meta["c2_mixed_honest"]["fixture"])
    x = meta["c2_mixed_honest"]["receipt_rev"]
    put(d, "SCORECARD.md", ROUND_HEAD +
        "- C2 evidence: re-run at revision {} naming `{}`.\n".format(x.upper(), RECEIPT_PATH))
    commit(d, "record names fixture revision in upper case")
    build_c2_repo(
        root, "c2_clean_realizable",
        "- C2 evidence: placeholder receipt line, replaced before the tip.\n",
        meta)
    # c2_clean_realizable must name the fixture receipt's own revision (lower case).
    d = Path(meta["c2_clean_realizable"]["fixture"])
    x = meta["c2_clean_realizable"]["receipt_rev"]
    put(d, "SCORECARD.md", ROUND_HEAD +
        "- C2 evidence: re-run at revision {} naming `{}`.\n".format(x, RECEIPT_PATH))
    commit(d, "record names the receipt's own revision")


# ----------------------------------------------------------------------------- C3

def province_block(date: str, recorded_at: str = None) -> str:
    s, m, i = LIVE_TRIPLE
    text = ("# kama fixture PROVINCE\n\n"
            "Round-73 host-identity block ({}). Host triple: `uname -s` -> `{}`; "
            "`uname -m` -> `{}`; `/etc/os-release` `ID` -> `{}`.\n").format(date, s, m, i)
    if recorded_at:
        text = text.rstrip("\n") + " recorded at {}.\n".format(recorded_at)
    return text


def build_c3(root: Path, meta: dict) -> None:
    edited = init(root / "fixtures/c3_edited")
    put(edited, "LOG.md", "# kama fixture LOG\n")
    a = commit(edited, "seed")
    put(edited, "PROVINCE.md", province_block("2026-11-03", recorded_at=a))
    commit(edited, "host block recorded at A")
    put(edited, "PROVINCE.md", province_block("2026-11-04", recorded_at=a))
    b = commit(edited, "edit the recorded date byte")
    meta["c3_edited"] = {"fixture": str(edited), "recorded_rev": a, "tip": b}

    clean = init(root / "fixtures/c3_clean")
    put(clean, "LOG.md", "# kama fixture LOG\n")
    a = commit(clean, "seed")
    put(clean, "PROVINCE.md", province_block("2026-11-03", recorded_at=a))
    commit(clean, "host block recorded at A")
    put(clean, "LOG.md", "# kama fixture LOG\nunrelated later commit\n")
    b = commit(clean, "unrelated edit")
    meta["c3_clean"] = {"fixture": str(clean), "recorded_rev": a, "tip": b}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=os.environ.get("KAMA_R74_SCRATCH",
                                                     "/fast/scratch/hyaku/kama-r74/controls-work"))
    ap.add_argument("--meta", default=None)
    args = ap.parse_args(argv)

    root = Path(args.work).resolve()
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)

    meta = {}
    build_c1(root, meta)
    build_c2(root, meta)
    build_c3(root, meta)

    meta_path = Path(args.meta) if args.meta else root / "fixtures-meta.json"
    meta_path.write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n")
    for name in sorted(meta):
        print("FIXTURE {} {}".format(name, meta[name]["fixture"]))
    print("META {}".format(meta_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
