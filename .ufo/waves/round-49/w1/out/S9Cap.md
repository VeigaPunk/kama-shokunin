# S9Cap — round-49 capability entries (canonical list + `## Capabilities` mirror)

**Verdict: drafted and demonstrated.** On a `git clone --shared` of the lane at `74558c71c38ceaeace15fd4cf8aa9d84977584b1` with the drafted block appended and the head mirror updated (nothing committed), `python3 tools/capability-repertoire-audit.py --repo <clone>` reports `listed 11 observed 11 missing 0 unsubstantiated 0 met True`, exit 0. Eleven capabilities, no row added; `append-only-audit` reworded for v4 (first-working round 46) and `live-receipt-replay` reworded for the `--witness-dir` execution witness and the bounded archive member (first-working round 47).

## Deliverables

| File | What it is | sha256 |
|---|---|---|
| `round49-canonical-capabilities.md` | the insertable block: `**Capabilities — canonical list as of round 49**`, the round-49 intro sentence and the 11-row table (16 lines; marker, blank, intro, blank, header, separator, 11 rows) | `c7fc9b4816b252cb6d119e7cebf1ad85a002178305e47debd3f2dcc254a15fc6` |
| `capabilities-mirror-round49.diff` | unified diff against `74558c71:SCORECARD.md` for the head `## Capabilities` mirror: line 117 (mirror sentence now says round 49 / §Round 49) and the two reworded rows at lines 130–131 | `2cfd02471d3cf3dfcc028f4182a86a8e19561372afef6aead9a5c59b952b4be1` |
| `capability-audit-after.out` | the census line at the demonstrated state (`listed 11 observed 11 missing 0 unsubstantiated 0 met True`) | `b9c3569e4208d66d8b90dbb9d0898675c8a25f3869f12bb1f57c4d66ed5c820a` |
| `capability-audit-after.json` | the same run's `--out` JSON (`canonical_line 2815`, `capability_tables 15`, `missing_names []`) | `9a99d4c9ecd96d9ee9a358584e20baf5708cc083a186e89658d457ee6c42b9d3` |
| `verify-clone.txt` | the demonstration transcript: clone, detach, worktree status, cursor run, `--selftest`, four sensitivity arms, restore | `4424091a9efc9c87f58da2d38ddb847d1cd96c38938d3fed388f4bc0e51d6cb4` |

Placement for the integrator: append the block **inside** the round-49 section that the SCORECARD scribe writes, as its last element (the round-48 section puts it the same way: intro paragraph, then the marker, then the table). The marker line, the intro paragraph and the table must stay contiguous — no other capability-shaped table may sit between the marker and the table (finding F3). The provisional heading I used for the clone demonstration was

```
## Round 49 — execution-witnessed live receipts at b11909 (operability) and append-only-audit v4 by line origin (calibration) (2026-10-26)
```

## What the two reworded rows now claim, and where the build backs it

`live-receipt-replay` (row text in the block; first-working round stays **47**) adds, after the round-48 v5 narration: `--witness-dir D` → the live tool writes `D/ready.json` {schema `kama-live-witness/v1`, port, pid of the llama-server child} once the server is ready and its checks ran, waits up to `--witness-timeout` (default 120 s) for `D/release`, tears down, and the rerun receipt records `witness` {released, waited_ms, port, pid, dir}; an outside observer can hash `/proc/<pid>/exe` against the frozen b11909 digest, tie the port's LISTEN socket inode and the `-m` argument to that pid, and round-trip a fresh nonce through POST `/tokenize` (`with_pieces`) and `/detokenize`; and a receipt is refused when the archive is not a regular file of ≤ 1 GiB, has > 4096 index entries, or its member is sparse or of a declared size other than the `--server` file's, all checked before the member is hashed.

Backing at `74558c71` (line numbers are the tip's):
- `tools/kama-llamacpp-live.py:277` `WITNESS_SCHEMA = 'kama-live-witness/v1'`; `:280-300` `hold_for_witness()` — `ready.json` written atomically (`:289-292`), `release` poll (`:293-295`), returns `{released, waited_ms}` (`:298-300`); `:1860-1864` `receipt['witness'] = hold_for_witness(...)`; `:52-57` and `:1264-1270` the `--witness-dir` / `--witness-timeout` (default `120.0`) contract.
- `tools/kama-llamacpp-live.py:208` `ARCHIVE_MAX_BYTES = 1 << 30`; `:209` `MEMBER_MAX_COUNT = 4096`; `:232` `provenance-archive-not-regular`, `:234` `-archive-too-large`, `:253` `-archive-too-many-members`, `:261` `-member-sparse`, `:263` `-member-size-mismatch`; `:218-222` states the checks precede hashing.
- `tools/kama-live-replay.py:42-45` the witness paragraph; `:275-281` passes `--witness-dir/{--witness-timeout}` to the live child and grows the process bound; `:450-453`, `:481-484` the CLI plumbing.
- `tools/round49-replay-witness-audit.py:65` (PREDICATE) is the counter side of the same contract — the counter observes the witness itself, the row only claims what the build provides.
- Evidence cell points at `tools/kama-live-replay.py`, `tools/kama-llamacpp-live.py`, `tools/round49-replay-witness-audit.py`, `.ufo/waves/round-48/c2/live/receipt-1.json`; all four resolve at the tip (`git cat-file -e 74558c71:<path>`, all present).

`append-only-audit` (row text in the block; first-working round stays **46**) folds v4 into the v3 narration: the exempt `## ` carve-out now also requires the deleted text to have been **born** in an exempt section (`origin`: the titles holding that text at its first appearance in `rev-list` order), the row token must occur as a whole word, a negation within three words before append-only unbinds, a wildcard row is not bound by a covered file's own blanket self-declaration, and the JSON keeps `"schema": "append-only-audit/v3"` while stating `"definition": "v4"`.

Backing at `74558c71`:
- `tools/append-only-audit.py:2-18` the v4 definition list (`origin(l)`, `ungraded`, `binding`); `:216-227` `binds()` (word-bounded token, `NEGATIONS` at `:141`, `NEG_WINDOW` at `:212`, wildcard self-declaration refused); `:423-441` the origin cache; `:474` the carve-out comment; `:504` `"definition": "v4"` in the output.
- `tools/round49-append-audit-v4-check.py:62` (PREDICATE) — one of the eight fixtures is `launder` (v3 would leave it ungraded; v4 grades 25 lines).
- Evidence cell points at `tools/append-only-audit.py`, `registry/append-only-contract.tsv`, `tools/round49-append-audit-v4-check.py`; all three resolve at the tip.

Names and first-working rounds are the round-48 set verbatim (10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47) — verified by parsing the block (`verify-clone.txt`, last section). The mirror rows are byte-identical to the canonical rows in the demonstrated file (checked by string index equality).

## Evidence (commands, outputs, exit codes)

```
$ git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
$ git -C $S/lane checkout -q --detach 74558c71c38ceaeace15fd4cf8aa9d84977584b1
$ git -C $S/lane rev-parse --show-toplevel      -> /fast/scratch/hyaku/kama-r49/S9Cap/lane
$ git -C $S/lane merge-base --is-ancestor 74558c71 122c4ee9   -> yes (lane tip is 122c4ee9)
$ git -C $S/lane status --porcelain             -> " M SCORECARD.md"   (my block + mirror only)
$ python3 tools/capability-repertoire-audit.py --repo $S/lane --out capability-audit-after.json
listed 11 observed 11 missing 0 unsubstantiated 0 met True
exit=0
$ python3 tools/capability-repertoire-audit.py --selftest
CAP_SELFTEST pass=2 fail=0
exit=0
```

`capability-audit-after.json`: `{"listed":11,"observed":11,"missing":0,"missing_names":[],"unsubstantiated":0,"met":true,"canonical_line":2815,"capability_tables":15}` — `2815` is the header of the round-49 table in the demonstrated file, i.e. the highest-numbered canonical marker wins as the counter's docstring says (`tools/capability-repertoire-audit.py:8-11`).

Sensitivity arms (each applied to the clone's `SCORECARD.md`, run, restored from the saved copy; `verify-clone.txt`):

| Arm | Change | Output | Exit |
|---|---|---|---|
| A | every evidence pointer of `live-receipt-replay` rewritten to a non-existent path | `listed 11 observed 11 missing 0 unsubstantiated 1 met False` | 1 |
| B | an extra capability-shaped table adding name `stray-capability` | `listed 11 observed 12 missing 1 met False` | 1 |
| C | a decoy capability-shaped table inserted directly after the round-49 marker | `listed 1 observed 11 missing 10 met False` | 1 |
| D | head mirror kept at the round-48 wording while the canonical table is round-49 | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` | 0 |
| restored | block only | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` | 0 |

## Findings (frozen instrument and census, reported not fixed)

**F1 — a row is substantiated by any one resolving pointer.** `tools/capability-repertoire-audit.py:145-149`: `unsubstantiated` counts a row only when *no* token in its evidence cell resolves (`if not any(path_exists(...))`, line 148). Arm A shows the consequence on the row this seat rewords: three of its four pointers can rot and the census still says `unsubstantiated 0 met True` (all four dead → `unsubstantiated 1`). Both reworded rows carry three or four pointers, so this is live at round 49. Proposed fix: require the first `tools/*.py` pointer to resolve, or every `.py` pointer (the `md`/`json`/`tsv` pointers may stay advisory). Reproduce: `verify-clone.txt`, arm A.

**F2 — mirror/canonical agreement is not checked.** The `## Capabilities` head table feeds `observed` by *name* only, so a mirror that keeps stale wording while the canonical rows are reworded passes. Arm D: round-48 mirror text + round-49 canonical text → `met True`, exit 0. Proposed fix: after resolving the canonical table, require every canonical row to appear byte-identical in the table under `## Capabilities`, or at least require the mirror sentence to name the same round number as the highest marker. Reproduce: `verify-clone.txt`, arm D.

**F3 — the canonical table is the *first* capability-shaped table after the highest marker.** `tools/capability-repertoire-audit.py:8-9` (contract) and `:129-134` (the `break` on the first table starting after the highest marker). Arm C: a decoy table inserted on the line after the marker becomes canonical (`listed 1`, `missing 10`). Integration constraint for this round: nothing but the intro paragraph may sit between `**Capabilities — canonical list as of round 49**` and the table. Proposed fix: prefer the table whose header follows the marker within the same paragraph block, or select the table with the largest row count among those after the marker.

**F4 (integration note, not a defect).** The mirror sentence names "§Round 49"; it is correct only once the round-49 section exists under that name. If the SCORECARD scribe titles the section differently (e.g. without "Round 49"), the mirror is prose-wrong while the census still passes (F2). The diff I ship sets the sentence and the two rows; the section title is the scribe's.

## Limits of this seat's evidence

- The demonstration is the working tree of a scratch clone (`--tip` omitted, so `path_exists` uses `os.path.exists`, `tools/capability-repertoire-audit.py:166-170`); nothing was committed, so no `--tip <rev>` run of the counter exists for the edited file. A post-integration run with `--tip` on the measured commit is the lane's job.
- I ran no counter, no lane tool with a server, and no build: this seat drafted and demonstrated the census only. `verify-clone.txt` is every command I ran against the clone.
- [INFERENCE] My mirror edit replaces three head lines (`SCORECARD.md:117`, `:130`, `:131`); they sit in `## Capabilities`, which the round-49 contract lists as exempt for `SCORECARD.md` (`registry/append-only-contract.tsv:3`: `exempt=## Axes|## Planned|## Retired|## Saturation|## Capabilities@SCORECARD.md:6`, note "re-derived in place since round 42"), and v4 keeps a line ungraded only when its text was born in an exempt section — the round-48 mirror text was born in that same `## Capabilities` region, and the round-49 text is born there now. I did not run `tools/append-only-audit.py` (my edit is uncommitted, so it is invisible to a history instrument); the lane's C2 seat measures the real commit.

## Out of scope (not touched, not reported as findings)

The two round-49 counters in `SKILL.md`'s instrument registry; the SCORECARD round-49 claims/controls/measured prose, LOG, lesson, QUALITY and README entries for round 49; `corpus/SOURCES.md` rows; the counters and controls themselves; any commit, push or lane write.

## Hygiene

No tool was installed or upgraded (nothing needed; no `pacman` run — the host pause stands). No service was started, and I started no `llama-server`: `pgrep -af llama-server` after the work shows only other seats' processes (e.g. `/fast/scratch/hyaku/kama-r49/M1Ctr/.../tools/kama-llamacpp-live.py`). The lane was read only through `git clone --shared`; the only file I modified was `SCORECARD.md` inside my own clone. Scratch `/fast/scratch/hyaku/kama-r49/S9Cap` was removed after the receipts above were copied here.

## Paths written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Cap.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Cap/round49-canonical-capabilities.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Cap/capabilities-mirror-round49.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Cap/capability-audit-after.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Cap/capability-audit-after.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Cap/verify-clone.txt`
