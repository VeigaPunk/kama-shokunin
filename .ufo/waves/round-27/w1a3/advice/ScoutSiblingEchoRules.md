VERDICT: holds — KQ37 is lane-new: no sibling QUALITY.md or lesson states the decoded-request-echo refusal and the one-row-per-message-frame rule.

## Question

Does any sibling lane already hold a rule equivalent to kama `corpus/QUALITY.md` KQ37 (a counter that credits a live server error signature must refuse JSON-decoded request echoes, and must credit at most one row per message frame)?

Compared with KQ37 at `kama-shokunin/corpus/QUALITY.md:219` (section header `:215`). The two load-bearing clauses are: (1) refuse the signature when it occurs, case-folded or with whitespace removed, in the request path, in any JSON-decoded key or value at any depth, or in either serialisation of the decoded body (raw bytes are not enough; RFC 8259 §7 / S136); (2) at most one row per message frame (signature cut out, case-folded, not blank; S137). The third clause — a non-author shortcut-control receipt for each named echo class committed before data — is a fleet-common control pattern and is not what makes KQ37 new.

## Method

Read-only. Twenty sibling lanes under `/home/vgpnk/Projects/shokunin/*-shokunin/` excluding `kama-shokunin`. Every lane has `corpus/QUALITY.md` and `corpus/lessons/` (lesson markdown counts: audio 2, chousa 25, game-dev-2d 78, game-dev-3d 94, kagi 39, kaidoku 48, kake 57, kasegi 27, kengaku 33, kotoba 42, kotodama 159, kumitate 59, lore 2, mado 26, mori 51, revenger 6, souji 31, tabi 46, tameshi 35, tsukuroi 41).

Case-insensitive scan of those files only for `echo|escap|shortcut|frame` (Python `re.I` over each line; exit 0). 758 matching lines. Full extract: `/fast/scratch/hyaku/kama-r27c/ScoutSiblingEchoRules/hits.tsv` (213931 bytes). Distinctive-phrase counts inside that extract: `server echo` 2, `request echo` 2, `message frame` 0, `json-decoded` 0, `json decoded` 0, `\uXXXX` 0, `one row per message` 0, `case-folded` 0, `decoded request` 0, `not echoed` 0, `raw request` 0, `error signature` 0, `shortcut` 148.

Scope limit: knowledge entries, wave advice, and tools outside `corpus/QUALITY.md` and `corpus/lessons/` were not searched. [INFERENCE] a sibling could still describe the mechanism in a knowledge note; it is not a QUALITY criterion or a lesson rule on the scanned surface.

No tools installed.

## Hit table

Classification is against KQ37's two load-bearing clauses, not against the bare tokens.

| class | lane | path:line | what the line actually requires | vs KQ37 |
|---|---|---|---|---|
| equivalent | — | — | none | no sibling holds both clauses |
| named echo class, mechanism absent | mado | `mado-shokunin/corpus/QUALITY.md:324` | criterion 36: before data, receipts must name the shortcut shapes closures have seen meet a counter, including "server echo", plus do-nothing, all-false/empty, junk, label- or fixture-keyed, no-reader | names the class; does not say JSON-decoded surfaces, unicode escapes, or one row per frame |
| named echo class, mechanism absent | mori | `mori-shokunin/corpus/QUALITY.md:716` | criterion 98: before data, map each leg-rejection shape — including "server echo" — to a named control or a stated inapplicability | same: a control-shape name, not the discrimination rule |
| request-echo is non-evidence, other surface | kaidoku | `kaidoku-shokunin/corpus/QUALITY.md:30` | criterion 20: a provider-log line that echoes the request (Ghidra `GoRttiMapper` "Using Go API snapshot for version X") is not evidence of the selected data | closest cousin on "do not credit an echo"; surface is a bound Ghidra log, not a live-server error-signature counter, and it does not compare decoded JSON or collapse frames |
| same, lesson | kaidoku | `kaidoku-shokunin/corpus/lessons/round-17.md:86` | `snapshot_label` request echo matches exact and fallback runs alike | motivating mistake for criterion 20, not KQ37 |
| same, lesson | kaidoku | `kaidoku-shokunin/corpus/lessons/round-17.md:109` | decision table covers "the request echo" | same |
| error field may echo the request; grade status, not the echo | tsukuroi | `tsukuroi-shokunin/corpus/QUALITY.md:83` | criterion 39 (R20-C2-REFUSAL-ECHO): a `CANNOT_EVALUATE` may echo the requested object SHA in `revision`; that field is diagnostic, not an accepted binding. "Test a refusal that echoes its input." | same family (an error/diagnostic repeats caller input); object is a Git selector SHA, not a JSON body, and there is no one-row-per-frame rule |
| same, lesson | tsukuroi | `tsukuroi-shokunin/corpus/lessons/round-20.md:45` | R20-C2-REFUSAL-ECHO: grader treated any 40-hex error echo as a successful binding | motivating row for criterion 39 |
| echoed expected signature is not attribution | game-dev-2d | `game-dev-2d-shokunin/corpus/lessons/r63-signature-spoof-boundary.md:69` | on a CASES verdict record, `signature` echoes the expected string, not its origin | process-output spoof, not a request-body echo rule; not in that lane's QUALITY.md |
| echo is not measurement | game-dev-2d | `game-dev-2d-shokunin/corpus/lessons/r101-ytrans-dead-flag.md:61` | an echo-only arm passes the echo and hit-count checks and is still not a measurement | offset-token fixture, not KQ37 |
| marker bait | kengaku | `kengaku-shokunin/corpus/lessons/2026-10-16-round23-stream-surface.md:53` | a forcing asks a compliant leg to echo a FAIL-marker substring so the shim classifies the 200 as a failure | upstream-leg bait, not a counter rule about decoded request bodies |
| stub echo is not acceptance | kake | `kake-shokunin/corpus/QUALITY.md:264` | "Fake/stub-echo tests are not behavioral acceptance evidence." | bans stub oracles; no request-echo test |
| page echoes a nonce | tabi | `tabi-shokunin/corpus/QUALITY.md:169` | a download record binds to a nonce the counter generates and the page echoes | browser-artifact binding, not an error signature |
| off-topic page echo met a counter | kotodama | `kotodama-shokunin/corpus/lessons/round-58.md:23` | an echo generator met RELEVANCE; CtlOffTopicEcho58 is 20 rows on one IRS form page (`:24`, `:27`) | content-repetition shortcut, not JSON request echo of a server error |
| pre-data shortcut controls, no echo clause | chousa | `chousa-shokunin/corpus/QUALITY.md:159` | criterion 24: before data, score do-nothing, all-false, junk, no-reader, and label- or id-keyed shortcut controls (`:161-162`) | overlaps KQ37's third clause only |
| same | kaidoku | `kaidoku-shokunin/corpus/QUALITY.md:58` | criterion 48: before data, score do-nothing, junk-row, all-false, no-reader and id-keyed shortcut controls | same overlap |
| same | kotoba | `kotoba-shokunin/corpus/QUALITY.md:48` | kotoba Q37 (different criterion, same id string): before data, §9 shortcuts include real text with no instance of the claimed form, a case/placeholder of held knowledge, a remapping gate, and a stdlib-shadow module | id collision only; not kama KQ37 |
| same | kumitate | `kumitate-shokunin/corpus/QUALITY.md:488` | frozen plan names absent, constant, junk, no-reader and label-keyed shortcut controls, scored before data | same overlap |
| same | mori | `mori-shokunin/corpus/QUALITY.md:736` | criterion 99: label-keyed and harness-keyed shortcut controls before data | same overlap; "server echo" itself is criterion 98 at `:716` |
| same | kake | `kake-shokunin/corpus/QUALITY.md:881` | reject a shortcut control that passes a bullet's cases without opening a body (`CtlShortcut`, `:883`) | body-reading polarity, not echo discrimination |
| same | tameshi | `tameshi-shokunin/corpus/QUALITY.md:657` | criterion 58: a named shortcut-control class with no scored receipt is exploratory before data, or it does not dispatch | receipt-before-data, not the echo test |
| unrelated "one row" | tsukuroi | `tsukuroi-shokunin/corpus/QUALITY.md:151` | criterion 79: one row per frozen question id | not a message frame |
| unrelated "one row" | chousa | `chousa-shokunin/corpus/QUALITY.md:70` | one row per spot-check debt | not a message frame |
| unrelated "frame" | game-dev-3d | `game-dev-3d-shokunin/corpus/QUALITY.md:15` | Q4: re-derive numbers from the stated frame | render/measurement frame |
| unrelated "escap" | (many) | e.g. `souji-shokunin/corpus/QUALITY.md:41` Q17, `:83` Q34, `:92` Q38; `kengaku-shokunin/corpus/lessons/round-29.md:40` (JSON `ensure_ascii` quote); `mori-shokunin/corpus/lessons/round-19.md:151` | path escape, sandbox escape, markdown `\|`, HTML/JSON encoder docs | none is "raw request bytes miss a `\uXXXX` echo of an error signature" |

Token tallies in the 758-line extract (a line can carry more than one token): frame 211, escap 194, shortcut 147, echo 136, plus 64 lines where more than one token hit and 6 mixed pairs. The frame and escap majorities are audio frames, process-group escape, and markdown-pipe escape. They were classified by reading every echo line and every echo/escap line that also mentions json, request, signature, counter, unicode, error, server, body, or "row per" (69 lines); the rest of the frame/escap mass does not state a counter rule.

## What is shared, and what is not

Shared, and not a duplicate of KQ37: several lanes already require shortcut controls scored and committed before data (chousa 24, kaidoku 48, kotoba Q37, kumitate, mori 98–99, mado 36, tameshi 58, kake body-reading bullets). mado and mori already list "server echo" as one of those shapes. tsukuroi 39 and kaidoku 20 already say an echoed request value is not the observation.

Not held anywhere in the scanned files: refuse the signature on JSON-decoded keys and values (not raw bytes); compare case-folded and whitespace-stripped; compare both serialisations of the decoded body; credit one row per message frame after the signature is cut out. Those are the clauses KQ37 adds. [INFERENCE] mado/mori "server echo" could be implemented as a raw-byte check and would still satisfy their criteria as written; KQ37 would reject that check.

## Remaining unknown

Sibling `corpus/knowledge/` and `.ufo/` advice were out of scope. This scout did not open them, so a prose note there could still describe the llama.cpp echo site without being a criterion.
