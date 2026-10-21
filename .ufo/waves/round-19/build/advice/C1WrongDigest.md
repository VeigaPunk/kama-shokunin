VERDICT: partial - a one-nibble digest flip is classified `mismatch` (never `missing`) with the observed digest printed on all four flip variants; three residual gaps remain: text output truncates digests to 12 hex, stale-token digests and documents are never printed, and no selftest case exercises the observed-digest branch (a mutant that removes it passes selftest and false-passes the flipped fixture with exit 0). A patch on the same tool closes all three.

# C1WrongDigest advice, round 19 (citation provenance)

**Evaluated state (sha256 at sync):** `tools/citation-provenance.py` `d442262d7879cbfbd57a06bfce8d5d04ed371ffb897adc371fb50fddf6e5616c`; `registry/required-citations.json` `f913b66fc5c8c24f34f529d657e5383987daea5d6696ab9072823aa13a0cb245`; `corpus/lessons/round-18.md` `a36c60f0b9b461448a816fe9d71037be726c33cefded344c061d4fa9e12226f1`. Lane HEAD = `origin/master` = `f1790e25b421f02596798ad665488b066541ae3a`. Work copy: `/tmp/kama-r19-C1WrongDigest`. Receipt: `out/receipt-latest.txt` (regenerate with `sh out/rerun-latest.sh`; logs in `out/logs/latest-*.txt`). Earlier receipts: `out/receipt-prev-9632e4a9.txt`, `out/s1-archive/`. Nothing installed. No servers. No lane writes except this file.

## One-nibble result
Row `gate-live-1` now pins rev `1b85a24e…`, path `.ufo/waves/round-18/runs/live-gate-1.stdout`, digest `1cb5a41b…c7`. Re-derived with `git cat-file blob 1b85a24e…:… | sha256sum` (exit 0). Fixtures `out/L1`–`out/L4` flip one hex digit in the registry, the lesson token at line 419, or both.

| Variant | Exit | Text row (`missing`) |
|---|---|---|
| L1: registry and token, digit 1 `1→0` | 1 | `mismatch … expected=0cb5a41bbfeb observed=1cb5a41bbfeb` (0) |
| L2: token only | 1 | `mismatch … expected=1cb5a41bbfeb observed=1cb5a41bbfeb` (0) |
| L3: registry only | 1 | `mismatch … expected=0cb5a41bbfeb observed=1cb5a41bbfeb` (0) |
| L4: registry and token, digit 40 `a→b` | 1 | `mismatch … expected=1cb5a41bbfeb observed=1cb5a41bbfeb` (0) |
| E5: lane path not a git repo | 2 | `lane is not a git repository` |
| Baseline, real files | 0 | `required=3 … verified=3 missing=0 mismatch=0 off_ref=0` |

Observed digest: printed in full by `--json`; text prints a 12-hex prefix. L4 JSON: `sha256 …3ba4…` against `observed_sha256 …3aa4…`.

## Findings
1. **[medium] Text output hides differences past hex digit 12.** `main()` prints `[:12]`, so L4 reads identically in text. Only `--json` shows it.
2. **[medium] Stale-token mismatches do not show the cited digest or document.** L2 prints `expected` equal to `observed` with status `mismatch`. The operator cannot tell which side to fix.
3. **[medium, test gap] No selftest case exercises the observed-digest branch.** With `elif error is not None or observed != want:` replaced by `elif False:` (`out/mutant-latest`), `--selftest` still prints `selftest: ok (15 cases)` and exits 0. Running that mutant on L1 gives `verified=3 mismatch=0`, exit 0. Every selftest registry carries the blob's real digest.
4. **[info] SCORECARD.md:824 says `selftest 5 cases`.** That line is a round-18 before/after record. The current count is 15 (SCORECARD.md:847, LOG.md:1146). No action unless the record is meant to be current.

## Patch: `out/patched-latest.diff` (dry-run applies cleanly to `d442262d`; not applied to the lane)
- `results` gain `stale_sha256` and `stale_documents`. Text prints full digests and `stale=<digests> in <doc>`.
- New selftest case `observed-mismatch`: registry digest `'0'*64`, matching token, blob `payload`. Asserts `(missing, mismatch) == (0, 1)` and `observed == sha256(payload)`. Count 15 → 16.
- Verified: patched `--selftest` exit 0; patched baseline exit 0 `verified=3`; L1 shows full digests; L2 `stale=0cb5…`; L3 `stale=1cb5…`; L4 shows `…3ba4…` against `…3aa4…`. Mutant with the branch removed (`out/mutant2-latest`) exits 1 with `SELFTEST FAIL observed-mismatch`, so the new case kills it.
- Harm check: no doc quotes the text-row format (grep of `corpus/`, `SCORECARD.md`, `LOG.md`, `registry/`). Ancestry gate unchanged (baseline `off_ref=0`).

## Residual risk and gaps
- The lane moved repeatedly during review. Gate row re-pinned `eb78788b…/b2043ba8…` → `1b85a24e…/1cb5a41b…`. Tool hashes seen in order: `edc9e06a…`, `00998d52…`, `2d07296d…`, `9632e4a9…`, `d442262d…` (off-ref gate added in `d442262d…`). HEAD went `8bf99cae…` → `7229fa95…` → `f1790e25…`. Re-run `sh out/rerun-latest.sh` on the integrated tree before relying on these numbers.
- Across snapshots, the first (`edc9e06a…`) classified doc-only and registry-only flips as `missing`. The current tool classifies them as `mismatch`. That change is the stale branch. My numbers come from the latest state only.
- My work copy's git HEAD is `7229fa95…` and its `origin/master` is `7229fa95…`. The off-ref check ran against that. Read-only check on the lane: both registry revs (`1b85a24e…`, `1c325b2e…`) are ancestors of the lane's `origin/master` `f1790e25…` (`merge-base --is-ancestor`, exit 0).
- The stale check ignores the `doc` binding, so a stale token in any scanned doc fails the row. No test covers a bound-doc row with a stale token elsewhere. [INFERENCE: intent unknown]
- Not checked: the round-18 runner, C2 install-tree pins, and any `--json` consumers.
