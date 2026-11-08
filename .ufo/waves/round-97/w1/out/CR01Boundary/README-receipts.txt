CR01Boundary — round-97 w1 receipts (seat CR01Boundary)
Lane kama-shokunin at e057166e; C3 inputs unchanged since freeze 9e605d41
(git diff 9e605d41 HEAD -- SKILL.md tools/round97-depth-boundary-audit.py tools/kama-probe.sh: empty).

AUDIT RUNS (exact):
  python3 tools/round97-depth-boundary-audit.py --repo . --rev 40763bd2ca1e3f99881247eaa9f5e3ef3b596653
    DEPTH_BOUNDARY97 rows=0 mismatches=1 met=False            exit=1
  python3 tools/round97-depth-boundary-audit.py --repo . --rev 9e605d41
    DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True    exit=0
  python3 tools/round97-depth-boundary-audit.py --repo . --rev e057166e
    DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True    exit=0
  python3 tools/round97-depth-boundary-audit.py --repo . --rev HEAD
    DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True    exit=0

PARSER RUNS (ROUTER_PY verbatim from HEAD, driver as router_file_states: python3 -c "$ROUTER_PY" body.json files 0):
  t833332-nd1-kv0.gguf     26,666,648 B  n_kv=0 -> 0 invalid   (table row 1 holds)
  t833332-nd1-kv2.gguf     26,666,682 B  n_kv=2 -> 0 -         (row 1 false: 4,999,996 + 8 = 5,000,004)
  t833332-nd1-kv1arch.gguf 26,666,691 B  n_kv=1 -> 0 -         (string KV: 4,999,996 + 5 = 5,000,001)
  t555555-nd4-kv0.gguf     31,111,104 B  n_kv=0 -> 0 invalid   (table row 5 holds)
  t555555-nd4-kv1.gguf     31,111,121 B  n_kv=1 -> 0 -         (row 5 false: 4,999,999 + 4 = 5,000,003)
  t700000-nd1-kv0.gguf     22,400,024 B  n_kv=0 -> 0 invalid   (C2 W11 class, control)
  t600000-nd5.gguf         14,400,100 B  first hdr nd=5 -> 0 invalid
      (probe:749-750 returns invalid after 7 steps; the table rule prices 4+600,000*10 = 6,000,004 -> "-")

INSTRUMENT TEST (fixture repo under scratch; own git init; toplevel asserted; SKILL.md = HEAD bytes):
  probe patched once: `skip(u64())  # name` followed by one extra `need(0)` per header (6 + nd)
  python3 tools/round97-depth-boundary-audit.py --repo <fixture> --rev HEAD
    DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True    exit=0   <-- green while rows are false
  patched parser t833332-nd1-kv0.gguf -> 0 -   (real -> 0 invalid; 4 + 833,332*7 = 5,833,328 > MAX_STEPS)
  patched parser t700000-nd1-kv0.gguf -> 0 invalid (4,900,004 <= MAX_STEPS; C2 W11 expectation preserved)

Fixture geometry:
  GGUF v3 preamble 24 B: magic(4) + ver(4) + n_tensors(8) + n_kv(8)
  tensor header 24 + 8*nd B (name len 8 + name 0 + nd 4 + dims 8*nd + type 4 + offset 8)
  u32 KV 17 B -> 4 steps (probe:734-736,744); string KV 43 B -> 5 steps
  steps = 4 + KVwork + T*(5+nd); need() raises when steps > MAX_STEPS, so exactly 5,000,000 is decidable.

Environment: python3 (system), git read-only. No installs, no pacman, no sysctls, no kills.
Scratch /fast/scratch/hyaku/kama-r97/CR01Boundary deleted before yield; this directory holds the receipts.
