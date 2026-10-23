# ScribeShonenBox2 — scoped report

## Behavior
Drafted the corrected SHONEN.md box 2 / line 8 text and a proposed LOG.md line naming the old-to-new wording. The correction distinguishes eight adverse controls (seven bad server shapes plus K6's injected teardown fault), frozen `accepted_bad=6` (five accepted bad receipts plus K6's receiptless escape), and K3's inconclusive result. The draft retains `[~]`, “Author assertion,” and “no non-author mark”; it adds no `[x]`.

## Gates and commands
No test, build, lint, control suite, receipt gate, or model-server command was run. The only shell command was `timeout 10s mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeShonenBox2 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/advice`; it returned no output and no error was reported. No tool was installed.

## Evidence / findings
- `tests/llamacpp-live/controls.py:17-18,525-578` documents the unchanged K1–K8 round-17 control shapes and identifies K6 as an in-process injected teardown fault using K0's good server shape.
- `.ufo/waves/round-17/runs/controls-frozen.json:2,58-73,118-135` records frozen accepted-bad=6, K3 inconclusive, and K6 escaped without receipt (tool exit 4; no gate invocation).
- `.ufo/waves/round-17/falsify/advice/ShonenProvince.md:39-47` supports the seven-plus-one classification, states that the current K1–K8 result rejected the controls, and provides the corrected formulation. `.ufo/waves/round-28/residual/advice/ResSelfAssessment.md:51-60` confirms the repair was routed and remained outstanding.
- The prompt named `tests/llamacpp-live/controls-frozen.json`; that file was absent from the live-control directory listing. The frozen result was found at `.ufo/waves/round-17/runs/controls-frozen.json` and used as the evidence source.

## Touched surfaces and scope
Created only these assigned artifacts:
- `.ufo/waves/round-29/w1/out/ScribeShonenBox2/shonen-line8.md`
- `.ufo/waves/round-29/w1/out/ScribeShonenBox2/evidence.md`
- `.ufo/waves/round-29/w1/advice/ScribeShonenBox2.md`

No tracked lane document, test, implementation, judge, Git/JJ state, fleet file, or sibling lane was changed. No claim beyond the static sources was verified by execution.
