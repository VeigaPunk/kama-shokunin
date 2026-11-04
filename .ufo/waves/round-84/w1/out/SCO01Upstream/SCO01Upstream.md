# SCO01Upstream — round 84 w1 recon

Axes: freshness, source fidelity, frozen-claim scope. Recon only; no production edits, tests, commits, installs, or delegation. Frozen `plans/round-84-claims.md` read in full before upstream fetches. Lane `master` observed at `eb03a64bcd8e2faab0f4f9bcdc55bfc5c1ed2c85`. Evidence collected 2026-11-04, retained by 14:52:48 UTC.

## Observed upstream tags — high confidence

| Engine | Newest stable tag | Comparison to supplied pin-watch read | Tag object |
|---|---|---|---|
| llama.cpp | `b12111` | unchanged | `52e53a76df0298d2c316ae7e704eeec03b0bf478` |
| SGLang | `v0.5.23` | unchanged | `7df5dd09bc2f0e7e1509a1f7c2a40dff00ad8a01` |
| vLLM | `v0.33.0` | unchanged | `3a4d82f569a9f57054ba81633e9b6c73b34b51fe` |

Selected maximum numeric `bN` or numeric `vX.Y.Z` release, excluding peeled duplicate refs and prereleases. vLLM also has `v0.33.0rc0` through `v0.33.0rc3`; none is a newer stable release. Raw advertisements retained alongside this report. `ls-remote` wildcard results can include nonrelease refs; these were not treated as release tags.

Distinct pure numeric b-tags above b7200 in this advertisement: **3398**. This is a fresh raw tag-population observation, not a rerun of pin-watch or a replacement for the round-83 historical `behind 3395` relation cell. Why that older population differed was not investigated.

Raw advertisement SHA-256:
- `llamacpp-tags.raw`: `708684abb856a100a9840bbe220fde13e65850f4ac0a82dd88e966b7f668f83f`
- `sglang-tags.raw`: `6ecbe4bfcae98783625f262c2b9ac6061d030d0b595e07e1385ce182e41b9c81`
- `vllm-tags.raw`: `ced858e18e24aa122f97dcb8ad7ba4e4589374215748d99b4fba66baf372bd16`

## b7200 document — high confidence; C3 relation 3 is reachable

URL: https://raw.githubusercontent.com/ggml-org/llama.cpp/b7200/tools/server/README.md

- curl exit **0**, HTTP **200**, **72181 bytes**.
- SHA-256: `fb4ab6f2e4db180bf9c89533ef63556559c60a66f9c39a92f0c23cd88f6c6a53`.
- Retained body: `b7200-tools.md` alongside this report; fetched first under the assigned scratch directory.
- Health section: **lines 404–416**, including trailing blank line; next endpoint starts at line 417. Header at 404, public/alias statement at 406, loading response at 410–412, ready response at 413–415.
- Located verbatim quote (line 406, ≤25 words): “This endpoint is public (no API key check). `/v1/health` also works.”
- Lines 412 and 415 distinguish loading from successfully loaded/ready. The document's existence removes the source-absence obstacle; the executor must still derive the actual recheck verdict from its registered comparison bytes.

The `examples/server/README.md` fallback was **not fetched**, because the first path returned 200.

## SGLang native API — high confidence; exact matrix input

URL: https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/docs/docs/basic_usage/native_api.mdx

- curl exit **0**, HTTP **200**, **18295 bytes**.
- SHA-256: `3ed171186990d6a67a1d950f1d491fe83986cf539bf24d1e65b95481e7d87a3c`.
- Retained body: `sglang-native.mdx` alongside this report.
- Section heading `## Health Check` at line 108; exact route lines:

Line 111:
```text
- `/ready`: Returns 200 when the server accepts new requests; 503 while starting, paused, unhealthy, or shutting down.
```

Line 112:
```text
- `/ping`: SageMaker health check. Returns 200 once the server is up; 503 while starting, unhealthy, or shutting down. Stays 200 while generation is paused. A failed `/health` or `/health_generate` probe marks the server unhealthy until a later probe succeeds.
```

These are the specifically requested exact route transcriptions; the single located Gate quote above is within 25 words. `/ping` staying 200 while paused must not be collapsed into `/ready` semantics.

**Digest discrepancy worth preserving:** the locally held `corpus/anchors/sglang-v0.5.23-health.txt:1` header names `d9477761c740bd1b6691a7613abee61cca8d175b56c1e7586cc76c3161acbb01`, not the fresh body digest above. This establishes header/body-digest difference, not by itself a content-verdict classification. No old full body was fetched and no recheck tool was run here.

## Assimilation fit — recommendations, not an adoption claim

**Merge package:** `/home/vgpnk/Projects/shokuknow/merge/kama/MERGE-REPORT.md` stages a route-specific health/readiness theme, particularly `runtime-health-surface-matrix-amendment-2026-10-23-r4.md` (“what actually raises a 503 in SGLang”) and staged S364's separation of readiness and health. That theme can ride **C3's already-frozen SGLang `/ready` and `/ping` dated matrix addition**, narrowly as an organizing distinction using this round's freshly opened pinned document. Do not import S364's extra tokenizer-manager, detokenizer-heartbeat, or error-taxonomy claims: they are outside these fetched bytes. The broader package's process-column, identity, and platform additions would widen the frozen work and should not ride this round. Thus a narrowly named health/readiness-theme assimilation is defensible; `Assimilation: none` is also honest if the owner elects not to adopt that theme. Reading the package alone is not assimilation.

**Newest daily proposal file:** directory listing confirms `considerthese/2026-10-26.md` is newest. Proposal **4, “Report the pin gap every morning,”** fits **C3** only as its ordinary dated upstream-tag comparison: today's three tags are unchanged, and b7200 now has an opened document. The recurring morning report/automation and comprehensive gap reporting are not delivered or authorized by this recon; do not claim the whole proposal implemented. Proposals 1 (daily deletion detection), 2 (proposal-outcome tracker), and 3 (running shortcut/mutant tally) would create new recurring surfaces rather than merely curate C1/C2's frozen repairs, so none should be imported wholesale. If the owner requires a fully adopted proposal rather than a scoped theme, `Assimilation: none` is the honest line.

## Commands, failures, and retained receipts

`commands.json` contains exact argv, true exit, stdout, and stderr for the five successful upstream commands, five evidence-copy commands, and scratch removal. All eleven subprocesses exited **0**. Specifically:

1. `git ls-remote --tags https://github.com/ggml-org/llama.cpp 'refs/tags/b*'` — 0.
2. `git ls-remote --tags https://github.com/sgl-project/sglang 'refs/tags/v*'` — 0.
3. `git ls-remote --tags https://github.com/vllm-project/vllm 'refs/tags/v*'` — 0.
4. `curl -sS -o /fast/scratch/hyaku/kama-r84/SCO01Upstream/b7200-tools.md -w '%{http_code}' https://raw.githubusercontent.com/ggml-org/llama.cpp/b7200/tools/server/README.md` — 0, HTTP 200.
5. `curl -sS -o /fast/scratch/hyaku/kama-r84/SCO01Upstream/sglang-native.mdx -w '%{http_code}' https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/docs/docs/basic_usage/native_api.mdx` — 0, HTTP 200.
6–10. `cp -- <scratch file> <same basename in own out directory>` for the two bodies and three raw advertisements — each 0; exact paths in JSON.
11. `rm -rf -- /fast/scratch/hyaku/kama-r84/SCO01Upstream` — 0; Python observed scratch path absent afterward.

Initial bash calls preceded those audited subprocesses:

```sh
mkdir -p /fast/scratch/hyaku/kama-r84/SCO01Upstream /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-84/w1/out/SCO01Upstream; echo "MKDIR_EXIT:$?"
```
Overall exit **0**. The following three initial tag wrappers were launched concurrently with mkdir, which was an avoidable prerequisite race:

```sh
git ls-remote --tags https://github.com/ggml-org/llama.cpp 'refs/tags/b*' > /fast/scratch/hyaku/kama-r84/SCO01Upstream/llamacpp-tags.raw; echo "LSREMOTE_EXIT:$?"; grep -oE 'b[0-9]+' /fast/scratch/hyaku/kama-r84/SCO01Upstream/llamacpp-tags.raw | sort -u | sed 's/^b//' | sort -n | tail -8 | sed 's/^/b/'; grep -c 'refs/tags' /fast/scratch/hyaku/kama-r84/SCO01Upstream/llamacpp-tags.raw
```
Overall exit **2**; redirection failed with missing directory, reported `LSREMOTE_EXIT:1`; git was not executed. Its unanchored tag postprocessing was not used as evidence.

```sh
git ls-remote --tags https://github.com/sgl-project/sglang 'refs/tags/v*' > /fast/scratch/hyaku/kama-r84/SCO01Upstream/sglang-tags.raw; echo "LSREMOTE_EXIT:$?"; grep -oE 'refs/tags/v[0-9][0-9a-z.]*' /fast/scratch/hyaku/kama-r84/SCO01Upstream/sglang-tags.raw | sed 's|refs/tags/||' | sort -uV | tail -10; grep -c 'refs/tags' /fast/scratch/hyaku/kama-r84/SCO01Upstream/sglang-tags.raw
```
Overall exit **0**, `LSREMOTE_EXIT:0`; printed v0.5.23 and 177 advertised lines. Replaced by the audited exact-ref parse.

```sh
git ls-remote --tags https://github.com/vllm-project/vllm 'refs/tags/v*' > /fast/scratch/hyaku/kama-r84/SCO01Upstream/vllm-tags.raw; echo "LSREMOTE_EXIT:$?"; grep -oE 'refs/tags/v[0-9][0-9a-z.]*' /fast/scratch/hyaku/kama-r84/SCO01Upstream/vllm-tags.raw | sed 's|refs/tags/||' | sort -uV | tail -10; grep -c 'refs/tags' /fast/scratch/hyaku/kama-r84/SCO01Upstream/vllm-tags.raw
```
Overall exit **2**; redirection failed with missing directory, reported `LSREMOTE_EXIT:1`; git was not executed.

```sh
git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master; echo "EXIT:$?"
```
Overall exit **0**, rev-parse exit **0**, printed the controls revision above. No other shell commands were run. Remaining operations used file-read/search tools and Python in-memory parsing/hashing/copy orchestration; their successful tool outputs are in the transcript. No package installation or upgrade occurred. No tests were run, and no claim counter is represented as passed.

## Boundaries and self-evaluation

Report is intentionally in the exclusive `out/SCO01Upstream/` directory, not the conflicting trailer location outside it; integration owner can publish the final report pointer. Only this seat's out directory and its removed scratch were written. LSP tracing is inapplicable: no code symbol or exported contract was investigated.

Confidence: high on observed tags/status/hash/bytes/lines; medium on scoped assimilation fit (owner adoption decision); unresolved historical tag-population difference and SGLang whole-body drift classification.

Self-evaluation: accuracy 4/5 (live hashes grounded; old full-body comparison not performed); completeness 4/5 (all five items covered, trailer conflict resolved by exclusive-write contract); clarity 4/5 (command ledger is necessarily long); actionability 4/5 (exact source bytes and matrix lines retained; integration still owns verdict/adoption); conciseness 4/5 (audit detail required). Mean 4.0. Highest-impact improvements: order mkdir before dependent jobs; reuse the machine-readable command ledger rather than first launching ad hoc wrappers. Would the user agree: likely, given disclosed failures and retained primary evidence.
