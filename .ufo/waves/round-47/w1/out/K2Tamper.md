# K2Tamper — round-47 C2 tamper-leg attack (lane kama, leaf seat)

**Verdict (one line):** The C2 counter's tamper leg pins only two receipts — a first-hex-digit flip of `provenance.model.sha256` and of `provenance.server.asset_sha256` — and a replay tool (M2) that refuses exactly those two cases but accepts every other wrong-receipt class tested (wrong server member, different asset URL carrying the recorded digest, twin-consistent model-digest change, outcome fail) still measures `met=True`; the counter's C2 result therefore does not establish "refuses a receipt whose recorded digest is wrong" beyond those two flips.

Axes (godspeed): operability (judged axis, C2 8->8), sufficiency of the tamper leg, replay-tool refusal coverage, counter leg attribution.

## Setup (all scratch; lane read-only)

- Scratch `S=/fast/scratch/hyaku/kama-r47/K2Tamper`; lane clone `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` (read-only).
- Base fixture: `git clone --shared $S/lane $S/F0`; `git checkout -q -b fixture-base 3a09a1d93dcc16799cf6c4b48786e6440af134c4`; one appended SOURCES registry row (`| S499 | ... b11909 ... caa8191df159f764fb0160e3d2fc6be008948aee ... |`; fixture identity `K2Tamper-fixture <k2tamper@fixture.local>`); `git rev-parse --show-toplevel` asserted to equal `$D` before the commit. F0 tip `e3ee84e11983275e6a83bfa221734b40120b23e1`.
- Variant fixtures F1–F4: clones of F0, one commit each mutating only `.ufo/waves/round-47/c2/live/receipt-1.json`. Fm: clone of F0 with M2 mutant at `tools/kama-live-replay.py`.
- Every counter run: `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round47-live-replay-audit.py --repo <clone> --tip <full> --scratch $S`. Full verbatim outputs in `.ufo/waves/round-47/w1/out/K2Tamper/evidence-run-outputs.log`.

## Result A — the counter catches all four variant classes today, but never via the tamper leg

| variant receipt (receipt-1) | counter | caught by | honest replay tool, direct |
|---|---|---|---|
| honest (F0) | receipts=1 replay=1 tamper=1 newrow=1 **met=True** | — | exit 0 match |
| F1 `provenance.server.member` := `llama-b11909/llama-cli` (exists, wrong binary) | receipts=1 replay=0 tamper=1 met=False | **replay leg** (rerun outcome `setup-error`, 11 checks lost; exit 1) | exit 1 match=False mismatches=12 — tool *attempts* the wrong binary, does not refuse it at intake |
| F2 `provenance.server.asset_url` := same URL + `?mirror=k2` (same bytes, same digest) | receipts=0 replay=1 tamper=1 met=False | **receipts leg** (`check_receipt` compares `asset_url` to the frozen constant; `round47-live-replay-audit.py:153-154`) | exit 0 match — the replay tool re-acquires from any URL and verifies bytes only |
| F3 `provenance.model.sha256` **and** `model.sha256` := `"5"*64` (twin-consistent) | receipts=1 replay=0 tamper=1 met=False | **replay leg** (`acquire` digest mismatch at `kama-live-replay.py:89-95`; exit 2) | exit 2 refused digest-mismatch |
| F4 `outcome` := `fail` | receipts=0 replay=0 tamper=1 met=False | **receipts leg** (outcome != pass; `:145-146`) and replay leg (outcome compare; exit 1) | exit 1 match=False mismatches=1 |

Notes: tamper=1 in every run (the two canonical flips are always refused). The receipts leg passes F1 and F3 (member is only required to be a non-empty string, `:157-158`; model sha is required to be 64-hex and equal to `model.sha256`, `:161-164` — there is **no frozen model digest** and the model URL is only required to start with `https://`, `:159-160`).

## Result B — sufficiency counterexample: M2 passes the whole counter while accepting all four wrong classes

M2 (`.ufo/waves/round-47/w1/out/K2Tamper/kama-live-replay.m2.py`, sha256 `d49da7647c9ddd984ed531980459645d4ad4baff6900fb7b61cc245316ccd6ed`, unified diff `kama-live-replay.m2.diff`) = the honest tool with four relaxations: (1) `acquire()` no longer compares downloaded bytes to the recorded sha (`:89-95` replaced; the asset flip is instead refused against a hardcoded frozen asset sha inside `provenance()`); (2) the member-existence/containment intake check (`:146-147`) dropped; (3) the live tool gets the **actual** downloaded model sha, not the receipt's recorded claim (so the live tool's own `model-digest-mismatch` gate cannot trip on a twin-consistent receipt); (4) `compare()` skipped — match is always True when a rerun receipt exists.

Direct runs (M2 from Fm tree):

| receipt | M2 exit / J | honest exit / J |
|---|---|---|
| F1 wrong member | **0**, match=True | 1, mismatches=12 |
| F2 different asset URL, same digest | **0**, match=True | 0, match=True |
| F3 twin-consistent digests | **0**, match=True | 2, refused |
| F4 outcome fail | **0**, match=True | 1, mismatches=1 |
| v2b file:// mirror asset URL, same digest | **0**, match=True | 0, match=True |
| canonical model flip | 2 refused | 2 refused |
| canonical asset flip | 2 refused | 2 refused |

Full counter on Fm (honest receipts + M2 in the tree): **`receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True`, exit 0**. The counter cannot distinguish the honest tool from a tool whose refusal gate is exactly the two canonical flips.

## Finding (defect in the counter — frozen, not fixed in place)

- **File/line:** `tools/round47-live-replay-audit.py:294-319` (tamper leg) — the only leg that presents deliberately bad receipts to the replay tool; it iterates exactly two key-paths (`("provenance","model","sha256")`, `("provenance","server","asset_sha256")`) and flips the first hex digit (`:305`).
- **Command that shows it:** `python3 tools/round47-live-replay-audit.py --repo $S/Fm --tip 256151b21d5c232e12a0c309c04306f3bc25ad8e --scratch $S` → `met=True` with the M2 tree (evidence-run-outputs.log §7).
- **Smallest safe correction:** widen the tamper corpus to the classes the claim asserts, each requiring nonzero exit and no pass rerun: (a) twin-consistent model-digest change (both `provenance.model.sha256` and `model.sha256` set to a different 64-hex); (b) wrong-but-existing member (`llama-b11909/llama-cli`); (c) altered asset URL carrying the same bytes (`?mirror=` query on the frozen URL); (d) `outcome: "fail"`. Optionally add a frozen model digest and a model-URL equality check to `check_receipt` (currently only `https://` prefix, `:159-160`) if "record where the model came from" is meant to pin the URL.
- **Scope note:** same-digest-different-URL receipts are *not impossible* (mirror/proxy serving identical bytes; demonstrated with a `file://` byte-identical mirror and with the `?mirror=k2` query — the replay leg itself ran successfully on the altered URL, F2 run). The honest tool accepts them by design (it verifies bytes, not URL identity); the counter currently stops them only via its own frozen `asset_url` constant. The claim's letter ("refuses a receipt whose recorded digest is wrong") is not violated by accepting correct-digest receipts, so the gap is the *sufficiency* of the tamper evidence, not a false met for the honest build.

Impacted axis: **operability** (C2). The L1 measurement at integration (receipts=1 replay=1 tamper=1 newrow=1) will be true for the honest build; this finding says that met does not certify replay-tool refusal beyond the two flips.

Tooling: no installs performed (nothing needed beyond python3 stdlib). No lane/fleet files modified; all fixtures lived in scratch and are deleted below.
