# Advice — ConfirmM10 (round 29, wave 1)

**Sid:** `SCORECARD.md:P:1c6c1f3e4c:0` · **Verdict:** `confirmed-false` · counter observed `p:absent` — correct.

Independent hand-check (counter not executed):

- W confirmed by blame: `7f84cd0e7662432b7b93e7586f86a40b06e5fdae` (2026-10-23T03:50:35Z, "round-26: …" commit).
- `cat-file -e W:.ufo/reports/round-25/kama.md` → exit 128 (absent). `git log --all --follow` for that path in the lane repo: empty — never existed at any lane revision, so no later lane commit could repair it.
- Lane `.ufo/reports/` at W contains only `round-5/kama.md` — the pointer is lane-plausible in form but unresolvable.
- Intended referent: the **fleet** repo's `/home/vgpnk/Projects/shokunin/.ufo/reports/round-25/kama.md` (tracked, fleet commit `f1a75c9` 2026-10-22T10:19:21Z, 177 lines, unchanged since). Lines 120-129 read exactly "- **quality: unchanged** …" / "- **discernment: unchanged** …" — the substance the SCORECARD sentence cites is true against the fleet artifact.

**Cause for the correction row (≤25 words):** Pointer cites the fleet repo's .ufo/reports/round-25/kama.md; that file exists only in the fleet repo, never in the lane tree.

**Observed value the L1 must paste (exact counter string):** `p:absent`.

Full evidence: `.ufo/waves/round-29/w1/out/ConfirmM10/verdict.json`, `REPORT.md`.
