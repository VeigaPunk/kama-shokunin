# K2Projection — stable projection attack

**Verdict: five fresh replays all passed, but `models` differs at the raw-body level because `created` is time-varying; this is correctly excluded, while several captured response values remain unprojected and untested.**

## Reproduction and evidence

From a shared clone at build commit `380bcdff9c8af06997c482f6eb03db926a794a2b`, ran five concurrent fresh replays of committed `c2/live/receipt-1.json`, each with independent `HOME`, `XDG_CACHE_HOME`, `TMPDIR`, and `--work` under `/fast/scratch/hyaku/kama-r48/K2Projection/runN`:

```sh
python3 tools/kama-live-replay.py --receipt <lane>/.ufo/waves/round-48/c2/live/receipt-1.json --work "$S/runN/work" --out "$S/runN/replay.json" --timeout 600
```

All five exited 0 and reported `replay match=True refused=None mismatches=0 exit=0`. The five rerun receipts are copied to `out/K2Projection/rerun-{1..5}.json`; `replay-results.txt` records outcomes. Compared each full `captures` member in the original receipt and all five reruns.

- `models` raw capture differed in all five runs versus the original: `data[0].created` changed from `1793053583` to `1793054163`/`1793054164`, with correspondingly changed body SHA-256. Across the reruns those two timestamp values both occurred. The `models` `meta` block was identical in this sample (vocab_type, n_vocab, n_ctx, n_ctx_train, n_embd, n_params, size, ftype).
- `props` capture also differed in all five: its raw `body_sha256` changed, although all five projected `fields` were identical: `build_info=b11909-caa8191df`, `default_generation_settings.n_ctx=256`, `is_sleeping=false`, `model_alias=kama-r48-live`, `total_slots=4`. `Content-Length` and response headers stayed identical in this sample. Since props body is not retained (`keep_body=False`), the varying byte(s) cannot be localized from these receipts; the hash difference is evidence of differing unprojected body content, not evidence those five fields varied.
- `health`, `slots`, and `metrics` captures were byte-for-byte equal across all six receipts. Slots had element_count 4 and the same body digest; health status/body digest same; metrics status 501/error null/path `/metrics` same.
- No flake was observed in replay outcome or current projection for these five runs. The changed `created` timestamp confirms why the replay excludes it. The props hash is a real cross-run variation, but does not currently make replay flaky because the projection excludes the hash and compares only the stable extracted fields.

## Projection coverage / gaps

The replay contract and implementation (`tools/kama-live-replay.py:17-26`, `154-175`) compare props `fields`; slots element count and body digest; health status and body digest; models sorted `data[].id|owned_by` and `models[].name`; metrics status; loading envelope and 503 body digest; teardown outcome; listener ownership. The counter's own `projection()` (`tools/round48-live-replay-v5-audit.py:206-226`) uses the same eight top-level surfaces and equivalent selected members; its round-trip leg compares that projection at lines 75-84's contract and runtime. Both omit:

- **models `meta`:** stable in this sample, but neither comparator detects mutation of `data[].meta` or the other unprojected models body fields. Since body digest is intentionally not compared to avoid `created`-timestamp noise, body mutations are invisible unless they affect projected IDs/names.
- **props beyond five extracted fields:** neither compares the capture `body_sha256`; additional raw `/props` properties are not represented in `fields`. The observed hash varies run-to-run, making whole-body equality unsafe without canonicalization or deliberate field selection. This sample cannot identify which bytes caused the hash change because the body is not kept.
- **slots body content:** both compare only `element_count` and `body_sha256`, not the raw body; this is content-protective via digest, but opaque and non-diagnostic. It did not vary here.
- **metrics headers:** the live capture deliberately reduces metrics to `{path,status,error}` (`tools/kama-llamacpp-live.py:847-849`), so headers are not captured and cannot be compared. Neither implementation can compare metrics headers from a receipt.

The projection key sets are identical: `props, slots, health, models, metrics, loading, teardown, ownership`. Their representations are not exactly the same: replay `models` is a dict with `data` and `models` keys (`kama-live-replay.py:160-170`), while counter `models` is a tuple of the two sorted lists (`round48-live-replay-v5-audit.py:210-223`). These represent the same selected values and are separately compared within each tool, but are not directly equality-compatible as Python values. This is maintainability/authority duplication: future edits can update one projection and miss the other. The smallest safe correction is a shared canonical projection implementation (or a parity test asserting canonicalized values/key membership) and explicit tests for the intentionally omitted fields; do not blindly compare raw props/models body hashes because `created` and observed props-body variation would make legitimate reruns fail.

## Axes impacted

**Operability**: no observed replay flake in this five-run sample. Projection blind spots mean some captured surface regressions can pass; the duplicated definitions can drift. Evidence is limited to five runs and one receipt, not a broad stability guarantee.

## Source anchors

- `tools/kama-live-replay.py:17-26,154-200` — documented projection, implementation, and comparison.
- `tools/round48-live-replay-v5-audit.py:48-56,75-84,206-226` — counter's contract and projection.
- `tools/kama-llamacpp-live.py:802-850` — selected props fields, slots count, and reduced metrics capture.
- `c2/live/receipt-1.json:20-94` — original capture fields and headers.

Evidence files: `.ufo/waves/round-48/w1/out/K2Projection/rerun-1.json` through `rerun-5.json`; `.ufo/waves/round-48/w1/out/K2Projection/replay-results.txt`.
