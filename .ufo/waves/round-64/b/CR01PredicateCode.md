# CR01PredicateCode — C1 freeze fidelity (operability), wave b

Scope: freeze predicate C1-r64 (`controls/freeze.txt`) vs `tools/round64-c1-counter.py` docstring vs enforced code, at tip f6a4ea9a8b5a876d685b08e7e582ec0723412a4a (clone at my scratch, HEAD verified). Findings only; no verdict on the claim. No commit, no lane edit, no tool installed (python3, git, `strings` from binutils already present; the pinned llama-server b11755 was used as-is, its sha matched `pick_server`).

## 1. Sentence vs docstring

- Predicate text ("C1-r64:", freeze.txt) is identical to docstring lines 6-25 after whitespace normalisation. The only difference is a hyphen line-wrap ("request-" / "plane", docstring lines 8-9). Script: `out/CR01PredicateCode/cmp.py`, output `00-freeze-vs-docstring.out`.
- Docstring lines 27-28 say "The counter never trusts receipt-claimed results". Not true in code: `hold_released` (615-616), `teardown_clean`/`teardown_port_closed` (616-618), `verdict` (683), `listener_owned` (686-687) and `listener_holders_pinned` (608-613) are pass criteria read from receipt fields. The counter-observed teardown (731-733, 918-928) is the only teardown evidence it does not take from the receipt.

## 2. Clause-by-clause status

Status: E = enforced as stated; P = partial; U = unenforced. Lines are in `tools/round64-c1-counter.py` unless noted.

| # | Sentence clause | Enforcing lines | Status |
|---|---|---|---|
| 1 | "byte-pinned tools/kama-completion-live.py" | tip blob read and written as-is: 1420-1428 (`tool_files`), 1578 (relabel), 1641/1686 (forged copies). No digest of the tool anywhere (grep: no sha constant for it). | U |
| 2 | "(schema kama-completion-live/v3)" | receipt-claimed string: 509. Holder bookkeeping that proves v3 behaviour: 608-613, 723-730 (`bind_claim`). Relabel control 1664-1706. | P |
| 3 | "runs one counter-opened hold-mode lifecycle" | counter creates hold dir 862-865, spawns tool with `--hold-dir` 872-878, observes hold.json 883-910. "one" and "this run" not checked: no freshness of receipt captures (see 4B). | P |
| 4 | "on the pinned llama.cpp fixture" | `SERVER_SHA` 49, `MODEL_SHA` 48, `pick_server` 1443-1451, `server_digest` 605-607 (receipt path), `model_digest` 602-604 (receipt path), argv model hash 432. | E |
| 5 | "whose receipt the counter re-derives from captured bytes" | `grade` 489-628; body sha re-sealed check 498-507; stored-vs-recomputed consistency 621-627. | E |
| 6 | "from procfs and its own code alone, loading nothing from the tip" | counter imports stdlib only 32-46; procfs readers 222-365. Tip-sourced inputs: forge patch texts 1168-1170, tool 1420, dependency 1429-1434, registry 1435-1439; `patch` binary from PATH 1156. | P (forgery definitions are read from the tip) |
| 7 | "binds the process that answers ... every holder of the run-port listener is the hold pid" | listeners 238-255; holder set via fd readlink 258-286; `bind_listener` 410-411; `bind_holders` 413-416; set stable across raw_a/raw_b 721-722; hold_port == port 416, 714-716. Other-uid holders skipped silently: 270-276 (PermissionError + st_uid != me -> no record). Own-uid unreadable pids started before the tool are dropped from `unreadable_own` (382-384) and `unreadable_old` (385) is never graded. | P |
| 8 | "its /proc/<pid>/exe re-hashes to the pinned llama-server digest at the server path the counter chose" | exe readlink + sha 343-346; `bind_exe` 417-419 (exe == counter's `sp`, sha == SERVER_SHA); `sp` chosen by counter 1443-1451, 1465. | E |
| 9 | "its argv ... the pinned set" | `argv_ok` 421-433: argv[0] realpath, `--port`, `--host`, `--alias`, `--model` (+ model sha). Any other argv element accepted. | P |
| 10 | "initial environment ... the pinned set" | `bind_env` 434-437: denylist `LD_*` and `GLIBC_TUNABLES` only. No allowlist, no pinned set. | P |
| 11 | "mapped files ... the pinned set" | `maps_ok` 439-463: deleted/memfd rejected 445-446; server-dir files must be in LIBS with matching sha 456-459; model 454-455; any other path under non-system prefix rejected 461. `SYSTEM_PREFIXES` 451-452 accepted unhashed. | P |
| 12 | "it is a descendant of the tool process" | ppid chain (8 levels) 299-308; `bind_ancestry` 465-466. | E |
| 13 | "started after the tool did" | `hold_fresh` start ticks >= tool ticks 472-473 (non-strict; equal ticks pass). `tool_ticks` 879. | P |
| 14 | "the hold.json is fresh" | `hold_fresh` 470-471 is only `mtime > t0`; upper bound absent. Schema check 474. | P |
| 15 | "teardown (the holder gone, the port closed) is observed by the counter after the counter's own release" | release written 916; poll loop 918-928; `pid_gone` 843-853 (zombie counts as gone); port via `listeners` 924; `teardown_observed` 731-733. | E |
| 16 | "the held child's answers to two outside probes drawn at random per run (prompt length and n_predict)" | rng seeded from urandom 1481; draws k in [2,24], n in [3,9], distinct pairs 751-764; probes sent to held child 898-901; distinct pair check 702-705; probe nonce check 1530-1532. | E |
| 17 | "agree with a reference pinned server the counter itself starts" | `reference_run` 806-840 (counter's pinned server, own port); comparison `probe_fails` 631-674 (`live_ref_text` 665-668, `live_ref_usage` 669-673). | E |
| 18 | "all 76 targeted controls ... each rejected by the check each names" | `EXPECT_FAMILIES` 58-66 (sums to 76: 41 + 35); `build_controls` 1225-1414 (41 items); `run_controls` 1551-1706 (plan fakes 1592-1621, forged tools 1622-1663, relabel 1664-1706); `is_hit` 1218-1222; `credit` 1555-1568; family equality 1509. | P (see 3 and 4J) |
| 19 | "family by family at the declared counts" | 1509, 1512-1519. Baseline prints `families_exact=1`. | E |
| 20 | caps "5 failing checks; 30 for the envelope break; 14 for a patched-tool forgery" | `MAX_COLLATERAL` 55 (default in `is_hit`), `ENVELOPE_CAP` 56 used 1243, `SCENARIO_CAP` 57 used 1660 (forge) and 1700 (relabel). | E |
| 21 | "a fake-tool scenario holding a genuine receipt copy must in addition show no receipt-level failure" | `clean_receipt` 1557-1562, applied at 1618 (plan fakes). | E |
| 22 | plan-fake cap (not stated in freeze) | `credit(..., 99, ..., clean_receipt=True)` 1618: cap 99 = unbounded. | U (sentence silent; code has no cap) |
| 23 | "the counter's own evaluator refuses all 3 planted wrong-reason controls, errors=0" | `eval_selftest_run` 1537-1548; required `st == 3` 1506, 1511; `errors` 1511. | P (see 4K) |
| 24 | "exit 0 iff met" | 1510-1511, 1522. | E |

## 3. Enforced by code, not stated by the sentence

- `bind_stable` 721-722 (raw_a vs raw_b holder signatures).
- `bind_claim` 723-730 (receipt `listener_holders` must equal the counter's own holder view).
- `hold_schema == kama-completion-hold/v1` 474; `hold_port == receipt port` 714-716.
- Model file digest via argv 431-432 and 709-710.
- `live_fp_capture` 700-701 (probe fingerprint == capture fingerprint), `live_nonce` 1530-1532 (probe nonce echoed in prompts).
- `unreadable_own` fail-closed 382-384, 415.
- Receipt content checks (request binding 581-584, determinism 590-594, tokenize 572-575, bad-request 597-599, timings 562-568, teardown return codes 616-617). Covered only generically by "re-derives from captured bytes".

## 4. Findings with evidence

A. **Tool bytes are not pinned (clause 1, U).** No digest of `tools/kama-completion-live.py` appears in the counter. The counter runs whatever blob the tip holds (1420-1428). Forged patches are also read from the tip (1168-1170) without a digest. Fix: add `TOOL_SHA` (and sha constants for the two patch files) or drop "byte-pinned" from the sentence by amendment.

B. **Receipt freshness is not bound to this run (clauses 3, 5; not a stated kill-rule, but a gap in "runs one ... lifecycle").** Harness `replay.py` (out/03): a fake that spawns the genuine pinned server, holds it, and writes a receipt copied from an earlier genuine run with only the nonce changed returns `met=True`, `fails=[]`. The replayed capture has the same completion `id` and `created` as the genuine run. The live probes do touch the new child, so the process-binding clauses hold; what is missing is any check that the captures were produced in this run (no comparison of `created` with `t0_ns` at 871, no per-run capture nonce). Smallest fix: require `created >= floor(t0_ns/1e9)` and echo a per-run capture nonce in the completion request body.

C. **"every holder" is only enforced for readable same-uid tables (clause 7, P).** `holder_pids` 270-276 silently skips other-uid pids whose fd table is unreadable. `unreadable_old` (385) is never read by `grade_binding`. Not exercised here (needs a second uid). Fix: count any unreadable pid that started after the tool, regardless of uid, as unreadable and fail closed.

D. **argv is not the pinned set (clause 9, P).** `argv_ok` (421-433) ignores extra flags. Offline (out/02): `cmdline + ['--lora', '/tmp/x.gguf']` -> `bind_argv=True`. Fix: exact argv set equality with the flag set the tool emits (tool 300-304: `--model --alias --port --host -c -t`).

E. **Initial environment is a denylist, not a pinned set (clause 10, P).** `bind_env` 434-437 rejects only `LD_*` and `GLIBC_TUNABLES`. Offline (out/02): `LLAMA_ARG_CHAT_TEMPLATE_FILE` in environ -> `bind_env=True`. The pinned libllama-common carries 155 `LLAMA_ARG_*` names (`strings`), including `LLAMA_ARG_API_KEY_FILE` and `LLAMA_ARG_SPEC_DRAFT_MODEL`, so env can change serving config with no argv trace. Note the counter's own runs are narrower in practice: `witness_run` filters the tool env to 5 keys (868-869, `_TOOL_ENV_KEYS` 148), and the tool's allowlist (kama-completion-live.py 322-324) admits `LD_LIBRARY_PATH`, `LLAMA_ARG_THREADS`, `XDG_CACHE_HOME`, none of which the counter passes. The check is still not written. Fix: exact `environ_keys` equality with the filtered set.

F. **Mapped files: system libraries are unhashed (clause 11, P).** Offline (out/02): a mapping `/usr/lib/libevil.so` with `sha256=None` -> `bind_maps=True` (451-452). Fix: compare the held child's mapped-path set to the set from the counter's own reference server (which it already starts, 806-840); a preload dropped under /usr/lib then fails.

G. **"started after" is non-strict (clause 13, P).** `start_ticks >= tool_ticks` (472-473). Offline (out/02): holder with `start_ticks == tool_start_ticks` -> `hold_fresh=True`.

H. **"fresh" has no upper bound (clause 14, P).** `mt > t0` (470-471). Live (out/05, `futlive.py`): a genuine child holder with `hold.json` mtime set +3600 s in the future -> `met=True`, `fails=[]`. Impact is limited because holder/ancestry checks still bind the process; the freshness wording still overstates. Fix: `t0 < mt <= t0 + hold_timeout + slack`.

I. **"loading nothing from the tip" (clause 6, P).** Forge patches (1168-1170) are tip text applied with the system `patch` (1156). A tip that edits those patch files changes the forgeries the counter scores. Fix: sha-pin the patch files (see A).

J. **Two of the 76 controls reject for a reason other than the freshness check (clause 18, P).** `stalehold` (`stale_old`, `stale_future`, 1595-1596) write a hold.json whose port and pid are closed. `hold_fresh` is False only because `hs` is empty (`bind_holders`, `bind_listener` also fail). Live output (out/04): both fail sets contain `hold_fresh` alongside 21 other checks; raw_a holders = 0. A future-dated mtime is not rejected by freshness at all (H). Fix: make the stale controls keep a live holder so that `hold_fresh` is the only freshness failure, and add the upper bound.

K. **The 3 self-test items (clause 23, P).** `eval_selftest_run` (1537-1548):
   - item 1 (stale nonce, expect `live_ptok`): refused, correct;
   - item 2 (envelope break, expect `completion_envelope`): this is a right-reason control, refused only because its re-score has 26 failing checks against the default cap 5. Out/06: `is_hit(cap=5)=False`, `is_hit(cap=30)=True`. It is not a wrong-reason refusal, so the label in the sentence is inaccurate;
   - item 3 (genuine receipt, expect `nonce_match`): refused, correct.
   The self-test is one-sided: with `score` replaced by a constant `met=True`, it returns `3`, i.e. 3/3 (out/06). The family table (1509) is what catches an evaluator that credits nothing. Fix: point item 2 at `ENVELOPE_CAP`, add a positive control (a no-op mutation must stay met), and amend the sentence.

## 5. Operability defect in the counter (within the judged axis)

Re-running `round64-c1-counter.py` on the same `--work` (not a fresh dir) gives:

```
tool_present=1 live_ok=1/1 controls_targeted=69/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[... canned=0/1 detach=0/1 pathcopy=0/1 preload=0/1 proxy=0/1 stalehold=0/2 ...]
error: fake detach: no receipt/witness ['tool exited before hold.json']   (and 6 more fake errors)
```

Cause: `witness_run` (862-865) reuses `work/<label>/hold`; a `release` file left by the previous run is never removed. The planted fakes call `hold_and_release` (980-988), which returns at once, unlinks `hold.json`, and the counter never sees it. The tip tool clears the witness dir (`prepare_witness_dir`, `kama-llamacpp-live.py` 290-304, called at `kama-completion-live.py` 309-311), so the live row still passes. This fails closed (met=False), so no false pass, but the verdict is misattributed. The C2 freeze requires work-reuse refusal; the C1 counter has none. Fix: clear `hold/release` and `hold/hold.json` in `witness_run` before launch, or refuse a non-empty `--work` (needs a numbered AMENDMENT before the next wave).

## 6. Smallest corrections (advisory; each instrument change is a numbered AMENDMENT before wave f)

1. Tool/patch digests (A, I).
2. Capture freshness vs `t0_ns` plus per-run capture nonce (B).
3. Upper bound on hold mtime; `>=` to `>` for start ticks (G, H).
4. Exact argv and environ key sets; mapped-path set from the reference server (D, E, F).
5. Count unreadable other-uid holders (C).
6. Isolate freshness in stale controls; fix item 2 of the self-test and the docstring "never trusts" sentence (J, K, §1).
7. Clear stale hold state in `witness_run` (§5).
8. Cap for plan fakes (1618 uses 99, unstated in the freeze): state a cap in the freeze, or use `SCENARIO_CAP` (14).

## 7. Evidence (out dir `.ufo/waves/round-64/b/out/CR01PredicateCode/`)

- `00-freeze-vs-docstring.out`, `cmp.py`: sentence vs docstring.
- `01-baseline-counter.out`: counter at f6a4ea9a, met=True.
- `02-offline-binding.out`, `offline.py`: clauses D, E, F, G, H-offline, `hold_fresh` semantics.
- `03-replay-capture.out`, `replay.py`, `receipt`-level replay (B).
- `04-stale-holds.out`, `stale.py`: stalehold rejection reasons (J).
- `05-future-hold-live.out`, `futlive.py`: future mtime with a live holder (H).
- `06-selftest.out`, `selftest.py`: evaluator self-test sensitivity (K).
- The reuse run (§5) output is archived as `07-workdir-reuse.out`.

Counter line (baseline, tip f6a4ea9a8b5a876d685b08e7e582ec0723412a4a):

```
tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True
```
