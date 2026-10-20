# ReviewInference — round 12 (static, author advisor; unrun != pass)

Scope: `corpus/knowledge/served-identity-crosswalk.md` and the S031 / S011 registry rows plus the appended D4 paragraph in `corpus/SOURCES.md`. Verifies that the proposed inference clarification (round-11 verifier D4, `corpus/lessons/round-11-verifier-spotcheck.md:221-225`) neither overclaims remote inventory/runtime nor lets registry supersession read as an upstream change. Static reads only; no endpoint, docs fetch, runtime, or check was executed. No files edited.

## Findings (by severity)

### 1. MEDIUM — D4 is only half applied; the crosswalk still states S031 inferences as grounded fact

The SOURCES D4 append (`corpus/SOURCES.md:66`) says: "The crosswalk remote-entry conclusion that cites S031 carries the same inference status." That is not yet true on disk. Unlabeled S031-derived conclusions in `served-identity-crosswalk.md`:

- `:38` item 6 "Ollama remote entry … Available inventory is not proof of local weights (S031/S010)" — sits under the heading `## Grounded failure cases`, so it reads as grounded.
- `:29` Ollama row, last column: "a tags entry does not prove local weights (S031)".
- `:52` "What cannot be concluded": "never establishes … local (vs remote) provenance on Ollama".
- `:63` kama use: "On Ollama that is availability, not loaded residency (S031/S010)".

The file already uses the convention correctly elsewhere (`:27`, `:33`, `:45` carry `[INFERENCE]`). The lesson itself says the locality consequence is "[INFERENCE] from documented remote fields, not a quotation" (`corpus/lessons/round-11.md:152-153`; verifier `:143`). Fix: add `[INFERENCE]` to `:29`, `:38`, `:52`, `:63` (or move `:38` out of the "Grounded" list). Ground the inference on the field text, not on "S031" alone.

### 2. MEDIUM — D4 misattributes one verbatim quote to two fields

`corpus/SOURCES.md:66` attaches the quote "Name of the upstream model, if the model is remote" after "`remote_model` and `remote_host` fields". Only the `remote_model` description is located verbatim anywhere in the corpus (`corpus/lessons/round-11.md:40`; `corpus/lessons/round-11-verifier-spotcheck.md:161-166`). The lesson paraphrases `remote_host` as "names the upstream Ollama host" (`:166`). `remote_host` text is not quoted in any corpus file I read. A round-11 seat records a different `remote_host` description ("URL of the upstream Ollama host, if the model is remote") at `.ufo/waves/round-11/verification/FrontierRecord.md:49`; that is a seat record, not re-opened here.

Also `SOURCES.md:43` teaches "`remote_host` the upstream Ollama URL" while the lesson says "host". Fix: one located quote per field, and reconcile "URL" vs "host" to the verbatim text. Do not edit the immutable S031 cell; correct in the appended paragraph.

### 3. MEDIUM — registry supersession can still be read as upstream correction

- `served-identity-crosswalk.md:59`: "Registry prose correction (S011 'locally available') is already handled by S031's supersession." "Handled" implies the S011 prose was corrected. It was not: the upstream ModelSummary still says "Summary information for a locally available model" (`:29`; `round-11-verifier-spotcheck.md:158` "upstream still saying `locally available`"). Reword: upstream text unchanged; S031 is a registry-level supersession of S011's local-residency implication; S011's row is not amended.
- `SOURCES.md:23` (S011) still reads "Ollama locally available model inventory" / "Lists locally available models", status `mined`, with no pointer to S031. A reader starting from S011 gets the overstated claim. The contract forbids amending `teaches` and the status enum has no "superseded" value (`.ufo/waves/round-11/verification/MetadataLearning.md:18`: "Only `status`, `recheck` and `used-by` change in place … A correction is a new row whose `teaches` opens `supersedes S0NN —`"). So the reader pointer must live in an appended note or index, not in the S011 cell. `.ufo/waves/round-11/advice/ReviewIdentity.md:114` and `.ufo/waves/round-11/verification/PriorCoverage.md:62` already flag this; the D4 append does not add a pointer from S011.
- `SOURCES.md:66` says "S011's non-status cells stay as written", which implies a status change that did not happen (S011 is still `mined` at `:23`). Remove the implication or state "status unchanged".

### 4. LOW–MEDIUM — same URL, same version, no revision pin: the registry cannot say whether upstream changed

S011 and S031 share URL `https://docs.ollama.com/api/tags` and anchor "OpenAPI 3.1.0, info.version 0.1.0" (`SOURCES.md:23`, `:43`). Neither row pins a commit or page-modified date. S011 (round 10, 2026-10-19) did not record the remote fields; S031 (2026-10-20) does. The lesson calls S031 a "correction" (`round-11.md:45`), which implies the round-10 reading was incomplete. But the registry cannot distinguish "round-10 omitted a field on the same page" from "upstream page changed between reads". D4 says it "does not claim upstream changed", which is accurate, but it does not say the question is open. Add: "upstream revision between the two reads is unpinned; neither a change nor its absence is asserted."

### 5. LOW — no explicit guard against reading `remote_host` as remote runtime

S031 teaches "the upstream Ollama URL" and "upstream" recurs throughout. Nothing in the crosswalk or D4 states that a remote entry's `remote_host` is not evidence that the host is reachable, running, or holds the model loaded. `:52` covers loaded weights generically. Suggested sentence for "What cannot be concluded": "A remote entry's `remote_host` names a host; the opened page does not document that the host is reachable, running, or serving the model."

### 6. LOW — unverified precondition cited to S010

`served-identity-crosswalk.md:38` says "S010's cloud-model selection example requires a **signed-in local server**". No corpus file read in this pass quotes or locates that example; `SOURCES.md:21` S010 row does not mention cloud or sign-in. Not re-opened (static scope). L1 should locate the sentence in the pinned S010 source (`docs/api/openai-compatibility.mdx` @ `c1737589973d5cefd676ef16eb43835663540035`) or drop the attribution.

## Checked and not overclaimed

- `served-identity-crosswalk.md:9`, `:13`, `:84`: remote entries and "supersedes S011's local-residency implication" are scoped to inventory, not runtime.
- `runtime-health-surface-matrix.md:49-51` and `endpoint-identity.md:161-169`: remote/local statements are labeled `[INFERENCE]` or limited to "not a guarantee of loaded weights".
- No corpus text found asserting that a remote Ollama host is running or has the model loaded.
- `SOURCES.md:43` S031 tier A is limited to the documented inventory fields (`round-11.md:42-45`), not runtime behavior.

## Suggested wording for the crosswalk (for owner to apply)

- `:59` → "Upstream wording is unchanged: its ModelSummary still reads 'locally available'. S031 supersedes S011's local-residency implication at registry level only; the S011 row is not amended."
- `:38`, `:29`, `:52`, `:63` → prefix each S031-derived clause with `[INFERENCE]` and cite the field, e.g. "[INFERENCE] from `remote_model`/`remote_host` (S031): available inventory is not proof of local weights."

## L1 checks to run (named, not run here)

1. `grep -n '\[INFERENCE\]' corpus/knowledge/served-identity-crosswalk.md` — expect a label on each S031-derived clause at the cited lines.
2. `grep -n 'Name of the upstream model' corpus/SOURCES.md corpus/lessons/round-11*.md` — expect the quote attributed only to `remote_model`.
3. `grep -n 'locally available' corpus/SOURCES.md corpus/knowledge/served-identity-crosswalk.md` — confirm each remaining hit is labeled as upstream or historical.
4. Locate the S010 cloud/sign-in sentence in the pinned source (finding 6) before accepting `:38`.
5. Existing registry check: `scripts/sources-census.sh validate --root <repo root> kama` (verifier reported `kama ok` plus W04 for S031's duplicate URL; that output is expected and is not a waiver).

Tools installed or updated by this seat: none.
