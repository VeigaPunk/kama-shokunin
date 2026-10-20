VERDICT: confirm — the round touched no registered consumer and `registry/history/` is byte-identical to `20e392e`. Every occurrence of `8080`/`34113` in the round's runtime artifacts is refusal-surface data (a declared refusal set or the refusal messages themselves); the two live runs served `32845` and `39375`, and the 144 probe-matrix stub binds all landed outside `{8080, 34113}`. One residual mechanism gap is reported below (unguarded `bind(:0)` in the matrix harness); it was not exercised.

# Attack

Two claims, attacked independently and read-only:

- **N1** — the round never contacted a registered consumer endpoint, i.e. no server bound, no probe aimed at, and no receipt recorded `8080` or `34113` as a served port.
- **N2** — `registry/history/` is unchanged since base commit `20e392e`.

Lane HEAD `b8e485cc6b201c8e4604a20808e58babbfe08e34` (`b8e485c`); base `20e392e` resolves (`git cat-file -t` → `commit`).

# N1 — port scan of the round's runtime artifacts

Scope: the receipt set the item names plus every `run-*.json` in the wave dir — `run-before.json`, `run-after.json`, `live/receipt.json`, `live/receipt-frozen-probe.json`, `live/controls.txt`, `frozen/manifest.json`, `measure-stdout.txt`, `run-check-selftest.txt`, `run-test-snapshot.txt`.

## N1.1 — hit census per file

```
$ for f in <the nine files above>; do grep -c -E '8080|34113' "$f"; done
run-before.json              hits=0
run-after.json               hits=0
live/receipt.json            hits=2
live/receipt-frozen-probe.json hits=2
frozen/manifest.json         hits=0
live/controls.txt            hits=5
measure-stdout.txt           hits=0
run-check-selftest.txt       hits=0
run-test-snapshot.txt        hits=0
```

Nine hits total, all enumerated below; each is refusal-surface, none is a request or a served port.

## N1.2 — the four receipt hits are the declared refusal set

```
$ grep -n -E '8080|34113' .ufo/waves/round-16/live/receipt.json \
                           .ufo/waves/round-16/live/receipt-frozen-probe.json
receipt.json:217:    8080,
receipt.json:218:    34113
receipt-frozen-probe.json:217:    8080,
receipt-frozen-probe.json:218:    34113
```

Both lines sit inside the `"port_refusal_set": [` array that opens at `receipt.json:216` — i.e. the literal statement of ports the harness refuses. This is the correct place for the strings to appear.

## N1.3 — the five controls hits are refusals plus a zero-listener assertion

```
$ grep -n -E '8080|34113' .ufo/waves/round-16/live/controls.txt
9:kama-llamacpp-live: port-refused-registered:34113
10:registered_port_34113_exit=2
11:kama-llamacpp-live: port-refused-registered:8080
12:registered_port_8080_exit=2
16:post_ss_8080_34113=0
```

Lines 9–12 are the refusal messages and their observed exit code `2` (refused before launch). Line 16 is the post-run listener assertion: zero listeners on either port. No line records a successful connection or a served identity.

## N1.4 — the actual served ports are unregistered

```
$ grep -n '"port"' live/receipt.json live/receipt-frozen-probe.json
receipt.json:213:  "port": 32845,
receipt-frozen-probe.json:213:  "port": 39375,
```

Both are JSON integers (verified by `json.load`: `type(port).__name__ == 'int'`), both are inside the ephemeral range and outside `{8080, 34113}`.

Every URL string appearing anywhere in either receipt — extracted by regex over the whole file, not just known fields:

```
receipt.json               urls=['http://127.0.0.1:32845', 'http://127.0.0.1:32845/v1']
receipt-frozen-probe.json  urls=['http://127.0.0.1:39375', 'http://127.0.0.1:39375/v1']
```

Two URLs each, same host:port as the recorded `port`, loopback only. No registered endpoint is addressed anywhere in the receipt bytes.

## N1.5 — the probe matrix never bound a registered port (144/144)

`run-before.json` and `run-after.json` contain `stdout_sha256`/`parsed` records with no URLs at all (`grep -o -E 'https?://…'` → no output, exit 0). Their ports are the empirical bind outcomes:

```
run-before.json  records=72 binds=72  port_min=32857 port_max=46723
                 intersect_registered=[]  count_8080=0 count_34113=0
                 port_mode_hist=Counter({'stub': 71, 'closed': 1})
run-after.json   records=72 binds=72  port_min=32841 port_max=51349
                 intersect_registered=[]  count_8080=0 count_34113=0
                 port_mode_hist=Counter({'stub': 71, 'closed': 1})
```

144 observed draws, zero intersections with the registry pins. Both commands were `python3 tests/probe-verdicts/check.py --probe …` in the lane cwd — no registry-row probing, no `file_match` semantics.

## N1.6 — host state now (read-only)

```
$ ss -ltnH 'sport = :8080 or sport = :34113' | wc -l   → 0
$ pgrep -x llama-server | wc -l                        → 0
```

Nothing is listening on either registered port and no server process survives the round. Corroborates the artifact's own `post_ss_8080_34113=0` (`controls.txt:16`).

# N2 — `registry/history/` unchanged since `20e392e`

## N2.1 — the item's command, verbatim

```
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --stat 20e392e b8e485c -- registry/history
EXIT=0            (no output)
$ git -C … diff --name-status 20e392e b8e485c -- registry/history
EXIT=0            (no output)
```

The tree is unchanged across the round commit. `registry/history/` holds exactly three tracked entries at both endpoints — `.gitignore`, `DELTA.md`, `latest.tsv` — and `git ls-tree -r` returns identical names for both.

## N2.2 — blob identity, not just diff silence

```
$ for f in DELTA.md latest.tsv .gitignore; do sha256(20e392e:$f) vs sha256(b8e485c:$f); done
DELTA.md    e9e57b9abcbc9229a42a211be823c008de333e4dc7503095d00c3b454f6db280  IDENTICAL
latest.tsv  f9f8f3b5bb1bfa61e6737a7fe95f7d7e0d0b53e287eb9c7fbe25d6cd0b7c2a2e  IDENTICAL
.gitignore  cf462371a8a0747015a999b82e82f894d776aa1cc1e26afa793bc90a603c364c  IDENTICAL
```

Last commit to touch the directory is `ea72c3e 2026-10-14 09:46:23 -0300 "round-3: re-census — derived --ufo-src, registry cut to live rows, corpus errata"` — six days before the round.

## N2.3 — working tree and gitignored runtime evidence

```
$ git status --porcelain -- registry
EXIT=0            (no output: no staged, unstaged, or untracked-in-registry changes)

$ ls -la --time-style=full-iso registry/history/
drwxr-xr-x .            2026-10-14 09:45:26
-rw-r--r-- .gitignore   2026-10-13 16:51:09
-rw------- .lock        2026-10-14 09:45:25   0 bytes
-rw------- 20261014T124232Z.json  2026-10-14 09:42:32
-rw------- 20261014T124525Z.json  2026-10-14 09:45:26
-rw-r--r-- DELTA.md     2026-10-14 09:42:32
-rw------- latest.tsv   2026-10-14 09:42:32

$ find registry/history -newermt '2026-10-20 00:00:00' -printf '%p %TY-%Tm-%Td %TH:%TM:%TS\n'
EXIT=0            (no output)
```

The two dated JSON snapshots are gitignored (`.gitignore` holds `*.json`) local evidence; their mtimes predate the round by six days, so the round wrote no snapshot even at the untracked level. `latest.tsv` still reads all three rows `DEAD connection-refused` — the registered consumers were not re-probed and their recorded state was not rewritten:

```
#@snapshot_id 20261014T124232Z
omp-llama-cpp-default  DEAD  connection-refused  -  8080   inherited
ufo-fsd-thetick        DEAD  connection-refused  -  34113  yes
ufo-fsd-local-helper   DEAD  connection-refused  -  34113  yes
```

## N2.4 — the only registry change the round made is a comment line

```
$ git diff 20e392e b8e485c -- registry
diff --git a/registry/endpoint-consumers.tsv b/registry/endpoint-consumers.tsv
@@ -29,7 +29,7 @@
-#   MODEL_OK | MODEL_MISMATCH | FOREIGN_SERVICE | UNAUTHORIZED_SERVICE | DEAD | NOT_HTTP
+#   MODEL_OK | MODEL_MISMATCH | FOREIGN_SERVICE | UNAUTHORIZED_SERVICE | DEAD | NOT_HTTP | MODEL_LOADING
```

One hunk, one comment line (`registry/endpoint-consumers.tsv:32`) extending the verdict legend. Zero data rows, zero `declared_baseurl` cells, zero ports, zero `consumer_path` cells changed. The append recorded in the round context does not alter any consumer's registered identity.

# N3 — mechanism: no writer could have fired

- `snapshot` is the only subcommand that writes history; it takes the directory explicitly — `--history DIR` at `tools/kama-probe.sh:109`, default `<repo>/registry/history` at `tools/kama-probe.sh:75` ("snapshot only").
- The round's `tools/kama-probe.sh` diff (`git diff -U0 20e392e b8e485c`) touches only: the header comment, `VOCAB`/usage strings, the new `body_is_llamacpp_loading` classifier, the `classify()` branch, and the `listeners` summary counters. **Nothing in the snapshot write path changed.**
- `tools/test-snapshot.sh` never reaches the default: `WORK=$(mktemp -d …)` (`:13`), `HIST="$WORK/history"` (`:88`), and every `snapshot` invocation passes `--history "$HIST"` or `--history "$WORK/port-history"` / `"$WORK/link-history"`. It even asserts the invariant after an unchanged re-run: `PASS unchanged snapshot leaves DELTA.md byte-stable` and `… latest.tsv byte-stable`, `RESULT pass=30 fail=0` (`run-test-snapshot.txt`).
- `tests/probe-verdicts/check.py` invokes the probe with `--port` only (no `snapshot` subcommand).
- `tools/kama-llamacpp-live.py` and `.ufo/waves/round-16/measure.py` never call `snapshot` (`grep -n snapshot` returns only docstring prose about the frozen *file* snapshot, not the subcommand).

# Residual unknown (reported, not exercised)

`tests/probe-verdicts/check.py` binds test stubs on `("127.0.0.1", 0)` with **no registered-port guard** — `check.py:266` (`bind_closed_port`) and `check.py:309` (`ThreadingHTTPServer(("127.0.0.1", 0), handler)`); the literals `8080` and `34113` appear nowhere in that file. The kernel range is `32768 60999` (`/proc/sys/net/ipv4/ip_local_port_range`, 28232 ports), so `34113` is reachable by `bind(:0)` while `8080` is not.

Consequence and size, both [INFERENCE]:
- A stub holding `34113` for the sub-second probe window would shadow a registered consumer's port on loopback only; it would fail loudly with `EADDRINUSE` if a consumer were already listening, so it cannot silently displace a live consumer.
- Per matrix run, ~71 held stub binds out of 28232 → ≈0.25% chance of one landing on `34113`; the live harness itself is guarded (`port_refusal_set`, plus explicit refusals at `controls.txt:9-12`), so this gap is confined to the matrix harness.
- Empirically it did not happen: 0/144 draws in `{8080, 34113}`, min 32841, max 51349.

This does not refute N1 (no observed contact), but it is an asymmetry worth closing if the matrix harness is ever run while a `34113` consumer is intended to be reachable: the harness's own `port_refusal_set` discipline is not applied to its stub allocator.

# Limitations

- "Touched no registered consumer" is established from artifacts plus current host state. I did not have packet capture for the round's wall-clock window, so a completed TCP connection to `8080`/`34113` that left no artifact and no listener would be invisible; the receipt byte-content (two URLs, both on the picked port) makes that implausible but not impossible.
- The 0.25% figure is an order-of-magnitude estimate; the exact probability depends on kernel ephemeral-allocator sequencing, which I did not model.
- I did not run `measure.py` (forbidden — it rewrites L1 receipts) and did not start any server, so nothing here re-derives the C1/C2 measurements.

# Installs

None. No packages, tools, or upgrades were installed or changed.

# Out of scope, flagged for routing

`live/receipt.json` records `"loading_observed": false` and `"loading_envelope_exact": null` — the L1 live run did not itself capture the loading envelope. Not my item (the `FamilyLoadingEnvelope`/`FamilyLoadingRace` seats name it), noted only so it is not lost.
