# X2Offline — round 48, lane kama: v5 replay failure modes

**Verdict:** five of the six enumerated failure modes fail closed exactly as required (exit 2, no rerun
receipt, nothing executed); **(d) `--timeout 1` does not fail at all — it exits 0 with a matching pass
rerun** (finding F1: the probe's bound sits above the rerun's ~0.35 s floor, and `--timeout` in fact
bounds only the live child, never the downloads), and the extra probe shows a **forged
`provenance.verified.member_sha256` still replays to exit 0** (finding F2: the v5 `verified` block's
digests are carried but never checked). Neither exit-0 case is forged evidence — both full reruns
re-derived `provenance.server.asset_sha256`, `provenance.model.sha256` and `server.sha256` from the
downloads — but both are contract gaps relative to the seat item and are reported as findings.

## Setup and code under test

```
S=/fast/scratch/hyaku/kama-r48/X2Offline; mkdir -p "$S"; export TMPDIR="$S"
git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
git -C "$S/lane" rev-parse --show-toplevel      # /fast/scratch/hyaku/kama-r48/X2Offline/lane
git -C "$S/lane" log -1 --format='%H %s'        # b85783e889c261ff870da65d091ff1014ffe7c10 round-48: wave spec ...
sha256sum "$S/lane/tools/kama-live-replay.py"   # 69837013ec64b78a192e91b5b6a604a7437890c9e5a9c21dd175a0e87eb8b15f
git -C "$S/lane" show 380bcdff9c8af06997c482f6eb03db926a794a2b:tools/kama-live-replay.py | sha256sum   # same
sha256sum "$S/lane/tools/kama-llamacpp-live.py" # 1e5ea0fde985367d9d6335eae3825068e64063f032bbbc59fc8909e7b7f9a6d2
git -C "$S/lane" show 380bcdff9c8af06997c482f6eb03db926a794a2b:tools/kama-llamacpp-live.py | sha256sum   # same
sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/c2/live/receipt-1.json
                                                # 164a4d9d232853deb35a64d9127382c7bb8ba8536b99f02c850eb2062f291344
```

- Both tools are byte-identical at the build commit `380bcdff…`, at the clone tip `b85783e8…` and in the
  lane worktree, so the run exercises the landed build; the clone's `git status --porcelain` stayed empty
  (my runs wrote nothing into it).
- Every case is a copy of the lane's `receipt-1.json` with exactly the documented mutation; the
  mutation set was re-diffed programmatically (`d-timeout-1` and `d2-timeout-subsecond`: IDENTICAL).
- (b) needs "another real revision of `ggml-org/models-moved`": one Hugging Face API request
  (`/api/models/ggml-org/models-moved/commits/main?limit=3`, evidence `hf-commits.json`) gave
  `e2d5caf5587262b440f392e36f06594da5afa1f6` (older `main`, 2025-10-28T09:18:28Z).
- No tool installed or upgraded (python3 stdlib only; `curl` for the one HF request; no pacman).

Driver: `mkvariants.py` writes the variants, `run-case.sh <case> [extra replay args]` runs one replay
with a fresh `--work`, records `exit`, `out.json` and a `find` listing of `--work`.

## Results

| case | mutation | exit | refused | left under `--work` |
|---|---|---|---|---|
| a-asset-404 | `provenance.server.asset_url` → `…/b11909/llama-b11909-bin-ubuntu-x64-missing.tar.gz` (real 404 on github.com) | 2 | `could-not-run:HTTPError:HTTP Error 404: Not Found` | empty `download/` only (no `.part`, no inputs) |
| b-commit-other-rev | `provenance.model.commit` → `e2d5caf5…`; URL keeps `/resolve/499bc882…/` | 2 | `provenance-url-revision-differs-from-commit` | nothing; refused before any network or dir creation |
| c-unreachable-host | `provenance.model.url` → `https://127.0.0.1:9/ggml-org/models-moved/resolve/499bc882…/tinyllamas/stories260K.gguf` | 2 | `could-not-run:URLError:<urlopen error [Errno 111] Connection refused>` | `download/llama-b11909-bin-ubuntu-x64.tar.gz`, 22,475,032 B, digest already verified `bf94332a…`; no model, no extract |
| d-timeout-1 | none; run with `--timeout 1` | **0** | — (`match=True`) | `download/` (archive+model), extracted 51-file `server/` tree, empty `tmp/`, **`rerun-receipt.json` outcome=pass** (54 files) |
| d2-timeout-subsecond *(control)* | none; run with `--timeout 0.2` | 2 | `could-not-run:TimeoutExpired:Command '['/usr/bin/python3', '…/kama-llamacpp-live.py', …` | `download/` + extracted 51-file `server/` tree + empty `tmp/` (53 files), no rerun receipt |
| e-no-verified | `provenance.verified` deleted | 2 | `provenance-not-verified-at-record` | nothing; refused before dir creation |
| f-v5-v4provenance | `schema` stays `kama-llamacpp-live/v5`, `provenance` reduced to the v4 shape (`server{asset_url,asset_sha256,member}`, `model{url,sha256}`; no `commit`, no `verified`) | 2 | `provenance-bad-commit` | nothing; refused before dir creation |
| g-forged-verified-member *(extra)* | `provenance.verified.member_sha256` → `"0"×64` | **0** | — (`match=True`, 0 mismatches) | `download/` + `server/` tree + **`rerun-receipt.json` outcome=pass** (54 files) |

Exact per-case stdout, `out.json` and work listing: `summary.txt` and `<case>/` in the evidence dir.
Reproduce any row with: `sh run-case.sh <case> [--timeout N]` (after `python3 mkvariants.py` with the
lane receipt present), the runner invoking
`python3 "$S/lane/tools/kama-live-replay.py" --receipt "$d/receipt.json" --work "$d/work" --out "$d/out.json"`.

No case produced a rerun receipt except d and g, and there the child ran and matched (exit 0 by the
tool's own contract: 0 = rerun matches). a, b, c, e, f all failed closed with exit 2 before execution.

## F1 — `--timeout 1` never fires; `--timeout` does not bound the downloads (case d)

Repro:

```
sh run-case.sh d-timeout-1 --timeout 1
# replay match=True refused=None mismatches=0 exit=0   (secs=2.6 including downloads)
# work/rerun-receipt.json: schema=kama-llamacpp-live/v5 outcome=pass
#   started_utc 2026-10-26T22:35:37.876Z  ended_utc 2026-10-26T22:35:38.255Z  (0.379 s)
```

Exit 0 with a pass rerun is "anything else" under the item's rule, so this is a finding. The cause is
not a fail-open: `subprocess.run(…, timeout=1)` (`tools/kama-live-replay.py:242`) completed normally
because the rerun child needs ~0.35 s (case g: 0.348 s; the lane receipt-1: 0.370 s), then
`compare()` ran and returned no mismatches (`:249`). The same receipt with a bound below the floor
(`--timeout 0.2`, case d2) does fail closed: exit 2, `could-not-run:TimeoutExpired…`, no rerun receipt,
no leftover process.

The deeper defect the case exposes: `--timeout` reaches only the child. `acquire()` (`:126-131`) calls
`fetch(url, dest)` with fetch's own default of 120 s (`:81`, used at `:88`), and `replay()` passes no
bound (`:218-219`), so a stalled github.com/Hugging Face download can consume up to 2×120 s regardless
of `--timeout 1`. The flag has no help text at all (`:396`).

Proposed fix (proposed text, not applied): thread the bound into the downloads and document the scope.

```diff
-def acquire(url, sha, dest):
-    fetch(url, dest)
+def acquire(url, sha, dest, timeout=120):
+    fetch(url, dest, timeout)
@@ replay()
-        res["inputs"]["archive_sha256"] = acquire(need["server.asset_url"], need["server.asset_sha256"], archive)
-        res["inputs"]["model_sha256"] = acquire(need["model.url"], need["model.sha256"], model)
+        res["inputs"]["archive_sha256"] = acquire(need["server.asset_url"], need["server.asset_sha256"], archive,
+                                                  timeout=min(timeout, 120))
+        res["inputs"]["model_sha256"] = acquire(need["model.url"], need["model.sha256"], model,
+                                                timeout=min(timeout, 120))
@@ main()
-    ap.add_argument("--timeout", type=float, default=600.0)
+    ap.add_argument("--timeout", type=float, default=600.0,
+                    help="bound in seconds for each download and for the live child")
```

For the probe itself: a 1 s bound cannot exercise a refusal while the live child's floor is ~0.35 s.
The calibration needs either a bound below that floor (as in the d2 control) or a selftest/fixture live
tool that sleeps (the selftest's fake live tool at `:283-291` could gain a sleep case). Whether to
re-calibrate the probe or to widen `--timeout` is the L1's call; both are stated here.

## F2 — `provenance.verified.*` digests are carried, never checked (case g)

Repro:

```
python3 mkvariants.py          # case g sets provenance.verified.member_sha256 = "0"*64
sh run-case.sh g-forged-verified-member
# replay match=True refused=None mismatches=0 exit=0
# work/rerun-receipt.json: outcome=pass, server.sha256=35ac50fb… (the real digest)
```

`provenance()` checks only `verified.at == "record"` (`tools/kama-live-replay.py:120-122`); nothing
reads `verified.archive_sha256`, `verified.member_sha256` or `verified.model_sha256`:
`grep -n 'archive_sha256\|member_sha256\|model_sha256\|verified' tools/kama-live-replay.py` returns only
the `verified` presence check (:120-122), the selftest fixtures (:318, :352-353) and the *input keys*
`res["inputs"]["archive_sha256"]` / `["model_sha256"]` (:218-219) — no access to a `verified` member.
The producer writes the three digests at `tools/kama-llamacpp-live.py:1564-1566`. The digests the
replay does enforce are `provenance.server.asset_sha256` and `provenance.model.sha256` (`:107-110`,
acquired at `:218-219`) and the pre-execution member digest `server.sha256` (`:228-233`). So a receipt
may carry an arbitrary `verified` block and still replay clean: the v5 record-time verification envelope
is decorative on the consumer side. This does not forge the evidence (the real digests are re-derived),
but an auditor who reads `verified.member_sha256` gets no guarantee it corresponds to the run, and a
tampered/incorrect envelope is undetectable.

Proposed fix (proposed text, not applied) — bind the block to the fields already checked:

```diff
         ver = prov.get("verified") if isinstance(prov.get("verified"), dict) else {}
         if ver.get("at") != "record":
             raise Refused("provenance-not-verified-at-record")
+        bound = {"archive_sha256": need["server.asset_sha256"],
+                 "model_sha256": need["model.sha256"],
+                 "member_sha256": (rec.get("server") or {}).get("sha256")}
+        for key, want in bound.items():
+            if ver.get(key) != want:
+                raise Refused(f"provenance-verified-digest:{key}")
     return need
```

This would not refuse the genuine receipts: for receipt-1, -2 and -3 on S492,
`verified.archive_sha256 == provenance.server.asset_sha256` (`bf94332a…`),
`verified.member_sha256 == server.sha256` (`35ac50fb…`) and
`verified.model_sha256 == model.sha256` (`270cba1b…`) all hold (checked by JSON comparison; lane files
read in place). A selftest case for a forged `verified` digest should be added next to
`v5-not-verified` (`:352-353`), which currently covers only a missing block.

## Observations (no action requested)

- Refusals leave partial downloads behind and mark nothing: (c) leaves the already-verified 22,475,032 B
  archive after the model host refuses; (d2) leaves downloads plus the extracted 51-file server tree
  after the killed child. Disk-only residue; nothing is executed and no rerun receipt is written.
- Provenance refusals precede `os.makedirs(work)` (`:212` before `:213`), so b, e and f wrote nothing —
  the `--work` dirs in their evidence copies are the driver's empty pre-created dirs.
- (a) leaves no `.part` file (fetch's `finally`, `:91-93`); the refusal token keeps the HTTP class
  (`HTTPError`) and the 404 line.
- (b) refused in 0.1 s with no network I/O and no inputs recorded.
- (f) fails closed, but its token is `provenance-bad-commit`: a v5 schema carrying a v4-shaped provenance
  is indistinguishable from a missing `model.commit`. Not a defect (it refuses), only less diagnostic
  than a dedicated `v5-provenance-missing` token.
- Process hygiene: after the forced kill (d2) and after both full reruns (d, g),
  `pgrep -af 'X2Offline.*llama-server'` and `pgrep -af 'X2Offline/cases/.*/work'` returned nothing;
  the only `llama-server`-matching process seen during the wave belonged to a sibling lane's scratch
  (`/fast/scratch/hyaku/kama-r48/L2Concurrent/…`), not to this seat.
- No timeout-path leak was observed either: the killed child left no listener, and its `tmp/` was empty.

## Evidence

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X2Offline/`
- `summary.txt` — case / exit / refused / work file count / rerun receipt / match
- `mkvariants.py`, `run-case.sh`, `hf-commits.json` — the two drivers hardcode
  `S=/fast/scratch/hyaku/kama-r48/X2Offline` and write `cases/` next to themselves, so copy them into a
  recreated `$S` (see the setup block) before re-running; this evidence dir is a record, not a run root.
  `mkvariants.py` reads the lane receipt in place (read-only) and `run-case.sh` uses the `$S/lane` clone.
- `receipt-1.source.json`, `receipt-2.source.json`, `receipt-3.source.json` (cited for the F2 binding check)
- `a-asset-404/`, `b-commit-other-rev/`, `c-unreachable-host/`, `d-timeout-1/`,
  `d2-timeout-subsecond/`, `e-no-verified/`, `f-v5-v4provenance/`, `g-forged-verified-member/`
  each with `receipt.json` (mutated copy), `out.json`, `stdout.txt`, `stderr.txt`, `work-tree.txt`.

Scratch (`/fast/scratch/hyaku/kama-r48/X2Offline`, including the shared clone and all downloads) was
removed after the evidence copies were verified.
