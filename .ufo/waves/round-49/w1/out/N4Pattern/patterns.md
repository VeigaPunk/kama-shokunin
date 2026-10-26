# Cross-claim instrument patterns — round 49 (N4Pattern)

Verdict: this round closed four round-48 closure items (R1 archive bound, K2Cheat/K2Urlswap replay witness, K1Regions exempt laundering, K1Binding substring binding) by replacing self-report with outside observation; the three round-48 N4Pattern-ranked residual acceptors (hexrun unverifiable note, GGUF `--receipt`, context-capacity CELLS pair) are untouched and remain open, and the cheapest remaining self-report (digest-ledger `unverifiable` = any non-empty note) is even lower-cost than the previously ranked hexrun hatch.

Axes: calibration and operability. Evidence from the lane build tip `74558c71c38ceaeace15fd4cf8aa9d84977584b1` (clone `/fast/scratch/hyaku/kama-r49/N4Pattern/lane`).

## What the round-49 build changed (self-report → outside observation)

The build diff (freeze `36d5ed26` → build `74558c71`) touches exactly four files:
`corpus/SOURCES.md` (+S494, +S495), `tools/append-only-audit.py` (101 +/–), `tools/kama-live-replay.py` (27 +/–), `tools/kama-llamacpp-live.py` (132 +/–).

- **C1 witness (operability, R5 K2Cheat/K2Urlswap).** `kama-llamacpp-live.py:280-300` `hold_for_witness()` writes `D/ready.json` `{schema kama-live-witness/v1, port, pid}` atomically and holds the server until `D/release` exists. The counter's `observe()` (`round49-replay-witness-audit.py:258-289`) does not trust the receipt: it reads `/proc/<pid>/exe` (frozen b11909 digest), the LISTEN socket inode owned by the pid, `-m` argv hashing to the frozen model, and round-trips a fresh nonce through `/tokenize`+/detokenize` against its own GGUF vocab decode; `witness_one()` (`:292-340`) also requires the server gone and port refusing after release. Outside observation replaces the self-reporting rerun receipt.
- **C2 origin (calibration, R5 K1Regions/K1Binding).** `append-only-audit.py:423-441` `origins()` derives each line's birth section from the first commit blob holding the text (git history), and `:474-476` ungrades only text born in an exempt section; `:14-19` (docstring) bind the row token as a whole word, apply a three-word negation window, and refuse wildcard self-declaration. Git history is the outside observer, not the section the text currently sits in.

## Ranked: instruments still accepting a self-reported artefact after this build

Order is by what a cheat would exploit first (cost to fake × value to the claim). All files are identical to the round-48 base for the flagged ones (verified: `git log 438127bc..74558c71 --` touches none of hexrun-census.py, gguf-identity.py, kama-context-capacity.py, digest-ledger.py, kama-ollama-evidence.py).

1. **digest-ledger.py:131-132 — `unverifiable` with any non-empty note.** Classification returns `unverifiable` whenever `r["note"].strip()` is truthy; nothing checks the note's content, length, or reason. Cheat: relabel any unknown token `unverifiable` with a one-word note ("why") → census passes. Lower bar than hexrun's 10 chars (see #2). Round-48 N4Pattern list did not name digest-ledger; it is the cheapest remaining hatch.
2. **hexrun-census.py:273-274 — `unverifiable` note-length hatch (round-48 N4Pattern #1, unchanged).** `len(row.note) >= NOTE_MIN` (10) passes without binding to evidence; a submitter adds a long assertion to any unknown token. Slightly more text than #1, same shape.
3. **gguf-identity.py:948,978-984 — `--receipt` reconciliation (round-48 N4Pattern #2, unchanged).** `load_receipt()` + `reconcile_receipt()` accept a supplied receipt; `evidence_scope` is labeled `receipt-self-report-not-authenticated-execution` (`:629`), but any downstream consumer treating reconciliation as provenance can be fooled by a forged/stale receipt stating metadata correspondence.
4. **kama-ollama-evidence.py:472-476 — caller-supplied offline captures.** `--tags/--ps` are supplied by the caller; `loaded_same_digest` (exit 0) follows from a self-consistent tags+ps snapshot pair. The tool is honest (`readiness=unknown`, `scope=offline-captures-not-runtime`) and has no current-claim usage (`grep` shows only round-14 acceptance), so exploit value is bounded today — but it is still a classifier over claimant-authored input with no acquisition.
5. **kama-context-capacity.py:602-635 — CELLS drift check (round-48 N4Pattern #3, unchanged).** Embedded cells are compared to the counter's CELLS; agreement is not independent semantic validation. A coordinated change of both the counter and tool definition passes. Calibration weakness, not an observed exploit.
6. **capability-repertoire-audit.py:140-161 — self-assessed capability rows.** Evidence cell only needs a repo-relative path token that resolves at the evaluated revision; nothing verifies the path substantiates the capability. A cheat can name any existing file in the evidence cell. Lower value: capability census is self-assessment by design.
7. **pin-trigger-consumed.py:19-29 — committed pin-watch receipt as ground truth.** `--receipt` is machine-derived from upstream `git ls-remote` (not claimant-authored), but the tool only checks that a consumer ledger exists for each `behind` row; a fabricated receipt with no behind rows trivially passes. Standing KQ check, not a frozen claim counter.

## Round-48 items this round closed

From the round-48 closure lesson (`corpus/lessons/round-48-verifier-spotcheck.md` §6) and the round-48 N4Pattern list:

| Round-48 item | Closed by |
|---|---|
| R1 Sen2Live F1: `verify_archive_member` hashed a sparse member of any declared size | Yes — `kama-llamacpp-live.py:208-263`: archive regular ≤1 GiB, ≤4096 index entries streamed, member non-sparse, declared size == `--server` file size, all checked before hashing; new tokens `provenance-archive-not-regular/-too-large/-too-many-members`, `provenance-member-sparse/-size-mismatch` |
| R5 K2Cheat/K2Urlswap: replay never witnessed server execution | Yes — C1 witness (`hold_for_witness` + counter `observe`, above) |
| R5 K1Regions: content-blind exempt-section laundering | Yes — v4 origin (`append-only-audit.py:423-441,474-476`) |
| R5 K1Binding: substring declaration binding | Yes — v4 whole-word token, three-word negation window, no wildcard self-declaration |
| R5 K2Record: record time never fetches the URLs | No — the witness covers replay time; record-time acquisition is unchanged |
| R5 L1Lowthr: sub-20-line deletions unwatched | No — threshold unchanged (limit `sub-20 threshold is unchanged`) |
| r47-D7 prerelease cliff | No — not touched |

Round-48 N4Pattern ranked items that remain open: hexrun (`:273-274`), GGUF (`:948,978-984`), context-capacity (`:602-635`) — all untouched by this build.

## Bounded move (pattern synthesis)

The round-49 pattern is "replace the receipt with an observer that re-derives the fact from a source the claimant cannot edit" — `/proc`, socket ownership, tokenizer round-trip, and git blob history. The same pattern is available at the cheapest remaining hatch: make `unverifiable` in both digest-ledger.py and hexrun-census.py require the note to cite a source the tool can re-verify (e.g., a path in the repo, a URL, a revision), matching C2's origin discipline, rather than any non-empty / ≥10-char string. Risk: legitimately unavailable upstream material would become `ledger_bad`; keep the category but require an auditable, located justification (like C2's located declarations) if a pass result is required. Verification for this move: a forged long-note ledger case (unit), a fabricated GGUF receipt case, a coordinated CELLS mutation case, and a fabricated Ollama tags+ps pair case.
