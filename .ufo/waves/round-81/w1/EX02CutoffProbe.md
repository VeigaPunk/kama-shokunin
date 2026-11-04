# EX02CutoffProbe — seat report (kama r81 w1)

Judged on: operability (C2 premise). Verdict of the probe: **PROVEN** — the frozen acceptance rule is
unsatisfiable for post-introduction events, and the disclosure ledger cannot bless them either.

## What was done
Two scratch clones of the lane (`git clone --shared`), each pinned at the frozen base
`e7d2fd729cf8204c89c32534303bc9f2a97fcee4` (lane master has since moved to `f6cb5303171cc…` on L1 helper
commits; base verified ancestral). `git rev-parse --show-toplevel` == the clone dir was verified before
every fixture mutation. All fixture commits live only in the scratch clones, deleted after receipts were
copied. No production file was written; no lane git write was run.

## Executable results
1. Baseline `python3 tools/round75-append-accepted.py --repo <clone>` (frozen base) → exit 1,
   `APPEND_ACCEPTED events=63 accepted=53 unaccepted=10 bad_rows=0 bad_declarations=0` — matches C2's
   frozen "before" line.
2. Appended one syntactically perfect row for event `4af44f78303f04a6ea32ea62cac586f89688d73a` /
   `corpus/lessons/round-79.md` (line `d217400656a…03785`, count=1, class `in-place-edit`, note with
   commit subject + "; " reason) to `registry/append-only-accepted.tsv`; committed in the fixture as
   `0bdb22d913c257e7212bcc380b34a02a752cb698` ("fixture: accept"). Re-run → exit 1,
   `APPEND_ACCEPTED events=63 accepted=53 unaccepted=10 bad_rows=1 bad_declarations=0` with verbatim:
   `APPEND_ACCEPTED_FINDING post-introduction line 391: 4af44f78303f04a6ea32ea62cac586f89688d73a corpus/lessons/round-79.md d217400656a81df399157a05ec6d167fe28fc9c8cd5cb11ea6af239d12703785: commit is not an ancestor of the register's introduction commit`
   Every non-temporal check (hash, count, class, note shape, event key) passed; only the introduction
   cutoff fired. `accepted` stays 53 — the rule cannot move it.
3. Same six-cell row appended to `registry/append-only-disclosures.tsv` in the second fixture
   (`00aeb4ae548825c2af9acf98168d9af386b6d369`, "fixture: disclose"); frozen audit → exit 1,
   `bad_disclosures=1`, verdict: `names a commit at or after the ledger's introduction b6bed925b032: restore by append`.
4. Register introduction `10f37171fb696c542586cbee96ea4a509ab74afc` (round-75, 2026-11-04T02:25:29-03:00,
   sole `--diff-filter=A` hit for the path); ledger introduction
   `b6bed925b032ac2c19b63ef4af358ebdd5922c26` (round-51). All nine distinct commits of the ten
   unaccepted (commit,file) events are strict descendants of both introductions
   (`merge-base --is-ancestor <intro> <event>` rc=0 ×18) and ancestors of neither register intro
   (converse rc=1 ×9 — the exact call `precedes()` makes).

## Mechanism (frozen base bytes)
- `tools/round75-append-accepted.py`: grade() docstring L69-72 (temporal cutoff rationale);
  L124-127 the `bad("post-introduction", …)`; L235-241 `intro = commits[-1]` of
  `git log --diff-filter=A --format=%H -- registry/append-only-accepted.tsv`; L244-250
  `precedes = commit != intro and merge-base --is-ancestor <commit> <intro> == 0`; selftest L170-172
  (observed `--selftest` exit 0: `post-introduction PASS exit=1 expected=1`).
- `tools/append-only-audit.py`: docstring L21-26 ("a ledger read from <to> may only disclose commits
  that precede its own introduction"); L569-575 `since` = first commit adding the ledger;
  L580-583 the at/after-since bad-row rule; selftest `t_v6_ledger_cutoff` L1385-1399.

## Files
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/EX02CutoffProbe/EX02.md` (≤40 lines)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/EX02CutoffProbe/EX02.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/EX02CutoffProbe/receipts/`
  (01-baseline.out/.err/.exit; 02-appended-row/fixture-commit/fixture-head; 03-after-row.out/.err/.exit;
  04-disclosure-row/fixture-commit/fixture-head; 05-audit-after-disclosure.json/.err/.exit;
  06-introduction-and-descendants.txt; 07-selftest.out/.exit; 08-converse-direction.txt)

## Risks / notes
- The fixture pins the base by a detached checkout **inside the scratch clone only** (lane untouched);
  recorded here because the hard VCS ban targets the lane and this is the item-mandated fixture flow.
- Receipts name scratch paths that are deleted on exit; contents are preserved verbatim in the seat dir.
- No tools installed or upgraded (none needed).
- Consequence for C2: the 53/10 split at the base is structural, not a data gap — `accepted` cannot
  exceed 53 under the frozen register, so the late register + re-pointed gate arm 8 is the only
  accepting path, exactly as the frozen plan states.
