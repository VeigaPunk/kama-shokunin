#!/usr/bin/env python3
"""round83-pin-rechecks.py - round-83 C3 (freshness): grade every engine-pin relation row
against its committed recheck row and the two committed anchor extracts.

Reads (paths relative to --repo unless absolute):
  --register registry/engine-pin-relations.tsv   relation register; one population row per
                                                 (engine, ref), 9 cells, header:
  engine	ref	kind	role	relation	newer	newest	receipt	dated
  --rows     registry/pin-recheck-rows.tsv       recheck register filed this round, 12 cells,
                                                 header exactly:
  engine	ref	newest	verdict	date	quote_pin	line_pin	quote_newest	line_newest	extract_pin	extract_newest	note
A lone `-` cell in the six placeholder-able columns (quotes, lines, extracts) means empty;
the ungraded row of the round-83 register uses that convention.

Anchor extract format: first line exactly
  # url=<https-url> sha256=<64-hex> ref=<ref> lines=<a>-<b>
The SHA-256 is recomputed over the bytes after the header line and must equal the header
digest. line_pin / line_newest are line numbers in the UPSTREAM document; the header's
lines=<a>-<b> declares the upstream range the excerpt covers, so a quote declared at line L
must sit on excerpt body line L - a + 1 (the b11755 extract covers 478-490 and its quote at
upstream line 481 sits on body line 4).

Grades, re-derived from the bytes rather than the declared word:
  holds             pin quote occurs verbatim (as UTF-8 bytes) in the newest extract
  reworded/moved/drifted
                    pin quote absent there AND the newest quote non-empty and different;
                    the choice among the three is the declarer's judgment, the counter only
                    checks byte-consistency
  ungraded          the lane holds no document at the ref; requires a note naming the missing
                    document (the note must cite the row's ref); never counts as graded
Any declared verdict that contradicts the byte comparison is bad (verdict-contradicts-bytes).
A word is a whitespace-separated token, punctuation included: a 26-token quote is
quote-too-long. Relations with zero recheck rows are missing-row, with two or more are
duplicate-row (the first row is graded, every further row is flagged), and recheck rows whose
(engine, ref) names no relation are unknown-row; all three are bad.

Output: one `PIN_RECHECK rows=<n> graded=<g> holds=<h> reworded=<rw> moved=<m> drifted=<d>
ungraded=<u> bad=<b>` line (population = relation register data rows; bad rows count only in
bad), then one `PIN_RECHECK_FINDING <class> <detail>` line per finding, in register order.

Exit: 0 every relation keyed once and byte-consistent; 1 findings; 2 could-not-evaluate
(absent or unreadable register, printed as `could-not-evaluate: no <path>`) - never silently 0.

--selftest builds 10 red mutant arms plus the green honest fixture in $TMPDIR and checks each
arm's exit code and finding class. --dump-fixtures DIR materializes the green fixture set
(register.tsv, rows.tsv, extracts/) for inspection and standalone runs. Committedness of the
extracts is the filer's property; the counter reads the working tree and runs no git command.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

REGISTER_HEADER = "engine\tref\tkind\trole\trelation\tnewer\tnewest\treceipt\tdated"
ROWS_HEADER = ("engine\tref\tnewest\tverdict\tdate\tquote_pin\tline_pin\t"
               "quote_newest\tline_newest\textract_pin\textract_newest\tnote")
PLACEHOLDER_CELLS = range(5, 11)  # quotes, lines, extracts: a lone `-` means empty
GRADED = ("holds", "reworded", "moved", "drifted")
VOCABULARY = GRADED + ("ungraded",)
MAX_WORDS = 25
EXTRACT_RE = re.compile(r"^# url=(\S+) sha256=([0-9a-f]{64}) ref=(\S+) lines=(\d+)-(\d+)$")

GREEN_SUMMARY = {"rows": 3, "graded": 2, "holds": 2, "reworded": 0,
                 "moved": 0, "drifted": 0, "ungraded": 1, "bad": 0}


class CouldNotEvaluate(Exception):
    pass


def read_table(repo: Path, given: str, expected_header: str, label: str):
    """(cells, line number) per data row, or CouldNotEvaluate; an absent register exits 2."""
    path = Path(given)
    path = path if path.is_absolute() else repo / path
    if not path.is_file():
        raise CouldNotEvaluate(f"no {given}")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise CouldNotEvaluate(f"unreadable {given}: {exc}") from exc
    lines = text.splitlines()
    if not lines or lines[0] != expected_header:
        raise CouldNotEvaluate(f"{label} header mismatch in {given}")
    return [(line.split("\t"), number) for number, line in enumerate(lines[1:], start=2)
            if line.strip()]


def parse_extract(repo: Path, given: str):
    """(info|None, problems[(class, detail)]); info carries ref, range, body and body lines."""
    problems: list[tuple[str, str]] = []
    path = Path(given)
    path = path if path.is_absolute() else repo / path
    if not path.is_file():
        return None, [("extract-missing", f"{given}: file not found")]
    try:
        data = path.read_bytes()
    except OSError as exc:
        return None, [("extract-missing", f"{given}: unreadable ({exc})")]
    cut = data.find(b"\n")
    if cut < 0:
        return None, [("extract-header", f"{given}: no header line")]
    head = data[:cut].decode("utf-8", "replace")
    match = EXTRACT_RE.match(head)
    if match is None:
        return None, [("extract-header", f"{given}: first line is not "
                       "'# url=<https-url> sha256=<64-hex> ref=<ref> lines=<a>-<b>'")]
    url, digest, ref, start, end = match.groups()
    if not url.startswith("https://"):
        problems.append(("extract-header", f"{given}: url is not https"))
    body = data[cut + 1:]
    actual = hashlib.sha256(body).hexdigest()
    if actual != digest:
        problems.append(("digest-mismatch",
                         f"{given}: header sha256 {digest} != sha256(bytes after header) {actual}"))
    info = {"given": given, "url": url, "ref": ref, "start": int(start), "end": int(end),
            "body": body, "lines": body.decode("utf-8", "replace").splitlines()}
    return info, problems


def quote_problems(info, quote, line_cell, side, given):
    """Problems locating `quote` at its declared upstream line inside the extract."""
    problems: list[tuple[str, str]] = []
    if len(quote.split()) > MAX_WORDS:
        problems.append(("quote-too-long",
                         f"{side}: {len(quote.split())} words > {MAX_WORDS} (punctuation counts)"))
    if not line_cell:
        problems.append(("quote-not-at-line", f"{side}: no line declared for the quote"))
        return problems
    try:
        want = int(line_cell)
    except ValueError:
        problems.append(("quote-not-at-line", f"{side}: line {line_cell!r} is not an integer"))
        return problems
    if want < info["start"] or want > info["end"]:
        problems.append(("quote-not-at-line",
                         f"{side}: declared line {want} outside extract range "
                         f"{info['start']}-{info['end']} of {given}"))
        return problems
    index = want - info["start"]  # upstream line L sits on body line L - start + 1
    if index >= len(info["lines"]):
        problems.append(("quote-not-at-line",
                         f"{side}: extract body has {len(info['lines'])} lines, short of "
                         f"declared range {info['start']}-{info['end']} of {given}"))
        return problems
    if quote not in info["lines"][index]:
        problems.append(("quote-not-at-line",
                         f"{side}: quote not on extract body line {index + 1} "
                         f"(upstream line {want}) of {given}"))
    return problems


def grade_row(repo: Path, engine: str, ref: str, cells, rows_name: str, problems) -> bool:
    """Validate one recheck row against its extracts; True when the row is bad."""
    state = {"bad": False}

    def flag(cls: str, detail: str) -> None:
        state["bad"] = True
        problems.append((cls, f"engine={engine} ref={ref} {detail}"))

    if len(cells) != 12:
        flag("bad-row", f"{rows_name}: {len(cells)} cells, want 12")
        return True
    cells = [("" if (index in PLACEHOLDER_CELLS and cell == "-") else cell)
             for index, cell in enumerate(cells)]
    (_engine, _ref, newest, declared, _date, quote_pin, line_pin,
     quote_newest, line_newest, extract_pin, extract_newest, note) = cells

    if declared not in VOCABULARY:
        flag("verdict-vocabulary", f"verdict {declared!r} not in {', '.join(VOCABULARY)}")
    if declared == "ungraded":
        if not note or ref not in note:
            flag("ungraded-without-note",
                 "ungraded row needs a note naming the missing document (must cite the ref)")
    elif declared in GRADED:
        for cell, side in ((quote_pin, "pin"), (quote_newest, "newest")):
            if not cell:
                flag("missing-quote", f"{side}: graded row declares no quote")
        for cell, side in ((extract_pin, "pin"), (extract_newest, "newest")):
            if not cell:
                flag("extract-missing", f"{side}: graded row declares no extract")

    bodies: dict[str, bytes] = {}
    for cell, want_ref, side in ((extract_pin, ref, "pin"),
                                 (extract_newest, newest, "newest")):
        if not cell:
            continue
        info, extract_problems = parse_extract(repo, cell)
        for cls, detail in extract_problems:
            flag(cls, detail)
        if info is None:
            continue
        if info["ref"] != want_ref:
            flag("ref-mismatch",
                 f"{side} extract header ref={info['ref']} disagrees with the row's "
                 f"{'ref' if side == 'pin' else 'newest'} cell {want_ref}")
        quote, line_cell = ((quote_pin, line_pin) if side == "pin"
                            else (quote_newest, line_newest))
        for cls, detail in quote_problems(info, quote, line_cell, side, info["given"]):
            flag(cls, detail)
        bodies[side] = info["body"]

    if declared in GRADED and "pin" in bodies and "newest" in bodies:
        present = quote_pin.encode("utf-8") in bodies["newest"]
        if declared == "holds" and not present:
            flag("verdict-contradicts-bytes",
                 "declared holds but the pin quote does not occur verbatim in the newest extract")
        elif declared != "holds" and (present or not quote_newest
                                      or quote_newest == quote_pin):
            shape = ("present" if present else
                     "duplicate of the pin quote" if quote_newest == quote_pin else "empty")
            flag("verdict-contradicts-bytes",
                 f"declared {declared} but the pin quote is "
                 f"{'present' if present else 'absent'} in the newest extract "
                 f"with a {shape} newest quote")
    return state["bad"]


def grade(repo: Path, register: str, rows: str):
    """(summary, findings[(class, detail)]); raises CouldNotEvaluate on absent input."""
    register_rows = read_table(repo, register, REGISTER_HEADER, "relation register")
    recheck_rows = read_table(repo, rows, ROWS_HEADER, "recheck register")
    for cells, number in register_rows:
        if len(cells) != 9:
            raise CouldNotEvaluate(
                f"relation register {register}:{number}: {len(cells)} cells, want 9")
    by_key: dict[tuple[str, str], list] = {}
    for cells, number in recheck_rows:
        if len(cells) < 2:
            continue  # unkeyable row: flagged below, never crashes the key map
        by_key.setdefault((cells[0], cells[1]), []).append((cells, number))

    findings: list[tuple[str, str]] = []
    summary = {"rows": len(register_rows), "graded": 0, "holds": 0, "reworded": 0,
               "moved": 0, "drifted": 0, "ungraded": 0, "bad": 0}
    for cells, number in recheck_rows:
        if len(cells) < 2:
            findings.append(("bad-row", f"{rows_name}:{number} {len(cells)} cells, want 12 "
                             "(engine and ref must lead the row)"))

    for engine, ref in [(cells[0], cells[1]) for cells, _number in register_rows]:
        matches = by_key.pop((engine, ref), [])
        problems: list[tuple[str, str]] = []
        if not matches:
            problems.append(("missing-row", f"engine={engine} ref={ref} "
                             "no recheck row for this relation key"))
        for cells, number in matches[1:]:
            problems.append(("duplicate-row", f"engine={engine} ref={ref} "
                             f"second recheck row at {rows}:{number}"))
        row_bad = bool(matches) and grade_row(repo, engine, ref, matches[0][0], rows, problems)
        findings.extend(problems)
        if not matches or len(matches) > 1 or row_bad:
            summary["bad"] += 1
        elif matches[0][0][3] == "ungraded":
            summary["ungraded"] += 1
        else:
            summary["graded"] += 1
            summary[matches[0][0][3]] += 1

    for (engine, ref), matches in by_key.items():
        for cells, number in matches:
            findings.append(("unknown-row", f"engine={engine} ref={ref} "
                             f"no relation row for this recheck key ({rows}:{number})"))
    return summary, findings


def render(result) -> str:
    s = result["summary"]
    head = (f"PIN_RECHECK rows={s['rows']} graded={s['graded']} holds={s['holds']} "
            f"reworded={s['reworded']} moved={s['moved']} drifted={s['drifted']} "
            f"ungraded={s['ungraded']} bad={s['bad']}")
    return "\n".join([head] + [f"PIN_RECHECK_FINDING {cls} {detail}"
                               for cls, detail in result["findings"]])


def verdict(result) -> int:
    return 0 if not result["findings"] else 1


# ---------------------------------------------------------------- selftest

SENTENCE_A = "READINESS: the health endpoint answers 200 when ready"
SENTENCE_B = "MODEL LISTING: the router lists every loaded model by name"
LONG_A = SENTENCE_A + " " + " ".join(["filler"] * 18)  # 8 + 18 = 26 words


def write_extract(root: Path, rel: str, url: str, ref: str, start: int, end: int, lines) -> None:
    body = ("\n".join(lines) + "\n").encode("utf-8")
    header = (f"# url={url} sha256={hashlib.sha256(body).hexdigest()} "
              f"ref={ref} lines={start}-{end}\n").encode("utf-8")
    (root / rel).write_bytes(header + body)


def build_green(root: Path) -> None:
    """The honest fixture: two graded holds rows and one ungraded row, all byte-consistent."""
    (root / "extracts").mkdir(parents=True)
    (root / "register.tsv").write_text(REGISTER_HEADER + "\n" + "\n".join([
        "engone\tb1\ttag\tengine-pins.tsv\tbehind\t2\tn2\t"
        "measured/after/c2-tags/engone.txt\t2026-11-04",
        "engone\tb2\tcommit\tsource-row S1\ttag:b1c\t5\tn2\t"
        "measured/after/c2-tags/engone.txt\t2026-11-04",
        "engtwo\tv1\ttag\tengine-pins.tsv\tbehind\t1\tv2\t"
        "measured/after/c2-tags/engtwo.txt\t2026-11-04"]) + "\n", encoding="utf-8")
    write_extract(root, "extracts/engone-b1.txt", "https://example.com/engone/raw/b1",
                  "b1", 10, 12, ["line ten", SENTENCE_A, "line twelve"])
    write_extract(root, "extracts/engone-n2-health.txt", "https://example.com/engone/raw/n2",
                  "n2", 10, 12, ["line ten", SENTENCE_A, "line twelve, extended"])
    write_extract(root, "extracts/engone-b2.txt", "https://example.com/engone/raw/b2",
                  "b2", 30, 31, [SENTENCE_B, "note one"])
    write_extract(root, "extracts/engone-n2-models.txt", "https://example.com/engone/raw/n2",
                  "n2", 40, 41, [SENTENCE_B, "trailer line"])
    rows = [
        ["engone", "b1", "n2", "holds", "2026-11-04", SENTENCE_A, "11", SENTENCE_A, "11",
         "extracts/engone-b1.txt", "extracts/engone-n2-health.txt",
         "held sentence byte-identical at n2"],
        ["engone", "b2", "n2", "holds", "2026-11-04", SENTENCE_B, "30", SENTENCE_B, "40",
         "extracts/engone-b2.txt", "extracts/engone-n2-models.txt",
         "held sentence byte-identical at n2"],
        ["engtwo", "v1", "v2", "ungraded", "2026-11-04", "-", "-", "-", "-", "-", "-",
         "lane holds no document at v1 (engtwo doc never opened at this ref)"],
    ]
    (root / "rows.tsv").write_text(
        ROWS_HEADER + "\n" + "\n".join("\t".join(row) for row in rows) + "\n",
        encoding="utf-8")


def edit_rows(dirpath: Path, fn) -> None:
    path = dirpath / "rows.tsv"
    path.write_text("\n".join(fn(path.read_text(encoding="utf-8").splitlines())) + "\n",
                    encoding="utf-8")


def set_row(lines, prefix, cells):
    return ["\t".join(cells) if line.startswith(prefix) else line for line in lines]


def selftest() -> int:
    scratch = Path(tempfile.mkdtemp(prefix="pin-recheck-selftest-"))
    cases: list[tuple[str, int, str | None, Path]] = []
    try:
        base = scratch / "green"
        build_green(base)
        cases.append(("green-honest", 0, None, base))

        def arm(name: str, mutate, want_class: str) -> None:
            target = scratch / name
            shutil.copytree(base, target)
            mutate(target)
            cases.append((name, 1, want_class, target))

        arm("missing-row", lambda d: edit_rows(
            d, lambda lines: [line for line in lines if not line.startswith("engtwo\t")]),
            "missing-row")

        def duplicate_b1(lines):
            return lines + [line for line in lines if line.startswith("engone\tb1\t")]
        arm("duplicate-row", lambda d: edit_rows(d, duplicate_b1), "duplicate-row")

        def add_ghost(lines):
            return lines + ["\t".join(["ghost", "r9", "g2", "ungraded", "2026-11-04",
                                       "-", "-", "-", "-", "-", "-",
                                       "no document at r9 (ghost doc never opened at this ref)"])]
        arm("unknown-row", lambda d: edit_rows(d, add_ghost), "unknown-row")

        def holds_but_absent(d):
            write_extract(d, "extracts/engone-n2-health.txt",
                          "https://example.com/engone/raw/n2", "n2", 10, 12,
                          ["line ten", "READINESS: the health endpoint now answers 503 "
                           "while loading", "line twelve, extended"])
            edit_rows(d, lambda lines: set_row(lines, "engone\tb1\t", [
                "engone", "b1", "n2", "holds", "2026-11-04", SENTENCE_A, "11",
                "READINESS: the health endpoint now answers 503 while loading", "11",
                "extracts/engone-b1.txt", "extracts/engone-n2-health.txt",
                "mutated: declared holds over an absent pin quote"]))
        arm("holds-but-absent", holds_but_absent, "verdict-contradicts-bytes")

        def drifted_but_present(d):
            extended = SENTENCE_A + " even under sustained load"
            write_extract(d, "extracts/engone-n2-health.txt",
                          "https://example.com/engone/raw/n2", "n2", 10, 12,
                          ["line ten", extended, "line twelve, extended"])
            edit_rows(d, lambda lines: set_row(lines, "engone\tb1\t", [
                "engone", "b1", "n2", "drifted", "2026-11-04", SENTENCE_A, "11",
                extended, "11", "extracts/engone-b1.txt",
                "extracts/engone-n2-health.txt",
                "mutated: declared drifted over a present pin quote"]))
        arm("drifted-but-present", drifted_but_present, "verdict-contradicts-bytes")

        def quote_26(d):
            write_extract(d, "extracts/engone-b1.txt", "https://example.com/engone/raw/b1",
                          "b1", 10, 12, ["line ten", LONG_A, "line twelve"])
            write_extract(d, "extracts/engone-n2-health.txt",
                          "https://example.com/engone/raw/n2", "n2", 10, 12,
                          ["line ten", LONG_A, "line twelve, extended"])
            edit_rows(d, lambda lines: set_row(lines, "engone\tb1\t", [
                "engone", "b1", "n2", "holds", "2026-11-04", LONG_A, "11", LONG_A, "11",
                "extracts/engone-b1.txt", "extracts/engone-n2-health.txt",
                "mutated: 26-word quotes on both sides"]))
        arm("quote-26-words", quote_26, "quote-too-long")

        def quote_not_at_line(d):
            edit_rows(d, lambda lines: set_row(lines, "engone\tb1\t", [
                "engone", "b1", "n2", "holds", "2026-11-04", SENTENCE_A, "10",
                SENTENCE_A, "11", "extracts/engone-b1.txt",
                "extracts/engone-n2-health.txt",
                "mutated: pin line displaced by one (line ten does not carry the quote)"]))
        arm("quote-not-at-line", quote_not_at_line, "quote-not-at-line")

        def digest_mismatch(d):
            path = d / "extracts" / "engone-b1.txt"
            path.write_bytes(path.read_bytes().replace(b"line twelve\n", b"line twelve X\n"))
        arm("digest-mismatch", digest_mismatch, "digest-mismatch")

        arm("ungraded-without-note", lambda d: edit_rows(
            d, lambda lines: [line.replace(
                "lane holds no document at v1 (engtwo doc never opened at this ref)", "")
                for line in lines]), "ungraded-without-note")

        arm("verdict-vocabulary", lambda d: edit_rows(
            d, lambda lines: [line.replace("engone\tb1\tn2\tholds\t",
                                           "engone\tb1\tn2\texpanded\t")
                for line in lines]), "verdict-vocabulary")

        fail = 0
        for name, want_exit, want_class, where in cases:
            try:
                summary, findings = grade(where, "register.tsv", "rows.tsv")
                got, got_summary, got_findings = (0 if not findings else 1), summary, findings
            except CouldNotEvaluate as exc:
                got, got_summary, got_findings = 2, {}, [("could-not-evaluate", str(exc))]
            classes = [cls for cls, _detail in got_findings]
            ok = got == want_exit and (want_class is None or want_class in classes)
            if name == "green-honest" and ok:
                ok = got_summary == GREEN_SUMMARY
            if ok:
                head = (render({"summary": got_summary, "findings": []}).splitlines()[0]
                        if got_summary else "no summary")
                print(f"PIN_RECHECK_SELFTEST_OK {name} exit={got} {head}"
                      + (f" finding={want_class}" if want_class else ""))
            else:
                fail += 1
                print(f"PIN_RECHECK_SELFTEST_FAIL {name} exit={got} want={want_exit} "
                      f"want_class={want_class} findings={got_findings[:3]}")
        print(f"PIN_RECHECK_SELFTEST pass={len(cases) - fail} fail={fail}")
        return 0 if fail == 0 else 1
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--register", default="registry/engine-pin-relations.tsv")
    parser.add_argument("--rows", default="registry/pin-recheck-rows.tsv")
    parser.add_argument("--json", action="store_true", help="print the receipt as JSON")
    parser.add_argument("--selftest", action="store_true",
                        help="run 10 red mutant arms plus the green honest fixture")
    parser.add_argument("--dump-fixtures", metavar="DIR",
                        help="materialize the green fixture set into DIR and exit")
    args = parser.parse_args(argv)
    if args.dump_fixtures:
        build_green(Path(args.dump_fixtures))
        print(f"green fixture written under {args.dump_fixtures}")
        return 0
    if args.selftest:
        return selftest()
    try:
        summary, findings = grade(Path(args.repo), args.register, args.rows)
    except CouldNotEvaluate as exc:
        print(f"could-not-evaluate: {exc}")
        return 2
    result = {"summary": summary, "findings": findings}
    print(json.dumps({"summary": summary,
                      "findings": [list(f) for f in findings]}, indent=2)
          if args.json else render(result))
    return verdict(result)


if __name__ == "__main__":
    sys.exit(main())
