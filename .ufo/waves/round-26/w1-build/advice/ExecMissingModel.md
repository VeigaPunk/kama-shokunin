# KamaR26.ExecMissingModel — w1-build advice

Verdict: one startup fault confirmed for model kind "missing" (non-existent model path) with signature `failed to open GGUF file`; the candidate row counts 1/1 under the frozen counter in a scratch `git archive` extract (counter exit 0, `registered 1 counted 1`).

## Fault reproduction (twice, own port block 47632-47635)

Fixture: `~/.local/bin/llama-server` (build 11755, commit 704366d76, sha256 b6a31a8e...) with model kind `missing` = `/nonexistent/kama-r26/missing.gguf` (the counter's own MISSING_MODEL constant).

- Run 1: `timeout 40 ~/.local/bin/llama-server -m /nonexistent/kama-r26/missing.gguf --host 127.0.0.1 --port 47632 -t 2 > run1.log 2>&1` → exit 1. Signature line: `0.00.005.000 E gguf_init_from_file: failed to open GGUF file '/nonexistent/kama-r26/missing.gguf' (No such file or directory)`.
- Run 2: same on port 47633 → exit 1, identical signature line.
- Both logs kept at `.ufo/waves/round-26/w1-build/out/ExecMissingModel/raw/run1.log`, `run2.log`.

## Signature choice

`failed to open GGUF file` (24 bytes; constant part of the format string).

- Source (clause d): `ggml/src/gguf.cpp` line 1021 (real repo path at commit 704366d76; lane snapshot basename `gguf.cpp`): `GGML_LOG_ERROR("%s: failed to open GGUF file '%s' (%s)\n", __func__, fname, strerror(errno));`
- Fresh fetch 2026-10-23: `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp` → sha256 `7505d6a434dc740941a682fd3b476ef9bd9893ab76adf18c9969daa528bd5be5`, byte-identical to the lane snapshot (same sha).
- Absent at base (clause b): `git -C <lane> grep -F -q -e 'failed to open GGUF file' 1560e4d83f42b04f40336357de6f9637eafa0f4b -- SKILL.md corpus` → exit 1 (absent).
- Healthy baseline (clause f): fixture model on port 47634, `/health` 200; signature count in baseline log 0; `llama-server --help` exit 0 and `--version` exit 0 both contain 0 occurrences.
- Startup channel (clause e): seen in stdout+stderr of both non-zero exits (exit 1 within 30 s).
- Not echoed (clause e): startup channel; no request bytes.
- One fault per row: trigger is exactly model kind "missing".

## Candidate entry (written to `out/ExecMissingModel/candidates.json`)

```json
{"signatures": [{"id": "TBD", "channel": "startup", "signature": "failed to open GGUF file",
  "args": [], "model": "missing", "occupy_port": false,
  "source": {"row": "TBD", "file": "gguf.cpp"}}]}
```

id/row are TBD placeholders for the L1 (full concrete id `KamaR26.MissingModel.Startup`, source row `S901` used in the scratch check below).

## Scratch frozen-counter check

Scratch `git archive a23c0e042114016a909eb15173aa6df74b5b7eb0` extract at `/fast/scratch/hyaku/kama-r26/ExecMissingModel/scratch/`; added `registry/error-signatures-r26.json` (`KamaR26.MissingModel.Startup` / `failed to open GGUF file` / S901 / gguf.cpp), a `## Round-26 live error signatures` SKILL.md row, a `S901` SOURCES row, and the pinned source snapshot (`gguf.cpp` sha256 matches). Ran under the host lock:

`flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 python3 .ufo/waves/round-26/count-c1.py --out kama-r26-c1-scratch.json`

Output: `registered 1 counted 1 target 12 met False not-counted []`, counter exit 0. All 12 checks true: id_unique, a_skill_row, b_long, b_new_at_base, c_source_row, d_source_pinned, d_in_source, e_error_shown (exit 1), e_signature_seen, e_not_echoed, f_absent_from_baseline, g_distinct. Full receipt (incl. channel_sha256 234a0028... and channel excerpt) in the extract's `kama-r26-c1-scratch.json`.

## Files written

- `.ufo/waves/round-26/w1-build/out/ExecMissingModel/candidates.json`
- `.ufo/waves/round-26/w1-build/out/ExecMissingModel/RUNS.txt`
- `.ufo/waves/round-26/w1-build/out/ExecMissingModel/raw/{run1.log,run2.log,baseline.log,help.txt,version.txt}`
- `.ufo/waves/round-26/w1-build/advice/ExecMissingModel.md` (this report)
- scratch only: `/fast/scratch/hyaku/kama-r26/ExecMissingModel/` (logs, fetch, extract, counter receipt)

Cleanup: no llama-server of mine remains (`pgrep -af llama-server` shows only sibling seats' processes on other ports); ports 47632-47635 verified free after use. No tools installed this session.

## Risks / notes for L1

1. Inter-row clause (g) overlap: the missing-model channel also contains the shared strings `error loading model: llama_model_loader: failed to load model from`, `common_init_: failed to load model`, `load_model: failed to load model, '`, and `exiting due to model loading error` (the last also in server.cpp for other startup faults). If a sibling row that named one of those is counted before this one in registry order, this row's g check fails (earlier counted signature in this channel). Recommendation: order the missing-model row before any row whose signature appears in this channel text, or ensure sibling seats avoid those shared strings.
2. The `S901` SOURCES row's correct fetch URL is the `ggml/src/gguf.cpp` path (root `gguf.cpp` and `gguf/gguf.cpp` 404 at commit 704366d76).
3. Baseline/`--help`/`--version` are clean of this signature, so no clause (f) risk for this row.
