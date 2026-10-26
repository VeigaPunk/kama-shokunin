# X0Digest — digests and object ids round 48 introduces (measured no-change for the assigned set)

**Verdict:** every assigned object id resolves at build `380bcdff9c8af06997c482f6eb03db926a794a2b` and stays resolved when a draft SCORECARD/LOG paragraph names it — `digest-ledger` `unknown=0` (exit 0) unchanged, `hexrun-census` at its pre-existing `unknown=1` (`d0012618`) — so **no ledger row is required for the assigned six values**; the live risk is adjacent: **7 of the 8 derived digests the v5 receipt records become `unknown`** if a round-48 summary reports them, and two of those (props, slots body digests) are **not recomputable from lane evidence at all**. Draft rows for all seven validated to zero both censuses.

Scope discipline: this seat ran only `tools/digest-ledger.py` and `tools/hexrun-census.py`. C1 (`round48-append-audit-v3-check.py`) and C2 (`round48-live-replay-v5-audit.py`) were **not** run here; nothing below claims their result. All work on one scratch clone `git clone --shared` of the lane; fixture commits exist in that clone only.

## 1. The assigned values and where they are pinned

| value | class at `380bcdf` | pinned at |
|---|---|---|
| server `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` | digest `external_ok` (ledger `registry/digest-ledger.tsv:16`) | `.ufo/waves/round-48/c2/live/install.txt:3`; receipt-1.json:405 `provenance.verified.member_sha256` |
| archive `bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b` | digest `external_ok` (`digest-ledger.tsv:17`) | `install.txt:4`; receipt-1.json:398 `provenance.server.asset_sha256` |
| model `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` | digest `external_ok` (`digest-ledger.tsv:6`) | `install.txt:6`; receipt-1.json:406 `provenance.model.sha256` |
| pinned HF revision `499bc8821c6b12b4e53c5bffcb21ec206f212d81` | hexrun `upstream_ok` (`registry/hexrun-ledger.tsv:25`) | receipt-1.json:393 `provenance.model.commit` |
| freeze `12284ba39fb1b46b43d43ee82423bebe08c700dc` | hexrun `lane_oid` | new this round (ancestor of the build) |
| build `380bcdff9c8af06997c482f6eb03db926a794a2b` (+ base `33e005827742b29772b153cda036ec9f27f653be` = `lane_oid`) | hexrun `lane_oid` | new this round |

All three `receipt-{1,2,3}.json` carry the same provenance (`schema=kama-llamacpp-live/v5`, receipt-1.json:409; `verified.at=record`), and `sha256sum` of the three on-host files reproduces the ledger digests today (`out/X0Digest/host-hashes.txt`: archive 22475032 B, model 1185376 B, server 17864 B). Independent check that the tool-time and audit-time records agree: `external_ok=9` is identical at the build and at every fixture below.

## 2. Commands, outputs, exit codes (full transcript `out/X0Digest/census-runs.txt`)

```
# clone
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane      # one live clone
# baseline, build
python3 tools/digest-ledger.py  scan --repo $L --rev 380bcdf…  → tokens=123 blob=107 external_ok=9 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0   exit=0
python3 tools/hexrun-census.py  scan --repo $L --rev 380bcdf…  → tokens=1803 distinct=288 lane_oid=184 md5_blob=1 upstream_ok=91 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=1            exit=1
```

The `unknown=1` is the known integration item, unchanged by this round: `d0012618894c7154683d97bb594b2dd5abbed013`, cited at `corpus/lessons/round-47-verifier-spotcheck.md:22`; `git -C /home/vgpnk/Projects/shokunin log -1 d0012618` → `round-47: kama report` (fleet repo, not a lane object). Not re-reported as a finding; a draft row for it is offered in §5.

## 3. Fixture experiment — a draft paragraph naming the assigned values

Three commits in the scratch clone, each detached from `380bcdf`, identity asserted with `git rev-parse --show-toplevel` and inline `-c user.name/user.email` (diffs: `out/X0Digest/fixture-diffs.diff`):

| fixture commit | paragraph | digest-ledger | hexrun-census |
|---|---|---|---|
| `5a4bdfc8220c2993fcb69d4892d5360cd9d7c631` | `## Round 48` block appended to **LOG.md**, naming all six values | `tokens=123 … unknown=0` **exit 0** (identical to baseline) | `tokens=1808 distinct=291 lane_oid=187 … unknown=1` exit 1 |
| `1bf9713d2ff6d4ca5e822bd5c7e4493ca872f96f` | same block appended to **SCORECARD.md** | `tokens=123 … unknown=0` **exit 0** | `tokens=1807 distinct=291 lane_oid=187 … unknown=1` exit 1 |
| `b56efcc9e27a8184804e39c3628ece6ba56ab386` | `5a4bdfc8` **+** a second bullet naming the receipt's derived digests | `tokens=131 … unknown=7` **exit 1** | unchanged (`unknown=1`) |

Named-token classes at the fixture (`--details`): `12284ba3…` `lane_oid`, `380bcdf…` `lane_oid`, `33e00582…` `lane_oid`, `499bc882…` `upstream_ok`, `704366d7…` (receipt source commit) `upstream_ok`. `lane_oid` is object **existence**, not reachability (`tools/hexrun-census.py:23`, `:186-197` `cat-file --batch-check`), so an unreachable ancestor would still resolve — the risk to watch is a *shallow or pruned* clone, not ordering. The SCORECARD variant differs from the LOG variant only in occurrence count (1807 vs 1808, one fewer citation of `704366d7…`), which confirms file choice does not change classification: both censuses tokenize the union of documents (`digest-ledger.py:75 is_doc`, `hexrun-census.py:16` — `.md`/`.tsv` outside `.ufo/`).

**Answer to "which would become unknown": none of the assigned set.** The paragraph that does cause unknowns is the one that reports measured surfaces (§4).

## 4. What would become unknown, and why

At `b56efcc9` (digest-ledger `unknown=7`, exit 1) — every value here is recorded in a v5 receipt, none is ledgered:

| token | what the receipt calls it | recomputable from lane evidence? |
|---|---|---|
| `9f1198f4e2d64495ea6e6c6dece9f95a34ab2e4e2a11f72fd7debd1024d5542e` | `server.install_tree_sha256` | **yes**, exactly (see below) |
| `5cb9f4865c8e1315dbd1baa99310c9bc65ddcf469929488359c66587b6470060` | `server.install_links_sha256` | **yes**, exactly |
| `431c5c2c57aff39fb220afe83adfe6f8eb232d8cbaedc1512d162eef63bc729b` | `captures.models.body_sha256` | **yes** (body string stored) |
| `baa09177700f64520a799fd2628bb3663c1486b25e17e4a507f2e6c81bef957c` | `loading_503.body_sha256` | **yes** (body string stored) |
| `b8f0f203f3c593225710bc2075b404944037b172c021e0136791dbff6f9043c2` | `server.server_impl_sha256` | **yes** — it is a real file: `/home/vgpnk/.local/opt/llama-b11909/libllama-server-impl.so` hashes to it |
| `f6cb10aaadd5ca999e3b0fe4855ed44eb4efa2b33f3e93a9752de8e3fd2422e6` | `captures.props.body_sha256` | **NO** — the body is elided (`keep_body=False`, `tools/kama-llamacpp-live.py:817`); only `fields` is kept (`:833`) |
| `6d345b4035d771f3303f5be226fae1ce9cc9c45182d43587ac073b2f583efb30` | `captures.slots.body_sha256` | **NO** — elided at `:836`; only `element_count` (`:844`), and slot bodies carry per-request state so a re-capture will not reproduce the digest |

Recomputations recorded in `out/X0Digest/recompute.txt` (equal=True for all of them, receipts 1–3): `install_tree_sha256` = sha256 over `'<name> <sha256>\n'` lines (`kama-llamacpp-live.py:255-256`); `install_links_sha256` = sha256 of canonical JSON of the link map (`links_digest`, `:260-265`); the three stored bodies (`health`, `models`, `loading_503`) hash to their recorded values.

One nuance worth knowing before citing a health body: `captures.health.body` is the 15-byte `{"status":"ok"}` and `a29ee2b1…` therefore classifies as `blob` for a reason unrelated to round 48 — the committed round-25 capture `.ufo/waves/round-25/a2-build/out/ExecCapacityTool/receipt/raw/K1.health.body` has exactly those bytes. `blob` proves "some committed blob holds these bytes", not "this round's capture is committed"; here it is harmless because the bytes are identical, and it is a clean route for the models/loading bodies too (commit the raw body under `.ufo/`, no ledger row needed).

## 5. Draft ledger rows (not applied) and their validation

`out/X0Digest/digest-ledger-proposed-rows.tsv` (7 rows: 1 `external` for `b8f0f203…` pointing at the on-host member, 6 `unverifiable` with the recompute rule or, for props/slots, the elision reason). `out/X0Digest/hexrun-ledger-proposed-rows.tsv` (1 row: `d0012618…` `unverifiable` with the fleet-repo identity — `upstream` is not available for it because the only lane evidence, the lesson line, holds the token but no upstream copy).

Validated by ledger **override** (lane ledger at `380bcdf` + the drafts, so nothing is replaced — a bare `--ledger` override would drop all 17/106 existing rows):

```
python3 tools/digest-ledger.py scan --repo $L --rev b56efcc9… --ledger merged-digest.tsv
→ tokens=131 blob=108 external_ok=10 external_absent=1 unverifiable=11 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0   exit=0
python3 tools/hexrun-census.py scan --repo $L --rev 380bcdf… --ledger merged-hexrun.tsv
→ tokens=1803 distinct=288 lane_oid=184 md5_blob=1 upstream_ok=91 unverifiable=10 wrong_flagged=2 ledger_bad=0 unknown=0            exit=0
```

(`out/X0Digest/{digest,hexrun}-ledger-override-validation.out`.) So the drafts are contract-valid and sufficient; whether to land them is the L1's call, and `props`/`slots` would land as `unverifiable`, which is honest but documents an evidence gap rather than closing it.

## 6. Risks

1. **Host-copy dependence.** The archive and model `external_ok` rest on `/home/vgpnk/.local/opt/llama-b11909-bin-ubuntu-x64.tar.gz` and `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf`. `~/.cache` eviction is a recorded past event (LOG.md round-47 entry, r45-D3), and an evicted path decrements to `external_absent`, which is **exit-neutral** (`digest-ledger.py:52`, `:384` count only `ledger_bad + wrong_unflagged + unknown`). A future paragraph citing the model digest would then pass the census with the digest unverified on disk. Today both files are present and match.
2. **Two of the v5 receipt's own digests cannot be checked from lane evidence** (`props`, `slots` bodies, §4). Any report that quotes them is quoting an assertion.
3. **Do not cite the fixture ids**: `5a4bdfc8…`, `1bf9713d…`, `b56efcc9…` exist only in the scratch clone (deleted). They are `lane_oid` there and `unknown` everywhere else.
4. **A `.ufo`-only citation does not count.** Both censuses exclude `.ufo/`, so a wave report or a receipt cannot satisfy either census on its own; the paragraph must land in a real document (LOG.md, SCORECARD.md, `corpus/…`).

## 7. Findings against the build

No defect found in what this seat measured: both censuses behave per their docstrings on the fixture, and the assigned values need no new row. One evidence-capability gap, in the v5 tool (not a counter, and not something this seat may edit — proposed, not applied):

- **Gap:** `tools/kama-llamacpp-live.py:817` and `:836` capture `/props` and `/slots` with `keep_body=False`, then record `body_sha256` in the capture row while the receipt keeps only `fields` (`:833`) / `element_count` (`:844`). Reproduce: `out/X0Digest/recompute.txt` — for receipts 1–3, `captures.props.body` and `captures.slots.body` are absent, so `f6cb10aa…` and `6d345b40…` are unrecoverable.
  *Fix options (either):* (a) land the two `unverifiable` rows from `digest-ledger-proposed-rows.tsv`, so a citation resolves with the reason recorded; or (b) set `keep_body=True` for `/props` and `/slots` — the props body is small and would become `blob`-resolvable if committed as raw evidence; `/slots` bodies carry request state and should stay a ledger row.

## 8. Tooling and hygiene

- No installs, no upgrades, no `pacman` (host pause respected); nothing written to `~/.local/bin`.
- Scratch `/fast/scratch/hyaku/kama-r48/X0Digest` removed after copying evidence; all paths above are the lane out directory.
- Nothing written outside `.ufo/waves/round-48/w1/out/X0Digest*`; the lane's git/jj state was never touched (all mutating git ran in the scratch clone, after `rev-parse --show-toplevel` assertion).

## Files

| path | contents |
|---|---|
| `.ufo/waves/round-48/w1/out/X0Digest.md` | this report |
| `.ufo/waves/round-48/w1/out/X0Digest/census-runs.txt` | 5 scan runs (build, 3 fixtures, details) with exit codes |
| `.ufo/waves/round-48/w1/out/X0Digest/host-hashes.txt` | on-host sha256 of archive/model/server/member, tool digest, health body |
| `.ufo/waves/round-48/w1/out/X0Digest/recompute.txt` | recompute of install-tree/links digests and of every stored capture body, receipts 1–3 |
| `.ufo/waves/round-48/w1/out/X0Digest/fixture-diffs.diff` | the three fixture commits (paragraphs + parent) |
| `.ufo/waves/round-48/w1/out/X0Digest/digest-ledger-proposed-rows.tsv` | 7 draft digest-ledger rows |
| `.ufo/waves/round-48/w1/out/X0Digest/hexrun-ledger-proposed-rows.tsv` | 1 draft hexrun-ledger row (`d0012618…`) |
| `.ufo/waves/round-48/w1/out/X0Digest/digest-ledger-override-validation.out`, `…/hexrun-ledger-override-validation.out` | merged-ledger runs that take both censuses to `unknown=0`, exit 0 |
