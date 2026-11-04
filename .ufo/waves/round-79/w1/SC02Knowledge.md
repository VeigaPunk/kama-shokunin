# SC02Knowledge — knowledge entry draft: the unregistered-listener census class (scribe)

Seat: SC02Knowledge (scribe, coverage axis). Milestone kama r79 w1. Leaf: no subagent
dispatch, no lane edits outside this seat dir, no commit, no scored gate run.
Lane tip: `f7442dea53bd8f474293a2252437b5d869801f49` at seat start; `d6408a63f4ac4efd1d7161180aa62bf10f6f591a`
at close (`git -C <lane> rev-parse master`, exit 0). The tip moved under this seat because the
L1 committed round-79 lesson/S553/entry/coverage-row work at `d6408a63`.

## Deliverable

Entry draft, 89 lines (under the 90-line cap), in the lane's shape (`source:`, `verified-at:`,
`recheck:` first, then the class, the probe surface, the inventory-not-readiness ground, the
non-claims, the live-host reading rule) and with the coverage-map row text in a fenced block:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC02Knowledge/unregistered-listener-census.md`

`corpus/knowledge/` and `corpus/README.md` were **not** edited; the L1 lands and indexes.

## Receipts (command → exit, artifact)

- `git -C <lane> rev-parse master` → `f7442dea…` (start) and `d6408a63…` (close), exit 0.
- `bash tools/kama-probe.sh listeners` (rev `d6408a63`, probe sha256 `0943fb46…`) → exit 0,
  summary `probed=34 model_endpoints=7 foreign_service=24 unauthorized_service=0 dead=3 not_http=0 model_loading=0 governed=0 unregistered=7 registry=ok`.
  Receipt: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC02Knowledge/listeners-class.out`
- `bash tools/kama-probe.sh listeners --json` (same rev, same probe sha) → exit 0,
  summary `probed=33 … dead=2 … governed=0 unregistered=7 registry=ok`; per-row `"registered"`
  values: `1234`, `8788`, `8789`, `8790`, `8791`, `8793`, `8795` = `no` (all `MODEL_OK`), every
  other row `-`.
  Receipt: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC02Knowledge/listeners-class.json.out`
- `git -C <lane> show d6408a63:registry/endpoint-consumers.tsv` (via `cut -f1,4`) → three rows;
  declared ports `8080`, `34113`, exit 0. Same three rows at the base revision `ee53f1a2`.
- `sha256sum /home/vgpnk/src/llama.cpp/tools/server/README.md` → `8fd5abde…`, exit 0;
  `git -C /home/vgpnk/src/llama.cpp rev-parse HEAD` → `39febd2a…`, exit 0 (read-only outside the
  lane; agrees with the freeze receipt and SCT02's blob cross-check).
- `grep -n "model_endpoints\|EXIT=" .ufo/waves/round-79/measured/before/c3-listeners-base.out` →
  `model_endpoints=7`, `EXIT=0`, exit 0.
- `wc -l <draft>` → 89, exit 0. `grep -n "/home/\|/fast/\|/tmp/" <draft>` → no match, exit 1
  (prose is absolute-path free).
- `git -C <lane> status --short tools/` → this seat modified no tracked file.

No clone, fixture, work tree or scratch registry was created; no `$S` tree exists to remove.

## Findings

1. **The entry was landed by the L1 before this draft, and is being revised in the worktree.**
   `corpus/knowledge/unregistered-listener-census.md` exists at `d6408a63` (58 lines) and is
   modified in the worktree (`downloading`/`incomplete` added). This seat did not touch it; the
   draft here is an independent candidate, not an edit. Delta this draft adds over the landed
   entry: (a) an explicit live-host **reading rule** — a run is a dated sample, `-` never means
   registered, `no` never comes from an unreadable registry, and the registry is a consumer
   registry, not a host-wide port inventory; (b) the observed churn evidence (two consecutive
   runs: `probed=34` with a `DEAD` `llama-server` on 51085, then `probed=33` without it);
   (c) the seven live `registered=no` rows with `governed=0 unregistered=7 registry=ok`.
2. **The class population is broader than `MODEL_OK`/`MODEL_MISMATCH`.** The landed
   implementation (`classify_registration`, `tools/kama-probe.sh`) assigns `yes`/`no` to
   `MODEL_OK`, `MODEL_MISMATCH`, `MODEL_LOADING` and `UNAUTHORIZED_SERVICE`, and `-` to
   `DEAD`/`NOT_HTTP`/`FOREIGN_SERVICE`. The draft states that set; an earlier revision of this
   draft had said only `MODEL_OK`/`MODEL_MISMATCH` and was corrected against the code before
   the receipt was taken.
3. **Committed-state mismatch to route.** At `d6408a63` the committed `tools/kama-probe.sh` has
   **no** `registered` class (its only `registered` hit is `consumer_rows_registered` in the
   `consumers` JSON), and `tools/round79-unregistered-census.py` is untracked. The committed
   entry and coverage row therefore describe a worktree surface, not that commit's `tools/`.
   The class exists only as an uncommitted worktree modification (sha256 `0943fb46…`) and it
   works there: both runs above exit 0 with the column and the `governed`/`unregistered`/
   `registry` keys. The L1's commit of the tools (and the C3 receipts) is what makes the
   landed entry true at a tip; this seat does not commit.
4. **Probe surface verified exactly:** last table column `registered` (`yes`/`no`/`-`), per-row
   JSON `"registered"`, summary keys `governed`/`unregistered`/`registry` after `model_loading`;
   a missing/unreadable `--registry` sets `registry=missing` and leaves every class `-` with a
   warning, never a probe error (code read; not exercised with a bad registry by this seat).
5. **Source grade adopted, not over-read.** Per SCT02Source caveat A, line 2227 belongs to the
   `?reload=1` bullet; the draft grounds "inventory" on line 2199 "Listing all models in cache",
   uses 2227 only for the refresh path, and lists six `status.value` values plus
   `failed`/`exit_code`. SCT02Source caveat B ("Router mode" is a paraphrase) is consistent with
   the draft citing `README line 2197` as the section locator.
6. **The S-row is resolved:** S553, per SC01Sources' draft; the landed SOURCES row at `d6408a63`
   bears the same id. The draft cites S553 plus the SC01 draft and the freeze receipt.

## Out-of-scope / untouched

- No edit to `corpus/knowledge/*`, `corpus/README.md`, `corpus/SOURCES.md`, `corpus/lessons/*`,
  `plans/*`, `registry/*`, `SKILL.md`, `PROVINCE.md`, `SCORECARD.md`, `LOG.md`,
  `.ufo/waves/round-79/measured/**`, or any other seat's directory.
- No `tools/round79-unregistered-census.py` run, no scored `pre-report-gate.py` run, no
  `round79-selfrecord-round78.py` run, no git mutation, no commit.
- Live probe runs are read-only toward services and wrote only this seat's receipts; the probe
  itself writes to a removed `mktemp` dir.

## Caveats for the L1

- If the L1 prefers the landed entry, use items 1(b)/(c) as an appended "reading rule" section
  rather than a rewrite; the entry is append-friendly and the rule is missing today.
- The draft's `verified-at:` dates the class reading to probe sha256 `0943fb46…` in the
  worktree; if the probe changes before the round's commit, re-run the two commands in
  `recheck:` and re-date rather than carrying this claim.
- `plans/round-79-claims.md:96-119` is the frozen predicate locator used in `source:`; the
  `## C3` heading is the stable fallback if lines shift.

## Evidence pointers (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC02Knowledge/unregistered-listener-census.md` (draft, 89 lines)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC02Knowledge/listeners-class.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC02Knowledge/listeners-class.json.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SC01Sources/sources-append.md` (S553 row, Gate, quote)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SCT02Source.md` (quote grading, caveats A/B)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/measured/before/source-router-models.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/measured/before/c3-listeners-base.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-78/measured/observation/unregistered-1234.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/unregistered-listener-census.md` (L1-landed entry, `d6408a63`; modified in worktree by another seat)
