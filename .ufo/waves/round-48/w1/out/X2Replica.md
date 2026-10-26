# X2Replica - round 48 independent replays outside the counter (C2 operability)

**Verdict: reproduced 4/4 receipts green and independently re-acquired every byte.** All three round-48
`kama-llamacpp-live/v5` receipts replay with `match=true`, `mismatches=0`, exit 0, a v5 rerun whose
`provenance.verified` block matches the frozen digests, 11/11 evaluated checks re-passed, and
`--compare` exit 0 against the original; the round-47 `v4` receipt also replays and compares green
(v4 schema preserved, no `verified` block by design). Non-vacuity is shown four ways: a mutated
stable surface fails `--compare`, an instance-only mutation still passes, a swapped archive and an
unpinned revision are refused at network level (exit 2, nothing extracted or started), and a `v5`-vs-`v4`
compare correctly reports 3 mismatches. One low-severity observation on the replay's `verified`-block
handling (F1, with a measured two-hunk fix: patched tool refuses an unbound `verified` block at exit 2
and still replays an honest receipt green, selftest 21/21) - no defect that changes the C2 measurement.

Lane at measurement: HEAD `b85783e889c261ff870da65d091ff1014ffe7c10` (wave spec), measured build
`380bcdff9c8af06997c482f6eb03db926a794a2b` - read-only throughout.
No clone was needed (I ran the lane's own tool on frozen receipts and never wrote in the lane); no
install, upgrade or service was performed this wave (`llama.cpp b11909` reused only as downloaded
archive, see below). Python 3.14.8.

## Environment (per run, all inside scratch)

For every run: `HOME=$S/homeN`, `XDG_CACHE_HOME=$S/xdgN` (both created empty, still empty afterwards -
`{1: [], ...}` verified), `TMPDIR=$S/wN/tmp`; `--work $S/wN`. Receipts and the tool were read from the
lane read-only. The server executed was the member **freshly extracted from the re-downloaded archive**
(`$S/wN/server/llama-b11909/llama-server`, sha256 `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0`),
never the host copy at `~/.local/opt` (that copy hashes identically, per `c2/live/install.txt`).

All four replays were launched concurrently (separate work dirs, separate empty HOME/XDG).

## Commands, exit codes, results

Command form (N = 1,2,3):

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-live-replay.py \
  --receipt /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/c2/live/receipt-N.json \
  --work $S/wN --out .../w1/out/X2Replica/replay-N.json
```

| run | receipt | exit | match | refused | mismatches | live_exit | rerun schema/outcome |
|---|---|---|---|---|---|---|---|
| r48-1 | `c2/live/receipt-1.json` | **0** | true | null | 0 | 0 | v5 / pass |
| r48-2 | `c2/live/receipt-2.json` | **0** | true | null | 0 | 0 | v5 / pass |
| r48-3 | `c2/live/receipt-3.json` | **0** | true | null | 0 | 0 | v5 / pass |
| r47-1 | `round-47/c2/live/receipt-1.json` | **0** | true | null | 0 | 0 | **v4** / pass |

Tool stdout, each: `replay match=True refused=None mismatches=0 exit=0`. `notes=[]` on all four, i.e.
the rerun's `tool.sha256` and `probe.sha256` equal the originals' (same tool and probe bytes).

### Inputs the tool re-acquired (hashed again by me, not read from `inputs`)

| file | bytes | sha256 | expected |
|---|---|---|---|
| `llama-b11909-bin-ubuntu-x64.tar.gz` (all 4 runs) | 22,475,032 | `bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b` | frozen asset digest |
| `stories260K.gguf` (all 4 runs) | 1,185,376 | `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` | frozen model digest |
| extracted `llama-server` (all 4 runs) | 17,864 | `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` | receipt `server.sha256` |

Each run downloaded independently into its own `--work` (four separate archive+model copies), so no
cache, no shared bytes: `$S/homeN` and `$S/xdgN` remained empty. Per replay that is 23.7 MB of network
(the task's ~70 MB figure is the counter's total, which also fetches the swap asset and swap model).

### Freshness and instance facts (rerun receipts)

| run | port | child_pid | started_utc | ended_utc (ms) | ownership | teardown |
|---|---|---|---|---|---|---|
| 1 | 43629 | 1422044 | 2026-10-26T22:34:10.144Z | 22:34:10.486 (342) | child | rc 0, sigterm true, sigkill false, port_refuses true |
| 2 | 36975 | 1422275 | 22:34:10.202Z | 22:34:10.544 (342) | child | rc 0, sigterm true, sigkill false, port_refuses true |
| 3 | 35387 | 1422429 | 22:34:10.223Z | 22:34:10.564 (341) | child | rc 0, sigterm true, sigkill false, port_refuses true |
| r47-v4 | 39641 | 1422518 | 22:34:10.415Z | 22:34:10.579 (164) | child | rc 0, sigterm true, sigkill false, port_refuses true |

Originals started 22:26:23-24Z, i.e. every rerun is strictly later than its original. Distinct loopback
ports; `port_listener_ownership="child"`; `log_path=null`; `ps -eo args | grep -c '[l]lama-server'` = **0**
after all runs (nothing left running). `argv` (rerun-1): extracted member, `-m` scratch model,
`--alias kama-r48-live --host 127.0.0.1 --port 43629 -c 256 -t 1 --no-webui --offline`;
`child_env_keys` = `HOME, LANG, PATH, TMPDIR` (empty HOME passed through, nothing cached);
`model_sha256_post` = frozen digest (model unchanged by the run); `internal_fault`/`setup_error` null.

### `provenance.verified` of the reruns (all three identical, byte-for-byte)

```json
{"archive_sha256": "bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b",
 "at": "record",
 "member_sha256": "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0",
 "model_sha256": "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"}
```

`provenance.model.commit` = `499bc8821c6b12b4e53c5bffcb21ec206f212d81` on all three, and the model URL
contains `/resolve/<that commit>/` - the rerun is itself revision-pinned and was verified at record
time (the live tool was given `--server-archive $work/download/...tar.gz` by
`tools/kama-live-replay.py:241`). Checks: 11/11 evaluated, all `passed` (`health_ready`,
`models_alias_id`, `models_owned_by_llamacpp`, `metrics_not_enabled`, `props_alias`, `probe_model_ok`,
`probe_mismatch`, `teardown_graceful`, `teardown_port_closed`, `loading_envelope_graded`,
`model_unchanged`).

The **round-47 v4 rerun** carries `provenance = {model, server}` only - no `verified`, no
`model.commit` - and its model URL remains `.../resolve/main/...` (the round-47 receipt's own URL). That
is the v4 contract; `--server-archive` is passed only for v5 (`tools/kama-live-replay.py:241`).

### `--compare`, original vs rerun

`python3 tools/kama-live-replay.py --compare <original> <rerun>`:

| pair | exit | stdout |
|---|---|---|
| receipt-1 vs rerun-1 | **0** | `compare match=True mismatches=0` |
| receipt-2 vs rerun-2 | **0** | `compare match=True mismatches=0` |
| receipt-3 vs rerun-3 | **0** | `compare match=True mismatches=0` |
| round-47 receipt-1 vs rerun-r47-v4 | **0** | `compare match=True mismatches=0` |
| rerun-1 vs rerun-2 (determinism across concurrent runs) | **0** | `compare match=True mismatches=0` |
| rerun-1 vs rerun-3 | **0** | `compare match=True mismatches=0` |

### Non-vacuity controls (my own, not the counter's)

Seven single-field mutations of `rerun-1` (`out/X2Replica/probes/*.json`, compared against
`c2/live/receipt-1.json`):

| mutation | exit | mismatch line |
|---|---|---|
| `instance-only` (port, child_pid, started/ended_utc, teardown.term_wait_ms, models `created`) | **0** | none - instance fields correctly ignored |
| `check-differs` (`health_ready.passed` flipped) | **1** | `check:health_ready:True->False` |
| `slots-count` (+1 element) | **1** | `projection:slots:[4, "6d345b40..."]->[5, "6d345b40..."]` |
| `health-status` (500) | **1** | `projection:health:[200, "a29ee2b1..."]->[500, "a29ee2b1..."]` |
| `schema-downgrade` (v5 -> v4) | **1** | `schema:kama-llamacpp-live/v5->kama-llamacpp-live/v4` |
| `teardown-outcome` (`port_refuses=false`) | **1** | `projection:teardown:[0, true, false, true]->[0, true, false, false]` |
| `ownership` (`child` -> `orphan`) | **1** | `projection:ownership:"child"->"orphan"` |

Cross-schema discrimination: `receipt-1` (v5) vs `rerun-r47-v4` (v4) is exit **1**, 3 mismatches -
`schema:kama-llamacpp-live/v5->kama-llamacpp-live/v4`,
`projection:props` (`model_alias kama-r48-live -> kama-r47-live`) and
`projection:models` (`["kama-r48-live|llamacpp"] -> ["kama-r47-live|llamacpp"]`) - the comparison is
not schema-blind.

Network-level refusals (mutated *provenance*, run end to end in fresh work dirs; receipts preserved in
`out/X2Replica/probes/`):

| probe | exit | `refused` | side effects |
|---|---|---|---|
| `swap-asset-b11906` (asset URL -> b11906 archive, digest kept) | **2** | `digest-mismatch:llama-b11906-bin-ubuntu-x64.tar.gz:want=bf94332a...:got=064ade6220799fd9e7b1804b574f5f92c38dde358cc987c6b8283cfaeb1eeef3` | bad archive unlinked, `download/` empty, no `server/` dir, no rerun receipt |
| `swap-model-rev` (model URL -> revision 22027b1a..., commit kept) | **2** | `provenance-url-revision-differs-from-commit` | nothing downloaded |
| `unpinned-main-url` (model URL -> `/resolve/main/`) | **2** | `provenance-url-revision-differs-from-commit` | nothing downloaded |
| `no-verified` (`provenance.verified` removed) | **2** | `provenance-not-verified-at-record` | nothing downloaded |

All four refusals happen **before** extraction/execution: the work dirs contain only an empty `tmp/`
(and, for the archive swap, an empty `download/`); `llama-server` process count stayed 0.
Note the ordering: for a v5 receipt the URL/commit binding (`tools/kama-live-replay.py:114-119`) is
checked before any download, so a *model-bytes* swap cannot be reached at network level under a pinned
commit; the archive swap and the counter's own model-digest control cover that byte-level refusal.

## Findings

**F1 (observation, low; not a defect in the measured claim).** `tools/kama-live-replay.py:120-122`
accepts a v5 receipt whenever `provenance.verified["at"] == "record"`; it never binds
`verified.archive_sha256` / `verified.member_sha256` / `verified.model_sha256` to the re-acquired bytes
or to the receipt's own digests. A receipt carrying a present-but-wrong `verified` block therefore
still replays green, because `replay()` checks the *provenance* digests (`provenance.server.asset_sha256`,
`server.sha256`, `provenance.model.sha256`) rather than the recorded verification. This does not weaken
C2 as measured: the counter's `receipts` leg does bind them
(`tools/round48-live-replay-v5-audit.py:246-249`, failing with
`provenance.verified ... does not bind archive, member and model`). Confirmed end to end, not just by
reading: `probes/verified-unbound.json` is `rerun-1.json` with `provenance.verified.archive_sha256`
set to 64 `1`s and `.member_sha256` to 64 `0`s, and replaying it in a fresh work dir gives
`replay match=True refused=None mismatches=0 exit=0` (`probes/refuse-verified-unbound-replay.json`) -
the recorded verification is never re-bound. Proposed fix (replay side, keeps the tool self-contained;
not applied - lane is read-only for me). Two hunks: the check, plus the tool's own v5 fixture, whose
`v5()` base carried only `{"at": "record"}` and would otherwise be refused:

```diff
--- a/tools/kama-live-replay.py
+++ b/tools/kama-live-replay.py
@@ -120,6 +120,12 @@
         ver = prov.get("verified") if isinstance(prov.get("verified"), dict) else {}
         if ver.get("at") != "record":
             raise Refused("provenance-not-verified-at-record")
+        # the recorded verification must bind the same bytes the receipt names
+        want = {"archive_sha256": need["server.asset_sha256"], "model_sha256": need["model.sha256"],
+                "member_sha256": (rec.get("server") or {}).get("sha256")}
+        for k, v in want.items():
+            if ver.get(k) != v:
+                raise Refused(f"provenance-verified-{k.replace('_sha256', '')}")
     return need
 
 
@@ -315,7 +321,8 @@
 
         def v5(**over):
             base = {"schema": LIVE_V5, "provenance.model.commit": commit,
-                    "provenance.verified": {"at": "record"}}
+                    "provenance.verified": {"at": "record", "archive_sha256": asha,
+                                            "member_sha256": ssha, "model_sha256": msha}}
             return receipt(**dict(base, **over))
 
         def run(name, rp, want_exit, want_refused=None, live=fake_live):
```

The patch was built against the lane file in my scratch and measured there (nothing applied in the lane):
`--selftest --scratch $S/st3` -> `KLR_SELFTEST pass=21 fail=0` (unpatched baseline also 21/0);
patched tool on `probes/verified-unbound.json` -> exit **2**, `refused=provenance-verified-archive`,
empty work dir, no server started (`probes/patched-verified-unbound-replay.json`); patched tool on the
real `c2/live/receipt-1.json` (`--live <lane>/tools/kama-llamacpp-live.py`, since `DEFAULT_LIVE` is
resolved next to the tool) -> exit **0**, `match=true`, `mismatches=0`, rerun `verified` block equal to
the frozen digests (`probes/patched-replay-1.json`). So the fix is non-vacuous and does not reject
honest receipts. Without the fixture hunk the same patch fails its own `v5-match` and
`v5-rerun-schema-differs` cases - the fixture gap is part of the finding.

**F2 (note, expected).** The round-47 v4 replay still downloads the model from `/resolve/main/`
(mutable ref). It matched today because `main` still serves the recorded bytes, and the digest check
makes failure loud rather than silent - but a v4 receipt is only replayable while `main` is unchanged.
That is exactly closure D6, fixed for v5; the v4 leg is a compatibility check, not evidence of pinning.

**F3 (note, transcript caveat).** A rerun receipt embeds instance paths
(`server.realpath`, `model.path`, `work`) that point into my scratch, which is removed after the wave.
`out/X2Replica/rerun-N.json` and `replay-N.json` are therefore transcripts; the durable facts are the
digests above and the stable projection, which `--compare` reproduces from any copy (§ projection).
`replay-N.json`'s `rerun_receipt` field likewise names the now-removed scratch path; the copied
`rerun-N.json` is the same bytes.

## Files written (all under the lane, my seat only)

- `.ufo/waves/round-48/w1/out/X2Replica.md` (this report)
- `.ufo/waves/round-48/w1/out/X2Replica/replay-1.json`, `replay-2.json`, `replay-3.json` (822 B each),
  `replay-r47-v4.json`
- `.ufo/waves/round-48/w1/out/X2Replica/rerun-1.json` (`7628864d...`), `rerun-2.json`
  (`0163cc8e...`), `rerun-3.json` (`9451ac9c...`), `rerun-r47-v4.json` (`7413fd73...`)
- `.ufo/waves/round-48/w1/out/X2Replica/fix-verified-binding.diff` - the F1 patch as a file (applies to
  `tools/kama-live-replay.py` at `380bcdff`, two hunks; measured only in my scratch, not applied)
- `.ufo/waves/round-48/w1/out/X2Replica/probes/` - 7 compare mutations (`instance-only`,
  `check-differs`, `slots-count`, `health-status`, `schema-downgrade`, `teardown-outcome`,
  `ownership`), 5 provenance mutations (`swap-asset-b11906`, `swap-model-rev`, `unpinned-main-url`,
  `no-verified`, `verified-unbound`), the 5 `refuse-*-replay.json` outputs, and the two patched-tool
  runs for F1 (`patched-verified-unbound-replay.json`, `patched-replay-1.json`; the patched tool itself
  lived only in scratch)

Lane git status (read-only check) shows only other seats' work (`M SKILL.md`, `?? corpus/lessons/round-48.md`,
`?? .ufo/waves/round-48/w1*`) plus my `?? .ufo/waves/round-48/w1/out/`; I wrote nothing else, mutated no
jj/Git state, started no service that survives, and left no `llama-server` process. Scratch
`/fast/scratch/hyaku/kama-r48/X2Replica` removed after copying the artifacts above.
