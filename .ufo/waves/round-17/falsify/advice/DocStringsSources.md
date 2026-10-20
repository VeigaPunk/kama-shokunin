VERDICT: partial — pinned source facts mostly match, but KQ21 coverage and source-label drift remain.

# Scope attacked

Reviewed all 11 `DOC` entries in `tools/kama-llamacpp-live.py:87-151` and the corresponding `documented_by` values in receipts 1–3. Opened the locally pinned llama.cpp b11755 copies under `.ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/`, the probe implementation, the retained C2 controls and their recorded outcomes, and KQ21. The receipts repeat the same documented strings; `model_unchanged` is explicitly labelled `lane input integrity, not subject behaviour` in the tool and receipts.

# Findings (severity order)

## High — Six subject-facing checks have no retained bad control that flips them (KQ21)

KQ21 says a live-run check is evidence about the running subject only when a retained misbehaving-subject control makes that same check fail through the tool and gate, with the gate-flip rejection too (`corpus/QUALITY.md:122`, “a retained control … makes that same check fail”). The retained C2 suite does not do this for six checks presented as live llama.cpp/probe behavior:

- `models_alias_id`, `models_owned_by_llamacpp`, `metrics_not_enabled`, `props_alias`, `probe_model_ok`, `probe_mismatch` (`.ufo/waves/round-17/live/receipt-1.json:111-170`; the same IDs/labels recur in receipts 2 and 3).
- `tests/llamacpp-live/controls.py:300-327` targets health in K1, loading-envelope behavior in K2, and teardown in K3–K8; there is no bad-control expectation for those six. Across those controls, `MODELS_OK` and `PROPS` remain fixed to the expected values (`controls.py:167-171`), and `/metrics` remains 501 (`:237-240`). The recorded current matrix likewise shows check failures only for health, loading, and teardown (`.ufo/waves/round-17/runs/controls-current.json:27-29,54-56,80-82,110-112,140-142,167-169,191-194,223-225`).
- Thus the controls do flip `health_ready`, `loading_envelope_graded`, `teardown_graceful`, and `teardown_port_closed`, but they do not demonstrate that the six above fail when the corresponding served identity, `owned_by`, metrics status, props alias, or probe result is corrupted. The probe assertions also consume server-derived `/v1/models` data (`tools/kama-probe.sh:521-542`); every control keeps that response correct.

If these six passing checks are counted as evidence about the live subject, they do not meet KQ21. The receipt gate does not enforce source/classification semantics: it only requires a nonempty `documented_by` string (`tests/llamacpp-live/check-receipt.py:644-646`). Add controls that flip the named fields, or state clearly that these are not admitted as subject evidence. `model_unchanged` is correctly marked input-integrity rather than subject evidence; see the wording issue below.

## Medium — `teardown_graceful` cites the moving Python `/3/` page, not S044's pinned version

`tools/kama-llamacpp-live.py:60-61` sets `POPEN_RETURNCODE_DOC` to `https://docs.python.org/3/library/subprocess.html#subprocess.Popen.returncode`; the same URL is serialized in `receipt-1.json:174` (and receipts 2–3). S044 instead cites `/3.14/` and explicitly notes that `/3/` serves Python 3.15 (`corpus/SOURCES.md:56`). The round-17 Gate rejects citing `/3/` because the host runs 3.14.8 (`corpus/lessons/round-17.md:66-67`, “Cite the `/3/` Python docs page | reject”). I opened both current official URLs: `/3.14/` is titled Python 3.14.8; `/3/` is titled Python 3.15.0. The negative-returncode sentence is present on both, so this is a reproducibility/version-anchor defect rather than a false paraphrase. The local `pins.json` covers llama.cpp files only; no saved S044 page/digest exists (`.ufo/waves/round-17/sources/pins.json:1-42`).

## Low — `health_ready` citation omits the source span that establishes HTTP 200

The `documented_by` string cites only `server-context.cpp L5288-5299` (`tools/kama-llamacpp-live.py:90-92`). That span contains the body call at 5297, but the check grades both status 200 and parsed body (`:1175-1179`). The helper that makes `res->ok(...)` status 200 is at pinned `server-context.cpp:4868-4871` (“status = 200;” at 4869). S042's registry anchor already names that helper span (`corpus/SOURCES.md:54`), but the receipt string does not. The body claim is supported; the status half needs the helper citation/binding.

## Low — `model_unchanged` overstates that only content mutation can make it fail

The integrity classification is correct, but `documented_by` says “only external mutation can flip it” (`tools/kama-llamacpp-live.py:147-149`; receipts 1–3 line 209). The post-run rehash catches `OSError` and stores `rehash-error:...`, then compares that string with the original digest (`:1357-1365`); a filesystem/read failure can therefore fail the check without changed GGUF bytes. This does not make it subject evidence; qualify the sentence as an input-integrity check that also fails if the rehash cannot be read.

# Source-string coverage notes

The remaining pinned claims I checked are supported by the named sources and predicates:

- `models_alias_id`: pinned README says `--alias` sets the custom `id` (`README.md:1284`).
- `models_owned_by_llamacpp`: the pinned README example has `owned_by: llamacpp` (`README.md:1300`); the docstring accurately presents its additional basis as the L1 smoke observation.
- `metrics_not_enabled`: README requires `--metrics` (`README.md:1133`) and shows the disabled endpoint's 501 response (`:2368-2376`); the check grades status 501 (`tools/kama-llamacpp-live.py:1195-1199`).
- `props_alias`: pinned source selects the configured alias as `model_name` (`server-context.cpp:1521-1525`), emits it as `model_alias` (`:5242-5247`), and GET `/props` returns that object (`:5438-5447`).
- `probe_model_ok` / `probe_mismatch`: `classify()` yields the documented verdict/reason for matching and mismatching IDs (`tools/kama-probe.sh:521-542`); the check also grades the corresponding exits (`tools/kama-llamacpp-live.py:1224-1237`).
- `teardown_port_closed`: its label matches the ownership-and-refusal predicate (`tools/kama-llamacpp-live.py:1333-1341`).
- `loading_envelope_graded`: the pinned not-ready middleware constructs the stated 503 envelope (`server-http.cpp:307-325`) and is installed as a pre-routing handler (`:331-355`). The tool's stored-body grading and cap are described consistently (`tools/kama-llamacpp-live.py:1342-1356`, `LOADING_BODY_MAX` at `:75`).
- `teardown_graceful`: the cited pinned server.cpp ranges show SIGTERM handler installation, shutdown handler termination, and the `return 0` path (`server.cpp:519-534,575-590`). However, the phrase “the documented graceful exit status” (`tools/kama-llamacpp-live.py:122`) conflicts with the round-17 Gate's explicit rejection that graceful exit 0 is documented: the README has no exit status and the claim is code-derived (`corpus/lessons/round-17.md:64`). Prefer “code-derived exit status.” The source supports the successful path, not an unconditional timing guarantee: pinned `server-queue.cpp:132-135` sets `running = false`, while `:278-280` sets it true on loop entry. [INFERENCE] A SIGTERM in the install-to-loop-entry window can be overwritten; the successful receipts establish only that their sampled teardowns returned 0.

# Verification gaps, commands, and installs

- LSP: attempted `read xd://lsp`; the tool returned “No such tool: xd://lsp.” No LSP status/references/definition/diagnostics were available. Grep results were used only as literal locators; claims above are grounded in the opened source lines, not presented as semantic-search proof.
- Shell/lane commands run: none (exit code: n/a). No live tool, gate, controls, build, or test was run.
- Installs/upgrades: none.
- Scratch: none created; nothing to remove.
- S044 has no saved page/digest, so I verified the current `/3.14/` and `/3/` pages but cannot prove byte identity with the page originally opened for the registry row.
