#!/usr/bin/env python3
"""port_v2_cases_to_v1.py - run append-only-audit v2's 15 selftest cases against v1's audit().

Round-47 wave-1 seat X1SelftestV2 (lane kama). The v2 tool (append-only-audit/v2, lane
commit 3a09a1d93dcc16799cf6c4b48786e6440af134c4) ships a 15-case selftest; v1
(bbcc6dc2fbd7fc04b1d91a97ffa239a6601cd5ba:tools/append-only-audit.py) shipped 10. This
harness ports every v2 case to v1, changing only:
  - the audit() call signature (v1: audit(repo, to, threshold, files); no contract arg),
  - the result field name restored_max -> restored_at_tip.
The fixture bodies, commit sequences and expected numbers are copied from v2 unchanged.
v2's restored_best has no v1 counterpart: an assertion on it is recorded as `skipped`
and the case verdict is reported twice -- `ok` (behavioral: every v1-expressible
assertion holds) and `strict_ok` (ok AND no v2 field was unavailable).

Usage:
  port_v2_cases_to_v1.py --v1-tool PATH [--scratch DIR] [--json OUT]

Read-only outside --scratch. Fixtures are removed on exit.
Exit: 0 harness ran (case verdicts are data, not the harness exit); 2 could not evaluate.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import sys
import tempfile

MISSING = object()
SKIP_FIELDS = {"restored_best": "absent from v1's event schema (v1 reports no witness commit)"}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def revtext(mod, repo):
    """HEAD as text: v1's _git is text=True, v2's returns bytes."""
    out = mod._git(repo, "rev-parse", "HEAD")
    return out.decode().strip() if isinstance(out, bytes) else out.strip()


def make_harness(v1):
    """v1.audit + a v1 Fixture that can also write raw bytes (v2's raw=True setups)."""

    class Fixture(v1.Fixture):
        def commit(self, files, delete=(), raw=False):
            for name, body in files.items():
                path = os.path.join(self.d, name)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "wb") as fh:
                    fh.write(body if raw else "".join(x + "\n" for x in body).encode())
            for name in delete:
                v1._git(self.d, "rm", "-q", name)
            v1._git(self.d, "add", "-A")
            self.n += 1
            v1._git(self.d, *self.IDENT, "commit", "-q", "--allow-empty", "-m", f"c{self.n}")
            return revtext(v1, self.d)

    def audit(repo, to, threshold=20, files=None):
        # v1 signature: audit(repo_path, to, threshold, files); v1 has no contract argument.
        return v1.audit(repo, to, threshold, files)

    def field(event, name):
        """v2 field name, falling back to v1's restored_at_tip; MISSING when absent."""
        if name in event:
            return event[name]
        if name == "restored_max" and "restored_at_tip" in event:
            return event["restored_at_tip"]
        return MISSING

    return Fixture, audit, field


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--v1-tool", required=True, help="v1 append-only-audit.py (read-only)")
    ap.add_argument("--v2-tool", help="v2 tool, only for the case list cross-check (optional)")
    ap.add_argument("--scratch", default=None)
    ap.add_argument("--json", help="write the per-case JSON here")
    a = ap.parse_args(argv)
    root = a.scratch or tempfile.gettempdir()
    os.makedirs(root, exist_ok=True)
    work = tempfile.mkdtemp(prefix="x1port-", dir=root)

    try:
        v1 = load(a.v1_tool, "aoa_v1")
        Fixture, audit, field = make_harness(v1)
        F = ["LOG.md", "SCORECARD.md", "corpus/QUALITY.md", "corpus/README.md", "corpus/SOURCES.md"]
        results = []

        def case(name, fn):
            entry = {"case": name, "ok": False, "strict_ok": False, "skipped": [],
                     "observed": {}, "why": ""}
            try:
                ok, obs, skipped, why = fn()
                entry.update(ok=ok, observed=obs, skipped=skipped, why=why)
                entry["strict_ok"] = bool(ok and not skipped)
            except Exception as exc:  # noqa: BLE001 - a crash is a failed case
                entry["why"] = f"exception {type(exc).__name__}: {exc}"
            results.append(entry)

        def obs_of(res, e, extra=None):
            o = {"events": len(e), "summary": res.get("summary")}
            if e:
                o["first"] = {k: (None if e[0].get(k) is None else e[0].get(k)) for k in
                              ("commit", "file", "deleted", "restored_max", "restored_at_tip",
                               "restored_best", "restored_by", "status")}
            if extra:
                o.update(extra)
            return o

        # ---- v2 case list, bodies unchanged apart from the adapted call -------------
        def t_none():
            f = Fixture(work)
            a30 = v1.lines("a", 30)
            f.commit({"LOG.md": a30})
            t = f.commit({"LOG.md": a30 + v1.lines("b", 5)})
            res = audit(f.d, t, files=F)
            ok = res["events"] == [] and v1.exit_code(res) == 0
            return ok, obs_of(res, res["events"]), [], ""

        def t_below():
            f = Fixture(work)
            a40 = v1.lines("a", 40)
            f.commit({"LOG.md": a40})
            t = f.commit({"LOG.md": a40[:21]})
            res = audit(f.d, t, files=F)
            ok = res["events"] == [] and v1.exit_code(res) == 0
            return ok, obs_of(res, res["events"]), [], ""

        def t_exact_unrestored():
            f = Fixture(work)
            a40 = v1.lines("a", 40)
            f.commit({"corpus/QUALITY.md": a40})
            c = f.commit({"corpus/QUALITY.md": a40[20:]})
            res = audit(f.d, c, files=F)
            e = res["events"]
            ok = (len(e) == 1 and field(e[0], "commit") == c and field(e[0], "deleted") == 20
                  and field(e[0], "status") == "unrestored" and field(e[0], "restored_by") is None
                  and field(e[0], "restored_best") in (None, MISSING) and v1.exit_code(res) == 1)
            skipped = [s for s, _ in SKIP_FIELDS.items() if field(e[0], s) is MISSING] if e else []
            return ok, obs_of(res, e), skipped, ""

        def t_restored():
            f = Fixture(work)
            a50 = v1.lines("a", 50)
            f.commit({"SCORECARD.md": a50})
            c = f.commit({"SCORECARD.md": a50[:10]})
            f.commit({"notes.md": ["x"]})
            r = f.commit({"SCORECARD.md": a50 + ["appended"]})
            t = f.commit({"SCORECARD.md": a50 + ["appended", "more"]})
            res = audit(f.d, t, files=F)
            e = res["events"]
            ok = (len(e) == 1 and field(e[0], "commit") == c and field(e[0], "restored_by") == r
                  and field(e[0], "restored_best") in (r, MISSING) and field(e[0], "status") == "restored"
                  and field(e[0], "restored_max") == 40 and v1.exit_code(res) == 0)
            skipped = [s for s in SKIP_FIELDS if e and field(e[0], s) is MISSING]
            return ok, obs_of(res, e), skipped, ""

        def t_partial():
            f = Fixture(work)
            a60 = v1.lines("a", 60)
            f.commit({"corpus/README.md": a60})
            f.commit({"corpus/README.md": a60[:20]})
            t = f.commit({"corpus/README.md": a60[:40]})
            res = audit(f.d, t, files=F)
            e = res["events"]
            ok = (len(e) == 1 and field(e[0], "status") == "partial" and field(e[0], "restored_max") == 20
                  and field(e[0], "restored_best") in (t, MISSING) and field(e[0], "restored_by") is None
                  and v1.exit_code(res) == 1)
            skipped = [s for s in SKIP_FIELDS if e and field(e[0], s) is MISSING]
            return ok, obs_of(res, e), skipped, ""

        def t_undeclared():
            f = Fixture(work)
            a50 = v1.lines("a", 50)
            f.commit({"notes.md": a50, "corpus/other.md": a50})
            t = f.commit({"notes.md": a50[:5], "corpus/other.md": a50[:5]})
            res = audit(f.d, t, files=F)
            ok = res["events"] == [] and v1.exit_code(res) == 0
            return ok, obs_of(res, res["events"]), [], ""

        def t_file_removed():
            f = Fixture(work)
            a25 = v1.lines("a", 25)
            f.commit({"corpus/SOURCES.md": a25, "LOG.md": ["keep"]})
            c = f.commit({}, delete=["corpus/SOURCES.md"])
            res = audit(f.d, c, 20, ["corpus/SOURCES.md"])
            e = res["events"]
            ok = (len(e) == 1 and field(e[0], "deleted") == 25 and field(e[0], "status") == "unrestored"
                  and v1.exit_code(res) == 1)
            return ok, obs_of(res, e), [], ""

        def t_merge_first_parent():
            f = Fixture(work)
            a40 = v1.lines("a", 40)
            f.commit({"LOG.md": a40})
            v1._git(f.d, "checkout", "-q", "-b", "side")
            f.commit({"LOG.md": a40[:10]})
            v1._git(f.d, "checkout", "-q", "-")
            f.commit({"LOG.md": a40 + ["main"]})
            v1._git(f.d, *Fixture.IDENT, "merge", "-q", "-s", "ours", "--no-edit", "side")
            m = revtext(v1, f.d)
            res = audit(f.d, m, files=F)
            e = res["events"]
            ok = (len(e) == 1 and field(e[0], "commit") != m and field(e[0], "deleted") == 30
                  and field(e[0], "status") == "restored")
            return ok, obs_of(res, e), [], ""

        def t_dashdash():
            f = Fixture(work)
            a = v1.lines("a", 30) + ["--out x", "---", "--- y"]
            f.commit({"LOG.md": a})
            c = f.commit({"LOG.md": a[19:30]})            # deletes 19 plain + 3 dashed = 22
            res = audit(f.d, c, files=F)
            e = res["events"]
            ok = len(e) == 1 and field(e[0], "deleted") == 22 and field(e[0], "status") == "unrestored"
            return ok, obs_of(res, e), [], ""

        def t_crlf_and_eof():
            f = Fixture(work)
            body = "".join(f"p{i} {os.urandom(3).hex()}\n" for i in range(25)).encode()
            crl = b"crlf line\r\n"
            f.commit({"LOG.md": body + crl + b"no newline at end"}, raw=True)
            c = f.commit({"LOG.md": b""}, raw=True)        # 27 deleted
            t = f.commit({"LOG.md": body + b"crlf line\n"}, raw=True)
            res = audit(f.d, t, files=F)
            e = res["events"]
            ok = (len(e) == 1 and field(e[0], "commit") == c and field(e[0], "deleted") == 27
                  and field(e[0], "restored_max") == 25 and field(e[0], "status") == "partial")
            return ok, obs_of(res, e), [], ""

        def t_multiset():
            f = Fixture(work)
            a = v1.lines("a", 20) + ["dup"] * 3
            f.commit({"LOG.md": a})
            f.commit({"LOG.md": []})                     # 23 deleted
            t = f.commit({"LOG.md": a[:20] + ["dup"]})
            res = audit(f.d, t, files=F)
            e = res["events"]
            ok = len(e) == 1 and field(e[0], "restored_max") == 21 and field(e[0], "status") == "partial"
            return ok, obs_of(res, e), [], ""

        def t_window_max():
            f = Fixture(work)
            a40 = v1.lines("a", 40)
            f.commit({"SCORECARD.md": a40})
            f.commit({"SCORECARD.md": a40[:15]})           # 25 deleted
            r = f.commit({"SCORECARD.md": a40})
            t = f.commit({"SCORECARD.md": a40[:35]})       # 5 of them deleted again (no event)
            res = audit(f.d, t, files=F)
            e = res["events"]
            ok = (len(e) == 1 and field(e[0], "restored_max") == 25 and field(e[0], "restored_by") == r
                  and field(e[0], "status") == "restored" and v1.exit_code(res) == 0)
            return ok, obs_of(res, e), [], ""

        def t_relocation():
            f = Fixture(work)
            a50 = v1.lines("a", 50)
            f.commit({"LOG.md": a50})
            c = f.commit({"LOG.md": a50[25:] + a50[:25]})
            res = audit(f.d, c, files=F)
            e = res["events"]
            ok = len(e) == 1 and field(e[0], "restored_by") == c and field(e[0], "status") == "restored"
            return ok, obs_of(res, e), [], ""

        def t_contract():
            f = Fixture(work)
            a30 = v1.lines("a", 30)
            f.commit({"AGENTS.md": ["lessons are append-only"], "corpus/lessons/r1.md": a30,
                      "notes.md": a30, v1.__dict__.get("CONTRACT", "registry/append-only-contract.tsv"):
                          ["path\trule\tdeclared_at\tnote", "corpus/lessons/*.md\tA-corr\tAGENTS.md:1\tx"]})
            t = f.commit({"corpus/lessons/r1.md": a30[:5], "notes.md": a30[:5]})
            res = audit(f.d, t)                       # v1: no contract argument, fixed file set
            e = res["events"]
            ok = res["files"] == ["corpus/lessons/r1.md"] and len(e) == 1 and field(e[0], "file") == "corpus/lessons/r1.md"
            malformed_rejected = False
            if hasattr(v1, "parse_contract"):
                try:
                    v1.parse_contract("path\trule\n")
                except v1.AuditError:
                    malformed_rejected = True
                ok = ok and malformed_rejected
            ok = ok and malformed_rejected
            return ok, obs_of(res, e, {"files": res.get("files"),
                                       "parse_contract_present": hasattr(v1, "parse_contract")}), [], ""

        def t_threshold_flag():
            f = Fixture(work)
            a40 = v1.lines("a", 40)
            f.commit({"LOG.md": a40})
            t = f.commit({"LOG.md": a40[:35]})
            res = audit(f.d, t, threshold=5, files=F)
            ok = len(res["events"]) == 1 and v1.exit_code(res) == 1
            return ok, obs_of(res, res["events"]), [], ""

        for name, fn in [("no-deletion", t_none), ("below-threshold", t_below),
                         ("exact-threshold-unrestored", t_exact_unrestored), ("restored-later", t_restored),
                         ("partial", t_partial), ("undeclared-file", t_undeclared),
                         ("declared-file-removed", t_file_removed), ("merge-first-parent", t_merge_first_parent),
                         ("dashdash-lines", t_dashdash), ("crlf-and-eof", t_crlf_and_eof),
                         ("multiset", t_multiset), ("window-max", t_window_max),
                         ("relocation", t_relocation), ("contract", t_contract),
                         ("threshold-flag", t_threshold_flag)]:
            case(name, fn)

        for r in results:
            print(f"{'pass' if r['ok'] else 'FAIL'} {r['case']:28s} strict={'pass' if r['strict_ok'] else 'FAIL'}"
                  + (f" skipped={','.join(r['skipped'])}" if r["skipped"] else "")
                  + ("" if r["ok"] else f" :: {json.dumps(r['observed'])[:220]} {r['why'][:160]}"))
        fails = [r["case"] for r in results if not r["ok"]]
        strict_fails = [r["case"] for r in results if not r["strict_ok"]]
        print(f"X1_V1_PORT cases={len(results)} fail={len(fails)} fail_cases={','.join(fails) or '-'}")
        print(f"X1_V1_PORT_STRICT fail={len(strict_fails)} fail_cases={','.join(strict_fails) or '-'}")
        if a.v2_tool:
            v2 = load(a.v2_tool, "aoa_v2")
            import inspect
            src = inspect.getsource(v2.selftest)
            names = ["no-deletion", "below-threshold", "exact-threshold-unrestored", "restored-later",
                     "partial", "undeclared-file", "declared-file-removed", "merge-first-parent",
                     "dashdash-lines", "crlf-and-eof", "multiset", "window-max", "relocation",
                     "contract", "threshold-flag"]
            missing = [n for n in names if f'("{n}"' not in src]
            print(f"X1_CASE_LIST v2_schema={getattr(v2, 'SCHEMA', '?')} ported={len(names)} "
                  f"missing_from_v2_selftest={missing or '-'}")
        if a.json:
            with open(a.json, "w", encoding="utf-8") as fh:
                json.dump({"v1_tool": os.path.abspath(a.v1_tool),
                           "cases": results,
                           "fail_cases": fails,
                           "strict_fail_cases": strict_fails}, fh, indent=1)
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
