#!/usr/bin/env python3
"""c2-boundary-control.py -- round-70 C2's boundary control (the frozen counter, completed).

The frozen counter (`refused-member-control.py`) asserts exactly one fact about the
census's exit: `(refused_fixture_exit != 0, allpass_fixture_exit == 0)`. Five distinct
non-compliant census designs satisfy that pair -- a refusal reclassified as a defect, a
literal population, a waiver that swallows a genuine failure, a second in-process call
that prints nothing, and refusal support deleted -- because the pair reads only the exit.
This control closes the gap without touching the frozen bytes: it runs the frozen counter
as a subprocess (check `frozen_counter`) and then asserts the facts the frozen predicate
names, on the frozen counter's own fixtures.

Checks (each one line, `ok <check>` / `FAIL <check>: <detail>`):

  frozen_counter        the frozen control subprocess exits 0 and prints (1, 0)
  bare_main_call        main() called with no arguments, under the harness's own argv, is
                        re-runnable: an argparse-in-main() census dies here (the frozen
                        control calls main() directly)
  fixture_refused       refused fixture: exit != 0, verdict not_evaluated=1 fail=0 total=2
  fixture_allpass       all-pass fixture: exit 0, verdict not_evaluated=0 fail=0 pass=2 total=2
  fixture_failing       failing-member fixture: exit != 0, verdict fail=1
  single_verdict_line   exactly one HOST_CENSUS-prefixed line on the refused fixture, so a
                        `grep '^HOST_CENSUS' | tail -1` reader gets counts, not prose
  target_literal        the freeze's contiguous literal `pass=<p> fail=0 not_evaluated=0
                        total=<t>` appears in the green verdict (WARN when a token is
                        interposed; token-wise readers are unaffected)
  waiver_refusal        waived refused member: exit 0, not_evaluated stays 1, waived>=1
  waiver_failure        waived FAILING member: exit != 0 and the member is not reported pass
  waiver_prefix         `--waive synthetic` must not waive `synthetic-refused`
  waiver_unknown        an unknown waiver name is loud (exit != 0), never silently ignored
  reentry               two main() calls on one module object match a fresh module
  population            22 members, 12 tier A + 10 tier B, exact pinned name set, and the
                        three pinned refusal markers still pinned on their members
  marker:<m>            an injected member printing <m> lands in not_evaluated, not pass/fail

Optional:
  --cli                 run `python3 <census> --waive no-such-member` and require exit != 0.
                        Costs a full census run if the waiver is validated after the loop.
  --frozen-control P    frozen counter path (default: the round-70 controls directory next
                        to this file; missing -> that one check is SKIPPED, never passed).

Exit: 0 no FAIL (warnings allowed), 1 any FAIL, 2 could-not-evaluate (census
unreadable/unloadable). Warnings are printed and counted, never silently passed.

Read-only on the given census: this control sets CENSUS_WAIVE and sys.argv only for the
duration of an in-process call, restores both, and writes nothing.
"""
import contextlib
import importlib.util
import inspect
import io
import os
import subprocess
import sys
from pathlib import Path

PASS_MARKER = "RESULT pass=30 fail=0"
REFUSAL_MARKER = "invalid path"
REFUSAL_REASON = "fail-closed refusal: synthetic NTFS stand-in (control)"

REFUSED = [
    ("A", "synthetic-pass", ["bash", "-c", f"echo {PASS_MARKER!r}"], PASS_MARKER, []),
    ("A", "synthetic-refused",
     ["bash", "-c", f"echo {REFUSAL_MARKER!r}: the lane holds a tracked path NTFS cannot check out"],
     "NEVER-PRINTED", [(REFUSAL_MARKER, REFUSAL_REASON)]),
]
ALLPASS = [
    ("A", "synthetic-pass", ["bash", "-c", f"echo {PASS_MARKER!r}"], PASS_MARKER, []),
    ("A", "synthetic-pass-2", ["bash", "-c", f"echo {PASS_MARKER!r}"], PASS_MARKER, []),
]
FAILING = [
    ("A", "synthetic-pass", ["bash", "-c", f"echo {PASS_MARKER!r}"], PASS_MARKER, []),
    ("A", "synthetic-broken", ["bash", "-c", "echo boom; exit 3"], "NEVER-PRINTED", []),
]

PINNED_NAMES = [
    "test-snapshot harness",
    "pin-watch selftest",
    "report-landing-audit selftest",
    "sources-append-only selftest",
    "citation-provenance selftest",
    "capability-repertoire-audit selftest",
    "instrument-agreement selftest",
    "round42-selfdesc-reconcile selftest",
    "gate-registry-check selftest (lane-tip arm)",
    "worktree-landing-check selftest",
    "receipt-pointer-audit selftest",
    "newest-closure-counter selftest",
    "digest-ledger selftest",
    "hexrun-census selftest",
    "kama-ollama-evidence selftest",
    "gguf-identity selftest",
    "manifest-crosscheck selftest",
    "error-verdict-census selftest",
    "seat-report-immutability selftest",
    "prereg-time-check selftest",
    "release-recheck selftest",
    "append-only-audit selftest",
]
PINNED_TIER_COUNTS = {"A": 12, "B": 10}
PINNED_REFUSALS = [
    ("test-snapshot harness", "missing dependency"),
    ("round42-selfdesc-reconcile selftest", "invalid path"),
    ("gate-registry-check selftest (lane-tip arm)", "cannot resolve master"),
]

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, "ok" if ok else "FAIL", detail))
    print(("ok " if ok else "FAIL ") + name + ("" if ok else f": {detail}"))


def warn(name, detail=""):
    RESULTS.append((name, "warn", detail))
    print(f"warn {name}: {detail}")


def skip(name, why):
    RESULTS.append((name, "SKIP", why))
    print(f"skip {name}: {why}")


def load(path):
    spec = importlib.util.spec_from_file_location("census_under_control", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def verdict(lines):
    """The counters line: the HOST_CENSUS line that carries k=v tokens.

    A second HOST_CENSUS-prefixed line (an explanation) must not shadow it: a reader
    doing `grep '^HOST_CENSUS' | tail -1` would then get prose, not counts.
    """
    hits = [l for l in lines if l.startswith("HOST_CENSUS ") and " pass=" in l]
    return hits[-1] if hits else None


def verdict_lines(lines):
    return [l for l in lines if l.startswith("HOST_CENSUS ")]


def toks(line):
    out = {}
    if line:
        for t in line.split()[1:]:
            if "=" in t:
                k, v = t.split("=", 1)
                out[k] = v
    return out


def raw_call(mod, members, env_waive=None, argv=None):
    """Call mod.main() once with MEMBERS replaced. No waiver kwarg."""
    mod.MEMBERS = members
    buf, err = io.StringIO(), io.StringIO()
    saved_argv = sys.argv
    if argv is not None:
        sys.argv = argv
    if env_waive is not None:
        os.environ["CENSUS_WAIVE"] = ",".join(env_waive)
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            code = mod.main()
    except SystemExit as exc:
        code = f"SystemExit({exc.code})"
    except BaseException as exc:
        code = f"{type(exc).__name__}: {exc}"
    finally:
        sys.argv = saved_argv
        os.environ.pop("CENSUS_WAIVE", None)
    return code, buf.getvalue().strip().splitlines(), err.getvalue().strip().splitlines()


def kw_call(mod, members, names):
    """Call mod.main(waive=...) when the signature exposes it."""
    mod.MEMBERS = members
    buf, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            code = mod.main(waive=tuple(names))
    except SystemExit as exc:
        code = f"SystemExit({exc.code})"
    except BaseException as exc:
        code = f"{type(exc).__name__}: {exc}"
    return code, buf.getvalue().strip().splitlines(), err.getvalue().strip().splitlines()


def waive_call(mod, members, names):
    """Try every waiver channel; return the first that changes the observable result.

    Returns (channel, exit, lines) or (None, exit_of_last, lines_of_last).
    """
    base = raw_call(load(mod.__file__), members)
    ref = (base[0], verdict(base[1]))
    if "waive" in inspect.signature(mod.main).parameters:
        got = kw_call(load(mod.__file__), members, names)
        if (got[0], verdict(got[1])) != ref:
            return "kwarg", got[0], got[1], got[2]
    got = raw_call(load(mod.__file__), members, env_waive=names)
    if (got[0], verdict(got[1])) != ref:
        return "env", got[0], got[1], got[2]
    got = raw_call(load(mod.__file__), members, argv=["census", "--waive", *names])
    if (got[0], verdict(got[1])) != ref:
        return "argv", got[0], got[1], got[2]
    # no channel changed the outcome: report the argv attempt's stderr, because that is
    # where a "waiver names no member" warning would be printed
    return None, got[0], got[1], got[2]


def main():
    args = sys.argv[1:]
    cli = "--cli" in args
    args = [a for a in args if a != "--cli"]
    frozen = None
    if "--frozen-control" in args:
        i = args.index("--frozen-control")
        frozen = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        print("usage: c2-boundary-control.py <census.py> [--frozen-control PATH] [--cli]",
              file=sys.stderr)
        return 2
    path = os.path.abspath(args[0])
    if not os.path.isfile(path):
        print(f"could-not-evaluate: not a file: {path}", file=sys.stderr)
        return 2
    if frozen is None:
        frozen = str(Path(__file__).resolve().parent / "refused-member-control.py")
    try:
        mod = load(path)
        members = list(mod.MEMBERS)
    except BaseException as exc:
        print(f"could-not-evaluate: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    # 1. the frozen counter's own pair, executed from its frozen bytes
    if os.path.isfile(frozen):
        p = subprocess.run([sys.executable, frozen, path], capture_output=True, text=True)
        line = next((l for l in p.stdout.splitlines()
                     if l.startswith("REFUSED_MEMBER_CONTROL ")), "")
        ok = p.returncode == 0 and "refused_fixture_exit=1" in line and \
            "allpass_fixture_exit=0" in line
        check("frozen_counter", ok, f"exit={p.returncode} line={line or '<none>'!r} "
                                    f"stderr={p.stderr.strip()[:200]!r}")
    else:
        skip("frozen_counter", f"frozen counter not found at {frozen}")

    # 2. main() under the harness's own argv (the frozen calling convention)
    mod2 = load(path)
    code, lines, err = raw_call(mod2, ALLPASS)
    v = verdict(lines)
    check("bare_main_call", code == 0 and toks(v).get("pass") == "2",
          f"exit={code} verdict={v!r} stderr={(err or [''])[0][:160]!r}")

    # 3-5. the frozen fixtures, verdict facts
    code, lines, _ = raw_call(load(path), REFUSED)
    v, t = verdict(lines), toks(verdict(lines))
    check("fixture_refused",
          code != 0 and t.get("not_evaluated") == "1" and t.get("fail") == "0"
          and t.get("total") == "2",
          f"exit={code} verdict={v!r}")

    code, lines, _ = raw_call(load(path), ALLPASS)
    v, t = verdict(lines), toks(verdict(lines))
    check("fixture_allpass",
          code == 0 and t.get("not_evaluated") == "0" and t.get("fail") == "0"
          and t.get("pass") == "2" and t.get("total") == "2",
          f"exit={code} verdict={v!r}")

    code, lines, _ = raw_call(load(path), FAILING)
    v, t = verdict(lines), toks(verdict(lines))
    check("fixture_failing", code != 0 and t.get("fail") == "1",
          f"exit={code} verdict={v!r}")

    # 5b. exactly one HOST_CENSUS-prefixed line (a reader doing `tail -1` must get counts,
    # not prose); then the freeze's contiguous literal on the green fixture
    mod3 = load(path)
    _c, lines3, _ = raw_call(mod3, REFUSED)
    vlines = verdict_lines(lines3)
    if len(vlines) == 1:
        check("single_verdict_line", True)
    else:
        warn("single_verdict_line",
             f"{len(vlines)} HOST_CENSUS-prefixed lines on the refused fixture: "
             f"{vlines!r} (a `grep '^HOST_CENSUS' | tail -1` reader gets prose)")
    mod3 = load(path)
    _c, lines3, _ = raw_call(mod3, ALLPASS)
    vlines = verdict_lines(lines3)
    literal = "pass=2 fail=0 not_evaluated=0 total=2"
    if vlines and literal in vlines[-1]:
        check("target_literal", True)
    else:
        warn("target_literal",
             f"the freeze's contiguous target {literal!r} does not appear in "
             f"{verdict(lines3)!r}; a token-wise reader is fine, a grep for the "
             f"literal is not")

    # 6. a refused member may be waived; the fact stays visible
    ch, code, lines, err = waive_call(mod, REFUSED, ["synthetic-refused"])
    v, t = verdict(lines), toks(verdict(lines))
    check("waiver_refusal",
          ch is not None and code == 0 and t.get("not_evaluated") == "1"
          and (t.get("waived") or "0") != "0",
          f"channel={ch} exit={code} verdict={v!r}")

    # 7. a FAILING member is never waivable
    ch, code, lines, err = waive_call(mod, FAILING, ["synthetic-broken"])
    v = verdict(lines)
    member_lines = [l for l in lines if "synthetic-broken" in l]
    check("waiver_failure",
          code != 0 and (toks(v).get("fail") == "1")
          and not any(l.startswith("pass ") for l in member_lines),
          f"channel={ch} exit={code} verdict={v!r} member={member_lines!r}")

    # 8. no prefix/substring waivers
    ch, code, lines, err = waive_call(mod, REFUSED, ["synthetic"])
    check("waiver_prefix", code != 0,
          f"channel={ch} exit={code} verdict={verdict(lines)!r} "
          "(a prefix waived a different member)" if ch else
          f"no waiver channel observed (exit={code}); a waiver surface is required "
          "by the round's C2 landing brief")

    # 9. unknown waiver name is loud
    ch, code, lines, err = waive_call(mod, ALLPASS, ["no-such-member"])
    named = any("no-such-member" in l for l in err) or \
            any("no-such-member" in l for l in lines)
    if code != 0:
        check("waiver_unknown", True)
    elif named:
        warn("waiver_unknown",
             f"exit=0 but the unknown name is named on stderr (visible in a 2>&1 "
             f"receipt); exit 2 would be louder: {err!r}")
    else:
        check("waiver_unknown", False,
              f"channel={ch} exit=0 and the unknown name is never named: {err!r}")

    # 10. re-entrancy: two calls on one module object match a fresh module
    m = load(path)
    c1, l1, _ = raw_call(m, REFUSED)
    c2, l2, _ = raw_call(m, ALLPASS)
    fresh1 = raw_call(load(path), REFUSED)
    fresh2 = raw_call(load(path), ALLPASS)
    check("reentry",
          (c1, verdict(l1)) == (fresh1[0], verdict(fresh1[1]))
          and (c2, verdict(l2)) == (fresh2[0], verdict(fresh2[1])),
          f"first={(c1, verdict(l1))!r} second={(c2, verdict(l2))!r}")

    # 11. population: 22 members, tiers, exact names, pinned refusal markers
    names = [row[1] for row in members]
    tiers = {}
    for row in members:
        tiers[row[0]] = tiers.get(row[0], 0) + 1
    pinned = {name: marker for name, marker in PINNED_REFUSALS}
    refusals_ok = all(
        any(marker in [r[0] for r in row[4]] for row in members if row[1] == name)
        for name, marker in PINNED_REFUSALS)
    pop_ok = (len(members) == 22 and tiers == PINNED_TIER_COUNTS
              and sorted(names) == sorted(PINNED_NAMES)
              and len(set(names)) == 22 and refusals_ok)
    detail = (f"total={len(members)} tiers={tiers} "
              f"names_match={sorted(names) == sorted(PINNED_NAMES)} "
              f"unique={len(set(names))} refusal_markers_pinned={refusals_ok} "
              f"pinned_refusals={pinned}")
    check("population", pop_ok, detail)

    # 12. each pinned refusal marker still means not_evaluated, not pass/fail
    for marker, _name in [(m, n) for n, m in PINNED_REFUSALS]:
        fixture = [("A", f"probe-{marker}",
                    ["bash", "-c", f"echo {marker!r}: synthetic probe"],
                    "NEVER-PRINTED", [(marker, "pinned refusal probe")])]
        code, lines, _ = raw_call(load(path), fixture)
        v, t = verdict(lines), toks(verdict(lines))
        probe = [l for l in lines if l.startswith(("pass ", "FAIL "))]
        check(f"marker:{marker}",
              code != 0 and t.get("not_evaluated") == "1" and t.get("fail") == "0"
              and not probe,
              f"exit={code} verdict={v!r} misclassified={probe!r}")

    # 13. optional real-CLI hygiene: an unknown waiver name must not start a green run
    if cli:
        p = subprocess.run([sys.executable, path, "--waive", "no-such-member"],
                           capture_output=True, text=True, timeout=900)
        combined = p.stdout + p.stderr
        if p.returncode != 0:
            check("cli_unknown_waiver", True)
        elif "no-such-member" in combined:
            warn("cli_unknown_waiver",
                 f"exit={p.returncode} with the unknown name named on "
                 f"{'stderr' if 'no-such-member' in p.stderr else 'stdout'}; exit 2 "
                 f"would be louder (and needs the registered exit map amended)")
        else:
            check("cli_unknown_waiver", False,
                  f"exit={p.returncode} and the unknown name is never named")
    else:
        skip("cli_unknown_waiver", "--cli not given")

    passed = sum(1 for _, s, _ in RESULTS if s == "ok")
    failed = sum(1 for _, s, _ in RESULTS if s == "FAIL")
    warned = sum(1 for _, s, _ in RESULTS if s == "warn")
    skipped = sum(1 for _, s, _ in RESULTS if s == "SKIP")
    print(f"C2_BOUNDARY_CONTROL pass={passed} fail={failed} warn={warned} skipped={skipped}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
