# Round 49 K1Design — C1 witness design critic

Verdict: **the C1 witness proves the round-48 no-server-replay class is closed (a frozen-binary server with a frozen-hashing model file was alive and answering a fresh nonce), but it does not prove the observed server is the process whose captures the rerun receipt holds, nor the model bytes the server loaded; three small, low-risk corrections for the next counter are specified.**

## 1. What I ran (evidence)

Scratch: `S=/fast/scratch/hyaku/kama-r49/K1Design` (rm -rf'd at the end). Lane clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` (HEAD `122c4ee9`; measured commit `74558c71c38ceaeace15fd4cf8aa9d84977584b1` present in the object store).

**C1 on the build tip** (frozen counter, run from my clone with `--scratch $S`):

```
$ python3 $S/lane/tools/round49-replay-witness-audit.py --repo $S/lane \
    --tip 74558c71c38ceaeace15fd4cf8aa9d84977584b1 --scratch $S --out $S/c1-receipt.txt
exit=0
tip=74558c71c38ceaeace15fd4cf8aa9d84977584b1
witness=1 cap=1 newrow=1 witnessed=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: witness w1: pid 262518 port 36909 exe+listen+model ok, nonce 'kama witness 4fcaff381a97bfd3' round-tripped
detail: witness w2: pid 263718 port 46355 exe+listen+model ok, nonce 'kama witness 303bdbaab93dce4a' round-tripped
detail: witness w3: pid 266857 port 33111 exe+listen+model ok, nonce 'kama witness 50afd92ca4ef1ebf' round-tripped
detail: cap sparse-1e15: exit 2 setup_error 'provenance-member-sparse' executed=False seconds=0.1 ok
detail: cap member-is-server-control: exit 2 setup_error 'server-exited-early-rc3' executed=True seconds=0.1 ok
detail: newrow: 2 rows new since base; 1 name the README at caa8191df159 and /tokenize: ['| S494 |']
Wall time: 12.30 seconds
```

**Honest standalone witness run** (replay tool directly, receipt-1, to harvest the artifacts the counter leaves behind):

```
$ python3 tools/kama-live-replay.py --receipt .ufo/waves/round-48/c2/live/receipt-1.json \
    --work $S/work1 --out $S/replay1.json --witness-dir $S/wd1 --witness-timeout 600
replay match=True refused=None mismatches=0 exit=0
$ cat $S/ready1.json
{"schema": "kama-live-witness/v1", "port": 40733, "pid": 286524, "written_utc": "2026-10-26T23:27:20.927Z"}
```

Rerun receipt (`$S/work1/rerun-receipt.json`): `child_pid = 286524`, `port = 40733`, `witness = {schema: kama-live-witness/v1, pid: 286524, port: 40733, released: true, waited_ms: 100, dir: ...}`, schema v5, outcome pass. So **in an honest run ready.json pid == receipt child_pid == witness.pid == port**; a continuity assertion is implementable with zero false positives.

**Same-vocab adversarial model construction** (demonstrates what the nonce leg binds):

```
$ python3 - "$S" <<'EOF'   # imports the counter's own gguf_tokens()
real  sha256 = 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d (= MODEL_SHA)
crafted sha256 = eacee0757678bdab2676bc02800f72484ea3644479ef45c802eb068f142c59b3 (!= MODEL_SHA)
crafted size = 6470 bytes, real = 1185376 bytes
same tokens list as real model: True (512 tokens, byte-identical)
EOF
```

## 2. What the witness does prove (balanced)

- The rerun server is a real process whose `/proc/<pid>/exe` hashes to the frozen b11909 digest (`round49-replay-witness-audit.py:260-262`), which owns a LISTEN socket on the announced loopback port (inode intersection, `:263-265`), was launched with `-m` pointing at a path whose **current on-disk bytes** hash to the frozen model (`:266-275`), and answers a fresh 64-bit nonce through POST /tokenize (with_pieces) and /detokenize with every returned piece equal to the counter's own GGUF vocab decode, then exits after release and the port refuses (`:276-329`). This closes the round-48 K2Cheat/K2Urlswap class (a replay that never ran a server) — the core R5 objective.
- The cap leg refuses a sparse / size-mismatched archive member **before** hashing a byte of it (`kama-llamacpp-live.py:258-267`; confirmed `provenance-member-sparse` in 0.1 s).
- Disclosed limits hold and are accepted: host-copy of the same binary still passes (no archive-origin proof at witness time); Linux /proc only; an unreadable process fails closed.

## 3. Findings (defect -> smallest correction -> next counter)

### F1 — The observed server is never bound to the receipt's claimed process (no pid continuity)
- Defect: `tools/round49-replay-witness-audit.py:306-329`. `witness_one()` takes `ready["pid"]`/`ready["port"]` and observes them (`:310-311`), then checks only `rr["witness"]["released"] is True` (`:324-326`). It never compares `ready["pid"]` with the rerun receipt's `child_pid` (or `witness.pid`). `grep -n child_pid tools/round49-replay-witness-audit.py` → no matches. The replay tool's `compare()` also deliberately treats `child_pid`/`port` as instance facts excluded from the stable projection (`tools/kama-live-replay.py:168-195`; its own selftest `compare-instance-only`, `:413-428`, shows two receipts differing only in `child_pid`/`port` compare equal).
- Counterexample: a harness can run the capture session (checks, captures, probes), tear that server down, then start a **fresh** b11909 server on the same port for the witness window. Every individual observable passes (exe, listener, -m file hash, nonce), `match=True` still holds because the rerun receipt's stable fields are unchanged, and the counter records "witness … ok" while the receipt's captures were produced by a different process. The fully-malicious variant — capture session never run, captures copied from the original round-48 receipt, only a witness server started — passes for the same reason; `compare()` accepts byte-equal captures from any earlier run.
- Impact: the claim "the server the rerun receipt holds was the witnessed server" is not established; only "a frozen-binary server was witnessed" is. Axis: operability (claim C1 predicate "finds the frozen llama-server binary executing as the listener … with the frozen model" is individually true, but the predicate's conflation of witness and captured server is unproven).
- Smallest correction (next counter only, ~4 lines after `:323`): assert `ready["pid"] == rr["child_pid"] == rr["witness"]["pid"]` and `ready["port"] == rr["port"] == rr["witness"]["port"]`; append to `probs` on mismatch. Verified to hold in the honest run (section 1), so no false positives.

### F2 — The nonce challenge is not correlated with the receipt (session binding)
- Defect: the counter's nonce (`:276`) proves liveness to the counter alone; the live tool never sees it, so nothing in the receipt can be checked against the exchange. Even with F1 fixed, a forger can report the witness server's `child_pid` while copying old captures, because nothing ties the receipt's content to the challenged session.
- Smallest correction (needs a tiny **tool** change plus a counter change; belongs in next round's build, not the frozen counter): the counter already writes `D/release` with text (`:312-313`) — include the nonce in that text; `hold_for_witness()` (`kama-llamacpp-live.py:280-300`) already reads release existence — record the release content (or the nonce substring) in the `witness` block; counter asserts `rr["witness"]["nonce"] == nonce`. A forger outside the held session cannot know the per-run nonce. Cost: ~2 lines in each file.

### F3 — `-m` path hashing proves the on-disk file, not the loaded bytes
- Defect: `tools/round49-replay-witness-audit.py:269-273` reads the cmdline `-m` argument and hashes the **file at that path at witness time** (`sha_file(mpath)`). That is disk state at observation time, not what the server opened/mapped at load.
- Counterexample (local, demonstrated): a 6,470-byte GGUF carrying the byte-identical `tokenizer.ggml.tokens` array (built with the counter's own decoder) hashes `eacee075…` ≠ `MODEL_SHA` yet decodes the exact same 512-token list, so the nonce/vocab leg cannot distinguish it from the frozen model. Any same-vocab re-quantization or re-packaging behaves identically. Two residual holes stay open: (a) swap-back TOCTOU — replace the file between the live tool's pre-start hash and the server's open, restore it before the witness hash, and the on-disk digest is frozen while the server loaded other bytes; (b) the server may have opened a different path/fd than `-m`.
- Impact: the predicate's "with the frozen model" is only a *file-at-path-at-witness-time* statement; tokenizer identity is content-bound, but weights are not.
- Smallest correction (next counter only, counter-side): additionally bind the model inode — `stat` the file at the `-m` path and require `(st_dev, st_ino)` to appear in `/proc/<pid>/maps` (mapped region) or `/proc/<pid>/fd` of the witnessed pid. This ties the open/mapped object to the exact inode whose current bytes hash to the frozen digest. Residual accepted limit (document it): in-place mutation *during* the load window; it is already double-sampled by the live tool's pre-start `model-digest-mismatch` and post-teardown `model_unchanged` rehash (`kama-llamacpp-live.py:1658-1659,1981-1990`) plus the witness-time hash.

### F4 — Nonce strength: adequate; document it
- `secrets.token_hex(8)` (`:276`) = 64 random bits, minted after readiness, single-use, sent only to a socket proven owned by the pinned pid. Online guessing is infeasible; transcript substitution would require answering from a socket the counter proved belongs to the pid, i.e. running the pinned binary. No change required beyond documenting "16 hex = 64 bits" in the counter docstring; the F2 echo (nonce in witness block) doubles as the receipt-side record.

### Minor
- `ready.json`'s `schema` field is never validated (`:306-308`); F1's equality checks implicitly validate pid/port. Optionally assert `schema == "kama-live-witness/v1"`.

## 4. Tooling

No tools installed or upgraded (stdlib only; RULES.md read). Network used: github.com + huggingface.co for the counter (75 MB × 3 replays, ~1 MB model) and for the standalone replay. No llama-server leftovers from my runs (only a pre-existing `K1Fresh` seat's processes remain, untouched).

## 5. Artifacts written

- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K1Design.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K1Design/c1.out` (counter stdout)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K1Design/c1-receipt.txt` (counter --out)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K1Design/ready1.json` (witness ready.json)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K1Design/rerun-receipt.json` (honest v5 rerun receipt with witness block)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K1Design/replay1.json` (replay result JSON)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K1Design/crafted-same-vocab.gguf` (F3 construction)
