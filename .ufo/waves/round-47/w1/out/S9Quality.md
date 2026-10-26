# S9Quality — round 47, lane kama: QUALITY.md criteria KQ69 onwards

**Verdict: KQ69–KQ71 are drafted, grounded and append-ready (highest existing is KQ68 at `corpus/QUALITY.md:388`); drafting them exposed two live documentation defects on the lane — `corpus/README.md:759-761` still declares a five-file append-only set against the contract's 85 audited paths, and `corpus/knowledge/consumer-registry.md:30` declares its own section append-only with no contract row — and I changed nothing in the lane, the counters, the preregistration or the controls.**

Axes: calibration (a criterion that makes the round detect the class the C1 preregistration's `limits` cell admits it cannot detect; a deletion-counter line model pinned to `git diff --numstat`) and operability (provenance that a fresh session can act on rather than a host path plus a digest).

## Delivered

- `.ufo/waves/round-47/w1/out/S9Quality/criteria.md` — the append-ready block: placement (append after line 390, end of file), what each row adds and leaves alone, the three rows KQ69/KQ70/KQ71, each citing `corpus/lessons/round-47.md` by section, and an evidence table with the commands behind every asserted fact.
- `.ufo/waves/round-47/w1/out/S9Quality/heading-census.py` — a 57-line read-only survey the KQ71 row cites as its uncovered-declaration check.
- Receipts beside them: `append-only-audit-v2-at-3a09a1d9.{out,json}`, `numstat-0718b6ab.out`, `heading-census-3a09a1d9.out`, `receipt-1-provenance.out`.

## Placement and numbering (checked, not assumed)

```
$ grep -n "^| KQ" corpus/QUALITY.md | tail -3       # 386 KQ66, 387 KQ67, 388 KQ68; footer at 390
$ git -C <clone> rev-parse 3a09a1d9:corpus/QUALITY.md 46a924e0:corpus/QUALITY.md
1d613cebbf5aae0a9302be90333f1d96efa42cbf
1d613cebbf5aae0a9302be90333f1d96efa42cbf
$ git -C <clone> diff --stat 3a09a1d9 46a924e0 -- corpus/QUALITY.md      # no output
$ git -C <clone> show 46a924e0:corpus/QUALITY.md | wc -l
390
```

`corpus/QUALITY.md` is the same 390-line blob at the freeze base, at the build and at the wave tip, so the block appends after line 390 and no existing line moves (KQ7, KQ14).

## Evidence

All lane runs are read-only; every tool run against a revision used a `git clone --shared` in my own scratch (`/fast/scratch/hyaku/kama-r47/S9Quality/lane`, `rev-parse --show-toplevel` = that directory, HEAD `46a924e0`).

| # | command | output | exit |
|---|---|---|---|
| 1 | `python3 tools/append-only-audit.py --repo <clone> --to 3a09a1d9 --contract registry/append-only-contract.tsv` | `deleted=2292 LOG.md restored`, `deleted=2421 SCORECARD.md restored_max=2420 partial`, `deleted=375 corpus/QUALITY.md restored`, `deleted=663 corpus/README.md restored`, `deleted=31 SCORECARD.md (dd9f5dc6) restored_max=24 partial`; `summary commits=303 files=85 events=5 restored=3 partial=2 unrestored=0` | 1 |
| 2 | same with `--json` | `"schema": "append-only-audit/v2"`, `files` = 85 = `LOG.md`, `SCORECARD.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md`, `registry/history/DELTA.md` + 79 `corpus/lessons/*.md` | 1 |
| 3 | `git -C <clone> diff --numstat --no-renames 0718b6ab^ 0718b6ab -- SCORECARD.md LOG.md corpus/QUALITY.md corpus/README.md` | `9 2421 SCORECARD.md`, `5 2292 LOG.md`, `4 375 corpus/QUALITY.md`, `2 663 corpus/README.md` — equal to run 1's `deleted` on all four | 0 |
| 4 | `python3 -c "…receipt-1.json…"` | `kama-llamacpp-live/v4`; `provenance.server` = b11909 asset URL + sha256 + member `llama-b11909/llama-server`; `provenance.model` = huggingface `models-moved` URL + sha256; `teardown.log_path` `None` | 0 |
| 5 | `tools/kama-live-replay.py:89-94` (`acquire`) precedes `:98` (`extract`), refusal at `:167-170` | digest compared by `sha256_file` before extraction, mismatch → `digest-mismatch:` + exit 2 | — |
| 6 | `cat .ufo/waves/round-47/controls/junk-c2-r46-relabel.c2.out` | `receipts=0 replay=0 tamper=0 newrow=0 rerun_checks=11 met=False`; `replay: rerun inputs not re-acquired under scratch: '/home/vgpnk/.local/opt/llama-b11906/llama-server' …`; `tamper-model: exit 0, rerun outcome pass: not refused` | 1 |
| 7 | `cat .ufo/waves/round-47/controls/junk-c1-v1-numstat.c1.out` | `lane=0 fixture=0`; `lane missing (…'SCORECARD.md', 2421, 2420, …)` vs `lane unexpected (…, 2421, 2413, …)` | 1 |
| 8 | `python3 heading-census.py --repo <clone> --head 3a09a1d9` | `headings=13 covered=11 uncovered=2` (`SKILL.md:1434`, `corpus/knowledge/consumer-registry.md:30`) | 0 |
| 9 | `sed -n '<declared_at line>p'` for the seven contract rows | every line declares the rule: `README.md:16`, `corpus/README.md:521`, `corpus/QUALITY.md:24`, `corpus/README.md:86`, `SKILL.md:578`, `corpus/lessons/round-23.md:100`, `registry/history/DELTA.md:3` | 0 |

The KQ70 row rests on runs 1–3 and control 7 (D1: 2417 vs 2421, 2290 vs 2292, and the tip-relative restoration 2416→2409 recorded as closure D2 at `corpus/lessons/round-46-verifier-spotcheck.md:140`). The KQ69 row rests on runs 4–6 and closure D5 (`:141`), plus round-46 lesson `## Mistakes` rows 1 and 3 (`corpus/lessons/round-46.md:35,37`). The KQ71 row rests on runs 2, 8, 9 and round-46 lesson row 4 (`:38`).

## Findings

**F1 — stale append-only declaration (lane documentation, not frozen).** `corpus/README.md:759-761` says "`tools/append-only-audit.py` … sets **the five files** the lane treats as append-only (SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md)". At `3a09a1d9` the declaration of record, `registry/append-only-contract.tsv:2-8`, declares seven patterns expanding to 85 paths (run 2), including `corpus/lessons/*.md` and `registry/history/DELTA.md`. Shown by:

```
$ sed -n '759,761p' corpus/README.md
$ python3 tools/append-only-audit.py --repo <clone> --to 3a09a1d9 --contract registry/append-only-contract.tsv --json | python3 -c "import json,sys;d=json.load(sys.stdin);print(len(d['files']))"
85
```

Proposed fix (README is `A-corr`: append, never rewrite): append a correction paragraph under the round-47 section naming the contract as the declaration, its seven rows and the 85-path expansion, and marking lines 759-761 as the round-46 five-file state.

**F2 — a file that declares itself append-only with no contract row (lane documentation).** `corpus/knowledge/consumer-registry.md:30` is the heading `## Errata — 2026-10-14 re-census (append-only; rows below keep their round-1 text)`; no row in `registry/append-only-contract.tsv` matches `corpus/knowledge/consumer-registry.md` (run 8 flags it, run 2's `files` does not contain it). Under KQ71 that section is not append-only evidence until a row exists. This is exactly the class the C1 preregistration's own `limits` cell discloses as undetected by the counter ("a lane file declared append-only but missing from the contract is not detected by the counter (attacked by wave seats)").

Proposed fix, in this order of preference for round 47: append a correction to `corpus/knowledge/consumer-registry.md` stating the section is a dated record kept by convention and is not audited as append-only. Do **not** add a contract row after data: a row changes C1's `files` (85) and can add events, i.e. it moves a frozen claim's measured values — that belongs to a round-48 build with its own counter run.

**F3 — the KQ71 heading rule has one false positive, disclosed, not fixed in place.** `SKILL.md:1434` is `## Round-46 instrument registry (freshness re-verification, append-only calibration)` — a topic label, not a claim on the file. `heading-census.py` reports it because the rule is a candidate generator; the KQ71 row requires each flagged heading be dispositioned rather than counted as a defect. Skip-listing `SKILL.md` in the tool would hide a real future self-declaration there, so the survey keeps flagging it.

## Limits (what I did not observe)

- **`corpus/lessons/round-47.md` does not exist at this wave** (`ls corpus/lessons/round-47.md` → `No such file or directory`; newest is `round-46.md`). The three rows cite it by section (`## Claims` bullets C1/C2, `## Gate`, and the C1 `limits` cell) as a forward reference to the lesson the L1 files after the wave; the L1 must confirm the anchors resolve once it is written. Every secondary anchor in the rows (closure D1/D2/D5, round-46 lesson rows 1/3/4/6) exists today at the lines cited.
- I did **not** run `tools/round47-append-audit-v2-check.py` or `tools/round47-live-replay-audit.py`, so I do not claim their legs. The `lane=1 fixture=1 stable=1` and `receipts=1 replay=1 tamper=1` values quoted in the rows are the counter contracts plus the L1's pre-wave dry run, marked as such; what I observed myself is runs 1–9 and the two control receipts.
- KQ69's "refuses a receipt whose digest is wrong" is evidenced by the tool's code path (run 5) and the relabel control (run 6, where the *round-46* receipts are not refused because they carry no provenance and the replay fell back to host paths); the b11909 tamper refusal itself is a C2 leg I did not execute.
- KQ71's declaration census covers headings only. A prose sentence that calls another file append-only without a row is not enumerated by the tool; the row asks the round to report such sentences, and this report's own F1 is an instance found by hand.

## Gates and hygiene

- Lane untouched: no `git add/commit/checkout/stash/reset`, no `jj` mutation, no writes inside `kama-shokunin` except my two report/out paths. `git` on the lane was read-only (`rev-parse`, `show`, `diff --numstat`, `log`).
- Fixture discipline: the only repository I created was the `--shared` clone at `/fast/scratch/hyaku/kama-r47/S9Quality/lane`; no fixture commits were made anywhere; `git -C <clone> rev-parse --show-toplevel` printed that directory before use.
- `TMPDIR=/fast/scratch/hyaku/kama-r47/S9Quality` for every run; the scratch tree was removed after the receipts were copied out (`rm -rf /fast/scratch/hyaku/kama-r47/S9Quality`), and no `/tmp` path is cited as evidence.
- No tools installed or upgraded, so no install record: `pacman` untouched (host-wide pause), and the runs used `python3` + `git` already on the host.
- No services started; no llama-server run in this seat; no subagents; no `agent://all`.

## Artifacts

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Quality.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Quality/criteria.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Quality/heading-census.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Quality/append-only-audit-v2-at-3a09a1d9.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Quality/append-only-audit-v2-at-3a09a1d9.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Quality/numstat-0718b6ab.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Quality/heading-census-3a09a1d9.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/S9Quality/receipt-1-provenance.out`
