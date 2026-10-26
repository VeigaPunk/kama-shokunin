# S9Lesson — round-48 wave seat report (lesson draft)

**Verdict: the round lesson is drafted in the round-47 shape with the three named Mistakes rows and the sweep that follows them; the sweep found two instances the round had not recorded (a declaration count no instrument reads, and the measured tool never fingerprinted) and confirmed the class-1 history peels back further than the build finding stated (rounds 43–45 rewrote banners too, all below the 20-line threshold). No claim was measured by this seat and no lane file was touched.**

Authority for everything below is the frozen preregistration `.ufo/waves/round-48/preregistration.json` and the two frozen counters' docstrings; this seat wrote only its own out dir.

## What was run (commands, outputs, exit codes)

| # | command | output | exit |
|---|---|---|---|
| 1 | `python3 tools/round48-append-audit-v3-check.py --repo $S/lane --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch $S/c1` | `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True` | 0 |
| 2 | `python3 $S/build/tools/append-only-audit.py --repo $S/lane --to 33e005827742b29772b153cda036ec9f27f653be --contract $S/build/registry/append-only-contract.tsv --json` (tool and contract extracted from `380bcdff`) | `summary.regressed=1`; `0718b6ab SCORECARD.md deleted 2421 graded 2349 ungraded 72 restored_max 2349 held_at_to 2348`; the five events otherwise restored | 1 |
| 3 | same, `--to 380bcdff…` | `events 5 restored 5 regressed 0 vanished 0 bad_declarations 0 ungraded_lines 89`; every event `restored` with `held_at_to == restored_max` | 0 |
| 4 | `git show 82b5e9d3:SCORECARD.md \| sed -n 6p \| sha256sum` vs `sed -n 2740p SCORECARD.md \| sha256sum`; same for `42ea1204` vs `2742` | `8f56ab3f…acb5` = `8f56ab3f…acb5`; `87a437e7…2fe3` = `87a437e7…2fe3` | 0 |
| 5 | `grep -h '^tip=' .ufo/waves/round-47/measured/*-fix.out` | five lines, all `tip=3442d707fdf926ec5ea3f34363cf2f0899cc79b5` — against the report text's "final tip `6b7e6cf8`" (closure D9) | 0 |
| 6 | `awk 'NR>1 && NF' registry/append-only-contract.tsv \| wc -l`; `sed -n '760p;783p' corpus/README.md` | `9`; `:760` "sets the five files…", `:783` "whose seven rows each name" | 0 |
| 7 | `python3 tools/sources-append-only.py --repo $S/lane --from 1641aa07 --to 052cb1e9`; `--from d48e8cc3 --to 6b8ccfb3` | `error: 052cb1e9:corpus/SOURCES.md:514: row-like line outside the parsed registry table; refusing to drop it`; `no append-only violations` | 2; 0 |
| 8 | `git log --oneline 33e00582..380bcdff -- tools/sources-append-only.py` | empty (unchanged since round 18; the last commit touching it is `c6dc46fa`) | 0 |
| 9 | `sha256sum tools/{kama-llamacpp-live,kama-live-replay}.py`; `git show 33e00582:<tool> \| sha256sum`; `grep -n 'tool' tools/round48-live-replay-v5-audit.py` | live `1e5ea0fd…9a6d2` vs base `65301a3c…ae65d`; replay `69837013…b15f` vs base `3c573444…0f2cb`; `tool` appears only in the docstring (`:12,30,37,41,67,75,104`) and constants (`:144`, `:145`) | 0 |
| 10 | structural read of `.ufo/waves/round-48/c2/live/receipt-{1,2,3}.json` (no replay, no network) | each: schema `kama-llamacpp-live/v5`, `outcome pass`, 11/11 checks evaluated+passed, `teardown.log_path` null, `tool.sha256 1e5ea0fd…`, `provenance.model.commit 499bc882…d81`, `provenance.verified.at record` with archive/member/model digests `bf94332a…`/`35ac50fb…`/`270cba1b…` | 0 |

Not run by this seat, and marked as such in the draft: the C2 counter (its replay leg re-downloads ~70 MB from github.com and ~4 MB from huggingface.co); the L1's pre-wave dry run figures `receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True` are quoted as **L1-reported**, and seat `S1Gate`'s independent run of both counters at `380bcdff` (`.ufo/waves/round-48/w1/out/S1Gate/c1.json`, `c2.json`, both `met=True`, C2 `started=2026-10-26T22:35:02Z`) is quoted as S1Gate's. S1Gate produced no decisions file before this draft; its `probes.txt` (§A, §B, §D, §G, §H) was folded into the Gate section: the pinned URL's headers re-confirmed, `main` resolving to the same commit today, and the signed 302 `location` differing per request with an hour-long `Expires` — which grounds the added reject on recording the CDN location as the locator.

## Deliverables

- `.ufo/waves/round-48/w1/out/S9Lesson/round-48.md` — the lesson draft: `## Claims` with `?` placeholders plus the build-state values this seat measured, `## Gate` (S492, S493: URL, access instant, located quotes of 2+9 and 17 words, one admit and one reject per row), `## Mistakes` with five rows (classes, evidence, captured-by, a fix shown able to fail), the `## Wave` stub, and an explicit fill list for the L1.
- `.ufo/waves/round-48/w1/out/S9Lesson.md` — this report.
- Evidence copied into `.ufo/waves/round-48/w1/out/S9Lesson/`: `c1-counter-at-build-380bcdff.out`, `v3-tool-at-base-33e00582.json`, `banner-byte-exact.txt`, `sources-guard-1641aa07-to-052cb1e9.out`, `evidence-sweep.txt` (sections A–I with the raw outputs).

## Findings

1. **Class 1 is wider than the build finding said.** The round taught "rounds 46–47 rewrote the banner without keeping it". The history says rounds 43, 44 and 45 did the same (`44fa5627` 1 line, `d48e8cc3` 1 line among 19 deletions, `21945c61` 1 of 3; `383f1fc7` 1 of 9), and every replacement is below the frozen threshold of 20 deleted lines, so v3 can only ever see the family through the `0718b6ab` mass event. Evidence: `.ufo/waves/round-48/w1/out/X1Banner/04-banner-replacement-ledger.txt`; the appended banners are byte-exact (`banner-byte-exact.txt`). Consequence for the lesson: the fix as built is a discipline plus a hash comparison, not a graded rule — a 1-line banner rewrite still exits 0. Proposed fix (for the L1 to route, not an edit here): compare `SCORECARD.md` line 6 across consecutive revisions, or lower the threshold for the head lines; the check fails on `4340cf2f` and `383f1fc7` today.
2. **A declaration count no instrument reads.** `corpus/README.md:760` says "the five files", `:783` says "seven rows"; `registry/append-only-contract.tsv` holds 9 rows. README is `A-corr` (corrections appended) and v3 grades deletions, so an ever-growing contract costs nothing and the prose drifts silently. Round-47 KQ71 named the "five" phrase; the "seven" phrase at `:783` is newer and was not named. Proposed: one derived count or a `--check` comparing every "N files/rows" phrase with `len(contract)`; it fails today (`five != 9`, `seven != 9`).
3. **Class 3's survivor: the measured tool is both object and subject.** The v5 receipts carry `tool.sha256` of the live tool that produced them, but neither round-48 counter compares a rerun's `tool.sha256` with the receipt's, and neither pins the tool bytes at the freeze (`grep` in row 9 above). Round-47 seat K2Cheat proposed exactly this pin (`.ufo/waves/round-47/w1/out/K2Cheat.md` §Proposed fixes item 3) and it was not adopted. The pin is falsifiable and non-vacuous: tool hashes differ between `33e00582` and `380bcdff`, and today's receipts carry the build tool's hash, so filed evidence would pass.
4. **Latent C1 escape hatch (peer, not mine).** Seat K1Regions (`.ufo/waves/round-48/w1/out/K1Regions.md`, seven fixtures) shows any dated text moved or retitled under an exempt `## ` title whose line count is held at or above the parent's — or regrown later in the window — is deleted as `ungraded` at exit 0; the lane at `380bcdff` exercises none of them, so the 89 ungraded lines are all genuine head text. This belongs in C1's disclosed limits or in round 49; the draft records it in §Wave and deliberately does not put it into the frozen claim text.
5. **Sources guard still blind, verified at the build (round-47 Mistakes row 5, routed r47-D8).** `--from 1641aa07 --to 052cb1e9` exits 2 with the row-like-line error; the last graded transition `--from d48e8cc3 --to 6b8ccfb3` exits 0; the tool is unchanged between the round-48 base and build (row 8). Not a new mistake and not re-reported as one — recorded in the lesson's sweep notes so that no reader takes its silence as coverage.

## Known integration items (as briefed; not re-reported as findings)

Gate registry lists the two round-48 counters unregistered; the round-41/42/43 counters read the spot-check count 33 vs 34; hexrun-census has one unknown (`d0012618`). All three are in the brief and unchanged by this seat's work.

## Out of scope / deliberately not done

- No claim counter for C2 was run (downloads); no live server was started; no `kama-*` tool was executed.
- No lane file, counter, preregistration or control was edited; the counters are frozen and the two proposals above are stated as findings with a failing check, not applied.
- No subagent dispatch, no `agent://all`, no fleet-root write, no git/jj mutation in the lane; the only git writes were the read-only `git clone --shared` into scratch, which was removed.
- Tooling record: nothing installed or upgraded; no pacman; `gh` not used.

## Artifacts written (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Lesson/round-48.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Lesson.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Lesson/c1-counter-at-build-380bcdff.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Lesson/v3-tool-at-base-33e00582.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Lesson/banner-byte-exact.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Lesson/sources-guard-1641aa07-to-052cb1e9.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Lesson/evidence-sweep.txt`
