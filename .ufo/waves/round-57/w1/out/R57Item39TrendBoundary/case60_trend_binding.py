#!/usr/bin/env python3
"""Distinct case 60 - does any lane instrument bind a trend verdict to LEARNING.md's observable?

Read-only over the lane. The frozen lane parser (tools/round44-verdict-ledger-audit.py)
is imported, not re-implemented, so the test is against the lane's own instrument.

Question: a fixture lesson that claims `expansion: improved`, `quality: improved` and
`discernment: improved` with zero evidence - does any lane instrument fail it?

Exit 0 = the fixture survives every lane instrument that could see it (the measured
result this seat reports); 1 = at least one instrument refused it.
"""
from __future__ import annotations

import argparse
import glob
import importlib.util
import os
import re
import subprocess
import sys

TREND_TOKENS = re.compile(r"expansion\|quality\|discernment")


def sh(*args, cwd=None):
    p = subprocess.run(list(args), capture_output=True, text=True, cwd=cwd)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.getcwd())
    ap.add_argument("--fixture", required=True)
    a = ap.parse_args()
    repo = os.path.abspath(a.repo)
    out = []
    emit = out.append

    emit("case=60")
    emit(f"repo={repo}")
    rc, tip, _ = sh("git", "-C", repo, "rev-parse", "HEAD")
    emit(f"tip={tip} (git rev-parse HEAD)")
    rc, dirty, _ = sh("git", "-C", repo, "status", "--porcelain")
    emit(f"tree_dirty={int(bool(dirty))} modified_tracked={len([l for l in dirty.splitlines() if l[:2].strip() and not l.startswith('??')])} untracked={len([l for l in dirty.splitlines() if l.startswith('??')])}")

    # 1. The frozen trend instrument, imported from the lane.
    tool = os.path.join(repo, "tools", "round44-verdict-ledger-audit.py")
    emit(f"frozen_trend_instrument={os.path.relpath(tool, repo)}")
    m = load(tool, "r44ledger")
    rounds = list(m.ROUNDS)
    emit(f"instrument_round_scope={rounds[0]}..{rounds[-1]} n={len(rounds)}")
    emit(f"instrument_trends={','.join(m.TRENDS)}")
    emit(f"instrument_ledger={m.LEDGER}")
    emit(f"instrument_scorecard_heading={m.HEADING!r}")

    fixture = open(a.fixture, encoding="utf-8").read().splitlines()
    parsed = {}
    for line in fixture:
        for trend, words in m.read_line(line).items():
            parsed.setdefault(trend, set()).update(words)
    emit("fixture_claims=" + ";".join(f"{k}:{','.join(sorted(v))}" for k, v in sorted(parsed.items())))
    emit("fixture_parsed_by_frozen_parser=" + str(bool(parsed)))

    # Population of the frozen instrument: which paths can it ever read?
    pop = set()
    for r in rounds:
        for side in ("self", "outside"):
            _repo, _rev, path = m.side_spec(r, side)
            pop.add(path)
    emit(f"instrument_population_paths={len(pop)}")
    fixture_in_population = os.path.relpath(a.fixture, repo) in pop
    emit(f"fixture_in_instrument_population={int(fixture_in_population)}")
    emit(f"instrument_reads_knowledge_entries={'corpus/knowledge' in open(tool, encoding='utf-8').read()}")
    emit(f"instrument_reads_verified_at={'verified-at' in open(tool, encoding='utf-8').read()}")

    # 2. Every lane tool that parses trend verdict vocabulary or the LEARNING observables.
    tools = sorted(glob.glob(os.path.join(repo, "tools", "*.py")))
    trend_parsers, knowledge_readers, verified_readers = [], [], []
    for t in tools:
        src = open(t, encoding="utf-8", errors="replace").read()
        if re.search(r"\(expansion\|quality\|discernment\)", src) or TREND_TOKENS.search(src):
            trend_parsers.append(os.path.basename(t))
        if "corpus/knowledge" in src:
            knowledge_readers.append(os.path.basename(t))
        if "verified-at" in src:
            verified_readers.append(os.path.basename(t))
    emit(f"tools_total={len(tools)}")
    emit(f"tools_parsing_trend_verdicts={','.join(trend_parsers)}")
    emit(f"tools_naming_corpus_knowledge={len(knowledge_readers)}")
    emit(f"tools_reading_verified_at={len(verified_readers)}")

    # 3. Tree observables per LEARNING.md's three trend rows.
    kn = sorted(glob.glob(os.path.join(repo, "corpus", "knowledge", "*.md")))
    emit(f"observable.expansion.knowledge_entries={len(kn)}")
    rc, last, _ = sh("git", "-C", repo, "log", "--diff-filter=A", "--format=%h %ad", "--date=short",
                     "-1", "--", "corpus/knowledge")
    emit(f"observable.expansion.last_knowledge_addition={last}")

    r42 = load(os.path.join(repo, "tools", "round42-selfdesc-reconcile.py"), "r42selfdesc")
    sc = open(os.path.join(repo, "SCORECARD.md"), encoding="utf-8").read()
    cn, crows = r42.canon(sc)
    head = (r42.sections(sc, "Capabilities") or [""])[0]
    hnames = [r[0].strip("` *") for r in r42.table_rows(head.split("\n")) if r]
    emit(f"observable.expansion.canonical_capability_rows={len(crows)} canonical_round={cn}")
    emit(f"observable.expansion.head_capability_rows={len(hnames)}")

    fresh = 0
    missing_va = missing_rc = 0
    for f in kn:
        txt = open(f, encoding="utf-8", errors="replace").read()
        mva = re.search(r"^verified-at:\s*(.*)$", txt, re.M)
        if not mva:
            missing_va += 1
        elif re.search(r"2026-10-2[6-9]", mva.group(1)):
            fresh += 1
        if not re.search(r"^recheck:", txt, re.M):
            missing_rc += 1
    emit(f"observable.quality.entries_verified_at_2026-10-26_or_later={fresh}")
    emit(f"observable.quality.entries_missing_verified_at={missing_va}")
    emit(f"observable.quality.entries_missing_recheck={missing_rc}")

    vs = sorted(glob.glob(os.path.join(repo, "corpus", "lessons", "*verifier-spotcheck.md")))
    emit(f"observable.discernment.verifier_spotcheck_lessons={len(vs)}")
    latest = max(int(re.search(r"round-(\d+)", os.path.basename(p)).group(1))
                 for p in vs if re.search(r"round-(\d+)", os.path.basename(p)))
    emit(f"observable.discernment.latest_outside_round={latest}")
    sp = open(os.path.join(repo, "corpus", "lessons", f"round-{latest}-verifier-spotcheck.md"),
              encoding="utf-8").read().splitlines()
    trends = []
    for line in sp:
        if re.search(r"expansion|quality|discernment", line, re.I) and re.search(
                r"improved|harmed|unchanged|unprovable", line, re.I):
            trends.append(re.sub(r"\s+", " ", line.strip())[:160])
    emit(f"observable.discernment.round{latest}_outside_trend_lines={len(trends)}")
    for t in trends:
        emit(f"  outside_line={t}")
    q = open(os.path.join(repo, "corpus", "QUALITY.md"), encoding="utf-8").read()
    emit(f"observable.discernment.quality_criteria_rows={len(re.findall(r'^\| KQ\d+', q, re.M))}")
    emit(f"observable.discernment.quality_rows_citing_round-{latest}={len(re.findall('round-' + str(latest), q))}")

    # 4. Ledger coverage vs KQ61's "each closed round's pair is ledgered".
    ledger = os.path.join(repo, m.LEDGER)
    rows = [l.rstrip("\n").split("\t") for l in open(ledger, encoding="utf-8")][1:]
    lrounds = sorted({int(r[0]) for r in rows})
    unledgered = [r for r in range(10, latest + 1) if r not in lrounds]
    emit(f"ledger.rows={len(rows)} header={len(open(ledger).readline().rstrip().split(chr(9)))} cells")
    emit(f"ledger.rounds={lrounds[0]}..{lrounds[-1]} n={len(lrounds)}")
    emit(f"ledger.closed_rounds_{lrounds[-1]+1}..{latest}_unledgered={len(unledgered)}")
    emit(f"ledger.rounds_unledgered={','.join(str(x) for x in unledgered)}")
    emit(f"ledger.kq61_expected_rows={(latest - 9) * 3 * 2} missing={(len(unledgered)) * 3 * 2}")

    # 5. Which instruments read the fixture at all?
    readers = []
    for t in tools:
        src = open(t, encoding="utf-8", errors="replace").read()
        if "corpus/knowledge" in src and re.search(r"\\(expansion\\|quality\\|discernment\\)", src):
            readers.append(os.path.basename(t))
    emit(f"tools_reading_knowledge_and_naming_expansion={','.join(sorted(readers)) or 'none'}")

    failing = []
    if fixture_in_population:
        failing.append("round44-verdict-ledger-audit")
    rc, audit, _ = sh("python3", os.path.join(repo, "tools", "round44-verdict-ledger-audit.py"),
                      "--repo", repo, "--tip", "HEAD", "--fleet", os.path.dirname(repo))
    emit(f"instrument_run.round44_verdict_ledger_audit_exit={rc}")
    emit(f"instrument_run.round44_verdict_ledger_audit_out={audit.replace(chr(10), ' | ') if audit else ''}")
    src_led = open(tool, encoding="utf-8").read()
    metline = [l.strip() for l in src_led.splitlines() if l.strip().startswith("met = 204 valid rows")]
    emit("instrument_met_predicate=" + (metline[0] if metline else "not-found"))
    emit(f"instruments_failing_fixture={','.join(failing) or 'none'}")
    emit("result=" + ("FIXTURE_SURVIVES_ALL_LANE_INSTRUMENTS" if not failing else "FIXTURE_REJECTED"))
    print("\n".join(out))
    return 0 if not failing else 1


if __name__ == "__main__":
    raise SystemExit(main())
