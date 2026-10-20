VERDICT: confirm — S041 `anchor` and `teaches` were rewritten in place at `ccc4bb3` after that row's first commit `b8e485c`; a pairwise sweep of all nine revisions of `corpus/SOURCES.md` finds no second rule-2 violation.

## Scope and method (read-only)

Commands, all read-only, run in `/home/vgpnk/Projects/shokunin/kama-shokunin`:

- `git log --format=%h -- corpus/SOURCES.md` → nine commits: `1e41928 3285cdf 33f4668 641e1b6 e545ed9 70af36c b8e485c 726f737 ccc4bb3`.
- `git log --merges -- corpus/SOURCES.md` → empty. `git log --all --format=%h -- corpus/SOURCES.md | wc -l` → 9, so every ref carries this one chain.
- `git log --follow --diff-filter=A -- corpus/SOURCES.md` → `1e41928` only: the file was added there, never renamed.
- For each commit, `git show <c>:corpus/SOURCES.md` was parsed into rows keyed by id with 11 cells (`id source kind tier scope anchor teaches status opened recheck used-by`), and every row was compared to the *previous revision in which the id exists* — not to a range base.
- Cross-checks: every row line in every revision has exactly 12 pipes (no cell contains a literal `|`, so no column shifting); per-pair `git diff --numstat` row-line deletions were `5,0,0,2,1,1,0,1` = 10, exactly the 10 replaced row lines found cell-wise. 11 rows were appended, none deleted or renamed, ids `S001`–`S041` contiguous at tip.

Allowed-to-change cells per contract: `.ufo/waves/kaika/SOURCES-CONTRACT-v1.md:49-51` — “Only `status`, `recheck` and `used-by` change in place, and each change / is logged old→new in the round lesson. A correction is a new row whose `teaches` opens / `supersedes S0NN —`.” (path is in the fleet root; read only).

## Findings (by severity)

### F1 — HIGH — the violation: S041 `anchor` + `teaches`, `726f737`→`ccc4bb3`, after first commit `b8e485c`

`corpus/SOURCES.md:53` is the tip row. Old→new, from the cell diff:

- `anchor` old: “receipt `kama-llamacpp-live/v1` 2026-10-20T13:49:38.040Z–13:49:38.170Z, port 32845, 10 checks”
- `anchor` new: “receipt `kama-llamacpp-live/v1` 2026-10-20T14:06:27.859Z–14:06:27.974Z, port 37527, tool sha256 b8c5e8d4…, 10 checks”
- `teaches` old began: “A real llama-server on the pinned build answers `/health` 200, `/v1/models` id = alias …”
- `teaches` new inserts: “answers `/v1/models` 503 with the exact loading envelope while loading, then”

This is not a cosmetic retarget: the teaches cell gained a *new observation*. The cited receipt confirms the new evidence is real, which is what makes the rule matter — the receipts at `b8e485c` and `726f737` record `loading_observed: false`, `loading_503: null`, while the regenerated receipt at `ccc4bb3` records `loading_observed: true`, `loading_envelope_exact: true`, `loading_503.status: 503`. Under rule 2 a newly observed fact takes a new row whose `teaches` opens `supersedes S041 —`; the in-place edit instead destroys the first-committed record (its values survive only in git). [INFERENCE] that the regenerated receipt motivated the edit; supported by the receipt deltas and by `corpus/lessons/round-16.md:147` “S041's anchor and teaches cells were amended before closure because the”.

The edit is disclosed — `corpus/lessons/round-16-verifier-spotcheck.md:184` “S041's anchor and teaches cells were amended after the row's first commit in `b8e485c`” — but disclosure does not restore the append-only property the contract requires.

### F2 — HIGH — no committed command can detect this class; the round-16 validation is green and blind

`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:27-32` lists its checks as E07 status enum, E08 opened date, E09 recheck, E10 tier, E11 used-by path, W01–W03. Nothing reads history, so cell rewriting is outside its power. The round-16 final validation ran on the already-violated tip and passed: `.ufo/waves/round-16/sources-final-validate.txt:3` is `exit=0`. The round-17 frontier item that would cover this, `tools/sources-append-only.py`, does not exist (`ls tools/sources-append-only.py` → “No such file or directory”; `tools/` holds only `kama-llamacpp-live.py`, `kama-ollama-evidence.py`, `kama-probe.sh`, `test-snapshot.sh`). Until it lands, rule 2 is enforced only by author disclosure.

### F3 — MEDIUM-HIGH — a base→tip diff cannot see an add-then-edit, so the round-16 audit method was structurally unable to catch F1

`git diff 20e392e ccc4bb3 -- corpus/SOURCES.md` is 58 additions / 1 deletion, and the single `-` row line is S017's; S041 appears only as a `+` line because it did not exist at `20e392e`. That is why `corpus/lessons/round-16-verifier-spotcheck.md:42` can say “`SOURCES.md` has one in-place change: the S017 `used-by` cell, which the lesson logs” while the same document routes the S041 edit at `:184`. The two statements come from different detectors (net diff vs per-commit); only the pairwise one sees F1. Round-17's acceptance for `sources-append-only.py` must pin the per-commit method, or the identical class passes again under a green base→tip diff.

### F4 — MEDIUM — no in-file old→new record for the S041 cells, and a standing note now contradicts the tip

`corpus/SOURCES.md:129` still reads “Round-16 falsify-wave notes on S035–S041 (2026-10-20; no cell changes).” while line 53 is not the text `b8e485c` committed. The file's own precedent logs the record it now omits — `corpus/SOURCES.md:85` round-14: “Old → new: S012 … → same plus `corpus/knowledge/ollama-evidence-replay.md`”. The old S041 values are gone from the working tree: `grep -rn "13:49:38\|32845" corpus LOG.md tools tests SCORECARD.md` returns nothing.

### F5 — MEDIUM — round-16 lesson self-contradiction on “no earlier-round row changed”

`corpus/lessons/round-16.md:58` logs “Row changes: new S035–S041; S017 used-by” (S017 is an earlier-round row; the change is an allowed `used-by` cell), and `:149` states “No earlier-round row changed.” Read literally the second sentence is false; it is true only as “no earlier-row cell outside the allowed set changed”, which is what this sweep confirms.

### F6 — MEDIUM — the amended teaches rests on a field no check grades (direct bridge to C2)

`corpus/SOURCES.md:53` advertises “10 checks” and asserts the loading envelope. The receipt's `checks` array has exactly 10 entries — `health_ready`, `models_alias_id`, `models_owned_by_llamacpp`, `metrics_not_enabled`, `props_alias`, `probe_model_ok`, `probe_mismatch`, `teardown_exited`, `teardown_port_closed`, `model_unchanged` — none of which is a loading check; `loading_envelope_exact` is a free-standing boolean written at `tools/kama-llamacpp-live.py:922`, and the lesson already records it as ungraded (`corpus/lessons/round-16.md:159-160`). Consequence for calibration: the registry's newest own-work row now carries a fact whose producer cannot fail on it, so a tool emitting `true` unconditionally would leave a false registry claim. C2's repair must grade the envelope and the row must re-cite the graded artifact — as a *new superseding row* per F1, not another in-place edit.

### Checked, no finding

- Anchor `tool sha256 b8c5e8d4…` is accurate: `git show ccc4bb3:tools/kama-llamacpp-live.py | sha256sum` = `b8c5e8d40259…`, and the receipt's own `tool.sha256` is `b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4`.
- S017's allowed `used-by` change (`70af36c`→`b8e485c`) is logged old→new at `corpus/lessons/round-16.md:58-60`, matching the contract's logging clause.
- Appendix prose is append-only across the whole history: `b8e485c`→`726f737` is 23 additions / 0 deletions; the only deleted lines anywhere in the file's history are the 10 registry row lines replaced by the 10 allowed cell rewrites plus F1.

## Complete sweep ledger

All 25 registry events in the file's history. “new row” = pure append; every other line is an in-place replacement.

| pair | row | cells changed | classification |
|---|---|---|---|
| `1e41928`→`3285cdf` | S001 | `used-by` | allowed |
| `1e41928`→`3285cdf` | S010 | `used-by` | allowed |
| `1e41928`→`3285cdf` | S011 | `status` (`queued`→`mined`), `used-by` | allowed |
| `1e41928`→`3285cdf` | S012 | `status` (`queued`→`mined`), `used-by` | allowed |
| `1e41928`→`3285cdf` | S016 | `status` (`queued`→`mined`), `used-by` | allowed |
| `1e41928`→`3285cdf` | S031 | new row | append |
| `3285cdf`→`33f4668` | S032 | new row | append |
| `33f4668`→`641e1b6` | S033 | new row | append |
| `641e1b6`→`e545ed9` | S012 | `used-by` (+`ollama-evidence-replay.md`) | allowed |
| `641e1b6`→`e545ed9` | S031 | `used-by` (+`ollama-evidence-replay.md`) | allowed |
| `e545ed9`→`70af36c` | S012 | `used-by` (+`lessons/round-15.md`) | allowed |
| `e545ed9`→`70af36c` | S034 | new row | append |
| `70af36c`→`b8e485c` | S017 | `used-by` (+`llamacpp-loading-lifecycle.md`) | allowed |
| `70af36c`→`b8e485c` | S035–S041 | seven new rows | append |
| `b8e485c`→`726f737` | — | appendix notes only (23+/0−) | append |
| `726f737`→`ccc4bb3` | **S041** | **`anchor`, `teaches`** | **VIOLATION (F1)** |

No other cell changed anywhere: `kind`, `tier`, `scope`, `opened`, and every `source` cell are byte-identical to each row's first commit, including every `opened` date (so the round-11 note at `corpus/SOURCES.md:67` that `opened` keeps the round-10 date is accurate).

## Controls this history supplies for `tools/sources-append-only.py`

- Positive control (must fail): `b8e485c`→`ccc4bb3`, row S041, two non-allowed cells.
- Negative controls (must pass): the eight allowed-cell replacements listed above; the eleven appends; the `b8e485c`→`726f737` appendix-only commit.
- Adversarial control: a value rewritten and then restored between two commits is still two in-place writes — with per-commit comparison it is visible at the middle commit, with base→tip it is invisible (F3). Pin the per-commit semantics in the tool and in its selftest.

## Residual risk and verification gaps

- History examined is the lane's linear chain of nine commits; there are no merges and no divergent ref (`git log --all` count equals the branch count). A history rewrite (rebase/jj operation) would change every pair and is outside this sweep's power; [INFERENCE] the lane's jj migration makes a one-off snapshot of the current chain the right pinning artifact for the new tool.
- Only `corpus/SOURCES.md` was swept; other corpus files' history was not in scope.
- I did not run any lane gate, `measure.py`, `mutants.py`, `controls.py`, or the probe, and bound no port; S041's live content was not re-verified against a server this round.
- Cell comparison is exact-string, so a whitespace-only edit would be reported as a change; none occurred.
- The “why” of the S041 edit is read from the lesson and receipt delta; the motivating decision itself is [INFERENCE].

## Installs

None. No tool installed, upgraded or started; no service action; no files written except this report.
