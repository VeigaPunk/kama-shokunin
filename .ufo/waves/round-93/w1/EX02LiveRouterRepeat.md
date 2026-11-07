# EX02LiveRouterRepeat — live router corroboration of C1

## Scope
- Live llama-server b12177 router, preset with 12 entries (bad01–bad12) all `model =` one slow invalid GGUF (150k tensor infos, truncated, 6,000,048 B, sha256 02184c6b…00581) + 1 valid entry goodone (stories260K copy).
- Probes at BASE 5af794958b0fc08f574aa2e67650282269549b02 and M1 fe5f031cb1b9d33e1160360d892149b8ac3c7771, `--expect bad01` and `--expect '*'`, plus router oracle POST /v1/chat/completions (max_tokens 2) for bad01/goodone.
- Binary: /home/vgpnk/.local/opt/llama-b12177/llama-server (pin ba272ee3…).
- Never touched 127.0.0.1:1234; all traffic to lane-owned child on free ports.

## Commands and outputs (exit codes)
- `python3 drive.py` (scratch /fast/scratch/hyaku/kama-r93/EX02LiveRouterRepeat/), 2 runs: run7 (with oracle POSTs) and run8 (fresh, no-oracle, probes pre-oracle). Both exit 0; router process-group SIGKILL on completion.
- Router log excerpt (run8): 13 entries [preset] bad01..bad12,goodone; listening http://127.0.0.1:50355.
- GET /v1/models (run8, pre-oracle): 13 entries ALL `status.value="unloaded"`, status.args = [binary, --host 127.0.0.1, --log-colors off, --port 0, --alias <id>, --model <slow|m1 path>], plus `preset` string, `architecture`, `source:"preset"`. No `failed`/`exit_code` before oracle.
- GET /props: `{"role":"router","max_instances":1,"models_autoload":true,...}` — matches counter PROPS shape.

### Oracle (run7, router child only)
- ORACLE POST bad01 http=500 dt=0.44s `{"error":{"code":500,"message":"model name=bad01 failed to load","type":"server_error"}}` — exactly the C1 oracle.
- ORACLE POST goodone http=200 dt=1.24s chatcmpl… usage completion_tokens 2.
- Post-oracle bad01 status: `value unloaded, failed:true, exit_code:1` (port 60783). goodone status `value loaded`.

### Probe verdicts
- Pre-oracle (run8, load ~50.9):
  - base expect=bad01 rc=2 MODEL_UNLOADED/router-model-invalid dt=0.85s
  - base expect='*' rc=0 MODEL_OK/router-unloaded-autoload dt=4.31s
  - M1 expect=bad01 rc=2 MODEL_UNLOADED/router-model-invalid dt=0.85s
  - M1 expect='*' rc=0 MODEL_OK/router-unloaded-autoload dt=0.76s
- Post-oracle (run7, load ~48.9): both revs bad01 → MODEL_UNLOADED/router-unloaded-failed dt 0.18/0.22s; '*' → MODEL_OK/expected-wildcard dt 0.20/0.22s (goodone now loaded, so '*' no longer goes through router-file check).

## Findings
- **NOTE** — Live /v1/models status.args shape matches the counter stub: stub builds `[abs, flag, path]` (round93-router-repeat.py:22-23,141-143); real router emits `[binary, --host, 127.0.0.1, --log-colors, off, --port, 0, --alias, <id>, --model, <abs path>]` (run8.log). `file_state` (kama-probe.sh:745-760) scans all PATH_FLAGS in args, so it finds the `--model` path regardless of prefix args; stub's `[abs,--model,path]` is a minimal instance of the same shape. No extra absolute path strings (e.g. /props?model=) are in args. Evidence: out/…/models-raw.json.
- **NOTE** — Probe verdicts pre-oracle agree with oracle for BOTH revisions despite repeat count 12: base already returns MODEL_UNLOADED/router-model-invalid at N=12 on this host. The round-92 SC02 flip required higher N / load to exhaust the shared 4s deadline; at 12 entries with 150k tensors, one parse (~0.85s) fits the budget, so base is also correct here. No flip observed at this N; the within-run timing contrast for '*' is the corroborating signal: base 4.31s vs M1 0.76s (load ~50), i.e. base spends the deadline re-parsing the same file for later entries while M1 memoizes by (dev,ino,size,mtime) (kama-probe.sh:580-593) and returns ~5.7× faster on the repeated-file wildcard scan. Single-entry bad01 dt identical (0.85s both).
- **NOTE** — After a real load attempt the router sets `failed:true, exit_code:1`; the probe then reports router-unloaded-failed (both revs), consistent with probe precedence (failed entries are skipped for file checks). The counter stub never emits `failed`, so this live-only transition is outside the frozen counter's shape but does not contradict it.
- Oracle comparison (pre-oracle state): bad01 oracle MODEL_UNLOADED (500) == probe MODEL_UNLOADED (both revs) → match. Goodone oracle MODEL_OK (200) not probed separately pre-oracle; '*' MODEL_OK/router-unloaded-autoload reflects that a loadable matching entry (goodone) wins among unloaded entries, consistent with round-89 rule.

## Deliverables (in .ufo/waves/round-93/w1/out/EX02LiveRouterRepeat/)
- run8.log — fresh pre-oracle run (raw router listing, probe table at both revs)
- run7.log — run with oracle POSTs (500/200 text, post-oracle statuses)
- models-raw.json — raw GET /v1/models body (13 entries, exact status.args shape)

## Risks/blockers
- Host load ~49-51 during probes; absolute dts are load-sensitive but the base-vs-M1 '*' ratio (4.31s vs 0.76s) is a within-run contrast on the same listing.
- N=12 may be below the base flip threshold on this host; the timing ratio corroborates the memo rather than a verdict flip.

VERDICT: holds — probe verdicts match the live oracle at both revisions; live status.args shape matches the counter stub; M1 memo cuts repeated-file wildcard scan 4.31s→0.76s with identical verdicts.
