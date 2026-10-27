# J1NoEnv — C1 env-leg ablation control (round 50, lane kama)

**Verdict: the frozen C1 counter's env predicate is live and load-bearing — with `live_env()` reverted to `dict(os.environ)` (live child inherits the full environment) at fixture commit `e8bfe4fb1e4e36a814e076e4236d30a57f3f24f9`, the frozen counter returns `bind=0 teardown=1 newrow=1 bound=0/3 met=False` (exit 1), failing all three bind legs on exactly one predicate, `server parent ... carries the planted KAMA_R50_CANARY`; the paired run at the unpatched build `97c864b…` in the same clone returns `bound=3/3 met=True` (exit 0).**

## Axes / scope

- Operability (C1, 8→8): the round-49 R1 closure claimed "PYTHONPATH/sitecustomize hijack of the counter's inherited environment met the counter" was closed by allow-listing the live child's environment (S497/S496 sourced). This seat asks the ablation question: if that allow-list is removed, does the counter notice? It does, per-leg.
- No lane file was edited; the patch exists only in a scratch fixture clone. Nothing was committed, added, checked out or reset in `/home/vgpnk/Projects/shokunin/kama-shokunin`.

## Setup (observable identity)

```
$ git -C kama-shokunin log -1 --format='%H %ad %s' 97c864bead3ee4a2f629574e77263d33834ec98a
97c864bead3ee4a2f629574e77263d33834ec98a Mon Oct 26 21:20:51 2026 -0300 round-50: build - replay isolation + parent-death teardown, live model-mapping record, append-only-audit v5 (birth-DAG origin, fence-aware sections, CRLF-normalized keys), S496-S498
$ sha256sum kama-shokunin/tools/kama-live-replay.py kama-shokunin/tools/round50-replay-bind-audit.py
d5c58972c0fd8f818b8dd2bd81f6cbc3a87c7f23b65805a804bf09b579a5a239  tools/kama-live-replay.py
ff6ac2ace541ea35a4d240ceebb019653c11a2a08c025e514770f3f94a9c5e89  tools/round50-replay-bind-audit.py
```

Scratch clone (`git clone --shared` of the lane) + fixture clone at the build commit; `git rev-parse --show-toplevel` printed `/fast/scratch/hyaku/kama-r50/J1NoEnv/fixture` before the fixture commit (asserted; printed `toplevel-ok`).

Ablation patch (`ablation.diff`, the whole delta — +2/−1 lines in one file):

```diff
--- i/tools/kama-live-replay.py
+++ w/tools/kama-live-replay.py
@@ -110,7 +110,8 @@ def set_own_pdeathsig(sig=signal.SIGTERM):
 
 
 def live_env(work):
-    env = {k: os.environ[k] for k in LIVE_ENV_KEYS if k in os.environ}
+    # J1NoEnv ablation: the live child inherits the replay's whole environment.
+    env = dict(os.environ)
     env["TMPDIR"] = os.path.join(work, "tmp")
     return env
```

`python -I` on the live child was kept (`tools/kama-live-replay.py:320` at the build: `argv = [sys.executable, "-I", live, …]`), so the only change is which environment names reach the live tool. Fixture commit identity (never a fleet/lane identity):

```
e8bfe4fb1e4e36a814e076e4236d30a57f3f24f9 J1NoEnv Fixture <j1noenv-fixture@invalid> J1NoEnv ablation fixture: live child inherits the full environment (live_env reverted to dict(os.environ), -I kept)
git -C fixture diff --stat 97c864b… e8bfe4f…
 tools/kama-live-replay.py | 3 ++-
 1 file changed, 2 insertions(+), 1 deletion(-)
sha256(tools/kama-live-replay.py at e8bfe4f) = 52e99507b96d3f5b9901ee1c9db592fa35ba2a09fc1de5ba758ff5032d67315d
```

## Ablation run (frozen counter, unmodified)

```
$ TMPDIR=$S python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-replay-bind-audit.py \
    --repo $S/fixture --tip e8bfe4fb1e4e36a814e076e4236d30a57f3f24f9 --scratch $S --out …/c1-ablation-receipt.txt
tip=e8bfe4fb1e4e36a814e076e4236d30a57f3f24f9
bind=0 teardown=1 newrow=1 bound=0/3 met=False
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: server parent pid 2066347 carries the planted KAMA_R50_CANARY
detail: bind b2: server parent pid 2087662 carries the planted KAMA_R50_CANARY
detail: bind b3: server parent pid 2106828 carries the planted KAMA_R50_CANARY
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 3 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']
COUNTER EXIT=1
```

Wall time 15.9 s. Receipt kept verbatim at `c1-ablation-receipt.txt` in this directory.

Reading of the receipt:

- `bind=0` because `bound == len(RECEIPTS)` (3) is required (`tools/round50-replay-bind-audit.py:586`); each leg contributes a separate prob list, and every one of the three contains exactly one prob — the canary.
- The canary is read from `/proc/<pid>/environ` of the server **and its parent** (`tools/round50-replay-bind-audit.py:353-358`). Only the parent line fired, i.e. the leak is one hop: counter env → invoker → replay → live tool. The server's own environ stayed clean because `kama-llamacpp-live.py` scrubs the server's env to `CHILD_ENV_KEYS` (`tools/kama-llamacpp-live.py:125`, `:1858-1861`). So the env leg is caught strictly where the round-49 R1 defect was (the live tool's inherited environment), not via the server.
- No other bind prob appears in any leg: exe digest, listener ownership, nonce round-trip, server-descent, `child_pid == observed pid`, and model mapping all passed in the ablation too (they are the same code path that reports success in the baseline below; on failure only the prob list is printed, so this is absence-of-prob evidence, backed by the paired run's success lines).
- `teardown=1` (0.10 s, port refuses) and `newrow=1` are unchanged by the env leg — the ablation isolates the env predicate from the pdeathsig/teardown mechanism and from S496.

## Paired baseline (same clone, unpatched build, same counter)

```
$ TMPDIR=$S python3 …/round50-replay-bind-audit.py --repo $S/fixture --tip 97c864bead3ee4a2f629574e77263d33834ec98a --scratch $S --out …/c1-build-baseline-receipt.txt
bind=1 teardown=1 newrow=1 bound=3/3 met=True
detail: bind b1: pid 2218471 port 46101 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 75925203 recorded, nonce 'kama witness 775d2c0143f45158' round-tripped
detail: bind b2: pid 2229845 port 42817 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1956276851 recorded, nonce 'kama witness 68de9d2268737951' round-tripped
detail: bind b3: pid 2239269 port 35481 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 76401381 recorded, nonce 'kama witness bd35fa07371be28b' round-tripped
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.20 s alive [] port refuses ok
detail: newrow: 3 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']
BASELINE EXIT=0
```

Wall time 24.4 s. Same clone, same scratch root, same counter file, same model/server acquisition; the *only* difference between the two runs is the `live_env()` body. Bind flips 3/3 → 0/3, exit 0 → 1, `teardown`/`newrow` do not move. That is the discriminator this ablation control exists to measure, and it is not vacuous.

## Findings (reports, not patches — nothing frozen was edited)

1. **J1-F1 — the `sitecustomize` marker half of C1's two-canary design is inert in every arm.** The marker only stamps when a Python interpreter imports `sitecustomize` from `PYTHONPATH`; every Python in the C1 pipeline is started with `-I`: the invoker and replay (`round50-replay-bind-audit.py:402`, both `-I`), and the live child (`kama-live-replay.py:320`), and `llama-server` is not Python. Consequence: the ablation *does* leak `PYTHONPATH` into the live child, and the marker still stayed empty (no `planted sitecustomize imported by …` prob in the ablation receipt) — so the marker can never move any C1 leg, at the build or away from it. The `KAMA_R50_CANARY` env-key check is the single load-bearing half. Not a counter defect for the current verdicts (bind=0 is reached by the canary leg alone), but the docstring's "a marker line or a canary … " claim (`round50-replay-bind-audit.py:34`) overstates coverage; a future counter revision could either drop the marker or launch one non-`-I` interpreter to give it discriminating power. Command that shows the flags: `grep -n '"-I"' kama-shokunin/tools/kama-live-replay.py` → line 320, and `grep -n '"-I"' tools/round50-replay-bind-audit.py` → invoker/replay argv.
2. **J1-F2 — the replay's rerun receipt self-reports `live_child.isolated: True` unconditionally** (`kama-live-replay.py:311`: `res["live_child"] = {"isolated": True, "env_keys": sorted(env), …}`). Under this ablation that field is false while still reading `True`, and `env_keys` would list the two canary names (code read; the counter deletes its scratch, so the ablation receipt itself was not retained). C1 does not read that field — it witnesses `/proc/<pid>/environ` directly — which is why the ablation is caught. Recorded so no future lane cites the receipt's `isolated` flag as evidence of isolation.
3. **Scope note on what this control proves.** It proves the counter observes the env leg through the server's parent and that removing the allow-list flips bind to 0/3. It does not test the inverse shape (an allow-listed env that is nevertheless hijacked, e.g. a same-named var passed through `PATH`/`HOME`), which the counter's env-key test cannot see; that is round-49 R1's residual surface and is not measured by J1NoEnv.

## Host observations (not mine, no action taken)

`pgrep -af llama-server` / `pgrep -af kama-live-replay` at the end of my runs show live replay/server processes under sibling scratch trees `/fast/scratch/hyaku/kama-r50/X15NoHarm2/r48/…` (live tool pid 2292306, replay pid 2279842) and `/fast/scratch/hyaku/kama-r50/J3NoMapping/c1b/…` (invoker pid 2284611, replays 2284676 and others). None belong to this seat — no process path contains `J1NoEnv`; my counter runs tore their own trees down (verified after both runs). Left untouched per leaf bounds.

## Tooling

No tools installed or upgraded (no pacman — host-wide pause; no uv/npx/binary fetches). Only the pre-existing `python3`, `git`, and the frozen counters were used. Counter-fed downloads: the counter's own frozen model (huggingface.co) and server assets (github.com) per leg, as designed.

## Files

- `c1-ablation-receipt.txt` — verbatim frozen-counter output at the ablation tip (exit 1).
- `c1-build-baseline-receipt.txt` — verbatim frozen-counter output at the build tip in the same clone (exit 0).
- `ablation.diff` — the complete +2/−1 fixture delta.
- `fixture-commits.txt` — build commit and fixture commit identities.
