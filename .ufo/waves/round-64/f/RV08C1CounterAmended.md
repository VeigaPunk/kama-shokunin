# RV08C1CounterAmended — amended C1 counter review

Scope: operability, with calibration of the instrument's own claims. Reviewed `tools/round64-c1-counter.py` at `23b3fdb1a925129a9961cf551f6d40bf251602cb`, against freeze `f6a4ea9a`, frozen controls including amendments 1/1a/1b, and wave-b `RV02CounterCode` D1–D12. All line references below are to this candidate's counter. Advisory findings only; no claim verdict, admission, source edits, or commits.

Evidence directory: `.ufo/waves/round-64/f/out/RV08C1CounterAmended/` (called `out/` below). `counter.diff` preserves the requested exact git diff. The `xd://lsp` device was unavailable (`No such tool`), so semantic definition/references/diagnostics could not be obtained; text search and direct source inspection are fallback evidence, not LSP proof. Read godspeed, operator rules, and self-evaluation skill. No tools installed or updated.

## Findings, severity order

### High — newly introduced: cleanup can kill a server the counter did not start

Lines 1045–1052 trust the tool's hold document to choose a port, collect **every** holder of that port, and add them to `seen`. Lines 1093–1097 kill these holders before scoring admission/ownership. `kill_if_same` (989–996) checks PID identity, not whether this counter started or owns that process. A forged tool can name an existing listener and its PID; failing `bind_ancestry` later does not undo the signal. This conflicts with the host rule never to kill a process not started by the seat. It also means even an incorrect hold port can be destructive.

Safe fault injection (`out/probes.py`, `out/probes.stdout`) returns an unrelated holder `{pid:999991,start_ticks:456}` from collection under tool PID 999990. `witness_run` invokes cleanup on that unrelated holder: `call(999991, 456)`. All process launch, HTTP, holder collection, and signals in this probe were mocked; no real listener was contacted or signalled. Real foreign-server killing was deliberately not tested. Recommendation: keep a counter-owned process identity/containment boundary for cleanup; an observed listener and a matching start tick are not ownership authorization.

### Medium — D5 not fully fixed: detached children before the first usable hold remain untracked

`start_new_session=True` (1027) and the `finally` (1093–1105) repair ordinary group-member/observed-holder leaks. But `seen` starts empty (1030) and is populated only after a parseable, integer-port hold document (1035–1057). A forger that starts a child in another session and never publishes a valid hold leaves that child outside both cleanup mechanisms. The no-hold timeout still reaches only the tool's group. The implementation's statement “every holder it saw” is accurate; it does not repair all of RV02 D5's no-hold leak class. Static path evidence only; I did not deliberately leak a detached server. Recommendation: establish owned descendant containment at launch, rather than discovering cleanup targets solely from a later untrusted hold.

### Medium — D12 not fully fixed: the first stat read still conflates unreadable and gone

`stat_fields` returns `(None,None)` for **every** `OSError`, parse error, and missing process (319–326). `pid_gone` immediately returns True when `pp is None` (975–977), before its new fail-closed branches (978–986). The teardown loop (1077–1083) can therefore claim disappearance for a still-live but unreadable holder when its listener is closed. Port closure is not process exit. Safe fault injection: `stat_fields -> (None,None)` makes `pid_gone(999999,123) -> True` (`out/probes.stdout`). Recommendation: distinguish ENOENT/confirmed disappearance from unknown/unreadable status; retain unknown as not observed gone.

### Medium — D6 partially fixed: unreadability is not consistently fail-closed

Any-UID `listdir('/proc/PID/fd')` PermissionError is now recorded and retried (270–316), fixing the original explicit other-UID skip. However, PermissionError from individual fd `readlink`s is swallowed (287–292); a readable directory with unreadable socket links becomes “readable, does not hold.” Separately, `collect` excludes a persistently unreadable PID if its start ticks cannot be obtained (452–455): `(None or 0) >= tool_ticks` is false for a normal positive tool start. Such a PID is counted in `unreadable_old` but not graded. Safe probes produce `(set(),set())` for denied fd links, and `unreadable_own=[]`, `unreadable_old=1` for an unreadable fd/stat pair. The disclosed pre-existing unreadable-holder exemption is intentional; unknown age is not proof of pre-existence. No full live acceptance bypass was demonstrated. Recommendation: preserve unknown status through both reads and age classification.

### Low — new identity check inherits path-only mapping deduplication

`read_maps` discards later mappings sharing a pathname before retaining device/inode (354–366). Thus `file_set` (373–376) and the new `bind_ref_files` comparison (835–840) do not actually compare every distinct `(path,device,inode)` mapping. A synthetic maps input with `/usr/lib/example.so` at inode 11 and inode 22 returns only inode 11 (`out/probes.stdout`). This is a concrete blind spot in the new identity-set check, not a demonstrated live forgery. Recommendation: deduplicate complete mapping identities, not pathname alone.

## D1–D12 disposition

| Wave-b item | Disposition | Candidate evidence |
|---|---|---|
| D1 receipt not linked to request/answer | **Fixed for reported defect** | Counter draws/passes request at 875–889, 1022–1024; `receipt_req`, text and usage equality at 800–826; controls at 1693–1723; replay at 2001–2017. The original fabricated-text/replay mechanism is now checked. |
| D2 argv/env partial checks | **Fixed** | Full argv equality at 491–496 and 553–557; environment key/value allowlist at 498–503, expected values at 449–450. Missing allowed env keys remain permitted, consistent with “holds only” wording. Extra flags/model aliases/env overrides have controls 1621–1638. |
| D3 undeclared fake cap 99 | **Fixed by disclosed contract amendment, not by lowering cap** | Call remains 99 at 1998; rule at 1769–1778 requires a clean receipt including new receipt-bind checks. Freeze amendment 1 explicitly removes the fake-tool cap. Original cap-5 interpretation was not restored. |
| D4 vacuous envelope selftest | **Fixed** | Eight cases at 1894–1927; the default-cap must-not-credit envelope remains, but there is now a separate must-credit envelope case at `ENVELOPE_CAP` (1914–1915). Clean-receipt veto and exact-family gate tested too. |
| D5 failure-path leaks | **Not fully fixed** | Finally/group cleanup at 1093–1105 fixes observed holders and same-group children; detached/unobserved no-hold case remains as above. No observed leak in my ordinary run. |
| D6 other-UID unreadability skipped | **Not fully fixed** | Explicit UID skip removed (270–316); remaining per-link and unknown-start-time gaps at 287–292, 452–455 above. |
| D7 blanket system-library exemption | **Not fixed as a hashing defect; substantially mitigated** | `maps_ok` still exempts system prefixes (524–525), as amendment 1 acknowledges. New reference identity comparison (835–840) rejects extra/different mapped files, but does not hash system-library content, and has the mapping-dedup limitation above. |
| D8 future hold mtime | **Fixed with explicit one-second tolerance** | Upper bound `mt <= collected_ns + 1_000_000_000` at 544–548; ten-second-future control at 1663–1664. Not strict rejection of every future timestamp. |
| D9 path-keyed hash cache | **Fixed** | 180–191 hashes afresh on every call; `cache` accepted but ignored. `_HASH_CACHE` declaration remains unused, not a scoring dependency. |
| D10 fuzz-tolerant patching | **Fixed for fuzz; offsets deliberately allowed** | Dry run plus real run both reject stdout containing `fuzz` (1334–1341). Missing patches now return explicit errors (1394–1399). Unlike RV02's suggested strict-offset policy, offsets remain documented/allowed (1325). |
| D11 reused work breaks fakes | **Fixed** | Nonempty work refused before extraction/scoring (1787–1795); new scenario directory creation also refuses reuse (1007–1010). My normal run started with a nonexistent work path and succeeded; subsequent reuse returned 2 before running a server. |
| D12 unreadable status means gone | **Not fully fixed** | Unknown recorded ticks, later read exceptions, and empty holder list now fail closed (978–986, 1077); first `stat_fields` failure still returns gone (975–977), above. |

## New-code invariants and residual risk

- `scenario()` (1946–1968) uses the same witness/scoring route as genuine execution and passes the actual run nonce and request to `score_run`; missing receipt/witness increments the family total without credit. Exceptions from witness execution add `errors`; scoring exceptions outside that try can still terminate with a traceback rather than the advertised summary line. This is a reporting gap, not silent success.
- `credit_rule` (1769–1778) includes named-check, rejection, collateral cap, and clean-receipt veto. Baseline success gates all controls (1846–1850); exact dictionaries gate family saturation (1764–1766). The observed 91/91 is saturation of the declared table, not coverage of all adversarial processes or schedules.
- `score_run` (1869–1891) saves/restores NONCE and TOOL_REQ in `finally`; safe injected scorer exception restored `outer` and `{'prompt':'outer'}`. Changes happen before the try, but the supplied witness requests on canonical routes are internal dictionaries. No aliasing defect found on those routes.
- `REF_FILES` is filled only after a healthy reference/probe sequence (954–958), copied into the baseline witness (1841), then reused from that witness in scenarios (1966). The replay reference changes the global but not the saved baseline witness. A failed reference leaves stale global state; canonical callers require valid result lengths/texts before proceeding, so I found no fail-open through that stale state. Concurrent/reentrant use is not supported or exercised.
- Initial draw requires three distinct nonempty answers, at most eight attempts (1819–1828); replay similarly demands a different nonempty answer, at most eight attempts (2003–2020). Exhaustion records an error rather than credit. This avoids the known identical-text control accident, but is probabilistic bounded rejection, not proof that honest runs cannot flake.
- New `killpg` runs after `proc.wait` may already have reaped the leader (1084–1097), without group-identity revalidation. PID/group reuse is a residual race, not a measured wrong kill. Identity check followed by `os.kill` in `kill_if_same` also has a check/signal race; no pidfd is held.
- D7, initial-environment-only visibility, writes to live memory, pre-existing unreadable holders, and post-release holders remain outside strong assurance, as disclosed by the freeze. The tool's own holder bookkeeping is not established as necessary by the amended claim.
- No resume path exists in this scoped counter; resume continuity is not an exercised contract here.

## Required live run and cleanup evidence

Command (cwd was my scratch, not fleet root): `python3 /fast/scratch/hyaku/kama-r64/f/RV08C1CounterAmended/clone/tools/round64-c1-counter.py --repo /fast/scratch/hyaku/kama-r64/f/RV08C1CounterAmended/clone --tip 23b3fdb1a925129a9961cf551f6d40bf251602cb --work /fast/scratch/hyaku/kama-r64/f/RV08C1CounterAmended/work-1`.

One unmodified counter run: exit 0, 91/91 controls, evaluator 8/8, errors 0. No flake occurred, so no live rerun. No mutants were created or scored by this review seat; the safe probes are fault injections of individual functions, not KILLED/SURVIVED mutant results.

`pgrep -af llama-server`: before **2** rows, after **1** row (`out/pgrep-before.txt`, `out/pgrep-after.txt`). Before: PIDs 1746854 and 3262613. After: only PID 3262613, unchanged argv. PID 1746854 pre-existed this run; its disappearance is not attributed to my run. No new surviving llama-server was visible after the run. Captured receipt child-PID existence checks are in `out/recorded-child-status.json`; receipt files are preserved under `out/receipts/`. This does not prove the exceptional detached/no-hold cleanup path safe.

Reused-work result: exit 2; stderr `work-reused`; stdout `tool_present=0 live_ok=0/1 controls_targeted=0/0 work_reused=1 errors=1 met=False` (`out/reuse.*`). Safe probes exited 0 (`out/probes.stdout`, empty stderr). No foreign listeners or processes were intentionally touched by the probes. Scratch removed after preserving evidence.

Verification gaps: one honest run, not a stability sample; no real other-UID/ptrace/detached-no-hold exploit, no live double-inode mapping experiment, no PID-reuse stress, no full counter acceptance demonstration for the remaining gaps. Read-only source review and mocked fault evidence are explicitly distinguished from runtime acceptance claims. No C2 or other runtime was invoked.

Self-evaluation: accuracy 4 (fault probes, not end-to-end exploits, for new findings); completeness 4 (all D-items/new targets covered, exceptional leak path not run); clarity 4 (disposition table separates code repair from amendment); actionability 4 (precise locations and containment recommendations, no source fix authorized); conciseness 4 (full requested review retained). Overall 4.0. Highest-impact improvement for a future authorized exercise: isolated owned-listener fixture for the cleanup-authorization path; never use a standing host listener.

## Unmodified counter output (exit 0)

tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True families[bind=30/30 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 receiptbind=4/4 relabel=1/1 replay=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
