# X4HexR45 — round-47 hexrun unknowns from `registry/recheck-r45.tsv` and `corpus/README.md`

**Verdict: PASS (calibration).** All five cited ids are real objects in the upstream repositories their `SOURCES.md` rows name — four commits and one commit whose file blobs are byte-equal to the lane's stored copies — and ledger as `class upstream`: on a fixture commit that carries the five evidence files, `hexrun-census.py scan` moves `unknown 22 -> 17`, `upstream_ok 68 -> 73`, `ledger_bad 0 -> 0`. Three integration items are handed to the lane L1 with evidence: two merge hazards in sibling rows (duplicate `d854d98b`, one `repo` cell the census cannot match) and one token the round's range split never assigns (`ec82db00`), for which an advisory row and evidence are supplied; with those three resolved the union preview reads `upstream_ok=90 ledger_bad=0 unknown=0`, rc 0.

Nothing in the lane's frozen material was edited. Six files were written under the assigned evidence directory, the rest under `w1/out/X4HexR45/`.

## 1. Tokens in scope, and what each one is

The item names four 8-character runs (`20259355`, `547934af`, `66ab8482`, `c03c1a14`) and one 40-character run (`d854d98b…`). The census token rule is "32 <= L <= 127, L != 64" (`tools/hexrun-census.py:61-63`), so the 8-character runs are only prefixes of the ledger keys; `registry/recheck-r45.tsv` contains 19 token occurrences / 10 distinct 40-hex runs, of which exactly five are `class=unknown` — the four full ids below plus `d854d98b…` itself. That is the whole "and any other unknown in that file" set; nothing else in the file is unexplained.

| token | object | upstream repo | cited at |
|---|---|---|---|
| `66ab8482e08035a3238dff04a5739c4371c61bfe` | commit `2026-10-25T21:25:58-07:00` "MLX, MLX-C: version bump - prompt speed up for gemma/flint/laguna (#19291)" | `ollama/ollama` | `registry/recheck-r45.tsv:2` (S010 `new_ref`, `SOURCES.md:22`) |
| `547934afa90a34298441caf80c43b27255c3a292` | commit `2026-10-18T02:49:01Z` "run conformance in strict mode, fix or declare violations (#444)" | `open-telemetry/semantic-conventions-genai` | `registry/recheck-r45.tsv:4` (S019 `pin_ref`, `SOURCES.md:31`) |
| `20259355b9631e3f032dcc099d1b5a2666818c42` | commit `2026-10-26T04:55:42Z` "Use `gen_ai.client.embeddings.duration` … move embeddings signals to one file (#578)" | `open-telemetry/semantic-conventions-genai` | `registry/recheck-r45.tsv:4` (S019 `new_ref`) |
| `c03c1a14507dfaf8b856c2608f9ac216021fc222` | commit `2026-10-18T13:14:58-10:00` "Linux 7.3"; annotated tag object v7.3 `091b06388b117fefdcb63336ac09956a4914b961` peels to it | `torvalds/linux` | `registry/recheck-r45.tsv:5-6` (S048 `new_ref`, `SOURCES.md:60`) |
| `d854d98bae598388ecea1ed84396587e5edc326d` | commit `2026-10-26T00:08:22+01:00` "cuda : use std::string instead of VLA for archName (#30463)"; lightweight tag `b11889` names it | `ggml-org/llama.cpp` | `corpus/README.md:679` (b11889..b11906 range), `registry/recheck-r45.tsv:8-10` (S041/S046/S055 `new_ref`, `SOURCES.md:235` S482) |

How each was confirmed — own blobless clones in the seat scratch, no API calls:

```
$ git -C ollama.git cat-file -t 66ab8482…            -> commit
$ git -C ollama.git rev-parse 66ab8482…:docs/api/openai-compatibility.mdx
  75218fc8f8044a8d0c0f0adc6c77684fec57711f   (cat-file -s 25472)
$ git -C ollama.git rev-parse c1737589…:docs/api/openai-compatibility.mdx
  272f98ea7ae8bf9d4cd463ebdca352793cbe1dda   (cat-file -s 24664)
$ git -C genai.git cat-file -t 547934af…  -> commit ; rev-parse 547934af…:docs/gen-ai/gen-ai-metrics.md -> c131e6d0…  (64991)
$ git -C genai.git cat-file -t 20259355…  -> commit ; rev-parse 20259355…:docs/gen-ai/gen-ai-metrics.md -> 04e38a4d…  (65149)
$ git ls-remote https://github.com/torvalds/linux.git refs/tags/v7.2 refs/tags/v7.3 'refs/tags/v7.2^{}' 'refs/tags/v7.3^{}'
  237a1c39e8dfd3e1c6f1f023eea37a48ec04cc63  refs/tags/v7.2
  8d3ae59288f1e7d58d76558a6ee96d533bc5019f  refs/tags/v7.2^{}
  091b06388b117fefdcb63336ac09956a4914b961  refs/tags/v7.3
  c03c1a14507dfaf8b856c2608f9ac216021fc222  refs/tags/v7.3^{}
$ git -C linux.git cat-file -p 091b0638…  -> object c03c1a14… / type commit / tag v7.3 / tagger Linus Torvalds …
$ git -C linux.git rev-parse c03c1a14…:net/ipv6/tcp_ipv6.c c03c1a14…:include/uapi/linux/in6.h
  7fa4ed2fd4f166a9c0454c2f4ee4cd3b541b4c84   5a47339ef7d7688f3ca50f574d1fa62783fc56fe
$ git -C linux.git rev-parse 8d3ae592…:net/ipv6/tcp_ipv6.c 8d3ae592…:include/uapi/linux/in6.h
  9e9155b1b3aa752631d8a2e4db73fb39a229b9ae   5a47339ef7d7688f3ca50f574d1fa62783fc56fe   (in6.h same blob -> row's unchanged-file)
$ git -C llama.git cat-file -t d854d98b…  -> commit
$ git -C llama.git rev-parse b11889 b11889^{commit}  -> d854d98b… and d854d98b…
$ git -C llama.git rev-list --count d854d98b…..4d71b42fd87db24b8b7c808c151b713aa4459cfd  -> 17
```

Byte equality, both directions (each blob hashed through the clone, then the lane's stored copy hashed locally with `git hash-object`):

| path | upstream blob at the cited commit | lane copy | file sha256 vs `.ufo/waves/round-45/c1/upstream/fetch.log` |
|---|---|---|---|
| `docs/api/openai-compatibility.mdx` @ `66ab8482` | `75218fc8…` 25472 | `.ufo/waves/round-45/c1/upstream/S010/new` → `75218fc8…` | `44071a12…` = log:2 |
| `docs/gen-ai/gen-ai-metrics.md` @ `547934af` | `c131e6d0…` 64991 | `…/S019/pin` → `c131e6d0…` | `bf2359b8…` = log:5 |
| `docs/gen-ai/gen-ai-metrics.md` @ `20259355` | `04e38a4d…` 65149 | `…/S019/new` → `04e38a4d…` | `a3ea5831…` = log:6 |
| `net/ipv6/tcp_ipv6.c` @ `c03c1a14` | `7fa4ed2f…` 65043 | `…/S048_tcp_ipv6.c/new` → `7fa4ed2f…` | `cc8f8c48…` = log:8 |
| `include/uapi/linux/in6.h` @ `c03c1a14` and @ `8d3ae592` | `5a47339e…` 7593 | `…/S048_in6.h/{pin,new}` → `5a47339e…` | `4b70a423…` = log:10 |

So the rows' "changed"/"unchanged" readings rest on the bytes upstream actually holds at both ends, not only on a live URL.

## 2. Evidence files (assigned path `.ufo/waves/round-47/hexrun-evidence/`)

Each holds `repo:`, `claim:`, `source:` (the lane cell that cites it), the clone/fetch commands, the commands with their real output (token present), a pin-side reverse check, a lane-side `git hash-object` check, a sha256 byte-equality check and a verdict.

- `66ab8482e08035a3238dff04a5739c4371c61bfe.txt` (3222 B)
- `547934afa90a34298441caf80c43b27255c3a292.txt` (2393 B)
- `20259355b9631e3f032dcc099d1b5a2666818c42.txt` (2611 B)
- `c03c1a14507dfaf8b856c2608f9ac216021fc222.txt` (4928 B) — seat `X4HexUp2` had already written an advisory note for this token (their range `a4b4feae..e1e006f1` contains it lexically). Their text is preserved verbatim at the head of the file; my confirmation block is appended below it, not over it.
- `d854d98bae598388ecea1ed84396587e5edc326d.txt` (2791 B) — rev-list distance 17, plus the four lane cells that name it
- `ec82db0076ed55986ff97bdf327e8d86054c510d.txt` (2574 B) — advisory, outside my assigned set; see §5 H3.

## 3. Gate — the census on a fixture that commits the evidence

Receipt: `w1/out/X4HexR45/gate.txt` (produced by `w1/out/X4HexR45/gate.sh`; it re-runs from the scratch layout described here and reads the commit ids from `fixture-commits.txt`, so reproducing it after scratch removal means recreating the four clones and the two fixture commits as described). Clones: `$S/ollama.git`, `$S/genai.git` (`clone --filter=blob:none --bare`), `$S/linux.git` (`init --bare` + `fetch --filter=blob:none --depth=1` for tags v7.3 and v7.2), `$S/llama.git` (`init --bare` + `fetch --filter=blob:none` for `refs/heads/master` and `refs/tags/b11889`). Fixture: `$S/lane` = `git clone --shared <lane>`, toplevel asserted as `$S/lane` before every commit; the gate commit `286bd41dc1c5d5c6193b473051ae999b2367fbaa` is lane tip `46a924e027f05614558c45ff02bf7a94ca57d3e1` plus exactly the five evidence files at their delivered bytes (written with `read-tree`/`hash-object -w`/`write-tree`/`commit-tree`, so the tree is the tip plus five blobs and nothing else). Union-preview commit `21d63db28d586f1fc812138605088809b04396b4` is the same tree plus every round-47 hexrun evidence file.

```
--- 1. baseline, unmodified ledger
$ hexrun-census.py scan --repo $S/lane --rev 3a09a1d93dcc16799cf6c4b48786e6440af134c4
tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=68 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=22   rc=1
$ hexrun-census.py scan --repo $S/lane --rev 46a924e027f05614558c45ff02bf7a94ca57d3e1
tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=68 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=22   rc=1

--- 2. control, fixture commit with the evidence, unmodified ledger
$ hexrun-census.py scan --repo $S/lane --rev 286bd41d…
tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=68 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=22   rc=1
   (evidence alone changes nothing: the files are .txt, not documents)

--- 3. gate, fixture commit with the evidence, rows.tsv appended (ledger-v2.tsv, 88 lines)
$ hexrun-census.py scan --repo $S/lane --rev 286bd41d… --ledger $S/ledger-v2.tsv
tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=73 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=17   rc=1
$ … --details  (this seat's five tokens)
detail: 20259355b9631e3f032dcc099d1b5a2666818c42 len=40 occurrences=1  class=upstream_ok
detail: 547934afa90a34298441caf80c43b27255c3a292 len=40 occurrences=1  class=upstream_ok
detail: 66ab8482e08035a3238dff04a5739c4371c61bfe len=40 occurrences=1  class=upstream_ok
detail: c03c1a14507dfaf8b856c2608f9ac216021fc222 len=40 occurrences=2  class=upstream_ok
detail: d854d98bae598388ecea1ed84396587e5edc326d len=40 occurrences=19 class=upstream_ok

--- 4. counterfactual: rows appended, evidence NOT in the tree at REV (lane rev 46a924e0)
$ hexrun-census.py scan --repo $S/lane --rev 46a924e0… --ledger $S/ledger-v2.tsv
tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=68 unverifiable=9 wrong_flagged=2 ledger_bad=5 unknown=17   rc=1
   (a ledger row without its evidence at REV is worse than no row: 5 bad rows)

--- 5. negative controls, one row broken at a time, at the fixture commit (all rc=1)
badrepo        d854d98b row repo cell 'ggml-org/ggml'                -> upstream_ok=72 ledger_bad=1 unknown=17
noevidence     547934af row evidence path renamed to a missing file  -> upstream_ok=72 ledger_bad=1 unknown=17
wrongevidence  20259355 row pointed at the 66ab8482 evidence file    -> upstream_ok=72 ledger_bad=1 unknown=17
```

The census's matching rule is a substring test on the evidence bytes (`tools/hexrun-census.py:248-256`: the token and, when non-empty, the `repo` cell), so the controls above are the three ways a plausible-looking row is still worthless, and each one is caught.

## 4. Union preview (advisory — the rows belong to the other seats)

`w1/out/X4HexR45/ledger-union-fixed.tsv` = lane ledger (83) + `X4HexUp1/rows.tsv` (5) + `X4HexUp2/rows.tsv` (5, `d854d98b` dropped) + `X4HexFleet/rows.tsv` (6, one repo cell corrected) + my `rows.tsv` (5) + my `rows-advisory.tsv` (1) = 105 lines, no duplicate token (the same file was `$S/ledger-union-fixed.tsv` when the gate ran; the copy is in the out directory).

```
raw concatenation of all four seats' rows   : upstream_ok=87 ledger_bad=2 unknown=1   rc=1
dedup d854d98b                               : upstream_ok=88 ledger_bad=1 unknown=1   rc=1
dedup + fleet repo cell + advisory ec82db00  : upstream_ok=90 ledger_bad=0 unknown=0   rc=0
```

The two intermediate `ledger_bad` tokens are named in `gate.txt` §6: `b0fd7b7f…` and `d854d98b…`.

## 5. Findings handed to the lane L1

**H1 — duplicate ledger row for `d854d98b…`.** My `rows.tsv` and `w1/out/X4HexUp2/rows.tsv:7` both carry a row for the same token; the census classifies a twice-ledgered token `ledger_bad` (`tools/hexrun-census.py:265-266`, "if len(rows) > 1"). Command: the raw union run in `gate.txt` §6, whose `--details` prints `detail: d854d98b… class=ledger_bad`. Fix: append exactly one of the two rows. Mine carries the clone resolution, the tag identity, the 17-commit distance and the four lane cells that name the token; Up2's row is in their deliverable, so dropping one is a one-line integration decision.

**H2 — `X4HexFleet/rows.tsv:7` `repo` cell the census cannot match.** The cell reads `vgpnk/shokunin (fleet)`; the evidence file `hexrun-evidence/b0fd7b7f5ae6a0ad7717461c5fea8cb8a8724025.txt:2` reads `repo: VeigaPunk/shokunin`, and no other line of that file contains `vgpnk/shokunin (fleet)`, so the substring test fails and the 104-occurrence token becomes `ledger_bad`. Command: `hexrun-census.py scan --repo $S/lane --rev 21d63db2… --ledger $S/ledger-union-dedup.tsv --details 2>&1 >/dev/null | grep ledger_bad` prints `b0fd7b7f… class=ledger_bad`. Fix (either): set the row's `repo` cell to `VeigaPunk/shokunin`, or add the literal `vgpnk/shokunin (fleet)` to the evidence file. Fleet's own report is the place to settle which name the lane uses.

**H3 — `ec82db0076ed55986ff97bdf327e8d86054c510d` is assigned to no seat.** It is the `pin_blob` of `registry/release-recheck-b11889.tsv:2` (S001, `tools/server/README.md` at the S001 file commit `c0fd78626405`), and it sorts *after* both range ceilings (`9706b3ac`, `e1e006f1`), so X4HexUp1 and X4HexUp2 both left it out; it is the one `unknown` the four hexrun seats leave behind. Verified from the same clone: `cat-file -t` → `blob`, `rev-parse c0fd7862…:tools/server/README.md` → `ec82db00…` (119356 B), release side `b11889^{commit}:tools/server/README.md` = `4d71b42f…:tools/server/README.md` = `8e27e37b8d4aa623006e413e7c8c4062a542e079` (126663 B), which also explains the b11906 row's "identical at b11889 and b11906". I supplied the evidence file and a row in `rows-advisory.tsv` (kept out of `rows.tsv` because it is outside my assigned token set); appending it takes the union to `unknown=0, ledger_bad=0, rc=0`.

**Note on the item's phrasing (not a defect).** The four 8-character runs in the item are prefixes; a ledger key must be a 32..127-character run, so the rows key the full 40-hex ids. `20259355…` and `547934af…` are both S019 refs (new and pin), and `c03c1a14…` is the v7.3 side of S048, so four prefixes cover four of the five keys, the fifth being `d854d98b…` named in full.

## 6. What integration has to do

1. Append `w1/out/X4HexR45/rows.tsv` to `registry/hexrun-ledger.tsv` — `proposed-ledger.diff` is that change as a unified diff (`@@ -81,3 +81,8 @@`; the file is 83 lines today).
2. **Commit the evidence files.** The five files are now in the lane's working tree at `.ufo/waves/round-47/hexrun-evidence/` but not committed; without them at the census REV the five rows are `ledger_bad` (`gate.txt` §4). The same holds for the other hexrun seats' files: `21d63db2…` was a scratch commit holding all of the round-47 evidence files at their final bytes, and only there does the union reach `unknown=0` (its id is recorded in `fixture-commits.txt`; the tree it pointed at is fully described by the evidence directory plus lane tip `46a924e0`).
3. Resolve H1 (one `d854d98b` row), H2 (`b0fd7b7f` repo cell), and decide H3 (accept the advisory `ec82db00` row).
4. Re-run at the integrated tip: `python3 tools/hexrun-census.py scan --repo <clone> --rev <tip>` should print `unknown=0 ledger_bad=0` if H1–H3 are accepted; `unknown=1` (ec82db00) plus `ledger_bad=0` if H3 is deferred with H1/H2 fixed.

## 7. Limits of this seat's evidence

- I confirmed object identity and bytes, not the round-45 rows' statements about those bytes (S010's "no health route", S019's three metric rows, S048's byte order). Those are the round-45 seats' readings; my reverse checks only show that the bytes they read are the bytes upstream holds today.
- No service was started; no `gh` API call was made (the four clones and one `ls-remote` were the only network use). No pacman, no tool installs, so there is no install record to carry.
- `/tmp` was not used: scratch was `/fast/scratch/hyaku/kama-r47/X4HexR45` and was removed after the receipts were copied out.

## 8. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/hexrun-evidence/66ab8482e08035a3238dff04a5739c4371c61bfe.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/hexrun-evidence/547934afa90a34298441caf80c43b27255c3a292.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/hexrun-evidence/20259355b9631e3f032dcc099d1b5a2666818c42.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/hexrun-evidence/c03c1a14507dfaf8b856c2608f9ac216021fc222.txt` (X4HexUp2's advisory text preserved, my block appended)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/hexrun-evidence/d854d98bae598388ecea1ed84396587e5edc326d.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/hexrun-evidence/ec82db0076ed55986ff97bdf327e8d86054c510d.txt` (advisory, H3)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X4HexR45/rows.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X4HexR45/rows-advisory.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X4HexR45/gate.sh`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X4HexR45/gate.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X4HexR45/verify-upstream.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X4HexR45/ledger-v2.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X4HexR45/ledger-union-fixed.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X4HexR45/proposed-ledger.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X4HexR45/fixture-commits.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X4HexR45.md`
