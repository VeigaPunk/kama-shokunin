# Round-49 documentation corrections — drafted, to be APPENDED (never edited in place)

Seat X1Docs, round 49, lane kama. Audited revision: build `74558c71c38ceaeace15fd4cf8aa9d84977584b1`
(one-parent base `438127bc01ff3b99f98468549d58046f932490ef`). The build commit touched only
`corpus/SOURCES.md`, `tools/append-only-audit.py`, `tools/kama-live-replay.py` and
`tools/kama-llamacpp-live.py` (`git show --stat 74558c71`), so every claim below is drift left by
a code-only change.

Rule for each block: the superseded line stays as written; the block is appended (KQ26 names the
superseded text). Rows quoted with `:NNN` are line numbers at `74558c71` in the lane's own files.

**Status against the live tree.** This draft is measured against the frozen build `74558c71`. While
this seat was working, other round-49 seats landed integration text in the lane's working tree:
a round-49 instrument registry at `SKILL.md:1486-1504` (seat S9Skill), criteria KQ76–KQ79 after
`corpus/QUALITY.md:411`, a `## Frontier disposition — round 49` after `corpus/README.md:1071`, a
round-49 paragraph after `corpus/knowledge/llamacpp-loading-lifecycle.md:451`, the
`corpus/lessons/*.md` contract row re-anchored to `corpus/README.md:1239`, and a witness case in
`tools/kama-live-replay.py`'s selftest. So **§1 below is redundant with the live `SKILL.md:1486-1504`**
(its pinned values match mine: `pass=30`/`pass=28`, `72 -> 65`, `89 -> 82`) and **§4 is redundant
with the live knowledge append**; both are kept only as the measured basis. What no live text yet
covers — and what this seat still owes — is §2 (KQ70/KQ71/KQ72/**KQ75** pointer and value
corrections), §3 (the stale `corpus/README.md` pointers and the substring sentence), §5 (contract
note) and §6 (replay docstring). None of the live edits touches those lines: the six
`append-only-audit.py:NNN` citations at `corpus/README.md:809,965,966,979,991` and
`corpus/QUALITY.md:397,408,411` are unchanged in the live tree (re-checked 2026-10-26).

Every number in the blocks below was measured by a command recorded in `X1Docs.md` §1; the
raw outputs are in `evidence/` beside this file.

---

## 1. SKILL.md — append after the round-48 registry section (after `SKILL.md:1484`)

*(Redundant with the live `SKILL.md:1486-1504`, which landed during this seat's work; kept as the
measured basis, verified against my own numbers. Do not apply twice.)*

Superseded, for the three graded instruments only: `SKILL.md:1473` (append-only audit v3 row),
`SKILL.md:1474` (live lifecycle receipt v5 row), `SKILL.md:1475` (replay and compare row).
The round-48 rows stay byte-identical; the round-49 counter rows (C1 replay-witness audit, C2
append-audit-v4 check) belong to the integration pass and are not drafted here.

```markdown
## Round-49 instrument registry (append-only v4 definitions, replay execution witness, bounded archive member)

Rows that supersede `SKILL.md:1473`, `:1474` and `:1475` for the three instruments the round-49
build changed (`74558c71`); the round-48 rows remain as written and their pinned values are
round-48 history. Same columns as `## Local gate/probe registry`. Drafted by seat X1Docs from
each tool's docstring and the commands in `.ufo/waves/round-49/w1/out/X1Docs/evidence/`.

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-49 append-only audit, v4 definitions (supersedes `:1473`) | tool + selftest: `python3 tools/append-only-audit.py --repo <dir> [--to <rev>] [--contract <tsv> \| --files <a,b,...>] [--threshold <n>] [--json]`; `python3 tools/append-only-audit.py --selftest [--scratch <dir>]` | unchanged from v3 (0 clean, 1 an event partial/unrestored or regressed, a vanished path, an unbound declaration; 2 could not evaluate); `--json` keeps schema `append-only-audit/v3` and now carries `"definition": "v4"`; `declarations` entries are `{path, declared_at, region, ok, reason}` | `AOA_SELFTEST pass=30 fail=0` (two cases over the round-48 `pass=28`: `launder-through-head`, `binding-v4`); lane at `74558c71`: `definition` v4, 10 contract rows, `files=92`, 5 events all restored, `ungraded_lines=82`, `regressed=0`, `vanished=0`, `bad_declarations=0`, exit 0 | read-only on `--repo`; selftest fixtures under `--scratch` or `$TMPDIR`, removed on exit |
| Round-49 live lifecycle receipt v5, bounded archive check and execution witness (supersedes `:1474`) | capability: as `:1474`, plus `--witness-dir <existing-dir> [--witness-timeout <s>]` (default 120 s) | as `:1474`; record time additionally refuses, before hashing the member, an archive that is not a regular file, larger than 1 GiB or holding more than 4096 index entries, and a member that is absent, not a file, sparse, or whose declared size differs from the `--server` file's — new tokens `provenance-archive-not-regular`, `provenance-archive-too-large`, `provenance-archive-too-many-members`, `provenance-member-sparse`, `provenance-member-size-mismatch` (with `:1474`'s four unchanged); a non-existent `--witness-dir` or `--witness-timeout <= 0` is an argparse error, exit 2 | `selftest: ok`; `_provenance_selftest` asserts all seven archive/member refusals (`tools/kama-llamacpp-live.py:1387-1400`); with `--witness-dir D` the tool writes `D/ready.json` `{schema: kama-live-witness/v1, port, pid, written_utc}` after its checks and holds the server until `D/release` exists or the timeout passes, and the receipt gains `witness {schema, dir, port, pid, released, waited_ms}` (`:280-300`) | `--out` and a temp log it deletes; starts one loopback llama-server it tears down |
| Round-49 live receipt replay with an execution witness (supersedes `:1475` for the replay) | tool + selftest: `python3 tools/kama-live-replay.py --receipt <v4-or-v5-receipt> --work <dir> --out <json> [--live <tool>] [--timeout <s>] [--witness-dir <existing-dir>] [--witness-timeout <s>]`; `--compare` and `--selftest` as `:1475` | as `:1475`, plus: a non-existent `--witness-dir` is an argparse error (exit 2, `--witness-dir must be an existing directory`); with a witness dir the live child's bound is `--timeout + --witness-timeout`, the live child receives `--witness-dir`/`--witness-timeout`, and a witnessed replay matches exactly as an unwitnessed one — the witness is not compared | `KLR_SELFTEST pass=22 fail=0` (unchanged count; the witness is exercised by the round-49 C1 counter's live leg, not by this selftest); `--compare` on round-48 receipts 1 and 2 prints `compare match=True mismatches=0`, exit 0 | `--work` and `--out` (replay; the output object gains `witness_dir` when it is used); nothing (`--compare`) |

v4 definitions the exit map above now carries (`tools/append-only-audit.py` at `74558c71`):
`origin(l)` is the set of `## ` titles (None before the first heading) holding the line text `l`
in the first commit's blob of the file that contains `l` (`:423-441`); a deleted line is
**ungraded** only when its parent section is an eligible exempt title **and** `origin(l)`
contains one of the file's exempt titles, otherwise graded (`:469-477`); the row token binds only
as a whole word (`re.search` with `[a-z0-9_]` guards, `:233`), a negation within three words
before `append-only`/`append only` unbinds (`NEG_WINDOW`, `:212-213`, `:226-227`; v3's four fixed
strings still apply at `:141`), and a wildcard row is not bound by a covered file merely saying
`append-only` (`:231-233`). Region grammar `:160-176`, section split `:265-272`, threshold filter
`:452` with the argparse default at `:961`, hunk-count/numstat cross-check `:456`, declaration and
pointer binding `:249-259`.

### Re-running live evidence (v5, round 49)

- Witnessed replay: `python3 tools/kama-live-replay.py --receipt .ufo/waves/round-48/c2/live/receipt-1.json --work <empty-dir> --out <json> --witness-dir <existing-dir>`; while it waits, `<existing-dir>/ready.json` names the running rerun server `{schema, port, pid}`; create `<existing-dir>/release` to end the hold. The rerun receipt's `witness` block and the replay JSON's `witness_dir` record that it happened; neither is graded by the replay, so the observer (round-49 C1 counter) is what makes the witness evidence.
- Record-time bounds: the `--server-archive` check refuses an unbounded or mismatched member before hashing it (tokens in the table row above); the round-48 five-hundred-byte-style sparse-member archive now exits 2 in under a second rather than reading ~10^15 bytes.
```

---

## 2. corpus/QUALITY.md — append as a correction block (KQ26 form)

Supersedes, by naming: the line pointers in KQ70 (`corpus/QUALITY.md:397`), KQ71 (`:398`),
KQ72 (`:408`) and KQ75 (`:411`), and KQ72's exemption sentence and pinned ungraded mass.

```markdown
## Round-49 correction to KQ70, KQ71, KQ72 and KQ75 (appended 2026-10-26; seat X1Docs, build `74558c71`)

The three rows above are unchanged as rules; their quoted line pointers and pinned values are
superseded by this block (the rules' text is left byte-identical).

- **KQ70 (`:397`).** The raise it cites as `tools/append-only-audit.py:203` is now `:456`
  (`raise AuditError(f"{c[:12]} {f}: hunk count {len(dl)} != numstat {ns[f]}")`); `:203` is
  `row_token`'s docstring at this tip. The rule (hunk count equals numstat, byte-exact lines) is
  unchanged.
- **KQ71 (`:398`).** The check's pinned line `headings=13 covered=11 uncovered=2` is superseded:
  `python3 .ufo/waves/round-47/w1/out/S9Quality/heading-census.py --repo <clone> --head 74558c71`
  prints `headings=21 covered=18 uncovered=3`, the third uncovered heading being the round-48
  registry heading `SKILL.md:1465` (and `SKILL.md:1444` the second; both name `append-only` as a
  topic and carry no claim on a file, the disposition `:1434` already uses). The `85 paths at
  3a09a1d9` figure stays a historical pin; at `74558c71` the same command prints `files=92`.
- **KQ72 (`:408`).** (a) Pointers: the declaring line binds at `tools/append-only-audit.py:249-259`
  (not `:190-199`, which is `parse_contract`), the region pointer at `:255-259` (not `:210-229`,
  which is `binds`), and the region cell parses at `:160-176`. (b) Exemption is now
  **origin-scoped**: an exempt `## ` section leaves a deleted line ungraded only when that text's
  origin — the `## ` titles holding it in the file's first blob that contains it (`:423-441`) —
  contains one of the file's exempt titles (`:469-477`); text born in a dated section, moved under
  an exempt heading and deleted there is graded. (c) The pinned mass in the check is superseded:
  the `0718b6ab` SCORECARD.md event is now `graded=2356 ungraded=65` (was `2349`/`72`), so the
  lane reads `ungraded_lines=82` = 17 (`dd9f5dc6`) + 65, `bad_declarations=0`, `regressed=0`,
  exit 0; "all 89 ungraded lines" in the row is history from `380bcdff`. Both numbers were
  re-measured at `74558c71` (`evidence/aoa-lane.txt`, `evidence/aoa-base-lane.txt` for the v3
  tool on the same tree: `ungraded_lines=89`, event `2349`/`72`).
- **KQ75 (`:411`).** Both replay-tool pointers are wrong at this tip: the stable projection the row
  names is enumerated in the module docstring at `tools/kama-live-replay.py:17-26` and implemented
  in `projection()` at `:168-196`, not `:154-175` (which is `evaluated`, `_get` and the start of
  `projection`); `--compare` is the argparse option at `:446` and `compare()` at `:198`, not
  `:397` (a selftest negative case, `run("v5-not-verified", …)`). This defect predates the build — the same two pointers were
  already off at the base `438127bc` (`compare()` at `:194`, the option at `:435`) — so it is a
  standing citation defect, not a round-49 regression, and the rule itself is unchanged.
```

---

## 3. corpus/README.md — append a round-49 addendum

Supersedes, by naming: `corpus/README.md:807-810` (the "declaring-line check lives only in the
round-47 counter" sentence and its `:184` pointer), `:964-966`, `:972-977` (still true, unchanged),
`:978-979`, `:983-989`, `:990-991` (pointers and the substring claim), and the two closed items in
`:1030-1039` and `:1064-1066`. The round-48 figures at `:954-960`, KQ72's `89`, and `:1026-1028`
are round-48 measurements and stay.

```markdown
**Round-49 documentation addendum (appended 2026-10-26; build `74558c71`).** The build changed
three instruments and no documentation; the corrections below name the lines they supersede. All
pointer numbers are at `74558c71`.

- *Pointers.* `tools/append-only-audit.py:184` (cited at `:809`) is now the contract header check;
  the file-set expansion is `:277` and the rule cell is validated at `:194-196`. `:147-151`
  (`:965`) is now the git helper — region titles and prefixes are checked at `:171-175`. `:231-239`
  (`:966`) is now `binds` and `line_at` — the no-section-before-the-first-`## ` rule is `:265-272`.
  `:396` (`:979`) is blank — the threshold filter is `:452`, the argparse default `:961`.
  `:171-174` (`:991`) is region parsing — the rule cell is `:194`.
- *The substring claim is closed.* `:983-989` says the path token is a bare substring match and
  the negation list four contiguous phrases; at this tip the token must be a whole word
  (`:233`), a negation within three words before `append-only` unbinds (`NEG_WINDOW`, `:212-213`),
  and a wildcard row is not bound by a covered file's self-declaration (`:231-233`). Both fixtures
  the bullet names now fail to bind: the round-49 C2 counter's `substring` and `negated` and
  `wildcard-self` scenarios each report `bad_declarations 1` and exit 1, while `word-token` and
  `wildcard-named` bind (`evidence/c2-counter.out`).
- *The declaring-line check is no longer counter-only.* `:807-810` (round-47 text) says the tool
  never reads `rule`, `declared_at` or `note`; since v3 it binds `declared_at` and region pointers
  (`:249-259`), and `--json` prints `declarations`.
- *The exemption is origin-scoped.* `:926-931` and KQ72 describe an eligible exempt section as
  ungraded whenever its line count holds; v4 additionally requires the deleted text's origin to
  contain an exempt title (`:423-441`, `:469-477`). On the lane this grades 7 more lines of the
  `0718b6ab` SCORECARD.md event — `graded=2356 ungraded=65`, `ungraded_lines=82` (was
  `2349`/`72`/`89`) — and the event stays `restored`, exit 0.
- *The frontier item is closed: a replay now witnesses a running server.* `:1030-1039`
  ("witnesses no process") and `:1064-1066` describe round 48. At this tip
  `kama-live-replay.py --witness-dir D` passes the flag to the live tool, which writes
  `D/ready.json {schema: kama-live-witness/v1, port, pid}` after its checks and holds the server
  until `D/release`; the rerun receipt carries `witness {released, waited_ms, port, pid, dir}` and
  the replay JSON gains `witness_dir`. The witness is not compared (a witnessed replay matches
  exactly as an unwitnessed one); what makes it evidence is an outside observer, which is what
  the round-49 C1 counter is.
- *The archive check is bounded.* `:1006-1011` says the tool hashed the archive and member before
  starting the server; at this tip it first refuses an archive that is not a regular file, is
  larger than 1 GiB or holds more than 4096 index entries, and a member that is sparse or whose
  declared size differs from the `--server` file's (`tools/kama-llamacpp-live.py:217-263`, tokens
  `provenance-archive-not-regular`, `-archive-too-large`, `-archive-too-many-members`,
  `-member-sparse`, `-member-size-mismatch`).
- *Still frontier after this build.* Content-aware eligibility (`:972-977`: unchanged — a
  same-length wholesale replacement is still invisible); the 20-line threshold as a derived
  policy (`:978-982`; at `--threshold 1` this tip reports `events=100 restored=18 partial=4
  unrestored=59 ungraded=19 ungraded_lines=187`, exit 1); a binding test a denial cannot pass
  (`:1062-1063`: the lexical tripwire is narrower, not replaced, and the C2 counter implements the
  same v4 rule on its own code path); the `A-row` mutable cells (`:990-993`); position-based
  restoration (`:994-996`); a region vocabulary for the preamble banner; and, new, that the live
  tool's `--selftest` has no case for `hold_for_witness` — the witness path is covered only by the
  C1 counter's live leg.
```

---

## 4. corpus/knowledge/llamacpp-loading-lifecycle.md — append after `:451`

*(Redundant with the live append that landed during this seat's work; kept as the measured basis.
Do not apply twice.)*

Supersedes, by naming: the replay invocation at `:442` and the "what the replay still cannot show"
list at `:444-451`, both written at `380bcdff`.

```markdown
**Round-49 execution witness and bounded record-time verification (appended 2026-10-26; build
`74558c71`; S494 and S495 are S494/S495 in `corpus/SOURCES.md`).** Two of the round-48 gaps this
entry listed are closed by the build, with the same schema (`kama-llamacpp-live/v5`,
`kama-live-replay/v1` unchanged).

- **A replay can now be watched while its server runs.** `tools/kama-live-replay.py --receipt R
  --work W --out J --witness-dir D` passes `--witness-dir D` (and `--witness-timeout`, default
  120 s) to the live tool. After the server is ready and its checks have run, the live tool writes
  `D/ready.json` `{schema: kama-live-witness/v1, port, pid, written_utc}` — `pid` is the
  `llama-server` child — and holds the server until `D/release` exists, the child exits or the
  timeout passes, then tears down as before (`tools/kama-llamacpp-live.py:280-300`). The rerun
  receipt gains `witness {schema, dir, port, pid, released, waited_ms}`; the replay's JSON gains
  `witness_dir`. The witness is recorded, not compared: a witnessed replay matches exactly as an
  unwitnessed one, so the value is for an observer outside both tools (round-49 C1 counter checks
  `/proc/<pid>/exe`, the listening socket inode, the `-m` argument's digest and a fresh nonce
  through `/tokenize` + `/detokenize`).
- **Record time no longer hashes a member of unbounded size.** `verify_archive_member()` refuses,
  before reading a member byte, an archive that is not a regular file, larger than 1 GiB
  (`ARCHIVE_MAX_BYTES`) or holding more than 4096 index entries (`MEMBER_MAX_COUNT`), and a member
  that is absent, not a file, sparse, or whose declared size differs from the `--server` file's
  (`tools/kama-llamacpp-live.py:212-263`); tokens `provenance-archive-not-regular`,
  `provenance-archive-too-large`, `provenance-archive-too-many-members`, `provenance-member-sparse`,
  `provenance-member-size-mismatch`. The round-48 seat's ~104-byte sparse archive declaring
  `GNU.sparse.realsize = 10^15` now exits 2 with `provenance-member-sparse` instead of reading
  ~10^15 bytes.
- **Unchanged and still unproven.** Instance facts (port, pid, timings, log text) are still not
  reproduced by a replay; provenance still binds only three artifacts (archive, member, model) and
  still proves bytes, not authenticity (no signature, no TLS pin); the loading window can still be
  missed. New: the live tool's `--selftest` exercises all seven archive/member refusals but has no
  case for `hold_for_witness`, so the witness path's only automated coverage is the round-49 C1
  counter. Scope is unchanged: one build (b11909), CPU, `stories260K`, `--ctx 256`, one unregistered
  loopback port per run.
```

---

## 5. registry/append-only-contract.tsv — proposed cell rewrite (patch, not appended)

`registry/append-only-contract.tsv` is tab-separated and cannot take an appended correction, and
its `note` cell is prose the tool ignores (`corpus/README.md:809`; the tool reads `path`, `rule`
(validated only), `declared_at`, `region`). Two edits are needed for the note to describe the
grading that now runs. **Authority question for the L1:** the contract is the lane's declaration,
so the L1 decides whether a `note` cell may be corrected in place; the patch is supplied in
`contract-note.diff` rather than applied.

---

## 6. tools/kama-live-replay.py — proposed docstring correction (patch)

The tool's own output contract, `tools/kama-live-replay.py:36-38`, enumerates the JSON it writes
and omits `witness_dir`, which `:279` adds when `--witness-dir` is used. Patch in
`replay-docstring.diff`.

---

## 7. Lines audited and found accurate (no correction)

- `corpus/README.md:954-960` (`380bcdff` figures `files=89`, `ungraded_lines=89`), `:1026-1028`
  (`replayed=3/3`), `:906-908` (build/base commits): round-scoped history, reproduced by the tools
  unchanged.
- `SKILL.md:1475` self-test cell `KLR_SELFTEST pass=22 fail=0`: measured 22 at this tip.
- `SKILL.md:1473` event-line and `summary` shapes; exit map 0/1/2; `SKILL.md:1474` "as v4" exit map.
- `corpus/QUALITY.md:387` (KQ67), `:409` (KQ73), `:410` (KQ74): commands and criteria still hold at
  this tip (`receipt-provenance-check.py` prints `receipts=3 bound=1`, exit 0; the audit prints
  `"regressed": 0`).
- `corpus/knowledge/llamacpp-loading-lifecycle.md:434-441` (round-47 and round-48 observations).
