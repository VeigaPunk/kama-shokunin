# F12C1WorkPath — C1 work-path falsification

Executed `/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-live.py --work <case> --nonce <nonce> --ollama-bin /home/vgpnk/.local/opt/ollama-v0.40.11/bin/ollama --model-gguf /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --out /fast/scratch/hyaku/kama-r60/F12C1WorkPath/receipts/<case>.json`; runner set `TMPDIR=/fast/scratch/hyaku/kama-r60/F12C1WorkPath` and scratch HOME. All runs used v0.40.11 / pinned fixture; all completed child runs reported `port_closed=true`, `sigkill_needed=false`.
Exact invocations were the common argv above with these individual arguments (runner environment: `HOME=/fast/scratch/hyaku/kama-r60/F12C1WorkPath/runner-home`, `TMPDIR=/fast/scratch/hyaku/kama-r60/F12C1WorkPath`):
| case | `--work` | `--nonce` | `--out` |
|---|---|---|---|
| quoted-space | `/fast/scratch/hyaku/kama-r60/F12C1WorkPath/space and 'single' plus "double"` | `f12wp001` | `/fast/scratch/hyaku/kama-r60/F12C1WorkPath/receipts/quoted-space.json` |
| symlink-work | `/fast/scratch/hyaku/kama-r60/F12C1WorkPath/work-link` | `f12wp002` | `/fast/scratch/hyaku/kama-r60/F12C1WorkPath/receipts/symlink-work.json` |
| prepopulated | `/fast/scratch/hyaku/kama-r60/F12C1WorkPath/prepopulated` | `f12wp003` | `/fast/scratch/hyaku/kama-r60/F12C1WorkPath/receipts/prepopulated.json` |
| readonly | `/fast/scratch/hyaku/kama-r60/F12C1WorkPath/readonly` | `f12wp004` | `/fast/scratch/hyaku/kama-r60/F12C1WorkPath/receipts/readonly.json` |
| nested-symlinks | `/fast/scratch/hyaku/kama-r60/F12C1WorkPath/nested-symlinks` | `f12wp005` | `/fast/scratch/hyaku/kama-r60/F12C1WorkPath/receipts/nested-symlinks.json` |

| case (`--work`; nonce) | exit / observed output |
|---|---|
| quoted path `/fast/scratch/hyaku/kama-r60/F12C1WorkPath/space and 'single' plus "double"`; `f12wp001` | 0, `MODEL_OK`, no failed checks; `v1_models_empty_data_form=null`. W1's reported quote-path `FAIL`/`other` did not reproduce. |
| symlink `/fast/scratch/hyaku/kama-r60/F12C1WorkPath/work-link` → `/fast/scratch/hyaku/kama-r60/F12C1WorkPath/symlink-target`; `f12wp002` | 0, `MODEL_OK`; artifacts resolved into target. |
| prepopulated work tree; `f12wp003` | 0, `MODEL_OK`; home/models sentinels retained; pre-existing `serve.log` marker was truncated/replaced. |
| read-only work tree; `f12wp004` | 1, no stdout/receipt; uncaught `PermissionError` opening `readonly/serve.log` at tool line 282. `Popen` is line 283, so this failure occurred before child start; sentinel remained. |
| `work/home` and `work/models` symlinked to sibling `outside-home` / `outside-models` within scratch; `f12wp005` | 0, `MODEL_OK`; observed `.ollama/id_ed25519`, cache files, model blob and manifest in those resolved sibling targets, outside lexical `--work` but still inside seat scratch. No host paths were used. |

Assessment: no A04 normal-path containment failure reproduced; the quote-path W1 anomaly is not graded by the C1 predicate and was not reproduced. **Bound:** there is no resolved-path containment check (`os.path.abspath(args.work)` only; child paths are joined and followed), so the documented “under `--work`” isolation holds only for non-escaping caller-provided symlinks; a symlinked subdirectory redirects writes. This is an observed lexical-vs-resolved boundary, not evidence of writes beyond the chosen symlink target. Read-only setup contradicts the tool's documented setup-error exit code 2: it emits a traceback and exits 1, but starts no child. The frozen C1 predicate does not explicitly grade either edge case.

Source evidence: `tools/kama-ollama-live.py` `work=os.path.abspath(args.work)`, `child_env()` joins `home`/`models`, `open(log_path,'wb')` before `Popen` and lifecycle `try/finally` (lines 178–190, 270–286, 402–425). W1 evidence: `.ufo/waves/round-60/w1/out/A04HostileWorkDir.md` and `case-summary.json`. Disk guard status was running/OK; no tools installed or updated.