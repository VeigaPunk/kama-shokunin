#!/usr/bin/env python3
"""C3 battery, v2: base = the lane PROVINCE.md as it stands (16 corrections, one per tag).

Each case is a fixture copy graded with the lane tool via --corrections; the lane
tool, PROVINCE.md and the freeze are never edited.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
S = Path("/fast/scratch/hyaku/kama-r71/CRT01ClaimsAttack")
CASES = S / "c3" / "v2"
SCRATCH = S / "c3" / "scratch"
TOOL = LANE / "tools/round71-province-host-claims.py"
BASE = "f3ee44f4"
SUMMARY_RE = re.compile(
    r"^PROVINCE_HOST_CLAIMS markers=(\d+) tags=(\d+) extra=(\d+) "
    r"contradicted=(\d+) uncovered=(\d+) exit=(\d+)$", re.M)
VERDICTS = {}
results = []


def run(name, text, want_uncovered, want_rewritten=(), want_exit=None, note=""):
    CASES.mkdir(parents=True, exist_ok=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    path = CASES / f"{name}.md"
    path.write_text(text, encoding="utf-8")
    proc = subprocess.run([sys.executable, str(TOOL), "--repo", str(LANE), "--base", BASE,
                           "--corrections", str(path), "--scratch", str(SCRATCH)],
                          capture_output=True, text=True)
    m = SUMMARY_RE.search(proc.stdout)
    rewritten = [ln.split("PROVINCE_HOST_CLAIMS_REWRITTEN ", 1)[1]
                 for ln in proc.stdout.splitlines()
                 if ln.startswith("PROVINCE_HOST_CLAIMS_REWRITTEN ")]
    exit_want = want_exit if want_exit is not None else (0 if want_uncovered == 0 and not want_rewritten else 1)
    ok = (proc.returncode == exit_want
          and ((m is not None and int(m.group(5)) == want_uncovered) or (m is None and want_uncovered is None))
          and tuple(rewritten) == tuple(want_rewritten))
    results.append((name, ok, m.group(0) if m else "<no-summary>", proc.returncode, rewritten, note))
    (CASES / f"{name}.out").write_text(
        f"$ python3 tools/round71-province-host-claims.py --repo . --base {BASE} --corrections {path}\n"
        f"{proc.stdout}\n[stderr]\n{proc.stderr}\n[exit={proc.returncode}]"
        f"\n[want uncovered={want_uncovered} rewritten={list(want_rewritten)} exit={exit_want}]"
        f"\n[{'HELD' if ok else 'FALSIFIED'}] {note}\n", encoding="utf-8")
    print(f"{'HELD     ' if ok else 'FALSIFIED'} {name}: {m.group(0) if m else '<no-summary>'} "
          f"exit={proc.returncode} rewritten={rewritten}")
    return proc


def main():
    lane_text = (LANE / "PROVINCE.md").read_text(encoding="utf-8")
    (S / "c3" / "province-lane-tip.md").write_text(lane_text, encoding="utf-8")
    tags = re.findall(r"^- correction-on-host \(\d{4}-\d{2}-\d{2}\) `province-host:([A-Za-z0-9._-]+)`"
                      r" \u2014 (present|absent):", lane_text, re.M)
    print(f"lane corrections: {len(tags)} lines, {len(set(t for t, _ in tags))} distinct tags")
    run("base_after_state", lane_text, 0, note="frozen counter shape at the lane tip")

    # route (i): right tag, flipped verdict — every tag, one at a time.
    for tag, verdict in tags:
        other = "present" if verdict == "absent" else "absent"
        pat = (rf"^- correction-on-host \(2026-11-03\) `province-host:{re.escape(tag)}` "
               rf"\u2014 {verdict}:")
        flipped = re.sub(pat, f"- correction-on-host (2026-11-03) `province-host:{tag}` \u2014 {other}:",
                         lane_text, count=1, flags=re.M)
        if flipped == lane_text:
            print(f"SKIP flip {tag}: anchor not found")
            continue
        run(f"i_flip_{tag}", flipped, 1)

    # route (i'): wrong tag inside a correction line must cover nothing.
    for label, old, new in (
        ("superset", "province-host:omp-binary", "province-host:omp-binary-x"),
        ("prefix", "province-host:llama-b11755-install", "province-host:llama-b11755"),
        ("sibling", "province-host:kama-cache-gguf", "province-host:fixture-gguf-model-2"),
        ("underscore", "province-host:omp-binary", "province-host:omp_binary"),
        ("case", "province-host:omp-binary", "province-host:OMP-binary"),
    ):
        pat = rf"(^- correction-on-host \(2026-11-03\) `){re.escape(old)}(`)"
        wrong = re.sub(pat, r"\g<1>" + new + r"\g<2>", lane_text, count=1, flags=re.M)
        assert wrong != lane_text, label
        run(f"i2_wrongtag_{label}", wrong, 1)

    # route (ii): dates that are not later than the claim date.
    for label, date in (("before", "2026-10-30"), ("same-day", "2026-10-31"),
                        ("far-before", "2020-01-01")):
        early = re.sub(r"(^- correction-on-host \()\d{4}-\d{2}-\d{2}(\) `province-host:omp-binary`)",
                       r"\g<1>" + date + r"\g<2>", lane_text, count=1, flags=re.M)
        run(f"ii_date_{label}", early, 1)

    # route (ii'): ISO-shaped but impossible calendar date.
    bogus = re.sub(r"(^- correction-on-host \()\d{4}-\d{2}-\d{2}(\) `province-host:omp-binary`)",
                   r"\g<1>2026-99-99\g<2>", lane_text, count=1, flags=re.M)
    run("ii2_date_impossible", bogus, 0,
        note="an impossible date (2026-99-99) covers the claim: the date is compared, never validated")

    # route (iii): false correction first, true one after.
    false_first = re.sub(
        r"(^- correction-on-host \(2026-11-03\) `province-host:omp-binary` \u2014 present:)",
        "- correction-on-host (2026-11-02) `province-host:omp-binary` \u2014 absent: decoy\n\\1",
        lane_text, count=1, flags=re.M)
    run("iii_false_then_true", false_first, 0, note="predicate says 'carries a later agreeing line': clears")

    # route (iii'): true first, later false correction.
    true_then_false = lane_text.rstrip("\n") + (
        "\n- correction-on-host (2026-12-01) `province-host:omp-binary` \u2014 absent: "
        "later decoy contradicting the live probe\n")
    run("iii2_true_then_false_later", true_then_false, 0,
        note="a later FALSE correction is never graded; uncovered stays 0 with a false line in the doc")

    # route (iv): duplicated marker paragraph inserted before the original, later date.
    dup = lane_text.replace(
        "- absent-on-this-host (2026-10-31) `province-host:omp-binary`",
        "- absent-on-this-host (2026-11-03) `province-host:omp-binary` \u2014 duplicated paragraph\n\n"
        "- absent-on-this-host (2026-10-31) `province-host:omp-binary`", 1)
    run("iv_dup_marker_later_first", dup, 1,
        note="duplicate changes the claim date (setdefault keeps the first) -> false red, no duplicate diagnostic")

    # route (v): delete a base marker paragraph.
    deleted = re.sub(r"- absent-on-this-host \(2026-10-31\) `province-host:janitor-md`[^\n]*\n"
                     r"(?:  [^\n]*\n)*", "", lane_text, count=1)
    assert deleted != lane_text
    run("v_delete_marker", deleted, 0, want_rewritten=("janitor-md",),
        note="kill rule (iii) holding arm")

    # route (v'): delete the paragraph, re-add the same tag in a new paragraph.
    readd = deleted.rstrip("\n") + (
        "\n- absent-on-this-host (2026-10-30) `province-host:janitor-md` \u2014 re-added after deletion\n")
    run("v2_delete_then_readd", readd, 0,
        note="FROZEN KILL RULE (iii) says a deleted base marker line exits 1; tag-presence check passes it")

    # route (v''): rewrite a base marker line's body, keep tag and date.
    rew = lane_text.replace(
        "`province-host:janitor-md` \u2014\n  `~/.config/opencode/agents/` does not exist.",
        "`province-host:janitor-md` \u2014\n  `/some/other/path/` does not exist.", 1)
    assert rew != lane_text, "rewrite anchor"
    run("v3_rewrite_body", rew, 0,
        note="frozen predicate: 'rewriting a base marker line exits 1' -> tag-presence check passes it")

    # route (vi): a marker tag with no declared probe fails closed.
    undeclared = lane_text.replace(
        "- absent-on-this-host (2026-10-31) `province-host:janitor-md`",
        "- absent-on-this-host (2026-10-31) `province-host:not-a-surface`", 1)
    run("vi_undeclared_tag", undeclared, None, want_exit=2,
        note="fail-closed exit 2, but no pinned summary line is printed on this path")

    # route (vi'): corrections file absent -> exit 2; and --json agreement.
    proc = subprocess.run([sys.executable, str(TOOL), "--repo", str(LANE), "--base", BASE,
                           "--corrections", str(CASES / "missing.md")],
                          capture_output=True, text=True)
    results.append(("vi2_missing_corrections", proc.returncode == 2, f"exit={proc.returncode}", proc.returncode, [], ""))
    print(f"{'HELD' if proc.returncode == 2 else 'FALSIFIED'} vi2_missing_corrections exit={proc.returncode}")
    proc = subprocess.run([sys.executable, str(TOOL), "--repo", str(LANE), "--base", BASE,
                           "--scratch", str(SCRATCH), "--json"], capture_output=True, text=True)
    doc = json.loads(proc.stdout)
    agree = doc["exit"] == proc.returncode == 0 and doc["uncovered"] == 0 and doc["rewritten"] == []
    results.append(("json_agreement", agree, json.dumps({k: doc[k] for k in
                   ("markers", "tags", "extra", "contradicted", "uncovered", "corrected") }
                   if k in doc else {"markers": doc["markers"]}), proc.returncode, [], ""))
    (CASES / "json_agreement.out").write_text(json.dumps(
        {k: doc[k] for k in ("markers", "tags", "extra", "contradicted", "uncovered",
                             "corrections_parsed", "rewritten", "exit")}, indent=1)
        + f"\n[proc_exit={proc.returncode}]\n", encoding="utf-8")
    print(f"{'HELD' if agree else 'FALSIFIED'} json_agreement exit={proc.returncode} "
          f"uncovered={doc['uncovered']} parsed={doc['corrections_parsed']}")

    print("\nTABLE")
    for name, ok, summary, rc, rw, note in results:
        print(f"{'HELD     ' if ok else 'FALSIFIED'} | {name} | {summary} | exit={rc} | rewritten={rw} | {note}")


if __name__ == "__main__":
    main()
