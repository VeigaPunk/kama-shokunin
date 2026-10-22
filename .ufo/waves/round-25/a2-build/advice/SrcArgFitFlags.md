Verdict: Fresh pinned arg.cpp supports the flag-handler claim; draft a new queued row because existing rows cover duplicate options, not context and fit semantics.

## Behavior and findings

Seat: KamaR25a2.SrcArgFitFlags, fresh attempt-2 source-report seat. Claim served: C2, coverage. Supporting review axes: depth (exact handler locations), freshness (fresh source fetch), calibration (source limits). No numeric axis promotion is asserted.

All source line references below resolve in `.ufo/waves/round-25/a2-build/out/SrcArgFitFlags/arg.cpp-704366d76.raw`, freshly fetched at the pinned commit this round.

- Lines 1641–1651: `-c` / `--ctx-size` assigns `params.n_ctx`. Help describes zero as loading context from the model. Specifically when the handler receives zero, it also sets `params.fit_params_min_ctx = UINT32_MAX`; the adjacent comment says this disables context reduction in `llama_params_fit`. It does not set `params.fit_params = false`: disabling context reduction is not the same as disabling fit altogether.
- Lines 2881–2894: `-fit` / `--fit` exposes on/off, assigns the Boolean `params.fit_params` through truthy/falsey handling, and throws for an unknown value. The help describes adjusting unset arguments to fit device memory. Its displayed default is formatted from the incoming parameter; these lines alone do not establish that parameter's original default.
- Lines 2934–2940: `-fitc` / `--fit-ctx` describes a minimum context size for fit and assigns `params.fit_params_min_ctx`. This is the same field written by explicit `-c 0`; do not turn the latter handler observation into a promise that no other option or environment input can change it.
- Lines 1727–1734: `-kvu` / `--kv-unified`, and `-no-kvu` / `--no-kv-unified`, assign `params.kv_unified`. Help describes a single KV buffer shared across sequences, enabled by default when the slot count is automatic. This is a declaration here, not inspection of the eventual allocation.
- Lines 1405–1406 initialize server `params.n_parallel = -1`. Lines 2545–2556 define server `-np` / `--parallel` as the number of server slots, document `-1 = auto`, reject zero, and assign other values. This does not establish how many slots auto will eventually select.
- Adjacent context, lines 1652–1659: `--kv-unified-per-slot` assigns its parameter; help says that without `-c` the shared pool is sized to `n_parallel*N`. Allocation and later caps are not implemented in this handler.

## Existing registry scope

The regex search `arg\\.cpp|llama\\.cpp/common|common/arg` over `corpus/SOURCES.md` found existing source rows S054 at line 66 and S056 at line 68. Both were read in full this round. Their raw-source hash matches this fetch.

- S054 scope: repeated or unknown command-line flags.
- S056 scope: scalar versus append-style repeated port, host, API-key and speculative-type options; its teaches cell supersedes S054.

Neither scope covers the context-size sentinel, fit switch/minimum, shared-KV declaration, or server parallel-slot definition. A new scoped row is appropriate; it need not supersede S056. No change was made to SOURCES.md. The placeholder S1xx below is deliberately not a live registry ID; L1 allocates the next unused numeric ID and changes queued to mined only after a real citing path exists.

## Draft registry row (11 columns)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S1xx | llama.cpp context, fit and server slot option handlers @ 704366d76 — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp | code | A | parser assignments and help declarations for context size, fit, fit minimum, unified KV and server slot count at this commit; not allocated capacity or live serving | common/arg.cpp lines 1405–1406, 1641–1659, 1727–1734, 2545–2556, 2881–2894, 2934–2940 at 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad; raw sha256 bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d | Explicit -c 0 sets the fit context-reduction sentinel, not the fit Boolean; fit and its minimum have separate handlers, while unified KV and parallel options declare shared-buffer and server-slot semantics. | queued | 2026-10-22 | on-release | — |

## Gate record for L1

- Candidate: S1xx, proposed queued; not yet admitted or cited by a knowledge entry.
- Canonical URL: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp
- Actually fetched URL: https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp
- Access date: 2026-10-22.
- Located quote: common/arg.cpp:1647, comment in the context-size handler: “disable context reduction in llama_params_fit if the user explicitly requests the full context size:” (14 words).
- Supporting implementation: common/arg.cpp:1648, `params.fit_params_min_ctx = UINT32_MAX;` within the zero-value branch at 1646.
- SHA256: `bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d`.
- Source length observed: 4833 newline-terminated lines, from `wc -l` below.
- Bounded search: existing source registry, path regex above, 2026-10-22; identified and screened two existing registry rows; neither covers this scope. One fresh upstream file opened; one queued row drafted, no live registry inclusion or rejection performed. Stop rationale: all requested option definitions located in the pinned file.
- Gate execution: none. This is source-opening material for L1's Gate section, not an executed verdict script, a non-author spot-check, or evidence that C2's live observation target passed.

## Commands and outcomes

Exact fetch/hash/length command executed:

```sh
mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/SrcArgFitFlags && curl -fsSL 'https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp' -o /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/SrcArgFitFlags/arg.cpp-704366d76.raw && sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/SrcArgFitFlags/arg.cpp-704366d76.raw && wc -l /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/SrcArgFitFlags/arg.cpp-704366d76.raw
```

Observed output:

```text
bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/SrcArgFitFlags/arg.cpp-704366d76.raw
4833 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/SrcArgFitFlags/arg.cpp-704366d76.raw
```

Exit code: [INFERENCE] 0 from the successful tool return and completed `&&` chain; the tool response did not expose a separate numeric exit-code field, and no explicit `$?` receipt was captured. The fetch was not rerun to decorate this report.

One exploratory shell read also executed:

```sh
cut -c1-80 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/SrcArgFitFlags/arg.cpp-704366d76.raw | sed -n '1630,1660p'
```

It displayed the context handler with long lines cut at 80 characters; exit code was not explicitly captured ([INFERENCE] 0 from normal tool completion). These cut bytes are not quotation evidence: complete ranges were subsequently opened with the read tool. This shell paging was unnecessary; the complete read-tool output is the source for the findings.

Native grep/read operations have no shell exit code to record. An initial option search with pattern `"ctx-size"|"ctx_size"|"fit"|"fit-ctx"|"kv-unified"|"parallel"` returned `No matches found` because those quoted strings omitted flag prefixes. Follow-up searches `fit` and `kv-unified|parallel` located the requested handlers, subsequently opened in full. No no-match result is used as absence evidence about the implementation.

## Does not establish / out of scope

- Actual allocated KV-pool size, padding, stream division, per-slot caps, or endpoint values for any registered cell.
- That fit raises an unset split context to training context times stream count; that requires the fit implementation and observed X1/X3 evidence, not these handlers.
- The initial numeric fit-context minimum or initial fit Boolean from parameter definitions outside the opened handlers.
- A permanent no-reduction guarantee under every subsequent option/environment assignment; --fit-ctx writes the same field.
- Auto selecting four server slots, inference-time KV allocation, or a binary-to-source identity proof.
- HTTP surfaces' ability or inability to reveal pool sharing, full-context concurrent-load success/failure, request error text, or L1–L3 outcomes.
- Model quality, production consumer health, other engines/releases, or ratification of the fixture scope.

Unrun is unverified: no llama-server child was started; no registered consumer was probed; no C1/C2 counter, tests, build, formatter, mutation grid, judge, commit, push, publish or deploy action was run. No tools were installed or updated.

## Instruction conflict record

Verbatim general skill text from MISSION.md: “Commit inside the owning repo then `git push`. Reports: `.ufo/reports/round-<N>/<lane>.md` on the main repo, commit + push.”

Verbatim scoped seat instruction: “Do not edit product code, judge, commit, push, publish, deploy, or invoke another runtime.”

The canonical scoped assignment was followed: this leaf seat only drafts source advice and preserves its downloaded source; it does not execute the general L1 round-closing actions. No round admission or axis judgment is asserted.

## Touched surfaces and artifact paths

Every file written by this seat (paths relative to the lane):

1. `.ufo/waves/round-25/a2-build/out/SrcArgFitFlags/arg.cpp-704366d76.raw` — fresh upstream source bytes, not product code edits.
2. `.ufo/waves/round-25/a2-build/advice/SrcArgFitFlags.md` — this report, including the draft registry row and Gate record.

Production files, SOURCES.md, Git index, jj state, sibling lanes and operator configuration were not written. Preregistration, both amendments, count-c2.py, pilot and attempt-1 disposition were read as required; attempt-1 partial source-seat artifacts were not reused.
