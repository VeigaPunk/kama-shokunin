# A09FalseGreenReading — round-60 C1 falsification: false-green paths in `tools/kama-ollama-live.py`

Seat: leaf member, wave w1, axes operability (advisory). Method: line-by-line reading of all 436 lines of
`tools/kama-ollama-live.py` at the frozen base, plus six patched **copies** run in seat scratch
(`/fast/scratch/hyaku/kama-r60/A09FalseGreenReading`, removed before this report was finalized; receipts and
copies preserved under `repro/`). The lane's own independent verifier (`round60-c1-counter.py::verify`, invoked
read-only via importlib) is used as the second layer on every repro, so each finding states whether it survives
end-to-end. Baseline honest run first; every verdict below names the attacked clause, the exact command, the
observed output and the exit code. No lane source was edited; no installs were needed (python3 stdlib only;
tooling-directive record: nothing installed or upgraded this seat).

Baseline (real tool, unpatched): `python3 tools/kama-ollama-live.py --work $S/work0 --nonce a09base001 --out …/baseline-receipt.json`
→ exit 0, verdict MODEL_OK, all 16 checks true, teardown `{returncode: 0, sigkill_needed: false, port_closed: true}`, elapsed 1.59 s.

---

## Confirmed holes

### H1 (highest) — a server death inside the post-capture window reaches `finish('MODEL_OK', 0)`; end-to-end when the death is a SIGTERM/exit-0
**Attacked clause:** teardown check detail `tools/kama-ollama-live.py:424-425` — "SIGTERM ended the child without SIGKILL and the port refuses connections" — and the C1 sentence "tears the child down".

**Mechanism (lines 395-432):** after the `ps-after` capture the try block makes **no further contact with the server**: `run_evidence` (line 200) replays captured files, and `check('evidence-after-load')` (line 400) grades only those files. A child death anywhere in that window (measured: the `run_evidence` subprocess alone runs **0.034 s**, so the unprotected window is tens of ms unpatched) or in the microsecond between try-end and `finally` is invisible: every check stays true, `rc_fail` stays False, the finally's `os.killpg(SIGTERM)` (line 407) hits a corpse (no-op on the zombie's group), `proc.wait` returns the death code, `killed=False`, `port_closed=True` → the teardown check passes **vacuously** (it never inspects `returncode` or liveness) → MODEL_OK, exit 0.

**Reproducers** (patched copy `repro/p1.py`: identical logic + child-pid recorder + a 20 s sleep inserted immediately after the line-400 check to widen the window; the driver kills only the PID the run itself recorded):
- p1a, external `kill -TERM <childpid>` during the window: `tool_exit=0`, verdict **MODEL_OK**, all checks true, teardown `{returncode: 0, sigkill_needed: false, port_closed: true}` — byte-shape identical to the honest teardown — and the lane counter **accepts** the receipt: `verify_bad=[] accepted=true`. **End-to-end false green**: the server was killed externally and never torn down by the tool, yet the C1 verifier passes the receipt. Ollama exits 0 on SIGTERM (the honest baseline's own `returncode: 0` shows it), so the counter's `td.get("returncode") not in (0, -15)` clause cannot distinguish this from a tool teardown.
- p1b, external `kill -9` during the window: `tool_exit=0`, verdict **MODEL_OK**, all checks true (teardown check passed despite `returncode: -9` recorded in the same receipt); the counter **rejects**: `verify_bad=["teardown"]`. So the counter backstops abnormal deaths but not clean ones.

**Fix shape (not applied):** make the teardown check require `returncode == 0` and add one final liveness probe (e.g. `GET /api/version`) after the last evidence check and before the finally, so a mid-window death becomes a fault; optionally assert `proc.poll() is None` at try end.

### H2 — the imported model is never tied back to the pinned GGUF at tool level (post-digest swap undetected)
**Attacked clause:** C1 sentence "imports the pinned fixture GGUF under a caller nonce"; `model-digest` (line 272) verifies the **source file** only; `tags-lists-model` (line 352) accepts any 64-hex digest; `ps-lists-loaded` (line 397) compares ps-digest to tag-digest (self-consistent pair). Nothing compares the imported blob/manifest to `pin['model_sha256']`. Asymmetry: the **binary** has a post-start identity check (`running-exe-digest`, line 314) but the **model** has no post-import identity check.

**Repro** (`repro/p2.py`: one line inserted after the model-digest early-return reassigning `gguf` to `mymod.gguf` = the pinned fixture + 3 appended bytes, sha256 `9c5241b4ff65a63eca4e8cf6c530a44f14fd2819c576c1a69298ef1158efbc53` ≠ pin `270cba1b…`; this deterministically simulates a swap in the seconds-wide window between line 272 and `ollama create` at line 339):
`A09_WRONG_GGUF=$S/gguf/mymod.gguf python3 $S/copy/p2.py --work $S/work2 --nonce a09p2swap01 …` → exit 0, verdict **MODEL_OK**, zero failed checks, imported manifest digest `584bcf43c49cab3c02e55c786fa89357d0f2c472de333e4eba59631ecff25dd5` (honest run: `8cf91c71…`) — a different model, fully green at tool level. The lane counter **rejects**: `verify_bad=["manifest-layer","blob-missing"]` (its work-dir re-derivation requires the manifest to reference `sha256:270cba1b…` and that blob to exist and hash correctly). **Backstopped end-to-end**, but the tool's own MODEL_OK verdict is wrong.

**Fix shape:** after create, assert the manifest's GGUF layer digest equals `pin['model_sha256']` and hash `work/models/blobs/sha256-<that digest>` against the pin (mirroring the counter's clauses 1:1). Note the honest tags digest is the *manifest* digest (`8cf91c71…`), not the GGUF digest — the tie must go through the manifest/blob, not `tags.digest`.

### H3 — `/api/show` (and empty-store `/v1/models`) are captured but never graded: an error surface is compatible with MODEL_OK **and** counter acceptance
**Attacked clause:** docstring lines 9-10 "captures the HTTP surfaces (… `/api/show`)"; no check reads `captures['show']` (grep: the only occurrences are lines 371-372). `v1-models-empty` is explicitly documented as a non-graded observation (docstring "non-graded facts such as the empty /v1/models body form"); **`show` is not** so documented, yet is equally ungraded.

**Repro** (`repro/p6.py`: the show request pointed at `/api/showX`; the unpatched server answers 404 — the patch emulates the server fault the verdict should catch): exit 0, verdict **MODEL_OK**, `captures.show.status=404`, and the lane counter **accepts**: `verify_bad=[] accepted=true`. Neither layer would notice a fault on this surface.

**Fix shape:** add `check('show', st == 200 and <model field matches qualified>, …)` (and optionally grade `v1-models-empty` status) or move `show` into `observations` explicitly.

### H4 — an exception in the `finally` block destroys the receipt; its exit code 1 collides with FAIL's 1
**Attacked clause:** the documented exit-code contract ("0 every evaluated check passed; 1 at least one check failed; 2 setup error or not evaluated"). Lines 405-425: any raise between `os.killpg` and `finish` (realistic candidate: `log.close()`; also anything unexpected) propagates out of `main`; `finish` never runs; **no receipt is written**; Python exits 1 — indistinguishable by exit code from a graded FAIL, and the teardown proof (which did execute) is lost.

**Repro** (`repro/p5.py`: `raise OSError('A09-simulated-finally-failure')` inserted after `log.close()`): exit **1**, `ls …/p5-receipt.json` → "No such file or directory", traceback ends `File "…/p5.py", line 423, in main / OSError: A09-simulated-finally-failure`; the child was already reaped before the raise (`kill -0 <childpid>` → gone). Not a false green — the opposite: a run whose teardown succeeded loses its entire record and masquerades as FAIL by exit code.

**Fix shape:** wrap the finally body so teardown/bookkeeping exceptions are recorded into the receipt (e.g. try/except around `log.close()` and the teardown dict, always reaching `finish`).

### H5 (mechanism, low) — `run_evidence`'s subprocess inherits the caller's full environment
**Attacked clause:** the isolation story ("lane-owned child … Environment values are never recorded", docstring lines 27-33). Line 200: `subprocess.run([sys.executable, … 'kama-ollama-evidence.py', …], capture_output=True, text=True, timeout=60)` — **no `env=`**, unlike both ollama invocations. Mechanism demo: `A09CANARY=leak-demo python3 -c "import subprocess,sys; subprocess.run([sys.executable,'-c','import os;print(os.environ.get(\"A09CANARY\"))'])"` → `child_saw_canary= leak-demo`. Impact: **none found** — `kama-ollama-evidence.py` reads no environment (grep: the only `environ` hit is its own docstring "never reads environment/config/default locations") and records none. Consistency gap only; fix shape: pass the same constructed `env` (plus whatever the interpreter needs) for uniformity.

---

## Suspects analyzed and cleared (no false green)

**`check('port-unregistered', …)` after `free_port` (lines 275-278).** The check re-evaluates the exact predicate `free_port` just enforced; it can only turn red (a racer binding between selection and check), never green. False-pass directions closed: REGISTERED_PORTS is a constant (the registered half cannot false-pass); a bound-but-not-listening squatter is invisible to `listening_ports()` (state `0A` filter) so the check could vacuously pass — but then the child's bind fails → `ready` red → FAIL; `/proc/net/tcp` unreadable → `listening_ports()` returns ∅ (OSError swallowed at lines 96-102) → same downstream catch. Repro (`repro/p4.py`: a squat thread binds the chosen port before the check): exit **1**, verdict FAIL, failed = `[port-unregistered, ready, teardown]` — the check fires. Design notes (not false greens): REGISTERED_PORTS={8080,34113} is hardcoded in **both** tool and counter and goes silently stale if the lane registers another consumer port; the check's return value is ignored, so on failure the tool still starts a child that cannot bind (wasteful, honest). Practical bound: `free_port` (bind port 0) draws from the ephemeral range **32768-60999** (measured `/proc/sys/net/ipv4/ip_local_port_range`), so it can never return 8080/34113/11434 — all three sit below the range.

**`pid_owns_listener` (line 129) / `listener-owned` (line 315).** A false pass requires the child pid to hold an fd whose readlink is `socket:[<inode of a LISTEN socket on the port>]` — i.e. the child *is* the listener. Squatter scenarios always red: a child that failed to bind exits (→ `running-exe-digest` red via OSError→None, or `ready` red); SO_REUSEPORT double-listen is closed because Go's `net.Listen` sets SO_REUSEADDR, not SO_REUSEPORT, and a second bind with SO_REUSEPORT against a non-SO_REUSEPORT socket fails with EADDRINUSE. Degradation is fail-closed: unreadable /proc → empty `want` → False → red.

**`rc_fail`/`evaluated_failed` tail logic (lines 427-432).** MODEL_OK requires `rc_fail == False` **and** no evaluated check failed; `rc_fail` is set only by not-ready (line 300) and the catch-all except (line 404). Grep: **zero** `evaluated=False` callers — the `evaluated` parameter and the schema field are dead code; every check is graded. The four-way tail is exhaustive; the false-green surface is exactly "all checks pass while reality is false", instantiated by H1-H3. The ignored return of `check('port-unregistered')` is safe because the check is recorded `evaluated=True`, so its failure still lands in `evaluated_failed` → FAIL.

**`child_env` leakage of caller env (line 178).** `env=env` in both `Popen` (line 283) and the create `subprocess.run` (line 339) **replaces** the environment (execve semantics) — no caller variable reaches the child. Repro (`repro/p3.py` dumps `/proc/<child>/environ` at exec time; driver env carries `A09CANARY=leak-a09-canary` and `TMPDIR`): child env names are exactly `['CUDA_VISIBLE_DEVICES','GGML_VK_VISIBLE_DEVICES','HIP_VISIBLE_DEVICES','HOME','OLLAMA_HOST','OLLAMA_MODELS','OLLAMA_NOPRUNE','OLLAMA_NO_CLOUD','PATH']`; `canary_present=False`, `tmpdir_present=False`. Cleared with evidence. Residual note: the child env sets no TMPDIR, so ollama may transiently use `/tmp` (seat bounds forbid *my* writes there; the tool's child is the tool's own behavior — flagged to the L1).

**Binary swap TOCTOU.** sha256→Popen race is covered by `running-exe-digest` (reads `/proc/<pid>/exe`, the exec'd inode); in-place modification of the running file is blocked by ETXTBSY. Sound. Residual (out of threat model, noted): the create step re-executes `binary` (line 339) without re-verification — a swap between serve-Popen and create runs a different binary for the import; a same-user attacker is outside the tool's threat model and the counter's blob/manifest re-derivation bounds the model identity regardless.

**Crash paths outside the try (lines 111, 282, 283).** `free_port` RuntimeError, `open(log_path)`, `Popen` — all before the try → unhandled → exit 1, no receipt (same exit-code collision as H4, no child to orphan). Code-reading only; no repro needed (no receipt is the observable).

---

## Not reached

- **N1 — unbounded second `proc.wait()` (line 418, no timeout).** After SIGKILL, a child stuck in uninterruptible (D) state hangs the tool forever, with no receipt and no timeout. Needs a D-state process to demonstrate; not reached on this host (no wedged block device available to the seat). Analysis only.
- **N2 — spontaneous clean exit (code 0) of the server during the window.** The counter accepts `returncode ∈ (0, -15)`, so a server that exits 0 by itself during the window would green end-to-end exactly as p1a does via an external SIGTERM. Demonstrating needs a server that exits 0 spontaneously; the window itself is demonstrated (p1a), so this adds only the note that the counter's teardown clause cannot attribute a 0/-15 exit to the tool's SIGTERM.
- **N3 — full independent re-verification of the committed receipt.** The L1's run dir `/fast/scratch/hyaku/kama-r60/live1` no longer exists, so the counter's dir-dependent clauses cannot be re-run. Partial re-verification against the committed receipt (nonce `b61c98ad5747`): `verify_bad=["log-listening","log-generate","manifest","blob-missing"]` — exactly the four dir-dependent clauses; everything internal (schema, nonce, verdict, binary-sha, port, all 16 checks, every capture sha, tags/ps/version/ps-before parse clauses, teardown shape) re-verifies clean.

## Residual risk

The layered design (tool checks + counter re-derivation from the run's own work dir) is genuinely strong; every tool-level hole found here is either backstopped by the counter (H2, H1-with-SIGKILL) or outside the claim's wording (H3). The one end-to-end false green (H1 via SIGTERM/clean exit) lives in a tens-of-ms window unpatched, but the window is structural: the tool's last graded server contact is the `ps-after` capture, and nothing after that observes the child. H4 is the mirror-image operability risk (records lost, exit codes colliding).

## Artifacts (relative to the lane root)

`repro/` under `.ufo/waves/round-60/w1/out/A09FalseGreenReading/`: `patch.py` (generates all six copies from the pristine source; every patch asserts a unique anchor), `p1.py`…`p6.py`, `verify.py`, `baseline-receipt.json`, `p1a-receipt.json`, `p1b-receipt.json`, `p2-receipt.json`, `p3-receipt.json`, `p3-child-environ.txt`, `p4-receipt.json`, `p5.stderr`, `p6-receipt.json`. Seat scratch removed; no lane source touched; no pacman transaction attempted (none needed).
