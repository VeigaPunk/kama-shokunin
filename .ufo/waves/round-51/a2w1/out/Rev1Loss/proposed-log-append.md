PROPOSAL ONLY — NOT APPLIED. Lane files are read-only for this seat; this text is
offered for the L1 integrator (KamaR51a2) or a later round to append to LOG.md if
the lane chooses to make the ed135b3c loss visible inside the log itself, rather
than only in registry/append-only-disclosures.tsv. It is a *correction entry*
(the A-corr rule: "corrections land as new entries"), not a restoration of the
withdrawn canon text: it names the pair, dates it, points at the disclosure rows,
and states that the withdrawn bar is not live. Appending it changes no disclosure
row and no counter outcome (the event stays `disclosed`; a *restoration* of the
five lines would flip it to `restored` and would erase the R6 calibration datum).

--- begin proposed append (8 lines + one blank separator; append at end of LOG.md) ---

## Correction (appended round 51, 2026-10-27) — the 2026-10-13 craft-hours entry was reverted, not lost to an edit

- The 2026-10-13 16:56:38 commit `33b167ec` added HOURS.md and a LOG.md entry
  ("## 2026-10-13 — HOURS.md ledger opened"); `ed135b3c` (17:04:57) reverted
  that whole commit, so the entry left LOG.md with it. The pair's trees are
  equal (`be181d4f`), so the revert restored the pre-canon tree exactly.
- Both commits are the canon side's (`ci <ci@local>`), not the lane's round-log
  identity; the fleet withdrew the same craft-hours canon the same afternoon
  (fleet `7e818675` 16:55:09 → `820eb26b` 16:58:09).
- The five removed lines are disclosed by key in
  registry/append-only-disclosures.tsv (commit `ed135b3c`, file LOG.md, class
  `revert`); the two other deleted lines are a blank separator and the
  EOF-newline rewrite of a line still present.
- Disposition: disclose, do not restore — the ≥10,000 craft-hour bar the entry
  announced is not live at either tip, so re-appending the text would assert a
  withdrawn requirement.

--- end proposed append ---
