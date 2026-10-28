# SCORECARD round-62 measured-results block — draft template

Source of truth for findings: `.ufo/waves/round-62/w1/W04ScorecardDraft.md`. Placeholders are
`<NAME>` tokens; base cells are copied verbatim from the freeze receipts and need no placeholder.

```markdown
### Round-62 measured results

Measured commit: `<TIP>` (fresh clone of the lane). Counters: `tools/round62-c1-counter.py`
sha256 `<C1_COUNTER_SHA>` (blob introduced at `<C1_COUNTER_COMMIT>`), `tools/round62-c2-counter.py`
sha256 `<C2_COUNTER_SHA>` (blob introduced at `<C2_COUNTER_COMMIT>`), `tools/kama-completion-live.py`
sha256 `<TOOL_SHA>`. `<COUNTER_BYTES_NOTE>`

| Claim | Base | Measured `<TIP_SHORT>` | Command | Receipt |
|---|---|---|---|---|
| C1 operability 8 → 8 | `<C1_BASE_LINE>` (exit 1) | `<C1_LINE>` (exit `<C1_EXIT>`) | `python3 tools/round62-c1-counter.py --repo <clone> --tip <full commit> --work <scratch>` | `.ufo/waves/round-62/controls/c1-base.txt`; `.ufo/waves/round-62/measured/c1.out` |
| C2 calibration 7 → 7 | `<C2_BASE_LINE>` (exit 1) | `<C2_LINE>` (exit `<C2_EXIT>`) | `python3 tools/round62-c2-counter.py --repo <clone> --tip <full commit> --work <scratch>` | `.ufo/waves/round-62/controls/c2-base.txt`; `.ufo/waves/round-62/measured/c2.out` |

Scores held: operability 8, calibration 7. Capabilities 12 → 13 only if C1 is admitted
(`live-completion-request-plane`, first-working round 62, outside the frozen 12-row C2
population); C2 adds no capability. No axis score delta is claimed by this paragraph.

Regressions at `<TIP_SHORT>` (`.ufo/waves/round-62/measured/*.out`, each with its `tip=` line):
gate `registered <R> unregistered <U> defective <D>`; capability census `listed <L> observed <O>
missing <M> unsubstantiated <N> met <True|False>`; round-41 head counter `<R41_LINE>`;
round-42 self-description `<R42_LINE>`; round-43 registry `<R43_LINE>`; pointer `met=<B>`;
digest-ledger `unknown=<K>`; hexrun-census `unknown=<K>`; `sources-append-only --from <BASE>`
exit `<rc>` (`<last line>`); `append-only-audit --to <TIP>` exit `<rc>` (`<summary tail>`);
selftests `AOA_SELFTEST pass=<n> fail=0`, `KLR_SELFTEST pass=<n> fail=0`, live `selftest: ok`,
`check-receipt` `<n> VALID / <n> mutations rejected`; prior-round counters `<…>`; then one clause
per red item naming whether it is **carried from the base** (with the base value) or **introduced
by this round** and which seat/closure owns it; end census exit `<rc>` (`<summary>`).

### What `met=True` does not show (round-62 wave attacks)

- **Disclosed before the wave** (freeze limits, not wave findings): the hold-window contact
  proves **one loopback port** — the counter POSTs to `127.0.0.1:<port>` read from the tool's
  `hold.json` (`tools/round62-c1-counter.py:67-75,239-252`) and never contacts a registered
  consumer (`registry/endpoint-consumers.tsv`: omp-llama-cpp-default 8080, ufo-fsd-thetick and
  ufo-fsd-local-helper 34113); C2's **sensitivity leg only mutates captured output**
  (`out.replace(pattern, MUT)`, lines 268-271) and never re-executes a check, so it is not a
  causal or semantic test; and the **scan bindings trust the real repository** — the
  `digest-ledger`/`hexrun-census` rows bind `--repo %R --rev TIPREV` (`%R` = the caller's
  repository, line 186), so their `unknown=0` is a statement about the named repo's objects plus
  host artifacts re-hashed at scan time, not about the extracted tip tree alone.
- **C1, wave findings.** `<…>`
- **C2, wave findings.** `<…>`
- **Integration fixes after the wave.** `<…>`
- **Separability holds** (seat `<…>`): `<…>`
```

Base cells, verbatim from `.ufo/waves/round-62/controls/{c1,c2}-base.txt`:

```text
C1 base: tool_present=0 live_ok=0/1 fake_rejected=0/2 stale_rejected=0/1 tamper_rejected=0/8 log_rejected=0/1 predead_rejected=0/1 sigterm_rejected=0/1 hold_rejected=0/1 outside_rejected=0/1 errors=1 met=False
C2 base: population=12 rows=0 covered=0/12 bound=0 eval_lines=0 sensitive=0/0 dead=0 mismatches=0 canonical=49 controls_rejected=0/8 errors=3 met=False
```

Counter key order (for the measured cells):
`C1: tool_present live_ok fake_rejected stale_rejected tamper_rejected log_rejected predead_rejected sigterm_rejected hold_rejected outside_rejected errors met`
`C2: population rows covered bound eval_lines sensitive dead mismatches canonical controls_rejected errors met`
