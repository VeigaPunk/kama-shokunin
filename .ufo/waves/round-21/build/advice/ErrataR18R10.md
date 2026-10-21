VERDICT: confirm - all four landed-omitted rows match git and report facts; r10 4066035 is a fair defect, not a false positive (minor); r18 rows fair, 101f3991 arguable

# ErrataR18R10: landed-omitted rows (r10 4066035; r18 101f3991, 1c325b2, c6dc46f)

Seat KamaR21.ErrataR18R10-6 (leaf, no dispatch). Draft a29bb84 = lane master (`rev-list --count a29bb84..master` = 0, exit 0). Fleet reports at first-add commits: r10 b69b7ba2, r18 23bdc3f8; working-tree bytes equal them (`diff --stat`, exit 0, empty). Scratch clone deleted (`rm -rf`, exit 0). No lane, fleet, ledger or MANIFEST writes.

## 1. Row facts (executed)

| Row | Sha is commit | Subject / author | Ancestor of a29bb84 | Committer time; gap before fleet add | Cited (report lines) | In Landed |
|---|---|---|---|---|---|---|
| r18 101f3991d3570bc9… | yes | `checkpoint(r18): … unadmitted` / kama-shokunin | yes | 2026-10-20 20:36:34 -03; 21758 s | 19 | no |
| r18 1c325b2e58fc… | yes | `round-18: retain measured arms…` / kama-shokunin | yes | 2026-10-20 20:13:58 -03; 23114 s | 27 | no |
| r18 c6dc46fabc51… | yes | `round-18: classify missing observations…` / kama-shokunin | yes | 2026-10-20 19:33:49 -03 (author 16:41:43); 25523 s | 26 | no |
| r10 40660352d4a9… | yes | `round-10: post-review fixes` / kama-shokunin | yes | 2026-10-19 19:47:40 -03; **75 s** | 114, 120 | no |

All four are on master and in the audit's required set (r18 required 7 = 4 Landed + 3 flagged; r10 required 2 = 1e41928 + 4066035). Errata tokens equal the full shas; errata line refs match (r18 19; 26-27; 26; r10 114). The errata evidence omits r10 line 120, a second citation; not an error.

## 2. r10 4066035: fair defect, not a false positive (severity low) [INFERENCE on severity]

1. The rule was in force at r10: `kama-round-10.md:68-69` reads "**Landed changes** — every change tied to a LOG.md entry and to the commit hash that carries it." Prompt bytes equal its last commit 5b471e4d (2026-10-19 18:23:55 -03, before 1e41928 at 19:34; `diff --stat`, exit 0). Identical at kama-round-18.md:107-108 and kama-round-21.md:107-108.
2. The commit carries changes (numstat, 0 deletions): `.ufo/round-10/audit/validate-new-pointers.sh` +44, `LOG.md` +5, `SCORECARD.md` +17, `corpus/lessons/round-10.md` +15.
3. The report is internally inconsistent: Landed line 30 says "All changes are in lane commit `1e41928`", while lines 112-120 document 4066035, committed 75 s before the landing commit.
4. The lane treats 4066035 as the landed state: `corpus/lessons/round-10-verifier-spotcheck.md:5` says "after the round landed at `40660352d`" (ancestor of a29bb84, exit 0).
5. No report-side LOG tie: LOG.md:525 "## round 10 — post-review fixes (2026-10-19)" exists, but no LOG line carries the hash and the report never cites that entry.
6. The tool counts this by design: docstring 15-19; selftest `checkpoint-omission-detected` (lines 297, 309) requires a commit cited only outside Landed to be flagged. `cited_elsewhere` is informational. The same standard already stands for the r20 row 0957ce61.
- Not caught by the audit: the corrected C1 measurement ("Output at `4066035`", line 120) is missing from the Before→after table, which still reads "After (`1e41928`)" and "uncorrected 0" (lines 42, 44). Contract §4 requires the measured commit.
- Design residual: the rule uses committer time. A post-review commit landing after the report is `post_report` and exempt (docstring 22-24). This one is cited by the report, so the flag stands.

## 3. r18 rows: fair; weight differs

- c6dc46f, material: LOG.md:1086 calls it "Landed implementation `c6dc46fabc…`". Numstat: `tools/kama-llamacpp-live.py` +487/-316, `tests/llamacpp-live/check-receipt.py` +768/-56, `tests/llamacpp-live/controls.py` +1550/-368; adds `c1/measure.py` and `c2/survivors.py`.
- 1c325b2, material evidence: adds `live/receipt-{1,2,3}.json` (612 lines each), which report line 27 reuses; modifies `c1/measure.py` (96/21) and `c2/survivors.py` (18/8).
- 101f3991, weakest: subject says "unadmitted"; report line 19 and LOG.md:1105-1106 treat it as the attempt-1 checkpoint. Numstat shows 66 falsify advice files, the set the report's disposition uses. The rule names `checkpoint(rN)` deliberately (docstring 15-16), so it is fair by rule. Whether an unadmitted checkpoint is a "landed change" is a contract question [INFERENCE].

## 4. Commands run (exit)

- `git clone` + `checkout -q a29bb84`; `rev-parse HEAD` → 0 (a29bb84). `git log -- .ufo/reports/round-{10,18}/kama.md` (fleet) → 0, one commit each.
- For the four shas: `cat-file -t`, `log -1`, `merge-base --is-ancestor <sha> a29bb84`, `branch -a --contains`, `show --numstat` → 0 each. `git log --all -E --grep=…` → 0.
- `python3 tools/report-landing-audit.py --no-errata --fleet-repo /home/vgpnk/Projects/shokunin --rounds 10,18 --json` → 1 (4 defects, all `cited_elsewhere: true`, `post_report: []`).
- Same with `--rounds 10-20` → 1 (9 defects: r10 1, r18 3, r20 5); with ledger → 0 (9 corrected). `--selftest` → 0 (15/15).
- Fleet `git diff --stat` (report vs first-add; prompt vs 5b471e4d) → 0, empty; `git log -1 -- .ufo/prompts/kama-round-{10,18,21}.md` → 0. Eval (py) recount of citations against the Landed span completed without error. `_grep` cross-checks agree (tool; no exit code).

## 5. Citations elsewhere, gaps, installs

- Elsewhere: 101f3991 → LOG.md:1106, corpus/lessons/round-18.md:264; 1c325b2 → LOG.md:1106, corpus/SOURCES.md:225-226; c6dc46f → LOG.md:1086,1106, SCORECARD.md:790; 4066035 → corpus/lessons/round-10-verifier-spotcheck.md:5,17 (not LOG).
- Not checked: report figures (out of scope); the live lane beyond a29bb84 (scratch master was a29bb84 at clone time).
- Installs: none (git, python3 stdlib). Deliverable: `build/out/ErrataR18R10/rows-check.md`.
