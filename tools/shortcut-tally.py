#!/usr/bin/env python3
"""shortcut-tally.py (v2) - tally counters that a shortcut can satisfy.

Question (unchanged from the round-47 draft): across the lane's rounds, is the
record saying that counter design is getting harder to fool, or only that
shortcuts are disclosed better? For each round report (a) how many frozen
counters the round's own `met=True` disclosure says a shortcut met, (b) how many
counter/tool mutants survived their mutation battery, and (c) whether a falsify
wave ran.

v2 (round 48) promotes the round-47 draft (`.ufo/waves/round-47/w1/out/X9Tally/
shortcut-tally.py`, `considerthese/2026-10-26.md` proposal 3) to a lane tool
with the following changes, every one of which the draft's own run needed:

  committed bytes only  `--repo`/`--rev` read SCORECARD.md and `.ufo/waves/**`
                        out of the git object tree at <rev> (`ls-tree` +
                        `cat-file blob`), never from a working tree. The draft
                        read the lane's files, so a seat could tally its own
                        uncommitted edits; --selftest case `committed-bytes`
                        pins the difference. <rev> is resolved once to a full
                        commit id and printed, so a tally names its bytes.
  `--check N`           the draft had it; semantics are kept and stated below.
  `--selftest`          fixtures under `--scratch` that build their own git
                        repos, including a case that must fail (a shortcut count
                        above the limit, an unreadable round, a contradictory
                        mutation report) - a check that cannot fail is not a
                        check.
  round 47 reads        two parse defects made round 47 `unreadable` and would
                        have made `--check` exit 1 forever:
                        (a) `A/B mutants killed` fed B into the bare
                            `N mutants killed` pattern, so `29/44 mutants killed`
                            reported killed {29,44}; the bare pattern now
                            refuses a preceding `/` or digit. Rounds 43/44/46
                            use `A of B ... killed` and are unchanged by this.
                        (b) a report may split its kills over two batteries
                            (`22 killed by the tool's own selftest, 3 killed by
                            the frozen counter, 5 equivalent, 3 survived`);
                            several killed counts now sum, and the sum must
                            still satisfy killed+survived+equivalent == total.
                            A split that does not add up stays unreadable.
  `wide` (diagnostic)   the gated count's id family is the draft's, frozen, so
                        rounds 40-46 reproduce the published table. That family
                        is tuned to `K<n>Cheat`-style names and undercounts a
                        round whose attack seats are named `V1Ctr`, `K1Fixture`,
                        `K2Checks`, `Sen2Replay`, `L1Lowthr`. `wide` counts the
                        same sentences under the generalised seat shapes and is
                        printed when it differs; it is never gated.

Sources (read-only, lane root, all at <rev>):
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
    - mutation reports: any `*.md` whose basename is `M<d>Ctr.md`, `M<d>Tool.md`
      or `M<d>Replay.md`, at any depth below the round directory.
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
  wide       the same sentences read with `(K|V|X)<d><Name>|M<d>(Ctr|Tool|
             Replay)|W<d><X><d>|R4<d><X><d>`; diagnostic only. It catches the
             round-47 seats the frozen family misses, and it also catches a seat
             named as a reviewer (round 44's K2Design), so it is no gate.
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
                          killed` | `<n> mutants <...> A killed` (summed when a
                          report splits its kills over batteries; the sum must
                          close the identity below)
               survived:= `A surviv(e|es|ed|ors)`, case-insensitive (round-47
                          M2Replay writes `10 SURVIVED both`)
               equivalent := `A equivalent`
               total   := the `of`/`/` denominator, or `A-mutant`, or
                          `A single-<kind> mutants`, or `A mutants of`, else
                          killed+survived+equivalent.
             A report is unreadable when a quantity is absent, a quantity is
             reported with two different values (survived, equivalent, total),
             or killed+survived+equivalent != total.

Status: ok | no-disclosure | unreadable:<reason>.
  unreadable  no `## Round N` section; a present disclosure block with no claim
              id; a mutation report that fails the parse; two mutation reports
              with the same seat basename; an unparseable spec.json/dispatch.json.

`--check N` exits 1 when the latest round's shortcut count is above N, when the
latest round cannot certify a count (no disclosure or unreadable), or when any
round is unreadable; exits 0 otherwise; exits 2 when the repository, the
revision or the lane tree itself cannot be read. `--json` prints the same
records as `{"meta": {"repo", "rev", "rounds"}, "records": [...]}` on stdout (the
meta names the repository and the full commit id the bytes came from; the check
verdict then goes to stderr so stdout stays parseable). `--selftest` builds
fixtures under `--scratch`
(default $TMPDIR) and prints `selftest pass=N fail=M`; it exits 1 if any case
fails.

Selftest cases (`--selftest`, fixtures under `--scratch`, each builds its own git
repository and proves its own toplevel before committing):
  readable-round            a round with a disclosure, a clean battery and a wave
                            reads ok with the expected counts
  check-fails               `--check 0` on a round that discloses one shortcut
                            exits 1 (a check that cannot fail is not a check)
  committed-bytes           an uncommitted worktree edit does not move the tally
  bad-rev                   an unresolvable `--rev` exits 2
  unreadable-round          a deleted `## Round N` heading makes `--check` exit 1
  split-slash-uppercase-kill `A/B mutants killed`, split kills and `N SURVIVED`
                            parse to survived/total
  contradictory-report      a battery that does not close killed+survived+
                            equivalent == total stays unreadable

Read-only: the repository is only read through `git rev-parse`, `git ls-tree`
and `git cat-file`; no network, no working-tree read, no write outside the
`--selftest` fixture root. Standard library only (git is invoked as a
subprocess; the draft needed no subprocess because it read files).
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
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
WIDE = re.compile(
    r"(?<![A-Za-z0-9])"
    r"((?:K|V|X)\d+[A-Z][A-Za-z0-9]*"
    r"|M\d+(?:Ctr|Tool|Replay)"
    r"|W\d+[A-Z]\d+|R4\d[A-Z]\d+)"
    r"(?![A-Za-z0-9])"
)
REPORT_NAME = re.compile(r"^(M\d+(?:Ctr|Tool|Replay))\.md$")
CHEAT_REPORT = re.compile(r"^(K\d+Cheat)\.md$")
FALSIFY_DEDICATED = re.compile(r"=\s*FALSIFY\b")
FALSIFY_MARKED = re.compile(r"(?i)falsif")
SC_NOT_RUN = re.compile(r"(?i)not dispatched|did not run|dispatch stalled|stalled at")

SCORECARD = "SCORECARD.md"
WAVES = ".ufo/waves"


class RepoError(Exception):
    """The repository, the revision or the lane tree cannot be read."""


# ------------------------------------------------------------ git object tree


class Tree:
    """The file names and blob contents of one commit; nothing else is read."""

    def __init__(self, repo: Path, rev: str) -> None:
        self.repo = repo
        self.rev = self._resolve(rev)
        self.paths = self._ls()
        self.path_set = frozenset(self.paths)
        self._dirs: frozenset[str] | None = None
        self._blobs: dict[str, bytes] = {}

    def _git(self, *args: str) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(
                ["git", "-C", str(self.repo), *args], capture_output=True
            )
        except OSError as exc:  # git missing
            raise RepoError(f"cannot run git: {exc}") from exc

    def _resolve(self, rev: str) -> str:
        p = self._git("rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")
        out = p.stdout.decode("utf-8", "replace").strip()
        if p.returncode != 0 or not out:
            why = p.stderr.decode("utf-8", "replace").strip() or "no such revision"
            raise RepoError(f"{self.repo}: cannot resolve {rev!r} to a commit ({why})")
        return out

    def _ls(self) -> tuple[str, ...]:
        p = self._git("ls-tree", "-r", "-z", "--name-only", self.rev)
        if p.returncode != 0:
            why = p.stderr.decode("utf-8", "replace").strip() or "ls-tree failed"
            raise RepoError(f"{self.repo}: cannot list {self.rev}: {why}")
        names = [n for n in p.stdout.decode("utf-8", "replace").split("\0") if n]
        return tuple(sorted(names))

    @property
    def dirs(self) -> frozenset[str]:
        if self._dirs is None:
            acc: set[str] = set()
            for path in self.paths:
                parts = path.split("/")[:-1]
                for i in range(1, len(parts) + 1):
                    acc.add("/".join(parts[:i]))
            self._dirs = frozenset(acc)
        return self._dirs

    def has(self, path: str) -> bool:
        return path in self.path_set

    def isdir(self, path: str) -> bool:
        return path in self.dirs

    def child_dirs(self, prefix: str) -> list[str]:
        pref = prefix.rstrip("/") + "/" if prefix else ""
        found = set()
        for path in self.paths:
            if not path.startswith(pref):
                continue
            rest = path[len(pref):]
            head = rest.split("/", 1)[0]
            if head and head != rest:
                found.add(head)
        return sorted(found)

    def files_under(self, prefix: str, suffix: str = "") -> list[str]:
        pref = prefix.rstrip("/") + "/" if prefix and not prefix.endswith("/") else prefix
        return [p for p in self.paths if p.startswith(pref) and p.endswith(suffix)]

    def read(self, path: str, errors: str = "strict") -> str:
        if path not in self._blobs:
            p = self._git("cat-file", "blob", f"{self.rev}:{path}")
            if p.returncode != 0:
                why = p.stderr.decode("utf-8", "replace").strip() or "cat-file failed"
                raise RepoError(f"{self.repo}: cannot read {path} at {self.rev}: {why}")
            self._blobs[path] = p.stdout
        return self._blobs[path].decode("utf-8", errors)


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


def parse_mutation_report(text: str) -> tuple[int, int, str | None]:
    """Return (survived, total, killed_note) or raise ValueError with the reason."""
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
    # a bare `N killed` / `N mutants killed`; the lookbehind keeps the
    # denominator of `A/B mutants killed` out of the killed set (round-47
    # M1Ctr/M2Ctr otherwise report killed {29,44} / {13,23})
    killed |= _ints(r"(?<![\d/])(\d+)\s+mutants?\s+\*{0,2}killed", pre)
    killed |= _ints(r"(?<![\d/])(\d+)\s+\*{0,2}killed\b", pre)
    survived = _ints(r"(?i)(\d+)\s+surviv(?:e|es|ed|ors?)\b", pre)
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
    if len(equivalent) > 1:
        raise ValueError(f"ambiguous equivalent {sorted(equivalent)}")
    if len(total) > 1:
        raise ValueError(f"ambiguous total {sorted(total)}")

    s = survived.pop()
    eq = equivalent.pop() if equivalent else 0
    note = None
    if len(killed) > 1:
        note = "killed=" + "+".join(str(k) for k in sorted(killed))
    k = sum(killed) if killed else None
    if total:
        t = total.pop()
    elif k is not None:
        t = k + s + eq
    else:
        raise ValueError("no total")
    if k is not None and k + s + eq != t:
        raise ValueError(f"inconsistent killed={k} survived={s} equivalent={eq} total={t}")
    return s, t, note


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


def wave_falsify(tree: Tree, round_prefix: str) -> tuple[str, str]:
    """Return (falsify value, note). Raises ValueError on unparseable wave json."""
    waves = []
    for name in tree.child_dirs(round_prefix):
        base = f"{round_prefix}{name}/"
        spec = f"{base}spec.json"
        dispatch = f"{base}dispatch.json"
        if not (tree.has(spec) or tree.has(dispatch)):
            continue
        context = ""
        if tree.has(spec):
            try:
                data = json.loads(tree.read(spec, errors="replace"))
            except (RepoError, json.JSONDecodeError) as exc:
                raise ValueError(f"spec.json unreadable: {name}: {exc}") from exc
            if isinstance(data, dict):
                context = str(data.get("context") or "")
        reports = len(tree.files_under(f"{base}out/", ".md"))
        waves.append(
            {
                "name": name,
                "dedicated": bool(FALSIFY_DEDICATED.search(context)),
                "marked": bool(FALSIFY_MARKED.search(context)),
                "reports": reports,
                "dispatch": tree.has(dispatch),
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


def _attack_parts(block: str):
    for part in re.split(r"(?<=[.;])\s+|\n+", block):
        if SHORTCUT_SENTENCE_MUTANT.search(part):
            continue
        yield part


def shortcut_ids(block: str) -> list[str]:
    """Control ids named in disclosure sentences that do not report a mutant battery."""
    found: set[str] = set()
    for part in _attack_parts(block):
        found |= {m.group(1) for m in CONTROL.finditer(part)}
    return sorted(found)


def wide_ids(block: str) -> list[str]:
    """The same sentences under generalised seat shapes (diagnostic only)."""
    found: set[str] = set()
    for part in _attack_parts(block):
        found |= {m.group(1) for m in WIDE.finditer(part)}
    return sorted(found)


# ----------------------------------------------------------------- per round


def tally_round(
    round_no: int,
    tree: Tree,
    blocks: dict[int, tuple[int, str]],
    sections: dict[int, str],
) -> dict:
    rec: dict = {
        "round": round_no,
        "shortcuts": None,
        "ids": [],
        "wide": [],
        "counters": [],
        "cheats": [],
        "mutants": None,
        "falsify": "none",
        "status": "ok",
        "notes": [],
        "provenance": [],
    }
    round_prefix = f"{WAVES}/round-{round_no}/"

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
        rec["wide"] = wide_ids(text)
        rec["shortcuts"] = len(rec["ids"]) if rec["ids"] else None
        rec["cheats"] = sorted({m.group(1) for m in CHEAT.finditer(text)})
        rec["provenance"].append(f"disclosure SCORECARD.md:{line_no}")
        if not claims:
            rec["status"] = "unreadable:no-claim-ids"
            rec["notes"].append("disclosure block names no C1/C2/C3")
        if not rec["ids"] and rec["wide"]:
            rec["notes"].append(
                "frozen family matched no id; wide names " + ",".join(rec["wide"])
                + " (naming blind spot, not a zero)"
            )
        try:
            fallback = parse_fallback_mutants(text)
        except ValueError as exc:
            fallback_error = str(exc)
    elif rec["status"] == "ok":
        rec["status"] = "no-disclosure"

    # mutation reports override the fallback
    report_failed = False
    if tree.isdir(round_prefix.rstrip("/")):
        reports: dict[str, str] = {}
        for path in tree.files_under(round_prefix, ".md"):
            m = REPORT_NAME.match(path.rsplit("/", 1)[-1])
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
                    s, t, k_note = parse_mutation_report(tree.read(path, errors="replace"))
                except (RepoError, ValueError) as exc:
                    rec["status"] = "unreadable:mutation-report"
                    report_failed = True
                    rec["notes"].append(f"{path}: {exc}")
                    continue
                survived += s
                total += t
                rec["provenance"].append(
                    f"{seat} {path} {s}/{t}" + (f" ({k_note})" if k_note else "")
                )
            if total and not report_failed:
                rec["mutants"] = f"{survived}/{total}"

        # seat-built cheat report files join the cheat list
        for path in tree.files_under(round_prefix, ".md"):
            m = CHEAT_REPORT.match(path.rsplit("/", 1)[-1])
            if m and m.group(1) not in rec["cheats"]:
                rec["cheats"].append(m.group(1))
                rec["provenance"].append(f"cheat report {path}")
        rec["cheats"].sort()
        if rec["cheats"]:
            rec["ids"] = sorted(set(rec["ids"]) | set(rec["cheats"]))
            rec["wide"] = sorted(set(rec["wide"]) | set(rec["cheats"]))
            rec["shortcuts"] = len(rec["ids"])

        try:
            value, note = wave_falsify(tree, round_prefix)
        except ValueError as exc:
            rec["status"] = "unreadable:wave-json"
            rec["notes"].append(str(exc))
            value, note = "?", ""
        rec["falsify"] = value
        if note:
            rec["notes"].append(note)
    else:
        rec["notes"].append(f"no {round_prefix} directory")

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
        if r["wide"] and r["wide"] != r["ids"]:
            extra = sorted(set(r["wide"]) - set(r["ids"]))
            print(
                f"detail: round {r['round']}: wide={len(r['wide'])} "
                f"(+{','.join(extra) or '-'})"
            )
        for prov in r["provenance"]:
            print(f"detail: round {r['round']}: {prov}")


# ----------------------------------------------------------------- selftest


FIX_SCORECARD = """# SCORECARD

## Round 10 — fixture round

| Claim | Before → after |
|---|---|
| C1 | 7 → 7 |

Body line.

### What `met=True` does not show (round-10)

- **C1.** Seat K1Cheat met C1 with a stub, and a print-only selftest beside it.

Scores held: calibration 7.

## Round 11 — second fixture round

### What `met=True` does not show (round-11)

- **C1.** Seat K1Fixture: the threshold is unexercised.

## Round 12 — third fixture round

No disclosure here.
"""

FIX_SPEC = '{"context": "one v2 wave: build + attack"}'
FIX_M1CTR = """# M1Ctr — fixture mutation report

Verdict: **1/3 mutants killed, 1 survived, 1 equivalent.**

## Detail

29/44 mutants killed is quoted in this body and must not be read.
"""

FIX_SPLIT = """# M2Ctr — fixture split-kill report

**Verdict: 33 mutants on the counter — 22 killed by the tool's own selftest,
3 killed by the frozen counter, 5 equivalent, 3 survived (B2, K2, S1).**

## Detail
"""

FIX_SLASH = """# M3Ctr — fixture slash-kill report

Verdict: **29/44 mutants killed, 13 survived, 2 equivalent.**

## Detail
"""

FIX_REPLAY = """# M5Replay — fixture replay-tool report

**Verdict:** 24 mutants of `tools/example.py` at deadbeef — 12 killed by
`--selftest`, 0 killed by the frozen counter alone, 10 SURVIVED both (real
coverage findings), 2 equivalent.

## Detail
"""

FIX_INCONSISTENT = """# M4Ctr — fixture contradictory report

Verdict: **5/9 mutants killed, 6 survived.**

## Detail
"""


def _git(path: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True)


def _fixture(path: Path) -> Path:
    """git init a fixture and prove it is the repository root before any commit."""
    path.mkdir(parents=True, exist_ok=True)
    p = _git(path, "init", "-q")
    if p.returncode != 0:
        raise RuntimeError(f"git init failed in {path}: {p.stderr.strip()}")
    top = _git(path, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.strip()).resolve() != path.resolve():
        raise RuntimeError(f"fixture {path} is not its own repository root: {top.stdout!r}")
    return path


def _commit(path: Path, message: str) -> str:
    p = _git(path, "add", "-A")
    if p.returncode != 0:
        raise RuntimeError(f"git add failed in {path}: {p.stderr.strip()}")
    p = _git(
        path,
        "-c", "user.name=shortcut-tally selftest",
        "-c", "user.email=selftest@example.invalid",
        "-c", "commit.gpgsign=false",
        "commit", "-q", "-m", message,
    )
    if p.returncode != 0:
        raise RuntimeError(f"git commit failed in {path}: {p.stderr.strip()}")
    head = _git(path, "rev-parse", "HEAD")
    return head.stdout.strip()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _run(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


def selftest(root: Path) -> int:
    fails = 0
    cases = 0

    def case(name: str, ok: bool, detail: str) -> None:
        nonlocal fails, cases
        cases += 1
        if not ok:
            fails += 1
        print(f"case {name}: {'PASS' if ok else 'FAIL'} {detail}")

    # fixture A: a readable round with a clean battery; also the pass/fail pair
    a = _fixture(root / "a")
    _write(a / SCORECARD, FIX_SCORECARD)
    _write(a / WAVES / "round-10" / "w1" / "spec.json", FIX_SPEC)
    _write(a / WAVES / "round-10" / "w1" / "out" / "M1Ctr.md", FIX_M1CTR)
    _write(a / WAVES / "round-11" / "w1" / "spec.json", FIX_SPEC)
    _write(a / WAVES / "round-11" / "w1" / "out" / "K1Fixture.md", "fixture seat note\n")
    _write(a / WAVES / "round-11" / "w1" / "out" / "K2Cheat.md", "fixture cheat note\n")
    sha_a = _commit(a, "fixture a")

    code, out, err = _run(["--repo", str(a), "--rev", sha_a, "--rounds", "10-11", "--check", "2", "--json"])
    recs = json.loads(out)["records"] if code == 0 else []
    r10 = recs[0] if recs else {}
    ok = (
        code == 0
        and r10.get("status") == "ok"
        and r10.get("shortcuts") == 1
        and r10.get("ids") == ["K1Cheat"]
        and r10.get("counters") == ["C1"]
        and r10.get("mutants") == "1/3"
        and r10.get("falsify") == "yes(w1,folded)"
        # round 11: the frozen family matches no id (K1Fixture is a wide shape);
        # only the K2Cheat report file puts a seat in the gated list
        and recs[1].get("shortcuts") == 1
        and recs[1].get("ids") == ["K2Cheat"]
        and recs[1].get("wide") == ["K1Fixture", "K2Cheat"]
        and recs[1].get("mutants") is None
    )
    case("readable-round", ok, f"exit={code} round10={ {k: r10.get(k) for k in ('shortcuts','ids','counters','mutants','falsify','status')} }")

    # the case that must fail: the same repo one short of its own count
    code, out, err = _run(["--repo", str(a), "--rev", sha_a, "--rounds", "10-11", "--check", "2"])
    code2, out2, err2 = _run(["--repo", str(a), "--rev", sha_a, "--rounds", "10-10", "--check", "0"])
    case(
        "check-fails",
        code2 == 1 and "shortcuts=1 > limit 0" in out2 + err2,
        f"exit={code2} verdict={(out2 + err2).strip().splitlines()[-1] if (out2 + err2).strip() else ''!r} (rounds 10-11 limit 2 exit={code})",
    )

    # committed bytes only: an uncommitted worktree edit must not move the tally
    _write(a / SCORECARD, FIX_SCORECARD.replace("Seat K1Cheat", "Seat V9Cheat and K1Cheat"))
    _write(a / WAVES / "round-10" / "w1" / "out" / "M1Ctr.md", FIX_INCONSISTENT)
    code3, out3, err3 = _run(["--repo", str(a), "--rev", sha_a, "--rounds", "10-11", "--json"])
    recs3 = json.loads(out3)["records"] if code3 == 0 else []
    case(
        "committed-bytes",
        code3 == 0 and recs3 == recs,
        f"exit={code3} identical={'yes' if recs3 == recs else 'no'} worktree_edit=ignored",
    )

    # an unresolvable revision is a usage error, not a silent empty tally
    code4, out4, err4 = _run(["--repo", str(a), "--rev", "no-such-rev", "--rounds", "10-10"])
    case(
        "bad-rev",
        code4 == 2 and "cannot resolve" in out4 + err4,
        f"exit={code4} msg={(out4 + err4).strip().splitlines()[-1] if (out4 + err4).strip() else ''!r}",
    )

    # fixture B: the round heading is gone, so the round cannot certify
    b = _fixture(root / "b")
    _write(b / SCORECARD, FIX_SCORECARD.replace("## Round 12 — third fixture round\n", ""))
    _write(b / WAVES / "round-12" / "w1" / "spec.json", FIX_SPEC)
    sha_b = _commit(b, "fixture b")
    code5, out5, err5 = _run(["--repo", str(b), "--rev", sha_b, "--rounds", "12-12", "--check", "99"])
    case(
        "unreadable-round",
        code5 == 1 and "unreadable rounds [12]" in out5 + err5,
        f"exit={code5} verdict={(out5 + err5).strip().splitlines()[-1] if (out5 + err5).strip() else ''!r}",
    )

    # fixture C: the two round-47 report shapes plus a contradictory one
    c = _fixture(root / "c")
    _write(c / SCORECARD, FIX_SCORECARD)
    _write(c / WAVES / "round-10" / "w1" / "spec.json", FIX_SPEC)
    _write(c / WAVES / "round-10" / "w1" / "out" / "M2Ctr.md", FIX_SPLIT)
    _write(c / WAVES / "round-10" / "w1" / "out" / "M3Ctr.md", FIX_SLASH)
    _write(c / WAVES / "round-10" / "w1" / "out" / "M5Replay.md", FIX_REPLAY)
    sha_c = _commit(c, "fixture c")
    code6, out6, err6 = _run(["--repo", str(c), "--rev", sha_c, "--rounds", "10-10", "--json"])
    r6 = (json.loads(out6)["records"] or [{}])[0] if code6 == 0 else {}
    case(
        "split-slash-uppercase-kill",
        code6 == 0 and r6.get("mutants") == "26/101" and r6.get("status") == "ok",
        f"exit={code6} mutants={r6.get('mutants')} status={r6.get('status')}",
    )

    _write(c / WAVES / "round-10" / "w1" / "out" / "M4Ctr.md", FIX_INCONSISTENT)
    sha_c2 = _commit(c, "fixture c contradictory")
    code7, out7, err7 = _run(["--repo", str(c), "--rev", sha_c2, "--rounds", "10-10", "--check", "99"])
    case(
        "contradictory-report",
        code7 == 1 and "inconsistent killed=5 survived=6" in out7 + err7,
        f"exit={code7} verdict={(out7 + err7).strip().splitlines()[-1] if (out7 + err7).strip() else ''!r}",
    )

    print(f"selftest pass={cases - fails} fail={fails}")
    return 0 if fails == 0 else 1


# --------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Tally shortcut-satisfiable counters, mutant survival and falsify waves per round."
    )
    ap.add_argument("--repo", type=Path, default=Path("."), help="git repository holding the lane (default: .)")
    ap.add_argument("--rev", default="HEAD", help="commit whose bytes are tallied (default: HEAD)")
    ap.add_argument("--rounds", default="40-47", help="round range, e.g. 40-47 (default)")
    ap.add_argument(
        "--check",
        type=int,
        default=None,
        metavar="N",
        help="exit 1 when the latest round's shortcut count is above N or a round is unreadable",
    )
    ap.add_argument("--json", action="store_true", help="print records as JSON")
    ap.add_argument("--selftest", action="store_true", help="build fixtures and prove the checks can fail")
    ap.add_argument("--scratch", type=Path, default=None, help="fixture root for --selftest (default $TMPDIR)")
    args = ap.parse_args(argv)

    if args.selftest:
        base = args.scratch or Path(tempfile.gettempdir())
        base.mkdir(parents=True, exist_ok=True)
        root = Path(tempfile.mkdtemp(prefix="tally-", dir=str(base)))
        try:
            return selftest(root)
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            print(f"selftest FAIL {exc}")
            return 1
        finally:
            shutil.rmtree(root, ignore_errors=True)

    m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", args.rounds)
    if not m:
        return fail(f"could-not-evaluate: --rounds must be A-B, got {args.rounds!r}")
    lo, hi = int(m.group(1)), int(m.group(2))
    if lo > hi:
        return fail(f"could-not-evaluate: --rounds {args.rounds}: empty range")

    try:
        tree = Tree(Path(args.repo), args.rev)
        if not tree.has(SCORECARD):
            return fail(f"could-not-evaluate: no {SCORECARD} at {tree.rev} in {tree.repo}")
        if not tree.isdir(WAVES):
            return fail(f"could-not-evaluate: no {WAVES}/ at {tree.rev} in {tree.repo}")
        lines = tree.read(SCORECARD).splitlines()
    except (RepoError, UnicodeDecodeError, OSError) as exc:
        return fail(f"could-not-evaluate: {exc}")

    blocks, sections = scorecard_blocks(lines)
    records = [tally_round(n, tree, blocks, sections) for n in range(lo, hi + 1)]

    if args.json:
        meta = {"repo": str(tree.repo.resolve()), "rev": tree.rev, "rounds": args.rounds}
        print(json.dumps({"meta": meta, "records": records}, indent=1, sort_keys=True))
    else:
        print(f"repo={tree.repo.resolve()} rev={tree.rev} rounds={args.rounds}")
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
    verdict = (
        f"latest={latest['round']} shortcuts={'-' if latest['shortcuts'] is None else latest['shortcuts']}"
        f" limit={args.check} result={result}" + (f" ({reason})" if reason else "")
    )
    # with --json stdout stays parseable
    print(verdict, file=sys.stderr if args.json else sys.stdout)
    return 1 if reason else 0


def fail(msg: str) -> int:
    print(f"shortcut-tally: {msg}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
