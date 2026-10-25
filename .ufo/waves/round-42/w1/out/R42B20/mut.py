#!/usr/bin/env python3
"""Apply one named mutation to a fixture copy of the lane tree (seat R42B20)."""
import sys

AUDIT = "tools/round42-digest-audit.py"
LEDGER = "tools/digest-ledger.py"


def sub(path, old, new, count=1):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if text.count(old) != count:
        raise SystemExit(f"anchor count {text.count(old)} != {count} in {path}: {old[:60]!r}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.replace(old, new))


def m_shutil(d):
    sub(f"{d}/{AUDIT}", "import shutil\n", "")


def m_files(d):
    sub(f"{d}/{AUDIT}", "    files = {}\n", "")


def m_oids(d):
    sub(f"{d}/{AUDIT}", """    names = {}
    for l in objs:
        if not l:
            continue
        oid, _, name = l.partition(" ")
        names[oid] = name
    p = subprocess.run(["git", "-C", repo, "cat-file", "--batch"], input="".join(o + "\\n" for o in names).encode(),
""", """    oids = dict.fromkeys(l.partition(" ")[0] for l in objs if l)
    p = subprocess.run(["git", "-C", repo, "cat-file", "--batch"], input="".join(o + "\\n" for o in oids).encode(),
""")


def m_merge(d):
    sub(f"{d}/{AUDIT}", """    with tempfile.TemporaryDirectory(prefix="r42c2-") as export:
""", """    with tempfile.TemporaryDirectory(prefix="r42c2-") as export, \\
            tempfile.TemporaryDirectory(prefix="r42c2-hyg-") as priv:
""")
    sub(f"{d}/{AUDIT}", """    # hygiene: round-41 counters leave their private TMPDIR empty
    with tempfile.TemporaryDirectory(prefix="r42c2-hyg-") as priv, tempfile.TemporaryDirectory(prefix="r42c2-src-") as src:
        subprocess.run(["tar", "-x", "-C", src], input=git(repo, "archive", "--format=tar", tip, binary=True), check=True)
        env = dict(os.environ, TMPDIR=priv)
""", """        # hygiene: round-41 counters leave their private TMPDIR empty
        env = dict(os.environ, TMPDIR=priv)
""")
    sub(f"{d}/{AUDIT}", "            if not os.path.isfile(os.path.join(src, tool)):",
        "            if not os.path.isfile(os.path.join(export, tool)):")
    sub(f"{d}/{AUDIT}", "                subprocess.run([sys.executable, tool, \"--repo\", repo, \"--tip\", tip], cwd=src, env=env,",
        "                subprocess.run([sys.executable, tool, \"--repo\", repo, \"--tip\", tip], cwd=export, env=env,")
    sub(f"{d}/{AUDIT}", "        legs[\"hygiene\"] = int(not left and all(os.path.isfile(os.path.join(src, t)) for t in (",
        "        legs[\"hygiene\"] = int(not left and all(os.path.isfile(os.path.join(export, t)) for t in (")


def m_ledgerload(d):
    sub(f"{d}/{LEDGER}", """    if ledger_file is not None:
        with open(ledger_file, encoding="utf-8", errors="replace") as f:
            ledger = parse_ledger(f.read())
""", """    if ledger_file is not None:
        ledger = load_ledger(ledger_file)
""", count=2)
    sub(f"{d}/{LEDGER}", "def scan_dir(root: str, ledger_file: str | None):",
        """def load_ledger(path: str) -> dict:
    with open(path, encoding="utf-8", errors="replace") as f:
        return parse_ledger(f.read())


def scan_dir(root: str, ledger_file: str | None):""")


def m_all(d):
    m_shutil(d)
    m_files(d)
    m_oids(d)
    m_merge(d)


def m_all2(d):
    m_all(d)
    m_ledgerload(d)


def m_oracle(d):
    """Inject a tool bug to test whether the counter's independent copy detects it."""
    sub(f"{d}/{LEDGER}", '                    key = "external_ok" if h == t else "ledger_bad"',
        '                    key = "external_ok"')


PIN = "tools/round41-pinwatch-audit.py"


def m_hygleak(d):
    """Make a round-41 counter leak a temp entry, with the merged single extraction."""
    m_merge(d)
    sub(f"{d}/{PIN}", "import tempfile\n", "import tempfile\n\ntempfile.mkdtemp(prefix=\"leak-\")\n")


def m_hygleak_orig(d):
    """Same leak, unmerged counter: does the hygiene leg still fail?"""
    sub(f"{d}/{PIN}", "import tempfile\n", "import tempfile\n\ntempfile.mkdtemp(prefix=\"leak-\")\n")


MUTATIONS = dict(none=lambda d: None, shutil=m_shutil, files=m_files, oids=m_oids,
                 merge=m_merge, ledgerload=m_ledgerload, all=m_all, all2=m_all2, oracle=m_oracle,
                 hygleak=m_hygleak, hygleak_orig=m_hygleak_orig)

if __name__ == "__main__":
    MUTATIONS[sys.argv[1]](sys.argv[2])
