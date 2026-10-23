VERDICT: partial — every §Claims, §X1-evidence, §Gate-decision, and §Fix-receipt cell checks against its seat report or receipt, but the committed §Mistakes row 1 misstates its own captured-by seat in two cells (both already cured by uncommitted working-tree edits), and three low-severity cells (Gate re-open count, the 1853 composition, the X1 sources list) overstate or undercount their sources.

Reviewer: KamaR27A3.ReviewLessonFinal-4 (residual, ≤8-seat call). 2026-10-23.
Target: `corpus/lessons/round-27.md` **at 52632caa2ed813c1c12f7a9dcab3556b4f0bd9eb**. No tool installs or updates were performed (none needed). No server started; no counter `main()` run; no git/jj writes in the lane; scratch only under `/fast/scratch/hyaku/kama-r27c/res-ReviewLessonFinal/` (RFC refetch, since removed); the committed lesson was materialized for reading to `residual/out/ReviewLessonFinal/lessons-at-52632caa.md`. The untrusted scratch directories were not read or cited.

## 0. File identity — the working tree is ahead of the assigned tip

```
git -C <lane> rev-parse HEAD           → 52632caa2ed813c1c12f7a9dcab3556b4f0bd9eb
git -C <lane> status --porcelain=v1 -- corpus/lessons/round-27.md
                                       →  M corpus/lessons/round-27.md
git -C <lane> diff -U2 -- corpus/lessons/round-27.md   (2 hunks, +2/−1):
  @@ -90,4  + adds the row "does the frame rule collapse distinct genuine faults? | ExecOfflineFrameReplay | …"
  @@ -135,5 + rewrites §Mistakes row 1 ("unbounded self-referential fixture write…" → "unbounded repeated fixture growth … mechanism not established …")
```

I reviewed the **committed** text (cells quoted from `lessons-at-52632caa.md`) and also
checked both uncommitted hunks, since they touch my assigned sections. Both hunks
verify (§3, §4): the added frame-replay row matches its seat report exactly, and the
rewritten Mistakes row 1 adopts precisely the corrections its captured-by seat demanded.

## 1. Findings (severity order)

### F1 (medium) — §Mistakes row 1, committed class cell asserts a mechanism its own captured-by seat explicitly declined to establish

Committed text (lessons-at-52632caa.md:133): "unbounded self-referential fixture write:
a seat's preload fixture was **appended to itself** until it filled /fast".
Source it summarises: `.ufo/waves/round-27/w1a3/advice/CriticMistakeRow.md`, verdict
"partial", class cell "partial": "The hook writes a formatted `sitecustomize hit pid=…`
record, **not its two source lines** (`sitecustomize.py.head4k:1-4`)"; "Use 'unbounded
fixture growth / disk exhaustion; exact writer and self-reference mechanism
unestablished.'" Corroborated by the retained bytes: `a3/mistake-runaway/sitecustomize.py.head4k`
is the two-line snippet (`open(os.environ["MARKER"],"a").write("sitecustomize hit …")`)
repeated — running that line emits a formatted record, not the source text — and
`a3/mistake-runaway/REMOVED-RUNAWAY.txt:1` says only 'MARKER **evidently** pointed back
at this file' (Main's inference, no writer command retained). The evidence-pointer cell
on the same row is accurate (262699483136 bytes = the note's figure; head4k = 4096 B;
both copies present). The class cell outruns the evidence. **The uncommitted working-tree
hunk 2 fixes exactly this** ("unbounded repeated fixture growth … mechanism not
established: the retained prefix repeats the two hook source lines, which the hook itself
does not write; Main's note says MARKER 'evidently' pointed back") — verified word-by-word
against CriticMistakeRow's demanded correction.

### F2 (medium) — §Mistakes row 1, committed fix cell is literally false over wave contexts

Committed text: "**every round-27 wave context** requires `ulimit -f` on fixture-writing
commands…". The attempt-2 wave context is a round-27 wave context and has no such rule:
`w1-controls/spec.json:4` caps "processes, memory and wall time" only — CriticMistakeRow's
fix-cell finding verbatim ("'every round-27 wave context' is false literally: the preserved
attempt-2 context is a counterexample"; its jq sweep of the 37-item spec found zero
`ulimit|RLIMIT_FSIZE|file-size|MARKER` mentions). **The uncommitted hunk 2 fixes this too**
("the attempt-3 wave and residual contexts require …"), matching the critic's smallest
correction, and adds the critic's other demanded nuance ("the cap bounds each file's size,
it does not stop the process"), which the committed §Fix receipt already carried.

### F3 (low-moderate) — §Gate: "The three new rows were re-opened" undercounts; S139 has no named non-author re-open

The Gate SOURCES table lists **four** new rows (S136, S137, S138, S139-supersedes-S136);
the following sentence says "The three new rows were re-opened by non-author seats:
ScoutReopenS136, ScoutReopenS137, ReviewLessonGate (all `holds`)". The three named reports
exist, all verdict lines read "holds", and ReviewLessonGate's own verdict names exactly
"All three round-27 Gate rows (S136, S137, S138)" — i.e. the sentence is a stale count
from before S139 was added in the same commit d183ec5 that landed this text. S139 has no
dedicated re-open pass. Substance is defensible: S139 re-uses S136's fetch
(sha256 61a5378f…2d7, which I reproduced), ScoutReopenS136's independent fetch quoted the
surrogate-pair sentence at rfc8259.txt lines 455–459, and CriticEntryFactsSources re-read
§7 — but no seat is on record re-opening an **S139 row**, and the sentence as written
misstates the row count.

### F4 (low-moderate) — §Mistakes row 4 (and header): the "7 attempt-3 repair files" composition is a reconstruction, not a measured cell

Header and row 4 state as fact: "the 1853 first written here also counted **7 attempt-3
repair files**". The cited seat does not establish this: ReviewUntrackedDisposal measured
`/usr/bin/find -type f | wc -l` → **1846**, `-mindepth 1` → **2257 paths**, found **no
mover manifest**, and hypothesised a different explanation ("most likely a lane-side count
taken before the move"). The arithmetic is consistent — the committed attempt-3 repair
files number exactly 7 (d3: README.json, info-help.txt, info-version.txt; d4: README.json
+ 3 `.error-lines.jsonl`, per SentinelCommittedBytesSecrets' 11-path inventory) and
1846+7=1853 — and the L1 is the only witness to its own earlier count, but no seat
measured the composition. The core defect (1853 ≠ the moved count; header corrected to
1846) is real and correctly captured; the explanatory clause is [INFERENCE]-grade
presented as fact.

### F5 (low) — §Claims X1 bullet: "Sources opened this round: S136, S137, S139" omits S138

S138 was opened this round by the L1 per the Gate table itself (accessed 2026-10-23T06:53Z)
and SOURCES.md (S138 row; search-log entry "round-27 echo-discrimination sources and S133
anchor correction" names S136, S137 "plus one correction row, S138"). If the list is meant
to be X1-scoped (S138 serves repair 7, not the echo rule) it should say so; as written the
round-level list is incomplete.

### Verification gap G1 (low) — the C1 tip receipt measures an ancestor, not the landed tip

`.ufo/waves/round-27/a3/c1-tip.out:1` records a fresh clone "at **d183ec57**2a5eed5…";
`git merge-base --is-ancestor d183ec57 52632caa` → exit 0 (ancestor). The kill rule reads
"counted < 15 **at the landed tip**". The tip itself holds no round-27 registry
(`git ls-tree 52632caa -- registry/` → no `error-signatures-r27.json`; counter bytes
identical at both commits, §2), so counted 0 follows structurally at 52632caa and the
**miss** verdict stands — but the receipt on file is not at the landed tip bytes. No seat
re-ran the counter at the tip (and this seat may not run `main()` without a port block).

### Verification gap G2 (low) — timestamps accepted from receipts

The Gate "accessed" cells (06:48Z/06:53Z) and the live probe's "observed 07:11:54Z" are
receipt assertions; this review verified same-day content stability (RFC refetch hash
match) and the probe receipt's `observed_at_utc` field, not wall-clock access itself.

## 2. Cells verified — §Claims (C1 miss wording)

| cell | source check | result |
|---|---|---|
| target `counted >= 15`; kill rule "counted < 15 at the landed tip is a miss: reported as a miss, never amended, never re-scaled" | `.ufo/waves/round-27/preregistration.json` target/kill_rule | holds |
| "the landed tip holds no round-27 registry" | `git ls-tree 52632caa -- registry/` → 7 entries, no `error-signatures-r27.json` | holds |
| "37-seat control wave dispatched 05:41:33Z died with the orchestrator" | `w1-controls/spawn-result.txt:1` "2026-10-23T05:41:33.096709Z … Spawned 37 background agents"; plan.json death 06:19:06Z | holds |
| "A3 counter, predicate, target and kill rule unchanged since `0ec32cac`" | `git show 0ec32cac:.ufo/waves/round-27/count-c1.py \| sha256sum` and same at 52632caa → both `49491b80…2765`; prereg byte-identical 0ec32cac↔324d5d62 (CriticC1Withdrawal §5); `--name-status` shows no later touch | holds |
| "C1 is reported as a miss (honest stop)" per the frozen kill rule | kill-rule text + registry absence; LOG.md:1762–1767 "C1 … — miss"; commit d183ec5 message "C1 reported as miss" | holds |
| "(first landed text said 'neither meets nor misses'; CriticC1Withdrawal showed that exemption is not in the frozen rule)" | CriticC1Withdrawal verdict/strongest-counterexample says exactly that, quoting prereg:16-17 | holds |
| "needs a committed non-author shortcut-control receipt for each class … before any data seat (round-26 spot-check defect 2)" | spotcheck:234 "Commit one shortcut-control receipt per class before any data seat"; CriticC1Withdrawal §4: 258 C1 receipt JSONs, none under the frozen A3 hash, only author base/pilot receipts | holds |
| "No data seat was ever dispatched" | CriticC1Withdrawal §1–3 (no data dispatch in committed history; spec.json:4 "no data seat runs in the wave"); w1a3 (d183ec5) added evidence seats only; still no registry/SKILL section at tip | holds |
| X1: "round-26 counter compared raw request bytes (line 384) and a base-tree shortcut met it 12/12; QUALITY.md held no echo rule" | shortcut.receipt.json registered 12 / counted 12 / met true (ExecOfflineEchoReplay §Inputs, SELFCHECK agree); r26 `:384 e_not_echoed = sig not in req_bytes`; CriticNoveltyAtBase found no echo/frame criterion in historical QUALITY | holds |
| X1: "Sources opened this round: S136, S137, S139 (supersedes S136)" | S136/S137/S139 all opened 2026-10-23 — **but S138 too** → finding F5 | partial |

## 3. Cells verified — §X1 evidence table (7 committed rows + uncommitted 8th)

| row | seat report cross-check | result |
|---|---|---|
| ExecLiveEchoProbe: "plain, first-char-escaped and fully escaped spellings give byte-identical 400 bodies holding the decoded value; two values share one frame; control 200 (receipt.json, observed 07:11:54Z)" | report: 3 A-spellings → resp sha `9ea801fb…5a06` byte-identical, 2 B-spellings → `96398469…7dc3`; decoded sig in every 400 message; `clause_h_all_frames_equal=true`; req4-control 200; `observed_at_utc 2026-10-23T07:11:54Z` | holds |
| ExecOfflineEchoReplay: "round-26 flags 0/12; A3 (f) as written 0/12 (string bodies); A3 shape check refuses 12/12; A3 (f) on decoded bodies 12/12" | harness stdout totals `r26_flags_echo 0/12 a3_flags_echo 0/12 a3_if_decoded 12/12 a3_schema_e_rejects 12/12` | holds |
| MutEchoDecodedLoadBearing: "raw-body-only mutant 0/12 (killed); other single-guard mutants survive because guards overlap" | M1 12→0/12 killed (exit 0→1→0, exact restoration); M2–M5 survive 12/12 | holds |
| MutFrameLoadBearing: "frame on 1/12 survivors, off 12/12 (killed)" | pristine/frame-only 1 survivor, 11 `h:same-message-frame`; mutated 12/12; detector exits 0→1→0; scratch module hash restored | holds |
| (uncommitted) ExecOfflineFrameReplay: "clause (h) verbatim: shortcut 1/12 survive (11 collisions); E26 17/17 survive, 0 collisions (9 rows have message = signature …; 3 process rows are outside its reach)" | stdout `shortcut_survivors 1/12`, 11 colliding pairs vs X26-01; `e26_survivors 17/17 … colliding pairs 0`; 9 message==signature rows guard-suppressed; E26-15/16/17 process-log rows, `error_message()`→None | holds |
| ScoutEchoSitesSnapshot: "12 request-string frames (S137 one of them) + 14 request-JSON dumps" | report: 26 client-chosen request-derived lines, "Distinct HTTP frames … **12** … S137 is one"; "The 14 dump lines … inside `437` or `585`" | holds |
| ScoutRawEchoInLaneTools: "only round-26 `count-c1.py:384`" | verdict: "KQ37's raw-bytes reject flags only round-26 `count-c1.py:384`"; no other raw echo test in tools/gates/census | holds |
| ScoutSiblingEchoRules: "no equivalent; two siblings name 'server echo' as a control shape only" | verdict "no sibling holds both clauses"; mado QUALITY:324 and mori QUALITY:716 name "server echo" as control shapes | holds |
| header "wave w1a3, 34 seats" | 34 `.md` reports under `w1a3/advice/` (35 dir entries − swarm-registry.json) | holds |

## 4. Cells verified — §Gate

SOURCES table (independent re-verification where cheap):

| cell | check | result |
|---|---|---|
| S136 sha `61a5378f…2d7`; "Any character may be escaped." — line 433 | my fetch: sha256 `61a5378f4255c720beb2a4b4a63b29540147c140f36988bf086291989b4cd2d7`; line 433 verbatim (matches ScoutReopenS136 + ReviewLessonGate) | holds |
| S137 sha `b4f4aae7…d442`; throw at :1375 | equals snapshot `.ufo/waves/round-27/sources/llama.cpp-704366d/server-common.cpp` hash; quote verbatim at 1375 (ScoutReopenS137 numbered fetch) | holds |
| S138 sha `dd1de0f2…2329`; open 1810, closing `}` 1835 | ReviewLessonGate numbered fetch: `1810 → bool try_clear_idle_slots() {`, `1835 → }`; supersedes S133's 1810-1834 (SOURCES row unchanged, correction carried in S138's teaches) | holds |
| S139 same-fetch sha; quote "the character is represented as a 12-character sequence, encoding the UTF-16 surrogate pair." — lines 456-457 | my fetch lines 456–457: "Plane, the character is represented as a 12-character sequence," / "encoding the UTF-16 surrogate pair." — exact | holds |
| "No existing row's `status`, `recheck` or `used-by` changed" | `git diff --numstat a720399e 52632caa -- corpus/SOURCES.md` → `6  0` (append-only: 4 rows + search log + blank) | holds |
| "S136 stays as landed; S139 supersedes its escape-length wording … and its STD 90 attribution" | S136 row unchanged (numstat); S136 teaches still carries the six-character wording; S139 teaches "supersedes S136 … twelve-character"; STD 90 absent from rfc8259.txt, present in RFC Editor/Datatracker indexes (ScoutReopenS136 fetches) | holds |
| re-open sentence "The three new rows …" | three reports exist, all "holds", covering S136/S137/S138 — but four new rows are listed; S139 unre-opened → finding F3 | partial |

Gate decision table — all 12 rows:

| row (finding → decision) | source check | result |
|---|---|---|
| SentinelCommittedBytesSecrets redaction → **reject** | sentinel: "no bearer/API tokens, passwords, private-key bytes, or credential-bearing URLs"; recommends exactly the listed redactions; `credentialId: 18` present in all three d4 `.error-lines.jsonl` (grep); ReviewRepairD4Bytes: committed lines byte-identical (sha256-equal) to independent re-extraction; spotcheck:236 "Commit the raw provider error bytes" | holds |
| CriticEntryRuleVsCode casefold/literal-deletion → **reject for this round** | critic's smallest correction proposes exactly `casefold()` + `message.replace(signature,"")`; gap recorded at entry "Shortfalls" bullet + QUALITY KQ37 qualification 3 | holds |
| ConnectorShortcutClasses generalisation → **reject as KQ37 scope** | finding text matches the report's proposed extension; "prompt §9" = kama-round-27.md:343 rule 9 "Claim sizing" ("Before freezing, build the cheapest control … commit that receipt"); "seven sibling QUALITY files" = scout's chousa 24, kaidoku 48, kotoba Q37, kumitate, mori 98–99, mado 36, tameshi 58 (kake excluded as body-reading polarity) | holds |
| string-body / shape-check (ExecOfflineEchoReplay, ScoutRawEchoInLaneTools) → admit | matches both reports (`e:bad-request` at count-c1.py:576-581 refuses str bodies; (f) alone 0/12); entry §"How the round-27 counter implements it" and KQ37 qualification 2 exist and say this | holds |
| boundary-shift 12/12 (CriticKQ37Wording) → admit | probe `kq37_mechanical_accepts: 12`; KQ37 qualification 1 + entry §The rule "Boundary" leg exist | holds |
| `lower()` / positional frame / tab-only remainder (CriticEntryRuleVsCode) → admit | critic's three component findings verbatim; entry "Shortfalls against the rule's wording" bullet + qualification 3 | holds |
| six-character escape / "whatever string" (CriticEntryFactsSources) → admit; S139; facts 1 and 2 rewritten | critic found both; entry fact 1 now cites S139/surrogate pair, fact 2 scoped to "nonempty type other than text, json_object or json_schema" | holds |
| CriticEntryLimits → admit; entry §limits and §rule | file/model provenance via spec CtlFileEcho not prereg (`spec.json:52-54` vs prereg `controls_required`); baseline-scope limit; conservative-rejection note in §The rule + §What this does not establish | holds |
| "neither meets nor misses" not in kill rule (CriticC1Withdrawal) → admit; C1 reported as a miss | report's strongest counterexample; lesson now reports a miss | holds |
| X1 novelty: decoded comparison prescribed at base (CriticNoveltyAtBase) → admit; entry "What is new here and what is not" | spotcheck:234 prescribes decoded comparison at a720399e; entry section exists with the concession | holds |
| LOG correction miscounts/omits f4066979 (ReviewRepairD1Log) → admit; second appended LOG correction | report: "three sentences" vs four changed; f4066979 (00:56:41Z, "LOG candidate count corrected") omitted; second correction exists at LOG.md:1747–1758, appended (numstat +19/−0), correcting exactly those two points, "The entry above is not edited" | holds |
| "1853 paths" not the moved count (ReviewUntrackedDisposal) → admit; header now 1846 files | header at tip says 1846 files; find = 1846 — but the added composition claim is unverified → finding F4 | partial |

## 5. Cells verified — §Mistakes rows 2–4 and §Fix receipt

- Row 2 (LOG correction from memory): evidence (first correction entry LOG.md:1728; ReviewRepairD1Log findings), captured-by, and fix (second correction at :1747) all hold.
- Row 3 (S136 paraphrase): S136 teaches cell says "any character of a JSON string may be written as a six-character \uXXXX escape"; CriticEntryFactsSources found the overbreadth; fix "S139 supersedes S136" landed. Holds.
- Row 4: core holds; composition clause → F4.
- §Fix receipt vs `w1a3/out/ExecFixtureBoundDemo/receipt.json`: "fixture that appends its own bytes to itself" = `open(__file__,'ab').write(open(__file__,'rb').read())` loop; A1 `ulimit -f 2048` → exit **153** (SIGXFSZ, SIG_DFL) at exactly **2,097,152**; A0 → exit **1**, `OSError [Errno 27] File too large` with bash-inherited `SIG_IGN` (signal_disposition: bash SigIgn bit 24 = signal 25, inherited across exec); B1 `ulimit -f 20480` + timeout 5 → **20,971,520**; C0 same 5 s timeout, 2048 blocks → **2,097,152** (cap, not clock); E2 swallow → exit **124** (timeout), 889,000 swallowed EFBIG, file pinned at cap. Lesson sentence "the rule bounds disk use; it does not end the process" is exactly E2/D3's conclusion. **All cells hold.**

## 6. Residual risk and verification gaps

- G1 (above): the on-file C1 receipt is at ancestor d183ec57, not tip 52632caa; the miss at the tip rests on the structural registry-absence check, not a tip-byte receipt.
- F3/F4/F5 wording cells remain in the working tree (only the two Mistakes-row-1 defects are cured by the uncommitted hunks).
- I did not re-verify: the d3 pin hashes against a live b11755 `--help/--version` (accepted from repair-3 receipt + ReviewRepairD3Pins report existence), ExecLiveEchoProbe's raw req/resp bytes (hash-chain accepted from its manifest), and ExecOfflineFrameReplay/MutE* internals beyond their reports' internal consistency — all seats report pinned input hashes matching the frozen counter (49491b80…2765), which I independently confirmed at 0ec32cac and 52632caa.
- Tooling directive: no installs or updates performed.

## 7. Checks the canonical reviewer may want to run

1. `git -C <lane> diff -- corpus/lessons/round-27.md` — decide whether to land the two uncommitted hunks (they close F1/F2) and whether to also fix F3 ("three new rows" → four, or name S139's evidence), F4 (mark the 7-file composition as reconstruction), F5 (add S138 or scope the list to X1).
2. Optionally re-run the frozen counter at the tip bytes in a fresh clone to convert G1 from a structural inference into a tip receipt (requires the port-block rules for `main()`; with no registry the run is offline and prints `registered 0 counted 0 target 15 met False not-counted []`).
