# X1Observe — round 49 independent outside witness observer (lane kama)

**Verdict: no defect — my independently written observer, run against its own witnessed replays of receipt-1/2/3 at 74558c71, agrees with the C1 counter on every leg (3/3); each held server was the frozen b11909 binary as the listener of the announced port with the frozen stories260K.gguf, its own tokenizer round-tripped a fresh nonce against my own GGUF vocab decoding, and after release the pid was gone in 40 ms and the port refused.**

Measured commit `74558c71c38ceaeace15fd4cf8aa9d84977584b1` (base `438127bc…`, the round-48 closure). Counter `tools/round49-replay-witness-audit.py` at that commit hashes `86b4a40dd027ad7dd62c71c9694b354d52e88ffdfc04aa83a1bb648799f0d6c1` = the preregistration's `C1.counter_sha256`, so the frozen counter is what ran.

## 1. What I built (and why it is independent)

I wrote my own observer **from the frozen contract text, not from the counter's code**: the C1 docstring (witness contract + the four legs it names), the round-49 preregistration C1 statement/predicate, and the primary sources the build cites — llama.cpp `tools/server/README.md` at `caa8191df159…` (`POST /tokenize` `with_pieces`, `POST /detokenize`) and proc_pid_exe(5). Nothing in `tools/` is imported or executed by the observer to make a judgement; the lane tools are only the thing observed (the replay that holds the server).

| file (out dir) | sha256 | role |
|---|---|---|
| `observe-witness.py` | `28a03d70053a507c632d10ff3ddb32edf3d5c9216441b434033f2ae8b114fb7a` | outside observer: `/proc` + HTTP checks, writes `release`, sees the pid die |
| `run-witnessed.py` | `11a6cf0d8520faa6ff6aa1f2906d1d64f7235c012d2b6f507c5347f6782ee107` | starts the observer, then the lane replay tool with `--witness-dir` |
| `compare-verdicts.py` | `9d3c247dfb2f57b59ab2b35441f34fd67a1a21ba64d47b866f537cd1e2ead157` | parses the counter receipt text, tabulates agreement per leg |
| `selfcheck-observer.py` | `df3ec92c2213bf9155b7590ff0eeca62b13fb06e69d379f8b01adb9ea943ba32` | negative controls: does the observer reject a *false* witness? |

Checks the observer makes, all from outside the replay process:
- `ready_contract` — `ready.json` parses, schema `kama-live-witness/v1`, int port, int pid (contract in `tools/kama-llamacpp-live.py:285-297`, write at `:297`).
- `exe_digest` — sha256 of `/proc/<pid>/exe` == `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0`.
- `listen_ownership` — a `LISTEN` row on the announced port in `/proc/net/tcp{,6}` whose inode is one of `/proc/<pid>/fd`, corroborated by `ss -ltnp` naming the same pid.
- `model_digest` — the `-m` argument of `/proc/<pid>/cmdline` hashes to `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`.
- `nonce_tokenize` — nonce `kama witness <16 hex>` → `POST /tokenize {with_pieces:true, add_special:false}`; **every returned piece equals my own decoding of `tokenizer.ggml.tokens[id]`**, which I parse myself out of the GGUF named on the child's command line (U+2581 read as a space, `<0xNN>` as that byte), and the pieces join to the nonce (one leading space allowed).
- `nonce_detokenize` — `POST /detokenize {tokens:[ids]}` returns the nonce text (one leading space allowed, as the frozen contract says).
- `pid_gone_after_release` — I write `<wdir>/release` only after the observations above; the pid must then be absent (a reused pid is detected by a changed `/proc/<pid>/stat` starttime field), and the port must refuse.

## 2. Commands run (all from `/fast/scratch/hyaku/kama-r49/X1Observe`)

```
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
git -C $S/lane checkout --detach 74558c71c38ceaeace15fd4cf8aa9d84977584b1
  → rev-parse --show-toplevel = $S/lane; HEAD = 74558c71…  (fixture assertion made before any checkout)

python3 tools/round49-replay-witness-audit.py --repo $S/lane --tip 74558c71… --scratch $S/c1scratch --out counter-c1.json
  → EXIT=0
  → tip=74558c71c38ceaeace15fd4cf8aa9d84977584b1
  → witness=1 cap=1 newrow=1 witnessed=3/3 met=True

for n in 1 2 3: python3 out/X1Observe/run-witnessed.py --lane $S/lane \
    --receipt $S/lane/.ufo/waves/round-48/c2/live/receipt-$n.json \
    --work $S/work$n --wdir $S/w$n --observations $S/obs$n.json \
    --replay-receipt $S/replay$n.json --witness-timeout 60
  → replay 1: observe verdict=ok pid=1556681 port=42983 checks=7 failed=[] ; replay match=True refused=None mismatches=0 exit=0
  → replay 2: observe verdict=ok pid=1567559 port=46011 checks=7 failed=[] ; replay match=True refused=None mismatches=0 exit=0
  → replay 3: observe verdict=ok pid=1579527 port=38395 checks=7 failed=[] ; replay match=True refused=None mismatches=0 exit=0

python3 out/X1Observe/compare-verdicts.py --counter counter-c1.json --obs obs1..3 --replay replay1..3
  → counter: witness=1 cap=1 newrow=1 witnessed=3/3 met=True (vocab 512)
  → receipt-1/2/3: counter(exe/listen/model/nonce)=all ok  mine(exe/listen/model/tok/detok/pidgone)=[True×6] released=True replay_match=True agree=True
  → agreement 3/3 disagreements=0 ; EXIT=0

python3 out/X1Observe/selfcheck-observer.py --scratch $S
  → lying-witness: verdict=fail, checks ready=true/exe=false/listen=false/model=false/tok=false/detok=false/pidgone=false, release written
  → wrong-schema: verdict=ready-malformed, ready_contract=false, release written
  → selfcheck ok=True failures=0 ; EXIT=0
```

Every replay's own rerun receipt records the witness released: `{"pid":…,"port":…,"released":true,"schema":"kama-live-witness/v1","waited_ms":50}` and `outcome: pass` (`rerun-receipt-1..3.json`).

## 3. Per-receipt evidence (my observer, `observer-receipt-N.json`)

| receipt | ready pid/port | /proc exe (path under my own clone's replay work dir) | listen | model | nonce → tokens | detokenize | after release |
|---|---|---|---|---|---|---|---|
| receipt-1 | 1556681 / 42983 | `work1/server/llama-b11909/llama-server`, sha `35ac50fb…` | inode 624151109 shared with the pid's fd; `ss` names `pid=1556681,fd=3` | `work1/download/stories260K.gguf`, sha `270cba1b…` | `kama witness 7ded5ee9667b7d7a`, 24 tokens, 512-token vocab, every piece == my decode | `' kama witness 7ded5ee9667b7d7a'` | pid gone 40 ms; connect → `ConnectionRefusedError` errno 111; no LISTEN row left |
| receipt-2 | 1567559 / 46011 | `work2/…/llama-server`, sha `35ac50fb…` | inode 624185283; `ss` names `pid=1567559,fd=3` | `work2/download/stories260K.gguf`, sha `270cba1b…` | `kama witness 5ef6b331608461c5`, 25 tokens, every piece == my decode | `' kama witness 5ef6b331608461c5'` | pid gone 40 ms; refused errno 111 |
| receipt-3 | 1579527 / 38395 | `work3/…/llama-server`, sha `35ac50fb…` | inode 624229665; `ss` names `pid=1579527,fd=3` | `work3/download/stories260K.gguf`, sha `270cba1b…` | `kama witness c8a4538b9e62e580`, 24 tokens, every piece == my decode | `' kama witness c8a4538b9e62e580'` | pid gone 40 ms; refused errno 111 |

`ready_ms` (ready.json appearing after the observer started): 2310 / 2268 / 2329 ms; each observer run lasted ≈ 2.4 s including the post-release wait.

## 4. Comparison with the counter at 74558c71

The counter's receipt (its `--out` file is plain text):

```
witness=1 cap=1 newrow=1 witnessed=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: witness w1: pid 290497 port 46483 exe+listen+model ok, nonce 'kama witness 94608a589c1276ea' round-tripped
detail: witness w2: pid 293161 port 34929 exe+listen+model ok, nonce 'kama witness 281b08009f929289' round-tripped
detail: witness w3: pid 296687 port 32997 exe+listen+model ok, nonce 'kama witness 12222a076744aa2c' round-tripped
```

Agreement (`comparison.json`): **3/3 receipts, 0 disagreements** on exe, listen, model and the nonce round trip; both observers decoded a 512-token vocabulary from their own model download; both saw the witness released and the replay match. The counter's runs are independent instances (different pids/ports, its own witness dirs), which is why the table compares verdicts and not instance facts.

## 5. Observer discrimination controls (my instrument, not the lane)

A second observer is worthless if it passes everything, so `selfcheck-observer.py` drove it against a *lying* `ready.json` (pid of a live `sleep` that owns no listener; port answered by a loopback stub that returns 501 to POST) and a wrong-schema `ready.json`:

- lying witness → `verdict=fail`, `ready_contract=true`, `exe_digest=false`, `listen_ownership=false`, `model_digest=false`, `nonce_tokenize=false`, `nonce_detokenize=false`, `pid_gone_after_release=false`, and the observer still wrote `release` so no replay can be stalled by an observer fault.
- wrong schema → `verdict=ready-malformed`, `ready_contract=false`, `release` written.

The controls also proved the observer survives an unanswered port (I added `safe_post()` after the first draft crashed on it) — that first draft was my bug, fixed before any measurement above.

## 6. Observations, limits, risks

- **No lane defect found.** The build does what the frozen contract says at the measured commit: `hold_for_witness()` writes `ready.json` atomically with the llama-server child's own pid (`tools/kama-llamacpp-live.py:285-297`), the replay passes the directory through (`tools/kama-live-replay.py:275-279`), and the rerun receipt gains the `witness` block (`tools/kama-llamacpp-live.py:1860-1863`).
- **`/detokenize` returns exactly one leading space** for these nonces (`' kama witness …'`), because SPM marks a word start with U+2581 and my first nonce begins at a word boundary. That is the allowance the frozen contract already makes ("one leading space allowed"); the piece-level check is exact and my observer's join check accepts only that single leading space, not arbitrary whitespace.
- **What the witness proves and does not:** my observer confirms the *frozen binary* is the listener serving the *frozen model* and that its tokenizer answered a counter-chosen nonce. It does not by itself prove that binary came out of the freshly downloaded archive — that is the replay leg's member-digest check. This run adds path-level evidence for it (the exe path is inside the replay's own `workN/server/llama-b11909/` extraction tree, never the host install), but not a digest chain from the download.
- **Environment limits inherited by the observer:** Linux-only `/proc` reading, same-uid (a child the observer cannot read fails closed); the pid-reuse guard uses `/proc/<pid>/stat` field 22 (starttime).
- **The counter's `--out` receipt is text, not JSON.** No format is promised anywhere I could cite, so this is not a defect; `compare-verdicts.py` parses those `detail:` lines. If a machine-readable counter receipt is wanted later, that is a new wish, not a repair.
- I did not read the C1 counter's code (only its docstring, which the assignment names as the contract); any resemblance in leg choice is the contract's, not copied implementation.
- No tool installs or upgrades were needed (python3 stdlib + `ss`, both already present). No host service was started; each replay's llama-server was loopback-only, held by the witness, and torn down by the lane tool — `pgrep -af llama-server` shows none started by this seat afterwards.
- The lane stayed read-only: the only writes are this report and the out directory; the observed run used a `git clone --shared` at the measured commit, and scratch was removed after the receipts were copied here.

## 7. Artifacts (absolute paths)

```
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Observe.md
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Observe/observe-witness.py
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Observe/run-witnessed.py
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Observe/compare-verdicts.py
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Observe/selfcheck-observer.py
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Observe/observer-receipt-{1,2,3}.json
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Observe/replay-result-{1,2,3}.json
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Observe/rerun-receipt-{1,2,3}.json
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Observe/counter-c1.receipt.txt
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Observe/comparison.json
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Observe/selfcheck-observer.txt
```
