VERDICT: partial - draft exits match (complete 0, omit-one 1) and errors fail closed, but omission is a mention test: two omissions exit 0.
Attacked: `tools/report-landing-audit.py --report 21=DRAFT` at lane tip a6617149 (tool blob identical to measured b76727f3; sha256 bd671a1e...). Axes: (1) required-draft exits, (2) omission completeness, (3) fail-closed errors, (4) replay of measured outputs.
Method: scratch clone of the lane at a6617149 (removed); `--fleet-repo /home/vgpnk/Projects/shokunin` (fleet HEAD 7fd7c785...; no fleet round-21/kama.md, so draft cutoff = audit time). 46 matrix runs + 4 probe runs; exits in `out/C1DraftDryRun/summary.tsv`, `commands.txt`, `runs/*.exit`, `probes/`.
Round-21 commits (`git log 7a6bc911..master`, all `round-21:`): a6617149, b76727f3, 4e75d9e8, 1471344b, a29bb84a.

## Required drafts
- `drafts/draft-complete.md` (5 full hashes): `/usr/bin/python3 tools/report-landing-audit.py --fleet-repo /home/vgpnk/Projects/shokunin --rounds 10-20 --report 21=.../draft-complete.md` -> exit 0. Round 21: required 5, post 0, defects 0; summary clean, corrected 9, required 47 = 42+5.
- `drafts/draft-omit-one.md` (omits 4e75d9e8): exit 1; round 21 `landed-omitted 4e75d9e85ba4bb26e17fb6a5e48922c349e2a19b`.

## Frontier (observed exit; bold = differs from expectation, [n] = expected)
- omit a6617149, 1471344b or a29bb84a: 1, each names its own commit.
- omit b76727f3, subjects copied verbatim: **0 [1]**. a6617149's subject contains "b76727f3", so the commit counts as cited.
- same omission, a6617149 subject rewritten (control): 1.
- omit a29bb84a bullet, prose "builds on a29bb84a" in Landed: **0 [1]**.
- subjects only, no hashes: 1 (4 omitted; b76727f3 masked as above).
- no Landed heading, or `## Landed Changes`: 1 (section-missing + 5 omitted).
- all five as 7-hex prefixes: 0. a29bb84a as 6-hex: 1. a29bb84a only in Work performed: 1 (cited_elsewhere).
- a29bb84a bullet typo `a29bb84c`: 1 (landed-unresolved + omitted). Fake 40-hex in Work: 1 (unresolved-full-hash).
- probe: a29bb84a listed in UPPERCASE hex: 1, reported omitted (fail-closed false positive).

Forged-date / naming probes (scratch clones; probe commits never left scratch; `probes/forge-probe-commits.txt`):
- past-dated probe 1a1c0492 (2026-10-21T11:00Z), absent from draft: 1, landed-omitted.
- future-dated probe e637332b (2026-10-22T09:00Z): **0**; text `round=21 required=5 post_report=1 defects=0`.
- `Round-21:` capitalised probe: 0, not required (case-sensitive regex).

## Controls
- `--rounds 21` alone: complete 0, omit-one 1.
- `--rounds 10-20`, no draft: 0, corrected 9, required 42, post 4; JSON byte-identical to `runs/b76727f3/c1-audit-ledger.stdout`.
- `--no-errata --json`: 1, 9 defects; byte-identical to `c1-audit-raw.stdout`.
- Explicit committed-ledger copy and the real-lane tool: text identical to the clone run, exit 0. Real-lane tool on omit-b76727f3: exit 0, so the masking reproduces on the lane.
- Control errata row for 4e75d9e8 (`drafts/ledger-plus-r21-control-row.tsv`): omit-one -> 0, corrected 10. Ledger rows are the only guard against a draft omission.
- Missing draft, directory, `21=`: 2. Clone without `--fleet-repo`: 2 (`not a git repository`; default fleet is the tool's parent directory).

## Mechanism (`probes/mechanism.txt`, computed with the tool's own functions)
- Omission = no bounded 7-40 lowercase-hex token anywhere in the Landed section is a prefix of the sha. Any mention counts; `cited_tokens` of omit-b76727f3 include `b76727f3`.
- Post-report = author epoch > cutoff. Author time is set by the author; a future-dated round commit is excluded with no defect (exit 0; `post_report=1` only in text).
- Subject match is `^round-21:` (case-sensitive) and author `kama-shokunin`.

## Assessment against C1
- Holds: complete -> 0; omit -> 1 for 4 of 5 commits; error paths; exact replay of measured outputs.
- Refuted at the "landed-omitted" bar. FN-1: any 7+ hex mention in Landed masks an omission. Likely in the live round-21 report [INFERENCE: round-20 cites commits inline in prose, and a6617149's subject contains b76727f3]. FN-2: author-date exclusion; needs a misdated commit, less likely.
- Low: case-variant subjects are invisible; uppercase hashes are false positives (fail-closed).

## Recommendations (not applied; seat is read-only)
1. Judge each Landed bullet by the leading hash of its own `- ` line; mentions elsewhere do not count (fixes FN-1).
2. Flag round commits with author time after the audit time or the fleet first-add as defects, not post_report (fixes FN-2).
3. Normalise or flag uppercase hashes; match `round-N:` case-insensitively and flag near-misses.

## Not tested
Live round-21 fleet report (not yet written); tool selftest (owned by C1SelftestReview); multi-section Landed; landed-ambiguous.

## Tooling
No installs or updates. Used pre-existing /usr/bin/python3 3.14.8 and git 2.56.0. No pacman, services, llama-server or background jobs. Scratch `/tmp/kama-r21-C1DraftDryRun` removed.
