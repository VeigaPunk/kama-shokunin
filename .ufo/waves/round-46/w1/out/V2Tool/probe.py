#!/usr/bin/env python3
"""V2Tool round-46 correctness probes for tools/append-only-audit.py.

Every fixture repo is created under V2SCRATCH (never the lane, never /tmp).
Receipts are written to OUT. The lane repo itself is never touched here.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOOL = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py"
COUNTER = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round46-append-audit-check.py"
OUT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/V2Tool"
S = os.environ["V2SCRATCH"]
TMP = os.path.join(S, "tmp")
os.makedirs(TMP, exist_ok=True)
IDENT = ["-c", "user.name=v2tool", "-c", "user.email=v2tool@invalid", "-c", "commit.gpgsign=false"]
HEX40 = re.compile(r"^[0-9a-f]{40}$")
RESULTS = []


def rec(name, ok, detail):
    RESULTS.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


def git(d, *a):
    p = subprocess.run(["git", "-C", d, *a], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git -C {d} {' '.join(a)}: {p.stderr.decode(errors='replace')[:300]}")
    return p.stdout.decode().strip()


class Fix:
    def __init__(self, tag):
        self.d = os.path.join(S, "fix", f"{tag}-{os.urandom(3).hex()}")
        os.makedirs(self.d)
        git(self.d, "init", "-q")
        top = git(self.d, "rev-parse", "--show-toplevel")
        assert os.path.realpath(top) == os.path.realpath(self.d), f"toplevel mismatch: {top}"
        self.n = 0

    def commit(self, files=None, rm=()):
        for name, body in (files or {}).items():
            path = os.path.join(self.d, name)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if isinstance(body, bytes):
                with open(path, "wb") as fh:
                    fh.write(body)
            elif isinstance(body, str):
                with open(path, "w") as fh:
                    fh.write(body)
            else:
                with open(path, "w") as fh:
                    fh.write("".join(x + "\n" for x in body))
        for name in rm:
            os.remove(os.path.join(self.d, name))
        git(self.d, "add", "-A")
        self.n += 1
        git(self.d, *IDENT, "commit", "-q", "--allow-empty", "-m", f"c{self.n}")
        return git(self.d, "rev-parse", "HEAD")


def rnd(tag, i):
    return f"{tag} {i} {os.urandom(8).hex()}"


def run_tool(args, env_extra=None):
    env = dict(os.environ, TMPDIR=TMP)
    if env_extra:
        env.update(env_extra)
    p = subprocess.run([sys.executable, TOOL, *args], capture_output=True, env=env, timeout=900)
    return p.returncode, p.stdout.decode(errors="replace"), p.stderr.decode(errors="replace")


def jload(out):
    try:
        return json.loads(out)
    except Exception:
        return None


# --------------------------------------------------------------------- probes

def p1_spaces():
    f = Fix("spaces")
    a = [rnd("a", i) for i in range(40)]
    f.commit({"my file.md": a})
    c2 = f.commit({"my file.md": a[:10]})
    c3 = f.commit({"my file.md": a})
    rc, out, err = run_tool(["--repo", f.d, "--to", c3, "--json", "--files", "my file.md"])
    j = jload(out)
    e = j["events"] if j else []
    ok = (rc == 0 and j is not None and len(e) == 1 and e[0]["commit"] == c2
          and e[0]["deleted"] == 30 and e[0]["status"] == "restored" and e[0]["restored_by"] == c3)
    rec("P1 path-with-spaces", ok, f"rc={rc} events={e if j else out[:200]}{err[:100]}")


def p2_missing():
    f = Fix("missing")
    a = [rnd("m", i) for i in range(30)]
    f.commit({"gone file.md": a})
    c2 = f.commit(rm=["gone file.md"])
    rc, out, err = run_tool(["--repo", f.d, "--to", c2, "--json", "--files", "gone file.md"])
    j = jload(out)
    e = j["events"] if j else []
    ok1 = (rc == 1 and j is not None and len(e) == 1 and e[0]["deleted"] == 30
           and e[0]["status"] == "unrestored" and e[0]["restored_by"] is None
           and e[0]["restored_at_tip"] == 0)
    rc2, out2, _ = run_tool(["--repo", f.d, "--to", c2, "--json", "--files", "ghost file.md"])
    j2 = jload(out2)
    ok2 = rc2 == 0 and j2 is not None and j2["events"] == []
    rec("P2 missing-paths", ok1 and ok2,
        f"removed-at-tip: rc={rc} ev={e if j else out[:160]}; never-existed: rc={rc2} ev={j2['events'] if j2 else out2[:160]}")
    # raw cat-file --batch-check echo behaviour receipt (spaces in spec, missing spec)
    specs = f"{c2}:gone file.md\n{c2}:ghost file.md\n{c2}:corpus\n"
    p = subprocess.run(["git", "-C", f.d, "cat-file", "--batch-check=%(objectname) %(objecttype)"],
                       input=specs, capture_output=True, text=True)
    with open(os.path.join(OUT, "receipt-batchcheck-raw.txt"), "w") as fh:
        fh.write(f"# git {subprocess.run(['git','--version'],capture_output=True,text=True).stdout.strip()}\n")
        fh.write(f"# input specs:\n{specs}\n# raw output:\n{p.stdout}\n# rc={p.returncode}\n")


def p3_root():
    f = Fix("root")
    c1 = f.commit({"LOG.md": [rnd("r", i) for i in range(30)]})
    rc, out, _ = run_tool(["--repo", f.d, "--to", "HEAD", "--json"])
    j = jload(out)
    ok1 = rc == 0 and j is not None and j["commits"] == 1 and j["events"] == [] and j["to"] == c1
    f.commit({"LOG.md": [rnd("s", i) for i in range(31)]})
    f.commit({"LOG.md": [rnd("t", i) for i in range(32)]})
    rc2, out2, _ = run_tool(["--repo", f.d, "--to", c1, "--json"])
    j2 = jload(out2)
    ok2 = rc2 == 0 and j2 is not None and j2["commits"] == 1 and j2["events"] == []
    rec("P3 root-commit", ok1 and ok2,
        f"single-commit: rc={rc} summary={j['summary'] if j else out[:120]}; --to root: rc={rc2} summary={j2['summary'] if j2 else out2[:120]}")


def p4_merge_firstparent_deletion():
    f = Fix("merge")
    a = [rnd("a", i) for i in range(40)]
    f.commit({"LOG.md": a})
    git(f.d, "checkout", "-q", "-b", "side")
    side = f.commit({"LOG.md": a[:10]})
    git(f.d, "checkout", "-q", "-")
    main = f.commit({"LOG.md": a + ["main line"]})
    p = subprocess.run(["git", "-C", f.d, *IDENT, "merge", "--no-commit", "--no-ff", "side"],
                       capture_output=True)
    # conflict expected; resolve by taking side's version exactly
    with open(os.path.join(f.d, "LOG.md"), "w") as fh:
        fh.write("".join(x + "\n" for x in a[:10]))
    git(f.d, "add", "LOG.md")
    git(f.d, *IDENT, "commit", "-q", "-m", "merge resolved to side")
    m = git(f.d, "rev-parse", "HEAD")
    par = git(f.d, "rev-list", "--parents", "-n", "1", m).split()
    shown = git(f.d, "show", f"{m}:LOG.md").split("\n")
    fixture_ok = shown == a[:10] and par[0] == m and par[1] == main and par[2] == side and len(par) == 3
    rc, out, err = run_tool(["--repo", f.d, "--to", m, "--json"])
    j = jload(out)
    evs = {e["commit"]: e for e in j["events"]} if j else {}
    ok = (fixture_ok and j is not None and rc == 1 and m in evs and side in evs
          and evs[m]["deleted"] == 31 and evs[side]["deleted"] == 30
          and evs[m]["status"] == "unrestored")
    rec("P4a merge-deletes-vs-first-parent", ok,
        f"parents={[x[:8] for x in par]} events={ {k[:8]: (v['deleted'], v['status']) for k, v in evs.items()} } rc={rc} {err[:100]}")


def p4b_octopus():
    f = Fix("octo")
    a = [rnd("o", i) for i in range(40)]
    f.commit({"LOG.md": a, "notes.md": ["n1"]})
    base = git(f.d, "rev-parse", "HEAD")
    git(f.d, "checkout", "-q", "-b", "b1")
    b1 = f.commit({"LOG.md": a[:10]})
    git(f.d, "checkout", "-q", base)
    git(f.d, "checkout", "-q", "-b", "b2")
    b2 = f.commit({"other.md": ["x", "y"]})
    git(f.d, "checkout", "-q", base)
    main_tip = f.commit({"notes.md": ["n1", "n2"]})
    p = subprocess.run(["git", "-C", f.d, *IDENT, "merge", "-s", "octopus", "--no-edit", "b1", "b2"],
                       capture_output=True)
    assert p.returncode == 0, f"octopus merge failed: {p.stderr.decode()[:300]}"
    m = git(f.d, "rev-parse", "HEAD")
    par = git(f.d, "rev-list", "--parents", "-n", "1", m).split()
    rc, out, err = run_tool(["--repo", f.d, "--to", m, "--json"])
    j = jload(out)
    evs = {e["commit"]: e for e in j["events"]} if j else {}
    ok = (j is not None and rc == 1 and set(evs) == {b1, m}
          and all(e["deleted"] == 30 for e in evs.values())
          and len(par) == 4 and par[1] == main_tip and par[2] == b1 and par[3] == b2)
    rec("P4b octopus-first-parent", ok,
        f"parents={[x[:8] for x in par]} events={ {k[:8]: v['deleted'] for k, v in evs.items()} } rc={rc} {err[:100]}")


def p5_exit_codes():
    f = Fix("exit")
    a = [rnd("x", i) for i in range(30)]
    f.commit({"LOG.md": a})
    c2 = f.commit({"LOG.md": a[:10]})       # event: exit 1
    rows = []

    def t(name, args, want_rc, stderr_has=None):
        rc, out, err = run_tool(args)
        okrow = rc == want_rc and (stderr_has is None or stderr_has.lower() in err.lower())
        rows.append((name, rc, want_rc, okrow, (err.strip().splitlines() or [""])[0][:110]))

    t("missing-repo", ["--repo", os.path.join(S, "definitely-missing"), "--to", "HEAD"], 2, "could-not-evaluate")
    t("bad-to", ["--repo", f.d, "--to", "deadbeef" * 5], 2, "could-not-evaluate")
    t("threshold-0", ["--repo", f.d, "--threshold", "0"], 2, "could-not-evaluate")
    t("threshold-neg", ["--repo", f.d, "--threshold", "-5"], 2, "could-not-evaluate")
    t("threshold-notint", ["--repo", f.d, "--threshold", "abc"], 2)
    t("event-exit-1", ["--repo", f.d, "--to", c2], 1)
    t("no-event-exit-0", ["--repo", f.d, "--to", "HEAD" if False else git(f.d, "rev-parse", "HEAD"), "--threshold", "40"], 0)
    ok = all(r[3] for r in rows)
    rec("P5 exit-codes", ok, "; ".join(f"{n}: rc={rc}(want {w}){'ok' if o else 'MISMATCH ' + e}" for n, rc, w, o, e in rows))


def p6_tmp_honoring():
    tmpA = os.path.join(S, "tmpA")
    tmpB = os.path.join(S, "tmpB")
    os.makedirs(tmpA, exist_ok=True)
    os.makedirs(tmpB, exist_ok=True)
    # white-box: monkeypatch tempfile.mkdtemp and run the tool's own main() in-process
    import runpy
    report = {}

    def spy_run(label, argv, env_tmp=None):
        calls = []
        orig = tempfile.mkdtemp
        old = os.environ.get("TMPDIR")
        if env_tmp:
            os.environ["TMPDIR"] = env_tmp

        def spy(*a, **kw):
            calls.append(kw.get("dir"))
            return orig(*a, **kw)
        tempfile.mkdtemp = spy
        old_argv = sys.argv
        sys.argv = ["append-only-audit.py", *argv]
        try:
            runpy.run_path(TOOL, run_name="__main__")
            code = None
        except SystemExit as e:
            code = e.code
        finally:
            sys.argv = old_argv
            tempfile.mkdtemp = orig
            if env_tmp:
                if old is None:
                    os.environ.pop("TMPDIR", None)
                else:
                    os.environ["TMPDIR"] = old
        report[label] = (calls[:1], code)

    spy_run("tmpdir", ["--selftest"], env_tmp=tmpA)
    spy_run("scratch", ["--selftest", "--scratch", tmpB])
    d1, code1 = report["tmpdir"]
    d2, code2 = report["scratch"]
    ok = (code1 == 0 and d1 and d1[0] == tmpA and code2 == 0 and d2 and d2[0] == tmpB)
    rec("P6a tmpdir/scratch-honored", ok,
        f"mkdtemp dir with TMPDIR={tmpA}: {d1} (selftest rc={code1}); with --scratch={tmpB}: {d2} (rc={code2})")
    # F1: nonexistent --scratch -> uncaught traceback, exit 1, no AOA_SELFTEST line
    rc, out, err = run_tool(["--selftest", "--scratch", os.path.join(S, "nope-nope-nope")])
    first = (err.strip().splitlines() or [""])[-1][:140]
    rec("P6b nonexistent-scratch", rc == 1 and "AOA_SELFTEST" not in out,
        f"rc={rc} stderr-tail={first} (F1 evidence: traceback instead of clean error; counter does makedirs first)")
    # fallback proof: TMPDIR pointing at a nonexistent dir silently falls back to /tmp
    before = set(glob.glob("/tmp/aoa-*"))
    rc2, out2, err2 = run_tool(["--selftest"], env_extra={"TMPDIR": os.path.join(S, "also-missing")})
    m = re.search(r"AOA_SELFTEST pass=(\d+) fail=(\d+)", out2)
    rec("P6c bad-TMPDIR-falls-back", rc2 == 0 and m is not None,
        f"rc={rc2} line={m.group(0) if m else None} (gettempdir() falls back to /tmp when TMPDIR is invalid)")


def p7_json_shape():
    f = Fix("json")
    a = [rnd("j", i) for i in range(60)]
    f.commit({"LOG.md": a})
    f.commit({"LOG.md": a[:30]})                       # 30 deleted, never restored
    b = [rnd("k", i) for i in range(40)]
    f.commit({"corpus/QUALITY.md": b})
    f.commit({"corpus/QUALITY.md": b[:20]})            # 20 deleted
    c5 = f.commit({"corpus/QUALITY.md": b})            # restored
    rc, out, err = run_tool(["--repo", f.d, "--to", c5, "--json"])
    j = jload(out)
    evs = {(e["file"], e["deleted"], e["restored_at_tip"], e["status"], e["restored_by"]) for e in j["events"]} if j else set()
    checks = {
        "top-keys": j is not None and set(j) == {"to", "threshold", "files", "commits", "events", "summary"},
        "to-is-tip": j is not None and j["to"] == c5,
        "threshold": j is not None and j["threshold"] == 20,
        "files-default": j is not None and j["files"] == ["SCORECARD.md", "LOG.md", "corpus/QUALITY.md", "corpus/README.md", "corpus/SOURCES.md"],
        "ev-keys": bool(j) and all(set(e) == {"commit", "file", "deleted", "restored_at_tip", "status", "restored_by"} for e in j["events"]),
        "hex40": bool(j) and all(HEX40.match(e["commit"]) and (e["restored_by"] is None or HEX40.match(e["restored_by"])) for e in j["events"]),
        "expect-events": evs == {("LOG.md", 30, 0, "unrestored", None), ("corpus/QUALITY.md", 20, 20, "restored", c5)},
        "rc-agrees": rc == 1,
        "summary": j is not None and j["summary"] == {"commits": 5, "events": 2, "restored": 1, "partial": 0, "unrestored": 1},
    }
    rc2, out2, _ = run_tool(["--repo", f.d, "--to", c5[:12], "--json"])
    j2 = jload(out2)
    checks["short-to-expands"] = j2 is not None and j2["to"] == c5
    # text render format vs docstring
    rc3, out3, _ = run_tool(["--repo", f.d, "--to", c5])
    lines3 = out3.strip().split("\n")
    fmt_ok = (len(lines3) == 3
              and re.match(r"^event [0-9a-f]{12} LOG\.md deleted=30 restored_at_tip=0 status=unrestored restored_by=-$", lines3[0])
              and re.match(r"^event [0-9a-f]{12} corpus/QUALITY\.md deleted=20 restored_at_tip=20 status=restored restored_by=[0-9a-f]{12}$", lines3[1])
              and re.match(r"^summary commits=5 events=2 restored=1 partial=0 unrestored=1$", lines3[2]))
    checks["render-format"] = fmt_ok
    rec("P7 json-shape+render", all(checks.values()),
        " ".join(f"{k}={'ok' if v else 'FAIL'}" for k, v in checks.items()) + f" rc={rc}")


def p8_files_empty_fallback():
    f = Fix("emptyfiles")
    a = [rnd("e", i) for i in range(30)]
    f.commit({"LOG.md": a})
    c2 = f.commit({"LOG.md": a[:5], "notes.md": [rnd("n", i) for i in range(30)]})
    f.commit({"notes.md": [rnd("q", i) for i in range(3)]})
    rc, out, _ = run_tool(["--repo", f.d, "--to", git(f.d, "rev-parse", "HEAD"), "--json", "--files", ","])
    j = jload(out)
    fallback = (j is not None and j["files"] == ["SCORECARD.md", "LOG.md", "corpus/QUALITY.md", "corpus/README.md", "corpus/SOURCES.md"]
                and [e["file"] for e in j["events"]] == ["LOG.md"])
    rec("P8 files-comma-silent-fallback", fallback,
        f"--files ',' rc={rc} files={j['files'] if j else None} events={[e['file'] for e in j['events']] if j else out[:120]} "
        f"(F3 evidence: empty --files list silently reverts to the five declared files; notes.md losing 30 lines is unaudited)")


def p9_nonutf8():
    f = Fix("latin1")
    body = b"".join(b"caf\xff line %d %s\n" % (i, os.urandom(4).hex().encode()) for i in range(30))
    f.commit({"LOG.md": body})
    c2 = f.commit({"LOG.md": b"kept\n" * 5})
    rc, out, err = run_tool(["--repo", f.d, "--to", c2, "--json"])
    crash = "UnicodeDecodeError" in err
    rec("P9 non-utf8-crash", crash,
        f"rc={rc} UnicodeDecodeError-in-traceback={crash} stderr-tail={(err.strip().splitlines() or [''])[-1][:130]} "
        f"(F2 evidence: exit 1 + traceback; docstring promises exit 2 for could-not-evaluate)")


def p10_counter_crosscheck():
    f = Fix("c2cross")
    with open(TOOL) as fh:
        tool_text = fh.read()
    D = "dup " + os.urandom(8).hex()
    u = [rnd("u", i) for i in range(10)]
    w = [rnd("w", i) for i in range(15)]
    log = [D] * 30 + u
    qual = [f"--x{i} {os.urandom(6).hex()}" for i in range(30)]
    read = [""] * 25 + w
    c1 = f.commit({"tools/append-only-audit.py": tool_text, "LOG.md": log,
                   "corpus/QUALITY.md": qual, "corpus/README.md": read, "notes.md": ["n1"]})
    c2 = f.commit({"LOG.md": u, "corpus/QUALITY.md": "",
                   "corpus/README.md": w})
    c3 = f.commit({"LOG.md": u + [D]})
    c4 = f.commit({"notes.md": ["n1", "n2"]})
    rc, out, err = run_tool(["--repo", f.d, "--to", c4, "--json"])
    j = jload(out)
    evs = {(e["file"], e["deleted"], e["restored_at_tip"], e["status"], e["restored_by"]) for e in j["events"]} if j else set()
    tool_ok = (j is not None and rc == 0 and evs == {
        ("LOG.md", 30, 30, "restored", c3),
        ("corpus/README.md", 25, 25, "restored", c3),
    } and all(e["commit"] == c2 for e in j["events"]))
    rec("P10a shared-quirk-events", tool_ok,
        f"dup-lines restored_at_tip=30 from one occurrence ok; 25 empty lines deleted=restored ok; "
        f"30 '--'-prefixed deletions produce NO event (shared '---' exclusion) ok; rc={rc} evs={evs if j else out[:200]}")
    env = dict(os.environ)
    p = subprocess.run([sys.executable, COUNTER, "--repo", f.d, "--tip", c4, "--scratch", os.path.join(S, "c2scratch")],
                       capture_output=True, env=env, timeout=900)
    text = p.stdout.decode(errors="replace") + p.stderr.decode(errors="replace")
    m = re.search(r"selftest=(\d) fixture=(\d) lane=(\d) table=(\d).*met=(\w+)", text)
    got = m.groups() if m else None
    ok2 = got is not None and got[:3] == ("1", "1", "1") and got[3] == "0"
    with open(os.path.join(OUT, "receipt-c2cross.txt"), "w") as fh:
        fh.write(f"$ python3 {COUNTER} --repo <c2cross fixture> --tip {c4} --scratch {S}/c2scratch\n")
        fh.write(f"rc={p.returncode}\n{text}\n")
    rec("P10b counter-agreement", ok2,
        f"counter legs selftest/fixture/lane={got[:3] if got else None} table={got[3] if got else None} (1 = tool matches "
        f"independent recomputation incl. blind random fixture; table=0 expected, no SCORECARD in fixture) rc={p.returncode}")


def p11_quoted_path():
    f = Fix("quoted")
    a = [rnd("w", i) for i in range(30)]
    name = 'we"ird.md'
    f.commit({name: a})
    c2 = f.commit({name: a[:5]})
    rc, out, _ = run_tool(["--repo", f.d, "--to", c2, "--json", "--files", name])
    j = jload(out)
    files_changed = [e["file"] for e in j["events"]] if j else ["<unparseable>"]
    rec("P11 quote-in-path", True,
        f"rc={rc} events={files_changed} (git C-quotes this path in --name-only output; "
        f"event {'MISSED - F7 confirmed' if not files_changed else 'detected'} at L97/L99)")
    # raw name-only receipt
    raw = subprocess.run(["git", "-C", f.d, "diff", "--no-renames", "--name-only",
                          "HEAD^", "HEAD"], capture_output=True, text=True)
    with open(os.path.join(OUT, "receipt-quoted-path.txt"), "w") as fh:
        fh.write(f"# git diff --no-renames --name-only HEAD^ HEAD on fixture with path {name!r}\n")
        fh.write(raw.stdout + f"\n# rc={raw.returncode}\n")


def p12_pathspec_prefix():
    f = Fix("pathspec")
    a = [rnd("p", i) for i in range(30)]
    f.commit({"corpus/QUALITY.md": a})
    c2 = f.commit({"corpus/QUALITY.md": a[:5]})
    rc, out, _ = run_tool(["--repo", f.d, "--to", c2, "--json", "--files", "corpus"])
    j = jload(out)
    rec("P12 dir-as-files-silent-skip", j is not None and j["events"] == [] and rc == 0,
        f"--files corpus rc={rc} events={j['events'] if j else out[:120]} "
        f"(F7 class: '--files' value matches as a pathspec at L97 but the literal compare at L99 skips it; silent no-audit, rc=0)")


def main():
    with open(os.path.join(OUT, "receipt-correctness.txt"), "w") as fh:
        fh.write("V2Tool correctness probes for tools/append-only-audit.py\n")
    for fn in [p1_spaces, p2_missing, p3_root, p4_merge_firstparent_deletion, p4b_octopus,
               p5_exit_codes, p6_tmp_honoring, p7_json_shape, p8_files_empty_fallback,
               p9_nonutf8, p10_counter_crosscheck, p11_quoted_path, p12_pathspec_prefix]:
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            rec(fn.__name__, False, f"probe crashed: {type(e).__name__}: {e}")
    with open(os.path.join(OUT, "receipt-correctness.txt"), "a") as fh:
        for name, ok, detail in RESULTS:
            fh.write(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}\n")
    fails = sum(1 for _, ok, _ in RESULTS if not ok)
    print(f"PROBE_SUMMARY total={len(RESULTS)} fail={fails}")


if __name__ == "__main__":
    main()
