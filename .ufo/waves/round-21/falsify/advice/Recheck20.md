VERDICT: confirm - C1 round-20 classification at a661714 reproduces the official raw output exactly; author-time and batch-check changes alter nothing; 0 FP / 0 FN found.

Attacked: C1 `tools/report-landing-audit.py` (at a6617149722c73d90e142fbdc8154d6967055f7e) round-20 verdict vs official run at b76727f31e522763ce24e43d6ec86d21b507a11f.

## Reproduction
- Scratch clone, detached at a661714 (`git rev-parse HEAD` = a661714..., exit 0).
- `python3 tools/report-landing-audit.py --lane-repo <clone> --fleet-repo /home/vgpnk/Projects/shokunin --rounds 20 --no-errata --json` → exit 1.
- Entry byte-equivalent to official `c1-audit-raw.stdout` round 20: cutoff 1792577594, round_commits 9, required 9, post_report [], report_committed true, same 5 defects with same `cited_elsewhere` flags (unresolved-full-hash 0957ce619789d13d894ef21bc863486bcb35b56c; landed-omitted 846e366d…, 92b14625…, 0957ce61…bb57 [cited elsewhere], 33a67778…).
- Tool identity: `git diff --stat b76727f3 a661714 -- tools/ registry/` empty (exit 0) — same instrument as the official run.
- Report identity: fleet blob at first-add commit 04eb5d2d = blob at HEAD = `54b1aff4cb8356db23c57f66a08714c40eb0e82e`; working tree clean vs HEAD (diff --quiet exit 0).

## Hand derivation (git log, author vs committer)
- Cutoff commit: `git log --diff-filter=A -- .ufo/reports/round-20/kama.md` → 04eb5d2d9b4712c5266bdc36fbb16c2fefd7b392, an=ct=1792577594. Exactly one add commit; tool takes oldest (`out[-1]`), correct even under re-add.
- Round-20 set (kama-shokunin, `^round-20:`/`^checkpoint(r20)`): 33a67778 (at 1792566309, ct 1792569678), 0957ce61bb57 (1792571024), 92b14625 (1792573685), 846e366d (1792574702), c7311039 (1792576506), 04de7a87 (1792576704), 9add96e4 (1792576824), 3ec5ea68 (1792576964), 7a6bc911 (at 1792577448, ct 1792577449). All 9 ≤ cutoff on BOTH clocks → required 9 either way; author-vs-committer time changes no r20 classification. Only 33a67778 has at≠ct (jj-style rewrite signature), both values still ≤ cutoff. Last r20 commit precedes the report commit by 146 s → post_report [] honest.
- History-wide subject scan: only these 9 match r20 patterns; the sole `checkpoint(...)` subject ever is checkpoint(r18) 101f3991 (r18 scope). protocol-shokunin's "round-19 verifier spot-check" 37bd4c5b is excluded by both author and subject filter — per declared contract, not a defect.

## Object resolution (batch-check)
- `git cat-file --batch-check` in lane: all 9 round commits present as `commit`; in fleet: all missing (lane-only objects) — matches docstring union semantics.
- Bad token 0957ce619789d13d894ef21bc863486bcb35b56c: `missing` in BOTH repos (exit 0) → unresolved-full-hash is real; report line 7 cites it, line 10 carries the resolving 0957ce619789d13bb5779606078fa1498114d2c7 — exactly the round-20 closure's line-7/line-10 flag.

## FP/FN probes (all negative)
- Token census: `grep -oE '[0-9a-f]{40}'` finds 7 unique tokens; zero hex runs ≥41 chars, so FULL's lookarounds select the same set. All 7 hand-checked against batch-check → exactly 1 unresolvable, reported. No FN.
- Uppercase: 9 `[0-9A-F]{7,}` runs are digit-only fragments inside the lowercase hashes (e.g. `5779606078` in line 10's hash), not skipped tokens.
- Landed section: single `## Landed changes` heading; 5 bullets, all 40-hex; 7–39-hex runs (lines 7/11/25/26/28/32/50/65: `runs/` dir prefixes, `753bfa73…` L0 digest) all lie OUTSIDE Landed → correctly not citation-checked. Omission set = required 9 − 5 landed-cited = the observed 4; none is prefix-matched by any Landed token → no FP; 0957ce61bb57's `cited_elsewhere:true` comes from line 10 (whole-report ABBREV scan, confirmed in source `audit_round`).
- `--no-errata` leaves errata_* empty in both runs; exit 1 consistent with ≥1 uncorrected defect.

## Residual risk / observations (not r20 defects)
- `lookup()` marks a token `found` if ANY repo resolves it, and an ambiguous result is silently overwritten by a later `found` (repo order lane→fleet). Unexercisable at 40 hex (no ambiguity); only reachable via short Landed abbrevs — r20 Landed has none.
- `checkable_abbrev` skips letter-less 7-digit Landed tokens by design (an all-digit abbrev hash would go unchecked); documented tradeoff, not triggered here.
- Classification depends on fleet working-tree report bytes; blob proven identical first-add→HEAD→now, so no drift.

Tooling: no installs/updates (git, python3, grep sufficed). Scratch `/tmp/kama-r21-Recheck20` deleted after evidence copy. Lane untouched (clone read-only; only writes were this report and out/ evidence).
