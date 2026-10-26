# Round-48 Gate decisions — lane kama

Verdict: the build's two claims are met at the build tip `380bcdff9c8af06997c482f6eb03db926a794a2b` on my own run (C1 `met=True` exit 0, C2 `met=True` exit 0), calibration stays 7 and operability stays 8; the gate **rejects eight evidence forms** the lane could otherwise have leaned on, and holds the round open until the counter receipts are re-run at the final tip (the lane is at `b85783e8`, five commits' worth of wave scaffolding after the build).

- Seat: S1Gate, leaf, round 48, lane `kama` (local model serving / endpoint health).
- Axes: **calibration** (C1, `7 -> 7`) and **operability** (C2, `8 -> 8`).
- Frozen contract: `.ufo/waves/round-48/preregistration.json` (frozen `2026-10-26T22:19:34Z`, lane commit `12284ba3`), counters `tools/round48-append-audit-v3-check.py` / `tools/round48-live-replay-v5-audit.py`, controls `.ufo/waves/round-48/controls/`.
- Build: `380bcdff`, base `33e005827742b29772b153cda036ec9f27f653be`.
- My runs are independent of the L1 dry run (own `git clone --shared`, own scratch, own receipts in this directory: `c1.json`, `c2.json`, `c1tool.json`, `probes.txt`, `loc1.txt`, `loc2.txt`). I did not start, stop or restart any service; the C2 counter's own replay was the only process tree that ran a `llama-server`, and it tore it down (counter exit 0, `replayed=3/3`).
- No lane file was edited; proposed text appears only as a finding below.

Each decision: **claim**, **evidence** (command + output), **verdict**, **flip condition**. Commands are run from my scratch with `$S=/fast/scratch/hyaku/kama-r48/S1Gate` and `$L=$S/lane` (clone of the lane, HEAD `b85783e8`, `git rev-parse --show-toplevel` = the clone).

---

## D1 — ACCEPT: the calibration verdict is the v3 tool's exit code at the measured tip, not a reading of the diff

**Claim.** A calibration claim about an instrument is decided by the instrument's own verdict at the tip, scored by the frozen counter, not by whether a reviewer finds the design reasonable.

**Evidence.**
```
$ python3 $L/tools/append-only-audit.py --repo $L --to 380bcdff... --json   # exit=0
schema append-only-audit/v3
{commits 311, files 89, events 5, restored 5, partial 0, unrestored 0, ungraded 0,
 ungraded_lines 89, regressed 0, vanished 0, unmatched 0, binary 0, bad_declarations 0}
events: dd9f5dc6 SCORECARD.md deleted 31 graded 14 ungraded 17 restored held_to 14 max 14
        0718b6ab LOG.md deleted 2292 graded 2292 ungraded 0 restored held_to 2292 max 2292
        0718b6ab SCORECARD.md deleted 2421 graded 2349 ungraded 72 restored held_to 2349 max 2349
        0718b6ab corpus/QUALITY.md deleted 375 graded 375 ... corpus/README.md deleted 663 graded 663 ...
$ python3 tools/round48-append-audit-v3-check.py --repo $L --tip 380bcdff... --scratch $S/c1run --out $S/c1.json
selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True   # exit=0
```
Exit rule under test: `tools/append-only-audit.py:470-474` (`1` on partial/unrestored/regressed/vanished/bad_declarations).

**Verdict.** ACCEPT. The five legs and the tool's own exit are the verdict; `regressed` reaches the exit (round-47 X1Stable) — `regressed 0` and `exit 0` are the same run.

**Flip condition.** A tip where the tool exits 1 while the counter's lane leg still prints `lane=1` (or the reverse). Then the counter is scoring its own recomputation, not the tool, and the claim's "measured" type fails.

---

## D2 — REJECT: the pre-build base state as calibration evidence

**Claim (rejected).** The base row shows the instrument was broken, therefore the build's correction is worth calibration credit by itself.

**Evidence.**
```
$ cat .ufo/waves/round-48/controls/base.c1.out          # exit=1
selftest=0 contract=0 lane=0 fixture=0 stable=0 rows=0 files=0 lane_events=0 lane_failures=NA ungraded_lines=0 fixture_fail=11 met=False
tip=33e005827742b29772b153cda036ec9f27f653be
detail: contract: header is not the v3 header (or CR present)
detail: fixture threshold: no v3 JSON (exit 2; could-not-evaluate: contract header is not path<TAB>rule<TAB>declared_at<TAB>note); exit 2 want 1
...
detail: fixture clean: no v3 JSON (...); exit 2 want 0
```

**Verdict.** REJECT. The base row is a floor, not a level: at the base the *v3 contract* does not exist, so every leg is `0` by construction (`rows=0 files=0`), not because the lane regressed. Citing it as evidence that the lane was at 6 or that the build "fixed 7 legs" would be reading a contract-absence artefact as a measurement.

**Flip condition.** A rerun of the frozen C1 counter at base `33e0058` that yields any leg `1`; then `base.c1.out` is misdescribed and that is a control defect, not a lane fact.

---

## D3 — REJECT: a relabelled v2 tool, or the v3 contract with the SCORECARD row dropped, as C1 evidence

**Claim (rejected).** Because `regressed=0`/`lane_failures=0` is reachable by removing the awkward row, a clean lane summary from a modified instrument counts.

**Evidence.**
```
$ sed -n 1p .ufo/waves/round-48/controls/junk-c1-v2-relabel.c1.out
selftest=0 contract=0 lane=0 fixture=0 stable=0 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=11 met=False
detail: lane: 0718b6abbda6 SCORECARD.md status tool=partial counter=restored
$ sed -n 1,3p .ufo/waves/round-48/controls/junk-c1-drop-scorecard.c1.out
selftest=0 contract=0 lane=0 fixture=0 stable=0 rows=8 files=88 lane_events=3 lane_failures=0 ungraded_lines=0 fixture_fail=11 met=False
detail: contract: required row SCORECARD.md missing
```

**Verdict.** REJECT. Both shortcuts keep the cheap-looking number (`lane_failures=0`, `ungraded_lines=0`) and lose the claim: the second drops an event and the row, the first is caught by the counter's own recomputation (`tool=partial` vs `counter=restored`). Contract completeness (`rows=9`) and the fixture leg are what make the lane number mean anything.

**Flip condition.** A relabelled instrument that passes all five legs *and* the eleven fixtures; then the legs are vacuous and the claim's instrument correction is unmeasured.

---

## D4 — ACCEPT (provisional): C1 is met at the build tip, calibration stays 7

**Claim.** At the measured commit, `append-only-audit/v3` + the 5-cell contract grade the lane's append-only files under declared bound regions, the counter agrees with the tool, and no graded loss/regression/vanished path/unbound declaration remains.

**Evidence.**
- My counter run (D1): `selftest=1 contract=1 lane=1 fixture=1 stable=1 ... lane_failures=0 ungraded_lines=89 met=True`, `exit=0`, tip `380bcdff`.
- The contract is 9 data rows × 5 cells, including the region cells the claim names: `registry/append-only-contract.tsv:3` `SCORECARD.md ... exempt=## Axes|## Planned|## Retired|## Saturation|## Capabilities@SCORECARD.md:6` and `:10` `corpus/knowledge/consumer-registry.md ... only=## Errata@...:30`. `SCORECARD.md:6` does declare those head sections re-derived (starts `**Current authority (round 48):** ...`).
- The build's own finding is carried by the tree and the run: the superseded authority banners now live as appended text under `SCORECARD.md:2736` (`### Superseded head banners (kept verbatim; round 48)`, with the r45/r46/r47 banner lines below it, file end 2744 lines), and the run reports 5 events with `regressed 0` where the prereg records v2 at the base reporting `regressed 1`. The banners' byte-exactness against the pre-rewrite heads is the build's claim, not something the counter's summary shows; I did not re-verify it.
- Stable leg is non-vacuous: base `33e0058` ≠ tip `380bcdff` (`stable base` per the counter docstring).

**Verdict.** ACCEPT at `380bcdff`; score 7 (unchanged, as preregistered). Provisional only because of D14.

**Flip condition.** Any leg `0` at the final tip → `met=False` → the prereg's kill rule applies (claim not achieved, never narrowed).

---

## D5 — ACCEPT (provisional): C2 is met at the build tip, operability stays 8

**Claim.** Three committed v5 receipts pin the model to an HF revision and carry record-time-verified provenance; the live tool refuses unverifiable provenance before starting a server; every receipt replays from committed bytes with an equal stable projection; wrong digests and swapped URLs are refused; the pin is a source row.

**Evidence.**
```
$ python3 tools/round48-live-replay-v5-audit.py --repo $L --tip 380bcdff... --scratch $S/c2run --out $S/c2.json
receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True
tip=380bcdff9c8af06997c482f6eb03db926a794a2b started=2026-10-26T22:35:02.370894+00:00   # exit=0
```
- Receipts: `.ufo/waves/round-48/c2/live/receipt-{1,2,3}.json`, schema `kama-llamacpp-live/v5`, 11 checks each, `build_info` `b11909-…`; receipt-1 provenance:
  `model.commit 499bc8821c6b12b4e53c5bffcb21ec206f212d81`, `model.url .../resolve/499bc882…/tinyllamas/stories260K.gguf`, `model.sha256 270cba1b…`, `verified.at record`, `verified.archive_sha256 = server.asset_sha256 = bf94332a…`, `verified.member_sha256 = server.sha256 = 35ac50fb…`.
- Pin is a source row: `corpus/SOURCES.md:245` (S492) quotes `x-repo-commit: 499bc882…` and `x-linked-etag: "270cba1b…"`; the counter's `newrow` leg found it (`newrow=1`).
- The counter re-acquired and re-ran: `replayed=3/3`; `tamper=1`, `urlswap=1` (the swap model 22027b1a serves `68c694e7…`, not the recorded digest — my own HEAD of that commit reproduces it: `x-linked-etag: "68c694e7584c358446e8ec05c4648c72382aa3457b56443e35a6fecf55b429d2"`).

**Verdict.** ACCEPT at `380bcdff`; score 8 (unchanged, as preregistered). Provisional only because of D14.

**Flip condition.** Any leg `0` at the final tip, or a receipt whose `verified` block disagrees with its own declared digests (D12's flip).

---

## D6 — REJECT: `x-linked-etag` as proof of the revision

**Claim (rejected).** `x-linked-etag: "270cba1b…"` names the commit the bytes came from, so pinning it pins the revision.

**Evidence.**
```
$ for c in 499bc882... e2d5caf5... 96f460f9... 22027b1a...; do curl -sSI ".../resolve/$c/tinyllamas/stories260K.gguf"; done
499bc882... (2025-10-28T10:43:38Z)  x-repo-commit: 499bc882...  x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
e2d5caf5... (2025-10-28T09:18:28Z)  x-repo-commit: e2d5caf5...  x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
96f460f9... (2025-10-28T08:55:08Z)  x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
22027b1a... (2025-10-28T08:07:12Z)  x-linked-etag: "68c694e7584c358446e8ec05c4648c72382aa3457b56443e35a6fecf55b429d2"
$ curl -sSL "<pinned URL>" | sha256sum     # 1,185,376 bytes
270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
```
Three distinct commits (499bc882, e2d5caf5, 96f460f9) share one etag, and that etag equals the sha256 of the downloaded bytes: it is the LFS *object* digest (content identity), not a commit identity. The header that names the commit is `x-repo-commit` on the same response.

**Verdict.** REJECT. A gate that accepted the etag as revision proof would accept any URL serving that object at any commit — exactly the "pinned" claim C2 is not making. The revision is carried by the URL's `/resolve/<40-hex>/` segment plus `provenance.model.commit`, and the digest is carried by sha256 of bytes.

**Flip condition.** A response where `x-linked-etag` differs between two commits serving byte-identical content, or differs from `sha256(body)`; either would show it is commit-derived.

---

## D7 — REJECT: the CDN redirect target as a locator

**Claim (rejected).** The `302 Location` (`https://us.aws.cdn.hf.co/xet-bridge-us/…?…`) can be kept as the replay locator, since it is what actually serves the bytes.

**Evidence.**
```
$ curl -sSI "<pinned URL>"      # 302, cache-control: no-store
location: https://us.aws.cdn.hf.co/xet-bridge-us/6580840062b6ed53c4c72d61/7cfbf69e…?…&Expires=1793057674&Policy=eyJTdGF0ZW1lbnQi…&Signature=…
Expires observed: 1793057674 -> 2026-10-26T23:34:34Z (fetch 22:34:34)
                  1793057702 -> 2026-10-26T23:35:02Z (fetch 22:35:02)      each = fetch + 3600 s
                  1793057735 -> 2026-10-26T23:35:35Z (fetch 22:35:35)
$ two HEADs one second apart, same Expires/xip -> "locations differ: DIFFER"; the only differing query field is
  Signature=MEQCIDdOs69S3Zh0dBSsAGFODKkFE9UeFRPRxC6%7EVVfJZpFFAiB53%7EZtBh1ksp84voCgPzvUCRp-iHMHETcwnGPjtsNc0A__   (loc1.txt)
  Signature=MEUCIBnPaMV10hDfs5Xu8zgj4z2x8idT394qiM9NXI0xTzO3AiEAy-8U2B124e2ple2Mg8khgxu1iSxXfuSd5gI0Yu6YnGE_   (loc2.txt)
```

**Verdict.** REJECT. The target is a per-request signed URL with a one-hour `Expires` and a `Signature` that changes per fetch; `cache-control: no-store` on the 302 says the same. A committed locator of that form is dead within the hour and its signature is not evidence of anything.

**Flip condition.** A redirect that is stable across fetches, unsigned and content-addressed.

---

## D8 — REJECT: the CDN response `etag` (xet hash) as the artifact digest

**Claim (rejected).** S490 quotes the CDN 200's `etag: "7cfbf69e…"`, so that value can stand in for the model digest.

**Evidence.**
```
$ python3 -c 'urllib.request.urlopen(Request(loc1, method="HEAD"))'   # HEAD on the loc1.txt CDN URL
status 200
etag = "7cfbf69e76aef0af92130af4e5c57a2a170423fb2a273b4f11a04bcc70088ba5"
content-length = 1185376
EOF
sha256(bytes) = 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d   (same 1,185,376 bytes)
302 response also carries: x-xet-hash: 7cfbf69e76aef0af92130af4e5c57a2a170423fb2a273b4f11a04bcc70088ba5
```
The CDN tag is the xet reconstruction hash (same value as `x-xet-hash` on the 302), not the LFS sha256.

**Verdict.** REJECT. Only the LFS digest (`x-linked-etag` / `provenance.model.sha256` / sha256 of bytes) identifies the artifact the lane serves; the CDN tag identifies an xet reconstruction and would silently pass a different packing of other bytes.

**Flip condition.** A CDN response whose `etag` equals `sha256(body)` for a non-xet-hosted file (then the tag is the content digest there and the reject is too strong).

---

## D9 — REJECT: keeping S490's `main` resolve URL as the replay locator

**Claim (rejected).** The round-47 receipts already name a resolve URL; `.../resolve/main/...` is good enough as the locator, so the v5 pin adds nothing.

**Evidence.**
```
$ python3 -c 'json.load(round-47/c2/live/receipt-1.json)["provenance"]'
schema kama-llamacpp-live/v4, model.url = https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf, verified = null
$ api/models/ggml-org/models-moved -> sha 499bc882... (lastModified 2025-10-28T10:43:38Z)
$ api/models/ggml-org/models-moved/commits/main?limit=50  -> four commits on 2025-10-28 (08:07:12, 08:55:08, 09:18:28, 10:43:38)
$ tree at the previous main e2d5caf5: tinyllamas/stories15M-q4_0.gguf lfs oid 696f4aeb… (at 499bc882 it is 66967fbe…)
$ tools/kama-llamacpp-live.py:71  PINNED_MODEL_URL = re.compile(r'^https://[^/]+/.+/resolve/([0-9a-f]{40})/.+')
$ tools/kama-llamacpp-live.py:1477 parser.error('--model-url must be pinned to a 40-hex /resolve/<commit>/ revision (v5)')
$ tools/kama-llamacpp-live.py:1300-1302  selftest: 40-hex -> True, resolve/main -> False, 7-hex -> False
```
`main` is a branch that moved four times inside 2 h 36 min on one day and did change content at that path (`stories15M-q4_0.gguf`). A `main` locator in a committed replay receipt therefore names bytes that can change under the receipt, which is precisely what makes a replay non-reproducible.

**Verdict.** REJECT. S490 stays as filed (append-only, it is an honest record of what a v4 receipt did); the round-48 locator is S492's pinned URL. Note the trap: today `main` and the pin return the same `x-repo-commit` and the same etag (probes B), so the main URL "works" — that is a coincidence of the current ref, not a property.

**Flip condition.** A tag or `main` at that repo that is documented immutable (HF `main` is not; the download guide's revision paragraph in `.ufo/waves/round-48/c2/hf-hub-download-doc.txt` requires the full-length commit hash for reproducibility).

---

## D10 — REJECT: a short (7-hex) revision, or any ref, as the pin — even though HF resolves it

**Claim (rejected).** If `.../resolve/499bc88/...` serves the right bytes, the locator is fine; the 40-hex rule is cosmetic.

**Evidence.**
```
$ curl -sSI 'https://huggingface.co/ggml-org/models-moved/resolve/499bc88/tinyllamas/stories260K.gguf'
HTTP/2 302
x-repo-commit: 499bc8821c6b12b4e53c5bffcb21ec206f212d81
x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
```
The server resolves a 7-character prefix; the lane's pin regex (`tools/kama-llamacpp-live.py:71`) and its parser (`:1477`) do not, and its selftest pins that behaviour (`:1302`, 7-hex -> False).

**Verdict.** REJECT. The gate scores the locator's *form* (40-hex commit, enforced by the tool, per the huggingface_hub guide: "it must be the full-length hash"), not whether a lenient server happens to resolve it. A prefix is resolved by the server's own rule and can be ambiguous; "it fetches today" is the same argument D7/D9 reject.

**Flip condition.** HF documenting prefix resolution as unique and stable, or the lane tool accepting a prefix and the claim surviving — neither holds.

---

## D11 — REJECT: the receipts leg alone, and a fabricated `verified` block, as operability evidence

**Claim (rejected).** Three structurally valid v5 receipts with a self-consistent `provenance.verified` block are the operability evidence; the replay legs are extra.

**Evidence.**
```
$ sed -n 1p .ufo/waves/round-48/controls/junk-c2-r47-relabel.c2.out
receipts=1 recordcheck=0 replay=0 compare=0 tamper=0 urlswap=0 newrow=0 replayed=0/3 met=False
detail: replay 1: rerun started_utc '2026-10-26T21:16:50.545Z' precedes counter start
detail: replay 1: server file '/home/vgpnk/.local/opt/llama-b11909/llama-server' not under scratch
detail: replay 1: model file '/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf' not under scratch
detail: compare props-n_ctx: exit 0 want 1   / tamper-model: exit 0: not refused
```

**Verdict.** REJECT. The relabelled round-47 receipts with a fabricated verified block pass `receipts=1`; the counter's own replay then catches host-cache reuse, a back-dated `started_utc` and a no-op compare. Operability rests on the re-acquisition and re-run legs (`replay`, `tamper`, `urlswap`), which is why the claim lists all seven.

**Flip condition.** A replay that copies host-cache bytes and still passes; the counter hashes the rerun's server, model and archive itself (`replay=1` at the tip) precisely so that this cannot happen.

---

## D12 — ACCEPT: sha256 of re-acquired bytes plus the record-time `verified` block, re-checked against the declared digests, is the binding evidence

**Claim.** The evidence that a receipt's bytes are the frozen ones is a hash of bytes the verifier obtained, with the receipt's record-time verification cross-checked against its own declarations — not headers and not the receipt's prose.

**Evidence.**
```
R48 receipt-1 provenance:
  verified.archive_sha256 = bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b = server.asset_sha256
  verified.member_sha256  = 35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0 = server.sha256
  verified.model_sha256   = 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d = model.sha256
  verified.at = record
$ curl -sSL "<pinned URL>" | sha256sum -> 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d   (my own download, 1,185,376 bytes)
```
The counter's replay leg hashes the rerun's `server.realpath`, `model.path` and `J.inputs.archive` itself, requires them under `--scratch`, and requires `started_utc` not before the counter start (round-47 D1); `replayed=3/3` at the tip.

**Verdict.** ACCEPT, with the limit stated: the `verified` block is record-time self-attestation and is worth exactly the counter's independent re-hash. My own download reproduces the digest three ways (header, CDN bytes, frozen constant).

**Flip condition.** A receipt whose `verified` fields disagree with its declared `server.sha256`/`asset_sha256`/`model.sha256`, or a rerun whose files hash elsewhere (D11's control already shows what that looks like).

---

## D13 — ACCEPT: the 89 ungraded lines are the declared carve-out, not a loss

**Claim (gate reading).** `ungraded_lines=89` should not be read as 89 lines the instrument stopped covering.

**Evidence.**
```
$ python3 tools/round48-append-audit-v3-check.py ... -> lane_failures=0 ungraded_lines=89 met=True
events: dd9f5dc6 SCORECARD.md deleted 31 graded 14 ungraded 17
        0718b6ab SCORECARD.md deleted 2421 graded 2349 ungraded 72
$ registry/append-only-contract.tsv:3
SCORECARD.md  A-corr  corpus/README.md:761  exempt=## Axes|## Planned|## Retired|## Saturation|## Capabilities@SCORECARD.md:6
$ sed -n 6p SCORECARD.md -> "**Current authority (round 48):** ..." (declares the head sections re-derived in place)
```
17 + 72 = 89, both from `SCORECARD.md` head sections the contract binds to `SCORECARD.md:6`, and the exemption is conditional (a gutted section becomes graded — the counter's `exempt-gutted` fixture, `fixture=1`).

**Verdict.** ACCEPT as declared and bound: the declaration binds (`contract=1`, `bad_declarations=0`), the region is conditional rather than a blanket skip, and the two `## Errata` and append-only regions are graded (`contract=1` requires `only=## Errata` on `corpus/knowledge/consumer-registry.md`).

**Flip condition.** An exempt section whose window maximum falls below its parent count (then the tool grades it and the number must move), or a graded line satisfied only by identical text in an exempt section — the prereg's stated multiset limit.

---

## D14 — OPEN: the round cannot close on a receipt measured at the build commit

**Claim.** The gate can score the wave only at the tip that is closed; `380bcdff` is not that tip.

**Evidence.**
```
$ git -C $L log --oneline -3 b85783e8
b85783e8 round-48: wave spec kama-r48-w1 (69 seats, policy v2) and dispatch
380bcdff round-48: build - append-only-audit v3 + v3 contract with bound regions (C1), ... freeze-time receipt
12284ba3 round-48: freeze - counters (C1 append-only-audit v3, C2 live replay v5), preregistration, controls, start census, pinned HF revision record
```
Prereg routed item `r47-D9`: "tip-level regression receipts are re-run and committed at the final tip". Both my run and the L1 dry run measured `380bcdff`.

**Verdict.** OPEN — not a defect. The two claims are met *at the build tip*; the round's receipts must be regenerated at the final tip and the gate re-scores them with the same command.

**Flip condition.** A counter run at the final tip that reproduces `met=True` on both claims closes the gate; any leg `0` opens the prereg kill rule instead.

---

## D15 — ACCEPT as known limits (not defects): the three integration items

**Claim.** The integration items are known and do not move either claim.

**Evidence (cited, not re-run — per the seat brief these are the L1's items).**
1. `gate-registry-check` lists `tools/round48-append-audit-v3-check.py` and `tools/round48-live-replay-v5-audit.py` unregistered.
2. The round-41/42/43 counters read the spot-check count 33 vs 34.
3. `hexrun-census` has one unknown, `d0012618` (the round-47 fleet report commit).

**Verdict.** ACCEPT as known: none of the three is on a C1/C2 path, and (1) is about where the counters are registered, not whether they run (they do, `exit=0`).

**Flip condition.** A counter that fails only because it is unregistered, or a census unknown that lands on a measured path.

---

## Score recommendation

| Claim | Axis | Before | After | Basis |
|---|---|---|---|---|
| C1 | calibration | 7 | **7** | `met=True` at `380bcdff` (my run), region grading bound and conditional; score unchanged by design (instrument correction, prereg `score: 7->7`) |
| C2 | operability | 8 | **8** | `met=True` at `380bcdff` (my run), `replayed=3/3`, pin is a source row; unchanged by design |

No axis moves; both claims are *met* rather than *lifted*. Withdrawal would need D4/D5's flip conditions, and the gate would then apply the prereg kill rule (`met=False -> not achieved`), never a narrowed claim.

## Findings (new — beyond the known integration items)

**F1 (low, precision of a source row's justification).** `corpus/SOURCES.md:51` (S039) says "the same path held three different byte strings on 2025-10-28". The path holds three byte strings *over its history*, but only two are 2025-10-28 revisions.
```
tree at 11b0244f / 688f41dd / efc95dcc / eaf70b0d: tinyllamas/stories260K.gguf lfs oid 047bf46455a544931cff6fef14d7910154c56afbc23ab1c5e56a72e69912c04b
tree at 22027b1a: 68c694e7584c358446e8ec05c4648c72382aa3457b56443e35a6fecf55b429d2
tree at 96f460f9 / e2d5caf5 / 499bc882: 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
api .../commits/main?limit=50 -> four commits on 2025-10-28 (22027b1a 08:07, 96f460f9 08:55, e2d5caf5 09:18, 499bc882 10:43)
```
Proposed replacement text for that cell's justification (full cell, lane not edited):
> Names the pinned GGUF by sha256 and size; the path held three different byte strings across its history (047bf464… until 2025-09-26, 68c694e7… at 2025-10-28T08:07, 270cba1b… from 2025-10-28T08:55), so the digest, not the path, identifies it.

Not a defect against either claim (S039 is not on a C1/C2 path); the conclusion S039 draws is *strengthened* by the exact oids. Flip: a third distinct oid for that path at any 2025-10-28 revision.

**F2 (gate-level, no lane change).** HF resolves a 7-hex prefix (`HTTP/2 302`, `x-repo-commit: 499bc882…`) and `main` to the same object as the pin today. Therefore "the locator fetches" is never gate evidence; the 40-hex form is a lane-tool contract (`tools/kama-llamacpp-live.py:71,1477`, selftest `:1300-1302`) that the gate must score directly. This is why D9/D10 exist as separate rejects rather than as prose cautions.

**F3 (limit, accepted by design).** The stable projection treats the served model alias/ids as stable surfaces, so a round-48 receipt compared with a round-47 receipt differs on `projection:models` and `projection:props.model_alias` and exits 1:
```
$ python3 $L/tools/kama-live-replay.py --compare R48/receipt-1.json R47/receipt-1.json
compare match=False mismatches=3   (schema v5->v4; projection props alias; projection models ids)   exit=1
$ ... --compare R48/receipt-1.json R48/receipt-2.json   -> match=True mismatches=0  exit=0
$ ... --compare R47/receipt-1.json R47/receipt-2.json   -> match=True mismatches=0  exit=0
```
Correct for a replay (a rerun that renames the model is not the same run), but it means `--compare` across rounds is expected to fail; no receipt pair from different rounds should be used as a compare control.

**F4 (note for later seats).** The two counters' `--out` receipt is the one-paragraph summary text (the same as stdout), not JSON:
```
$ file c1.json -> ASCII text; content = "selftest=1 contract=1 ... met=True\ntip=380bcdff...\n"
```
`--json` belongs to `tools/append-only-audit.py`; parsing the counter receipt as JSON fails. Not a defect — recorded so the next gate does not re-derive it.

## Evidence in this directory

| File | What |
|---|---|
| `probes.txt` | verbatim commands + outputs of every probe (A–U) |
| `c1.json`, `c2.json` | my counter receipts at `380bcdff` (plain-text summary form, F4) |
| `c1tool.json` | `tools/append-only-audit.py --repo <clone> --to 380bcdff --json` at the tip tree |
| `loc1.txt`, `loc2.txt` | the two signed CDN locations, one second apart (D7) |
