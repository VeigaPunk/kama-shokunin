#!/usr/bin/env python3
"""shortcut-tally.py - round-47 X9Tally: tally counters that a shortcut can satisfy.

Question: across the lane's rounds, is the record saying that counter design is
getting harder to fool, or only that shortcuts are being disclosed better? For
each round report (a) how many frozen counters the round's own `met=True`
disclosure says a shortcut met, (b) how many counter/tool mutants survived their
mutation battery, and (c) whether a falsify wave ran.

Sources (read-only, lane root):
  SCORECARD.md
    - the `## Round N` heading sets the current round; every line containing
      "What `met=True` does not show" while a round is current is a disclosure
      block for that round. A heading line (`### ...`) starts a block that runs
      to the next `^#` heading; any other matching line is a one-line block
      (the lane's rounds 42-44 write the disclosure as one long paragraph line).
    - a round's section text runs from its `## Round N` heading to the next
      `## Round M` heading (other `## ` headings stay inside it) and is used
      only for the falsify-wave cross-check.
  .ufo/waves/round-N/
    - mutation reports: any `*.md` whose basename is `M<d>Ctr.md` or
      `M<d>Tool.md`, at any depth below the round directory.
    - waves: any immediate subdirectory holding `spec.json` or `dispatch.json`.
      `spec.json` "context" is the wave goal. A wave is `dedicated` when its
      goal matches `=\\s*FALSIFY` (the lane's explicit `wave N = FALSIFY`
      spelling); otherwise `marked` when the goal matches `(?i)falsif`.
      `reports` is the count of `*.md` under `<wave>/out` (recursive).
      falsify value, first hit wins:
        dedicated + reports>0   -> yes(wN,dedicated)
        dedicated + reports==0  -> planned-not-run(wN)
        marked    + reports>0   -> yes(wN)
        marked    + reports==0  -> stalled(wN)
        neither   + reports>0   -> yes(wN,folded)   (one v2 wave: build+attack)
        neither   + dispatch    -> stalled(wN)
        otherwise               -> none
      SCORECARD cross-check: `not dispatched|did not run|dispatch stalled|
      stalled at` in the section text sets sc_not_run; a `yes(...)` beside it is
      reported as `conflict=sc-says-not-run`, which is a printed note and never
      an unreadable round.

Fields per round:
  shortcuts  the number of distinct shortcut/attack controls the round's own
             disclosure names: ids matching K<d>Cheat|K<d>Hist|K<d>R<d>|
             V<d>Code|X<d><Name>|W<d><X><d>|R4<d><X><d>|M<d>Ctr|M<d>Tool, in
             any sentence of the disclosure block that does not itself report a
             mutant count (`A of B ... mutants`, `A mutants`, `A killed`,
             `A survived`). A mutation seat named only beside its battery is
             therefore not counted as a shortcut (the lane's W1R03, M2Ctr,
             M2Tool in the rounds that name them); a seat whose sentence also
             reports a shortcut is not counted either, which undercounts.
             A printed range counts only its two endpoints (K1R01-K1R10 = 2).
             `K<d>Cheat.md` report files in the round's waves are unioned in.
             `-` when the round filed no disclosure block (status
             no-disclosure).
  ids        that id list.
  counters   distinct claim ids C1, C2, C3 (regex (?<![A-Za-z0-9])C[123]
             (?![0-9])) in the disclosure block: the frozen counters the round
             says a shortcut met. Zero ids in a present block is unreadable.
  cheats     distinct `K<d>Cheat` seat ids in the disclosure block plus
             `K<d>Cheat.md` report files in the round's waves: seat-built cheats.
  mutants    survived/total summed over the round's mutation reports; with no
             report, the disclosure block's `X of Y ... mutants survive` pair;
             `-` when neither exists.
             Per report (lines before the first `^## ` heading):
               killed  := `A of B ... mutants ... killed` | `kills only A of B`
                          | `A mutants killed` | `A killed` | `A/B mutants ...
                          killed`
               survived:= `A surviv(e|es|ed|ors)`
               equivalent := `A equivalent`
               total   := the `of`/`/` denominator, or `A-mutant`, or
                          `A single-<kind> mutants`, or `A mutants of`, else
                          killed+survived+equivalent.
             A report is unreadable when a quantity is absent, a quantity is
             reported with two different values, or
             killed+survived+equivalent != total.

Status: ok | no-disclosure | unreadable:<reason>.
  unreadable  no `## Round N` section; a present disclosure block with no claim
              id; a mutation report that fails the parse; two mutation reports
              with the same seat basename; an unparseable spec.json/dispatch.json.

`--check N` exits 1 when the latest round's shortcut count is above N, when the
latest round cannot certify a count (no disclosure or unreadable), or when any
round is unreadable; exits 0 otherwise; exits 2 when the lane root itself cannot
be read. `--json` prints the same records as JSON on stdout.

Read-only: the lane is only ever opened for reading; no git, no network, no
subprocess. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DISCLOSURE_MARK = "What `met=True` does not show"
ROUND_HEAD = re.compile(r"^## Round (\d+)\b")
ANY_H1 = re.compile(r"^#")
CLAIM = re.compile(r"(?<![A-Za-z0-9])C([123])(?![0-9])")
CHEAT = re.compile(r"(?<![A-Za-z0-9])(K\d+Cheat)(?![A-Za-z0-9])")
CONTROL = re.compile(
    r"(?<![A-Za-z0-9])"
    r"(K\d+Cheat|K\d+Hist|K\d+R\d+|V\d+Code|X\d+[A-Z][A-Za-z]*"
    r"|W\d+[A-Z]\d+|R4\d[A-Z]\d+|M\d+(?:Ctr|Tool))"
    r"(?![A-Za-z0-9])"
)
REPORT_NAME = re.compile(r"^(M\d+(?:Ctr|Tool))\.md$")
CHEAT_REPORT = re.compile(r"^(K\d+Cheat)\.md$")
FALSIFY_DEDICATED = re.compile(r"=\s*FALSIFY\b")
FALSIFY_MARKED = re.compile(r"(?i)falsif")
SC_NOT_RUN = re.compile(r"(?i)not dispatched|did not run|dispatch stalled|stalled at")


def fail(msg: str, code: int = 2) -> int:
    print(f"shortcut-tally: {msg}", file=sys.stderr)
    return code


def read_text(path: Path, errors: str = "strict") -> str:
    with path.open("r", encoding="utf-8", errors=errors) as fh:
        return fh.read()


# ---------------------------------------------------------------- SCORECARD


def scorecard_blocks(lines: list[str]):
    """Return (disclosure blocks, section texts) keyed by round number.

    blocks: round -> (line number, block text)
    sections: round -> text from its `## Round N` heading to the next one
    """
    blocks: dict[int, tuple[int, str]] = {}
    starts: list[tuple[int, int]] = []  # (line index, round)
    current: int | None = None
    i = 0
    while i < len(lines):
        m = ROUND_HEAD.match(lines[i])
        if m:
            current = int(m.group(1))
            starts.append((i, current))
        if current is not None and DISCLOSURE_MARK in lines[i] and current not in blocks:
            if lines[i].startswith("#"):
                j = i + 1
                body = [lines[i]]
                while j < len(lines) and not ANY_H1.match(lines[j]):
                    body.append(lines[j])
                    j += 1
                blocks[current] = (i + 1, "\n".join(body).strip())
                i = j
                continue
            blocks[current] = (i + 1, lines[i].strip())
        i += 1

    sections: dict[int, str] = {}
    for idx, (start, round_no) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        # only the first `## Round N` heading of a round opens its section
        if round_no in sections:
            continue
        sections[round_no] = "\n".join(lines[start:end])
    return blocks, sections


# ------------------------------------------------------------ mutation parse


def preamble(text: str) -> str:
    """Report lines before the first `## ` heading: title and verdict."""
    out = []
    for line in text.splitlines():
        if line.startswith("## "):
            break
        out.append(line)
    return "\n".join(out)


def _ints(pattern: str, text: str) -> set[int]:
    return {int(m.group(1)) for m in re.finditer(pattern, text)}


def parse_mutation_report(text: str) -> tuple[int, int]:
    """Return (survived, total) or raise ValueError with the reason."""
    pre = preamble(text)
    killed: set[int] = set()
    total: set[int] = set()

    for m in re.finditer(
        r"(\d+)\s+of\s+(\d+)[^.\n]{0,30}?\bmutants?\b[^.\n]{0,30}?\bkilled", pre
    ):
        killed.add(int(m.group(1)))
        total.add(int(m.group(2)))
    for m in re.finditer(r"\bkills?\s+only\s+(\d+)\s+of\s+(\d+)", pre):
        killed.add(int(m.group(1)))
        total.add(int(m.group(2)))
    for m in re.finditer(r"(\d+)\s*/\s*(\d+)\s+mutants?[^.\n]{0,30}?\bkilled", pre):
        killed.add(int(m.group(1)))
        total.add(int(m.group(2)))
    killed |= _ints(r"(\d+)\s+mutants?\s+\*{0,2}killed", pre)
    killed |= _ints(r"(?<![\d/])(\d+)\s+\*{0,2}killed\b", pre)
    survived = _ints(r"(\d+)\s+surviv(?:e|es|ed|ors?)\b", pre)
    equivalent = _ints(r"(\d+)\s+equivalent", pre)
    for pattern in (
        r"(\d+)[- ]mutant\b",
        r"(\d+)\s+single[- ](?:rule|site|point)[- ]?mutants?\b",
        r"(\d+)\s+mutants?\s+of\b",
    ):
        total |= _ints(pattern, pre)

    if not survived:
        raise ValueError("no survived count")
    if len(survived) != 1:
        raise ValueError(f"ambiguous survived {sorted(survived)}")
    if len(killed) > 1:
        raise ValueError(f"ambiguous killed {sorted(killed)}")
    if len(equivalent) > 1:
        raise ValueError(f"ambiguous equivalent {sorted(equivalent)}")
    if len(total) > 1:
        raise ValueError(f"ambiguous total {sorted(total)}")

    s = survived.pop()
    k = killed.pop() if killed else None
    eq = equivalent.pop() if equivalent else 0
    if total:
        t = total.pop()
    elif k is not None:
        t = k + s + eq
    else:
        raise ValueError("no total")
    if k is not None and k + s + eq != t:
        raise ValueError(f"inconsistent killed={k} survived={s} equivalent={eq} total={t}")
    return s, t


def parse_fallback_mutants(block: str) -> tuple[int, int] | None:
    for pattern in (
        r"(\d+)\s+of\s+(\d+)[^.\n]{0,30}?\bmutants?\s+surviv",
        r"(\d+)\s*/\s*(\d+)\s+mutants?\s+surviv",
    ):
        pairs = {
            (int(m.group(1)), int(m.group(2))) for m in re.finditer(pattern, block)
        }
        if len(pairs) == 1:
            return pairs.pop()
        if len(pairs) > 1:
            raise ValueError(f"ambiguous mutant pairs {sorted(pairs)}")
    return None


# ----------------------------------------------------------------- waves


def wave_falsify(round_dir: Path) -> tuple[str, str]:
    """Return (falsify value, note). Raises ValueError on unparseable wave json."""
    waves = []
    for child in sorted(round_dir.iterdir()):
        if not child.is_dir():
            continue
        spec = child / "spec.json"
        dispatch = child / "dispatch.json"
        if not (spec.exists() or dispatch.exists()):
            continue
        context = ""
        if spec.exists():
            try:
                data = json.loads(read_text(spec, errors="replace"))
            except (OSError, json.JSONDecodeError) as exc:
                raise ValueError(f"spec.json unreadable: {child.name}: {exc}")
            if isinstance(data, dict):
                context = str(data.get("context") or "")
        out = child / "out"
        reports = sum(1 for _ in out.rglob("*.md")) if out.is_dir() else 0
        waves.append(
            {
                "name": child.name,
                "dedicated": bool(FALSIFY_DEDICATED.search(context)),
                "marked": bool(FALSIFY_MARKED.search(context)),
                "reports": reports,
                "dispatch": dispatch.exists(),
            }
        )

    if not waves:
        return "none", "no wave dir"

    for w in waves:
        if w["dedicated"]:
            if w["reports"]:
                return f"yes({w['name']},dedicated)", ""
            return f"planned-not-run({w['name']})", ""
    for w in waves:
        if w["marked"]:
            if w["reports"]:
                return f"yes({w['name']})", ""
            return f"stalled({w['name']})", ""
    ran = [w for w in waves if w["reports"]]
    if ran:
        return f"yes({ran[0]['name']},folded)", ""
    dispatched = [w for w in waves if w["dispatch"]]
    if dispatched:
        return f"stalled({dispatched[0]['name']})", ""
    return "none", "wave dir without spec or dispatch"


SHORTCUT_SENTENCE_MUTANT = re.compile(
    r"(?i)(?:\b\d+\s+of\s+\d+\b[^.;]*\bmutants?\b"
    r"|\b\d+\s+mutants?\b|\b\d+\s+killed\b|\b\d+\s+surviv(?:e|es|ed|ors?)\b)"
)


def shortcut_ids(block: str) -> list[str]:
    """Control ids named in disclosure sentences that do not report a mutant battery."""
    found: set[str] = set()
    for part in re.split(r"(?<=[.;])\s+|\n+", block):
        if SHORTCUT_SENTENCE_MUTANT.search(part):
            continue
        found |= {m.group(1) for m in CONTROL.finditer(part)}
    return sorted(found)


# ----------------------------------------------------------------- per round


def tally_round(
    round_no: int,
    lane: Path,
    blocks: dict[int, tuple[int, str]],
    sections: dict[int, str],
) -> dict:
    rec: dict = {
        "round": round_no,
        "shortcuts": None,
        "ids": [],
        "counters": [],
        "cheats": [],
        "mutants": None,
        "falsify": "none",
        "status": "ok",
        "notes": [],
        "provenance": [],
    }
    round_dir = lane / ".ufo" / "waves" / f"round-{round_no}"

    if round_no not in sections:
        rec["status"] = "unreadable:no-section"
        rec["notes"].append("SCORECARD.md has no `## Round N` heading")
    block = blocks.get(round_no)
    fallback: tuple[int, int] | None = None
    fallback_error: str | None = None
    if block is not None:
        line_no, text = block
        claims = sorted({int(m.group(1)) for m in CLAIM.finditer(text)})
        rec["counters"] = [f"C{c}" for c in claims]
        rec["ids"] = shortcut_ids(text)
        rec["shortcuts"] = len(rec["ids"]) if rec["ids"] else None
        rec["cheats"] = sorted({m.group(1) for m in CHEAT.finditer(text)})
        rec["provenance"].append(f"disclosure SCORECARD.md:{line_no}")
        if not claims:
            rec["status"] = "unreadable:no-claim-ids"
            rec["notes"].append("disclosure block names no C1/C2/C3")
        try:
            fallback = parse_fallback_mutants(text)
        except ValueError as exc:
            fallback_error = str(exc)
    elif rec["status"] == "ok":
        rec["status"] = "no-disclosure"

    # mutation reports override the fallback
    report_failed = False
    if round_dir.is_dir():
        reports: dict[str, Path] = {}
        for path in sorted(round_dir.rglob("*.md")):
            m = REPORT_NAME.match(path.name)
            if not m:
                continue
            seat = m.group(1)
            if seat in reports:
                rec["status"] = "unreadable:duplicate-report"
                rec["notes"].append(f"{seat} reported twice: {path}")
                continue
            reports[seat] = path
        if reports:
            survived = total = 0
            for seat, path in sorted(reports.items()):
                try:
                    s, t = parse_mutation_report(read_text(path, errors="replace"))
                except (OSError, ValueError) as exc:
                    rec["status"] = "unreadable:mutation-report"
                    report_failed = True
                    rel = path.relative_to(lane)
                    rec["notes"].append(f"{rel}: {exc}")
                    continue
                survived += s
                total += t
                rec["provenance"].append(f"{seat} {path.relative_to(lane)} {s}/{t}")
            if total and not report_failed:
                rec["mutants"] = f"{survived}/{total}"

        # seat-built cheat report files join the cheat list
        for path in round_dir.rglob("*.md"):
            m = CHEAT_REPORT.match(path.name)
            if m and m.group(1) not in rec["cheats"]:
                rec["cheats"].append(m.group(1))
                rec["provenance"].append(f"cheat report {path.relative_to(lane)}")
        rec["cheats"].sort()
        if rec["cheats"]:
            rec["ids"] = sorted(set(rec["ids"]) | set(rec["cheats"]))
            rec["shortcuts"] = len(rec["ids"])

        try:
            value, note = wave_falsify(round_dir)
        except ValueError as exc:
            rec["status"] = "unreadable:wave-json"
            rec["notes"].append(str(exc))
            value, note = "?", ""
        rec["falsify"] = value
        if note:
            rec["notes"].append(note)
    else:
        rec["notes"].append(f"no {round_dir.relative_to(lane)} directory")

    # the disclosure block's mutant pair is the fallback, never an overlay
    if block is not None and rec["mutants"] is None and not report_failed:
        if fallback_error is not None:
            rec["status"] = "unreadable:mutant-fallback"
            rec["notes"].append(fallback_error)
        elif fallback is not None:
            rec["mutants"] = f"{fallback[0]}/{fallback[1]}"
            rec["provenance"].append(f"mutants SCORECARD.md:{block[0]}")

    # SCORECARD cross-check of the falsify column
    section = sections.get(round_no, "")
    sc_not_run = bool(SC_NOT_RUN.search(section))
    if rec["falsify"].startswith("yes") and sc_not_run:
        rec["notes"].append("conflict=sc-says-not-run")
    return rec


# ------------------------------------------------------------------- output


def render(records: list[dict]) -> None:
    header = ["round", "shortcuts", "ids", "counters", "cheats", "mutants", "falsify", "status"]
    rows = []
    for r in records:
        rows.append(
            [
                str(r["round"]),
                "-" if r["shortcuts"] is None else str(r["shortcuts"]),
                ",".join(r["ids"]) or "-",
                ",".join(r["counters"]) or "-",
                ",".join(r["cheats"]) or "0",
                r["mutants"] or "-",
                r["falsify"],
                r["status"],
            ]
        )
    widths = [max(len(h), *(len(row[i]) for row in rows)) for i, h in enumerate(header)]
    print("  ".join(h.ljust(w) for h, w in zip(header, widths)).rstrip())
    for row in rows:
        print("  ".join(cell.ljust(w) for cell, w in zip(row, widths)).rstrip())
    for r in records:
        for note in r["notes"]:
            print(f"note: round {r['round']}: {note}")
        for prov in r["provenance"]:
            print(f"detail: round {r['round']}: {prov}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Tally shortcut-satisfiable counters, mutant survival and falsify waves per round."
    )
    ap.add_argument("--lane", type=Path, default=None, help="lane root (default: six parents up from this file)")
    ap.add_argument("--rounds", default="40-46", help="round range, e.g. 40-46 (default)")
    ap.add_argument("--check", type=int, default=None, metavar="N", help="exit 1 when the latest round's shortcut count is above N or a round is unreadable")
    ap.add_argument("--json", action="store_true", help="print records as JSON")
    args = ap.parse_args(argv)

    lane = args.lane
    if lane is None:
        here = Path(__file__).resolve()
        lane = here.parents[6] if len(here.parents) > 6 else Path.cwd()
    lane = lane.resolve()
    scorecard = lane / "SCORECARD.md"
    waves = lane / ".ufo" / "waves"
    if not scorecard.is_file():
        return fail(f"no SCORECARD.md under {lane}")
    if not waves.is_dir():
        return fail(f"no .ufo/waves under {lane}")

    m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", args.rounds)
    if not m:
        return fail(f"--rounds must be A-B, got {args.rounds!r}")
    lo, hi = int(m.group(1)), int(m.group(2))
    if lo > hi:
        return fail(f"--rounds {args.rounds}: empty range")

    try:
        lines = read_text(scorecard).splitlines()
    except OSError as exc:
        return fail(f"cannot read {scorecard}: {exc}")
    blocks, sections = scorecard_blocks(lines)

    records = [tally_round(n, lane, blocks, sections) for n in range(lo, hi + 1)]

    if args.json:
        print(json.dumps(records, indent=1, sort_keys=True))
    else:
        render(records)

    if args.check is None:
        return 0

    latest = records[-1]
    unreadable = [r["round"] for r in records if r["status"].startswith("unreadable")]
    reason = None
    if unreadable:
        reason = f"unreadable rounds {unreadable}"
    elif latest["shortcuts"] is None:
        reason = f"latest round {latest['round']} cannot certify a shortcut count ({latest['status']})"
    elif latest["shortcuts"] > args.check:
        reason = f"latest round {latest['round']} shortcuts={latest['shortcuts']} > limit {args.check}"
    result = "FAIL" if reason else "PASS"
    print(
        f"latest={latest['round']} shortcuts={'-' if latest['shortcuts'] is None else latest['shortcuts']}"
        f" limit={args.check} result={result}" + (f" ({reason})" if reason else "")
    )
    return 1 if reason else 0


if __name__ == "__main__":
    sys.exit(main())
