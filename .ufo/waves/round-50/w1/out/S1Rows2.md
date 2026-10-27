# S1Rows2 — sources rows S496, S497, S498 re-opened against their sources

**Verdict: S496 admits unchanged (no cell wrong); S497 carries one wrong cell and S498 two — both `teaches` quotes are not present verbatim in the page, S497's is also 28 words, and S498's `anchor` lost a verified full-page sha256 in the post-build fix `3d42897b`, a loss that the row parser did not force. Replacement rows are proposed, gate-clean (exit 0) and parseable by the append-only guard.**

Detail: `.ufo/waves/round-50/w1/out/S1Rows2/rows.md` (per-cell audit, findings with commands, full replacement rows, lesson Gate draft, receipts index).

## What was done

Read at lane HEAD `3b79eaddf38246c637cc7ba1a94ab363422876b6` (build `97c864be…`, freeze `601c8889…`): `corpus/SOURCES.md:249/250/251`. Re-fetched all three URLs and matched them to the three text copies, hashed everything, then graded every cell of every row. Ran the seat's gate (`scripts/sources-census.sh validate`) on a `git clone --shared` in scratch, with and without a placeholder for the integration lesson, and ran `tools/sources-append-only.py` at the build blob, at HEAD, and on three fixture variants of the proposed rows (each fixture a fresh `git init -q`, `rev-parse --show-toplevel` asserted, commits made with `-C` and a scoped identity, only `corpus/SOURCES.md` ever written).

Not done, deliberately: the two round-50 counters were not run (this seat's judgement is about the source rows, not the measurement); no server was started; no installer ran, so there is no tool/version record to report.

## Gates

| gate | command | outcome |
|---|---|---|
| census, registry as committed | `sources-census.sh validate --file <clone>/corpus/SOURCES.md` | exit 1 — `93 W04, 3 E11, 1 W01`; the three E11 are S496/S497/S498 → `corpus/lessons/round-50.md` (the known integration item) |
| census, placeholder lesson present | same | exit 0 — `file ok`, `93 W04, 1 W01`; nothing else is hidden behind the E11 |
| census, proposed rows C (primary) | same, registry replaced | exit 0 — **0 E-codes** |
| census, proposed rows B (fallback) | same | exit 0 — **0 E-codes** |
| append-only, build → fix | `sources-append-only.py --from 97c864be --to 3d42897b` | **exit 2** — `97c864be…:corpus/SOURCES.md:251: unterminated table row (no closing pipe)` |
| append-only, fix → HEAD | `--from 3d42897b --to 3b79eadd` | exit 0 — `no append-only violations` |
| append-only, proposals | fixture `base→C` / `base→D` / `base→E` | exit 1 (immutable-cell diffs, no parse error) / **exit 2** at `:251` / exit 1 (anchor only) |
| live provenance | `curl` the three URLs, `sha256sum` | 200/11702, 200/10684, 200/514698; spec page = `c85f56cc…`, exactly the full-page hash the c2 copy records |

## Findings

1. **S497 `teaches` — quote over the cap and not verbatim** (`corpus/SOURCES.md:250`). The cell quotes `… each subreaper process ... to which the caller is subsequently reparented.`; the page has `(see PR_SET_CHILD_SUBREAPER(2const))` at `.ufo/waves/round-50/c1/PR_SET_PDEATHSIG.2const.txt:89`, so the string is absent, and the quote is 28 words against the 25-word cap. Shown by `python3 …/check-quotes.out` (`28 False`). Fix: the two verbatim sentences at copy:87-90 (20 words) and copy:100-101 (12 words).
2. **S498 `teaches` and `anchor` regressed by `3d42897b`** (`corpus/SOURCES.md:251`). That commit replaced `"… backtick characters (`) or tildes (~)."` with `"… backtick characters or tildes."` — not in §4.5 — and dropped `; full page sha256 c85f56cc…` from the anchor. `git show 3d42897b -- corpus/SOURCES.md` prints both cells; the dropped hash re-fetches byte-identically today.
3. **The guard could not grade the commit that made that edit, and the sha256 loss was not forced.** At the build the row is unparseable (exit 2 at `:251`) because one raw backtick inverts `split_cells`' code-span state, so `3d42897b`'s immutable-cell rewrite was never compared. Fixtures: restoring the raw glyph is exit 2 (forced), restoring the sha256 on the HEAD row is exit 1 with only that cell changed (**not** forced), and the entity form keeps both the quote and the sha256 at even parity.
4. **S498 `scope` omits two §4.5 clauses the counter enforces** — the backtick info-string restriction (copy:12-14) checked by `tools/append-only-audit.py:282-292`, and `(Tildes and backticks cannot be mixed.)` (copy:7). The behaviour rests on unregistered text.
5. **`used-by` omits the three tools and names a knowledge file with no round-50 content.** `tools/kama-llamacpp-live.py:681`, `tools/kama-live-replay.py:102` and `tools/append-only-audit.py:8` cite the sources by name; the precedent (`S089`, `S091`, `S096`, `S100`–`S102`) lists `tools/` in `used-by`. `corpus/knowledge/llamacpp-loading-lifecycle.md` has no S496/S497 content at HEAD (`grep` empty) while its round-49 paragraph cites S494/S495 — so this is a **new integration item**, not the known lesson one.
6. *Observation:* S497's scope omits the other clearing cases (set-uid/`capabilities` exec, credential changes, copy:101-105); nothing in the build trips it, so it is a boundary note, not a wrong cell.
7. *Observations:* the two c1 copies carry no in-file fetch record (URL/time/hash) unlike the c2 copy; `proc_pid_maps(5)`'s ` (deleted)`, blank-pathname and newline caveats bound the model-mapping inference (the tool fails closed on them).

## Two `teaches` cells the round's own lesson should not reproduce

The Gate draft in `rows.md` §8 lists all three as admits with the corrected quotes and adds three rejects this evidence supports: the tick-stripped quote form, a `... `-elided 28-word span, and "the sha256 had to go for the row parser" (disproved).

## Touched surfaces

- Wrote only `kama-shokunin/.ufo/waves/round-50/w1/out/S1Rows2.md` and `.ufo/waves/round-50/w1/out/S1Rows2/` (report artefacts, receipts, proposed registries built from the lane's copy).
- The lane, the fleet repo and `shokuknow` were read-only throughout; no jj/git mutation in the lane, no write at the fleet root, no service or installer touched. Fixture commits live only in scratch repos that were deleted after their output was copied.

## Out of scope / not claimed

- No statement about C1 or C2 passing: the counters were not run here.
- Landing the rows is the L1's call: `SOURCES-CONTRACT-v1` rule 2 freezes the seven immutable cells, so `rows.md` §6 gives both append-only-clean routes (an errata section, as round-21 did, or new superseding rows, as `S040`/`S047`/`S056` did) and recommends one.
- S496 needs no cell change; the anchor sha256 for the two man pages is offered as optional hardening (§7), not as a defect.

## Artefacts

- `.ufo/waves/round-50/w1/out/S1Rows2.md` — this report
- `.ufo/waves/round-50/w1/out/S1Rows2/rows.md` — cell audit, findings, proposed rows, Gate draft
- `.ufo/waves/round-50/w1/out/S1Rows2/receipt-notes.txt` — every command, exit code and scratch path
- `.ufo/waves/round-50/w1/out/S1Rows2/` + `validate-head.out`, `validate-head-with-placeholder.out`, `validate-proposed-C.out`, `validate-proposed-B.out`, `sources-append-only-at-build.out`, `sources-append-only-head.out`, `append-only-proposed-C.out`, `append-only-D-raw-glyph.out`, `append-only-E-sha-restored.out`, `fetch-hashes.out`, `check-quotes.out`, `check-candidates.out`, `proposed-A.md`, `proposed-B.md`, `proposed-C.md`, `proposed-D-raw-glyph.md`, `proposed-E-head-plus-sha.md`
