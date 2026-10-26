# K2Cheat — C2 shortcut attack on the frozen counter (round 48, lane kama)

Verdict: **the frozen C2 counter is satisfiable without running the recorded lifecycle** — a 19-line change to the committed replay tool alone flips all seven legs to `met=True` (fixture A), and the "three receipts" are unconstrained duplicates (fixture B).

## Setup (evidence chain)

- Scratch: `S=/fast/scratch/hyaku/kama-r48/K2Cheat` (exported as `TMPDIR`).
- Lane clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`; tip verified
  `380bcdff9c8af06997c482f6eb03db926a794a2b` (the build landing commit).
- No tools installed/upgraded (system `python3` + `git` only; no pacman/uv/npx).
- Tool hashes at tip (git show | sha256sum):
  - `tools/kama-llamacpp-live.py` = `1e5ea0fde985367d9d6335eae3825068e64063f032bbbc59fc8909e7b7f9a6d2`
    (= the `tool.sha256` embedded in every v5 receipt, e.g. `receipt-1.json:575-578`)
  - `tools/kama-live-replay.py` = `69837013ec64b78a192e91b5b6a604a7437890c9e5a9c21dd175a0e87eb8b15f`
  - counter `tools/round48-live-replay-v5-audit.py` = `6bc16e2532469f160cee59c78103688b8d16a9713fdb4d3c255f894975fb0c09`
    (matches preregistration `counter_sha256`).

Baseline on the genuine build tip (for reference):

```
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round48-live-replay-v5-audit.py \
    --repo $S/lane --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch $S
receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True
tip=380bcdff9c8af06997c482f6eb03db926a794a2b started=2026-10-26T22:34:46.282004+00:00
$ echo $? → 0   (wall 12.51 s)
```

## Attack A — synthesized rerun: rewrite `tools/kama-live-replay.py` (SHORTCUT: yes, zero servers)

Fixture A (fresh `git init` + `remote add lane` + fetch of the base; identity `K2Cheat-fixture`; commit
`4c3481188ffc199dc6b0eec84359cc24fbf1e7de`). It changes only one committed file, the replay tool.

Change: replace `kama-live-replay.py:242-257` (the `subprocess.run(argv, …)` block that executes the live
tool and thus the server) with a synthesis block at `:242-276` (exact diff: `out/K2Cheat/fixtureA-replay-synth.patch`,
42 lines). The replaced code keeps the genuine, unmodified top of `replay()` — `provenance()` (`:96-123`),
`acquire()` network fetch + sha256 of both pinned inputs (`:218-219`), archive extraction and member digest check
(`:220-230`) — so every refusal path is byte-identical; only the execution step is removed. The synthesis then:

- deep-copies the original receipt (`rr = _copy.deepcopy(rec)`),
- rewrites only instance paths: `server.realpath`/`server.arg` = the extracted, digest-verified server binary;
  `model.path`/`model.arg` = the downloaded GGUF,
- stamps `started_utc`/`ended_utc` = now,
- writes it as the rerun receipt and reports `match=True` (`compare()` is trivially equal on a copy).

Counter run against fixture A:

```
$ python3 …/round48-live-replay-v5-audit.py --repo $D --tip 4c3481188ffc199dc6b0eec84359cc24fbf1e7de --scratch $S
receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True
tip=4c3481188ffc199dc6b0eec84359cc24fbf1e7de started=2026-10-26T22:35:11.319648+00:00
$ echo $? → 0   (wall 13.26 s)
```

No llama-server is ever executed: after the patch, `replay()` contains no `subprocess.run` call (verify
`fixtureA-replay-synth.patch`). Why each leg still passes:

- `receipts` — receipts untouched; structure valid (this leg is disclosed as structural in the preregistration, `limits`).
- `recordcheck` — the live tool is untouched at tip; genuine stub behavior (counter `:289-342`).
- `replay` — counter checks at `:402-434` are all satisfied by the synthesized copy: exit 0, `j.match=True`,
  `refused=None`, rr schema v5/outcome pass, `started_utc >= t0` (stamped), frozen model commit (copied),
  `server.realpath`/`model.path`/`inputs.archive` under the counter scratch hashing to the receipt's `server.sha256`,
  `MODEL_SHA`, `ASSET_SHA` (the files are the genuine downloaded bytes), evaluated checks equal (copied),
  stable projection equal (copied).
- `tamper` / `urlswap` — these legs run the same replay tool on mutated receipt copies; the refusal happens in the
  unchanged `acquire()`/`provenance()` steps before the replaced block (exit 2 `digest-mismatch`, no rerun),
  so they pass exactly as in the baseline (counter `:500-543`).
- `compare` — `--compare` mode is untouched.
- `newrow` — base commit already carries the SOURCES row.

Note the r47-D1 hardening (`started_utc` bound to the counter start) is defeated: the copy stamps "now", and the
counter cannot observe that no server ran because it trusts the committed runner's output.

## Attack B — one recording duplicated as three receipts (evidence-origin shortcut; not a lifecycle shortcut)

Fixture B (same base, commit `4b3a21787d484585b8fb32b19375ea433b37a1a7`): `receipt-2.json` and
`receipt-3.json` replaced by byte-identical copies of `receipt-1.json` (all three sha256
`164a4d9d232853deb35a64d9127382c7bb8ba8536b99f02c850eb2062f291344`); tools untouched.

```
$ python3 …/round48-live-replay-v5-audit.py --repo $D --tip 4b3a21787d484585b8fb32b19375ea433b37a1a7 --scratch $S
receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True
tip=4b3a21787d484585b8fb32b19375ea433b37a1a7 started=2026-10-26T22:35:46.990308+00:00
$ echo $? → 0   (wall 13.08 s)
```

The genuine receipts are pairwise distinct (child_pid 611093/612878/615051; ports 33779/41891/45023; started
22:26:23.509Z/.935Z/24.331Z, from `receipt-{1,2,3}.json`), so a uniqueness check is feasible. The counter has
none; its `receipts` leg (`:229-261`) never compares receipts to each other. Because the replay leg genuinely
re-runs each duplicate (real downloads, real server), B is not a "skip the lifecycle" shortcut — but it lets the
claim's "three receipts" be one recorded session replicated.

## What would catch each

1. **Pin the executable surface hash (catches A, and the analogous live-tool hijack).** The counter already pins
   asset/model/member digests. Extend in the same style: `main()` hashes `tools/kama-live-replay.py` and
   `tools/kama-llamacpp-live.py` at tip (from the same `git archive` tree it already extracts, `:360-368`) and
   fails the `replay`/`recordcheck` legs if they differ from the frozen hashes; additionally `check_receipt`
   (`:229-261`) should require `rec.tool.sha256 ==` the frozen live-tool hash — a field that already exists in
   every receipt but is never read. Frozen values today: live `1e5ea0fde…a6d2` (== every receipt's `tool.sha256`),
   replay `69837013ec64b78a192e91b5b6a604a7437890c9e5a9c21dd175a0e87eb8b15f`. This would also have broken the
   r47-relabel control (its fabricated receipts carry the v4 tool hash with `1e5ea0fde…a6d2`).
2. **Receipt-uniqueness leg (catches B).** In `check_receipt`/`receipts`, require pairwise-distinct
   `(child_pid, port)` and strictly increasing `started_utc` across `RECEIPTS`.
3. **Complementary in-loop guards (do NOT catch a deliberately modified runner).** A counter-supplied nonce that
   must travel through a live server interaction (e.g. the alias field: counter appends a random suffix to the
   alias and requires the rerun's `props.model_alias`/models id to carry it), or a live-tool heartbeat file +
   counter-side HTTP probe while the server is alive. These detect bypasses of the *genuine* pipeline; they are
   insufficient alone because the runner controls the code that writes the outputs.

## Fundamental limit

The counter is a behavioral oracle over lane-committed code. Every leg that delegates execution to committed tools
(`replay`, `tamper`, `urlswap`, `recordcheck` all call the tools at tip) can be satisfied by committing modified
tools; the pre-registration's own disclosure ("the receipts leg is structural … the replay and urlswap legs carry
the evidence") does not extend to the identity of the runner. The only anchors the counter genuinely controls are
cryptographic hashes of artifacts and facts it observes itself outside the tools' outputs — hence fix 1 is the
necessary condition; fixes 2-3 are sufficient only on top of it.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K2Cheat.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K2Cheat/fixtureA-replay-synth.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K2Cheat/receipt-1.json`,
  `receipt-2.json`, `receipt-3.json`, `install.txt` (copied from the lane)
