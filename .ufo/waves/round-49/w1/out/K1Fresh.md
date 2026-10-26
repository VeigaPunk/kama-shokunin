# K1Fresh — round-49 fresh-session witnessed replay (C1 operability)

**Verdict: PASS.** A fresh session using only SKILL.md, the `--help` of `kama-live-replay.py`/`kama-llamacpp-live.py`, and the round-48 receipt can run a witnessed replay of `receipt-1.json`, observe the held server with independent commands (exe digest, listener inode ownership, model digest, nonce round-trip), release it, and get `match=True exit=0` with `witness.released=true`. The guesses I had to make are small, all protocol-level, and each has a proposed SKILL.md how-to line (draft in `skilling-draft.md`).

## What I ran (fresh materials only)

Fresh sources used: `SKILL.md` (lanes; zero "witness"/"ready.json" occurrences — confirmed by `grep -n -i -E "witness|ready.json|hold_for_witness" SKILL.md` → no hits), `python3 tools/kama-live-replay.py --help`, `python3 tools/kama-llamacpp-live.py --help`, receipt `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/c2/live/receipt-1.json` (v5, outcome pass, `provenance.verified` member `35ac50fb…`, model `270cba1b…`).

```
S=/fast/scratch/hyaku/kama-r49/K1Fresh; mkdir -p "$S/home" "$S/work" "$S/witness"; export TMPDIR="$S"
HOME=$S/home python3 <scratch-clone>/tools/kama-live-replay.py \
  --receipt <lane>/.ufo/waves/round-48/c2/live/receipt-1.json \
  --work $S/work --out $S/rerun.json --witness-dir $S/witness
```
(no `--witness-timeout`; documented default 120 s used)

## Evidence (all commands ran, outputs captured; full transcript in `witness-observation.txt`)

| Check | Command | Observed | Expected (from receipt) | Result |
|---|---|---|---|---|
| ready.json | poll `$S/witness/ready.json` | `{"schema":"kama-live-witness/v1","port":35223,"pid":251045,...}` | {port,pid} of server child | OK |
| exe digest | `sha256sum /proc/251045/exe` | `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` | `provenance.verified.member_sha256` | MATCH |
| model digest | `tr '\0' ' ' < /proc/251045/cmdline` → `-m <model>`; `sha256sum <model>` | `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` | `provenance.verified.model_sha256` | MATCH |
| listener ownership | `ss -ltnp \| grep ":35223 "`; `grep "0100007F:8997 00000000:0000 0A " /proc/net/tcp`; `ls -l /proc/251045/fd` | `LISTEN 127.0.0.1:35223 users:(("llama-server",pid=251045,fd=3))`; row inode `619047879`, uid `1000`; fd `3 -> socket:[619047879]` | LISTEN socket inode in `/proc/<pid>/fd` | MATCH |
| nonce round-trip | `curl -s 127.0.0.1:35223/tokenize -d '{"content":"<nonce>","with_pieces":true}'`; POST `{"tokens":[ids]}` to `/detokenize` | tokenize http=200; pieces all non-empty; `''.join(pieces)` == detokenized content == `" "+nonce` | nonce round-trips, one leading space allowed | MATCH |
| release | `touch $S/witness/release` | replay log `replay match=True refused=None mismatches=0 exit=0`; `rerun.json` `match:true, live_exit:0`; rerun receipt `witness:{released:true, waited_ms:27403}`, `outcome:pass`, checks 11/11 | exit 0, match true, witness.released true | MATCH |
| teardown | `kill -0 251045`; `curl 127.0.0.1:35223/health` | pid gone; http=000 / rc=7 refused | pid gone, port refuses | MATCH |

The pid/port I observed match the witness block in the rerun receipt (`witness.pid=251045`, `witness.port=35223`). My observations cover all four counter legs (`tools/round49-replay-witness-audit.py` docstring lines 40-52: exe, listen, model, nonce; line 48 "one leading space allowed").

## Guesses a fresh session had to make (each removed by a proposed how-to line)

1. **The witness capability is invisible in SKILL.md** — zero hits for `witness`/`ready.json`; only `--help` reveals it. → how-to: the exact command line and the ready.json protocol (write `ready.json` {port,pid} after checks, hold until `release`, default 120 s).
2. **Expected digests**: from the receipt's own `provenance.verified` (`member_sha256`, `model_sha256`) — inferable but worth one line (plus the pinned b11909 values).
3. **`/proc/net/tcp` byte-swaps the local IPv4** — the listener row reads `0100007F:8997`, not `7F000001:8997`; my first grep for `7F000001:8997` found nothing. → how-to shows the swapped form and the inode/Fd cross-check.
4. **`/detokenize` rejects the `with_pieces` objects** — posting `{"tokens":[{id,piece},...]}` returned `HTTP 400 Bad Request`; the body must be `{"tokens":[plain int ids]}`. → how-to states the payload shape.
5. **Leading-space convention**: detokenized content equals the nonce only with one leading space (the byte-pair tokenizer prepends `" "` to the first word); `''.join(pieces)` equals it exactly. → how-to says "one leading space allowed", matching the counter.
6. **Release filename and timing**: `touch <witness-dir>/release`; observe before releasing; late release → `released:false`. → how-to line.
7. **HOME isolation** (`HOME=$S/home`, `TMPDIR=$S`): given in the seat spec, not in SKILL.md; the graded counter runs under scratch HOME/XDG_CACHE_HOME/TMPDIR. → how-to line.

## Defects / findings

- **SKILL.md has no round-49 witness section** (the two counters' absence from the instrument registry is a known L1/scribe item; not re-reported). My scoped addition is the how-to subsection; full proposed text in `skilling-draft.md` (append after line 1484).
- No defect found in the tools: `--help` is accurate; ready.json/release semantics match behavior; rerun receipt's witness block is consistent with what I observed; teardown verified.

## Deliverables

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K1Fresh.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K1Fresh/ready.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K1Fresh/rerun.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K1Fresh/rerun-receipt.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K1Fresh/receipt-1-round48.json` (cited input)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K1Fresh/witness-observation.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K1Fresh/skilling-draft.md`

Scratch `/fast/scratch/hyaku/kama-r49/K1Fresh` removed; no leftover llama-server processes from this run (verified `pgrep -af llama-server`).
