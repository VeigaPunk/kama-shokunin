# Defect 4 — context-capacity wording errata

## Frozen line evidence

Revision: `a23c0e042114016a909eb15173aa6df74b5b7eb0`.

`corpus/knowledge/context-capacity.md:55-56`:

> 55:   the pool is 4096 (`-c 4096`), the served ceiling is 2048, and the only trace
> 56:   is a log warning `n_ctx_seq (4096) > n_ctx_train (2048)`.

`corpus/knowledge/context-capacity.md:137`:

> 137:   `n_tokens = 1025` (`final/raw/L1.server.log` lines 1849-1866): 2 × 1025

Raw-log checks:

- `.ufo/waves/round-25/final/raw/K5.server.log:1083`: `0.00.008.336 W srv    load_model: the slot context (4096) exceeds the training context of the model (2048) - capping`
- `.ufo/waves/round-25/final/raw/L1.server.log:1852`: `0.00.524.972 I slot      release: id  0 | task 2 | stop processing: n_tokens = 1025, truncated = 0`
- `.ufo/waves/round-25/final/raw/L1.server.log:1866`: `0.00.525.056 I slot      release: id  1 | task 3 | stop processing: n_tokens = 1025, truncated = 0`

The 1025 count includes the token that could not be placed; each slot held 1024 cells. Thus 2 × 1024 cells filled the shared 2048-cell pool; 2 × 1025 were not placed cells occupying that pool.

## Errata convention

The entry has no dedicated errata section or convention. A case-insensitive search for `errata` finds only line 42's reference to the external `.ufo/waves/round-25/errata-attempt-2.json`; a search for an errata heading returns no match. Append a new dated errata section at the end of the entry.

## Exact text to append to `corpus/knowledge/context-capacity.md`

```markdown
## Errata — round 26 (2026-10-23)

The following corrections preserve the original round-25 wording and qualify it at its frozen revision (`a23c0e042114016a909eb15173aa6df74b5b7eb0`).

- **Lines 55-56 — additional cap trace.** The `n_ctx_seq (4096) > n_ctx_train (2048)` warning is not the only log trace of the cap. `K5.server.log:1083` also says: `the slot context (4096) exceeds the training context of the model (2048) - capping`.
- **Line 137 — attempted token versus occupied cells.** Each L1 slot held 1024 cells. The logged `n_tokens = 1025` includes the token that could not be placed; the 1024 placed cells in each of two slots filled the 2048-cell pool. The extra counted token per request was not another occupied cell. Both admitted requests failed.
```

## Check performed

Read the frozen entry at the cited lines and read the round-25 raw K5 and L1 logs at the cited lines. This is a proposed append-only correction; the entry was not edited.