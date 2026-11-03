# Round71 independent first-output technical judgment

Reviewer judge_kama_round71, 2026-11-03. Technical judgment: PASS and bounded capability admission recommended, conditional only on truthful final metadata integration. This report does not infer a live serving result or a numeric-axis gain.

## Binding and actual execution

The independently frozen contract/oracle landed b2f1f17ffa88dce5d68ee21eaed89e932089bdef before candidate implementation. Manifest SHA25698ca09718d714ced3715c441802983373d49cb9fed1b7e402f0858e118448b0c. First candidate landed1ccd5d0db476344fefcd58e4ab342f66d8f1f9d4, file SHA256be3dec7e88cc49bec38da717580f1f802e2e86bdd29d06bb7951776a34f60201. Evaluator payload landed5ef6578a454de5bbc55b941d3019be24e0c47c45 with HASHES.json SHA256a427920333f86a946dc8e9dccbadb0443ce3b9126b9087826165b28d2c07e0a1.

One original local batch began2026-11-03T03:48:35.090497+00:00. Its raw RESULTS.json is728042 bytes, SHA2565d932f643ef6169d3a6b74531943f427cef628a86ea8f66fe4d1050a91dffad2. No candidate, mutant, baseline or entire batch was rerun. RESULT-MANIFEST binds raw results, controller and staging receipt. Independent READBACK-FIRST.json is derived by the separately written read-only adjudicator, not by trusting the runner passed flag. Raw technical output is retained unchanged.

## Independent outcomes

-83 candidate fixtures exactly match prospective canonical outputs and exit codes:20 COMPLETE,14 INCOMPLETE,3 STREAM_ERROR,46 INVALID_OR_INSUFFICIENT.
-5 invocation refusals each exit64 with empty stdout.
-10 actual source-mutant target invocations produce the intended semantic disagreement with legitimate classifier JSON/exits; all10 paired benign controls remain exact. No crash, timeout or malformed output earns kill credit.
-16 epistemic-field mutations differ in precisely the named field and canonical bytes, with unchanged exit.
-8 historical r31 presence-proxy invocations match their independently assigned booleans. On this new completion question, the proxy accepts missing-finish, undispatched-terminal, post-terminal-malformed and error-terminal examples; it misses valid CR/no-space/multiline framing. It passes the conventional complete case. These distinctions are not a retrospective failure of r31's narrower presence task.

Exact inventory132, no missing or duplicate records, no runtime errors/stops/cleanup errors. Maximum invocation wall time0.03442667199851712 seconds; maximum stdout+stderr495 bytes. Scalar score calibration7/operability8 remains unchanged; finite fixtures do not justify broad protocol correctness.

## Isolation and cleanup evidence

Actual batch cgroup reads memory.max536870912, memory.swap.max0, pids.max64. Each record attests CPU2s, address256MiB, core0, fsize0, nofile32. Reviewed controller uses private PID/network bwrap namespaces, readonly minimal interpreter/stdlib/candidate/fixture mounts and an empty masked site-packages directory. All132 recorded command lines retain those bounds. The controller compares candidate PID/net namespaces with its own and records no mismatch. Reused namespace inode values across sequential calls are not claimed as132 simultaneous unique namespaces.

Runtime Python3.14.8. Staging verifies107 runtime objects and664 stdlib files with no drift against inventory SHA256a59fe35541c7cd747087a9d6adc9c4163c2ea7736bbb9b9fbefda44465a194de, already preserved at round70/result/runtime-inventory.json. Package metadata in staging does not mean those packages were mounted into candidate sandbox; site-packages was masked.

Controller systemd invocation exits0. Cleanup kill/stop return1/5 because the collected unit is already absent; subsequent show exits0 with LoadState=not-found, ActiveState=inactive, empty ControlGroup. This establishes unit absence, not a separately inspected cgroup-membership census or universal leak proof. No new setup, service restoration, endpoint/model call or provider contact occurred.

## Source/taste and residual scope

Independent primary reads verify WHATWG event-framing rules and pinned llama.cpp final-choice, optional-usage, exhausted-reader marker and error termination distinctions. S544–S546 and the practical knowledge note correctly separate source facts from lane-defined strict synthetic projection policy. Full API response objects, HTTP status/headers, request/capture provenance, multiple choices, token output, timing and live state remain excluded. The classifier establishes no current readiness, weight/model identity, process ownership, successful real request or output quality. Six protected legacy files remained byte-identical before outputs; final metadata check is separate.

Retained mistakes: prefreeze double-BOM expectation corrected before candidate existed; author's first source-line check was off by one; pending SKILL oracle path typo was corrected prospectively at7b51a6f98f3b4893a108108221acb2faa2a7f612. Neither these metadata repairs nor unchanged historical debts earn capability/score credit. First candidate and first technical outcomes were not repaired or replaced.
