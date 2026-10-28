# C1 mutation probe — M03C1AttackThe

Base tip: `65d7cad0fce90e34de37527cde22e97b63b118bf`.
Axes: operability and calibration. Counter loaded from the lane checkout at that tip; `score()` and `grade()` executed from the counter module against a copied receipt and synthetic live witness matching the receipt identity.

Receipt origin: `/fast/scratch/hyaku/kama-r62/measure/c1b/receipt.json` was absent, so ran the C1 counter with `--work /fast/scratch/hyaku/kama-r62/w/M03C1AttackThe`; copied its receipt into the report scratch.

Probe outputs (each tuple is `score()` output):
- Pristine receipt: ACCEPTED — `{\047met\047: True, \047alltrue\047: True, \047verdict_ok\047: True, \047live\047: True, \047inconsistent\047: []}`.
- Stale nonce (`receipt.nonce = r60-deadbeef`, while counter NONCE remains receipt original): REJECTED — `{\047met\047: False, \047alltrue\047: False, \047verdict_ok\047: True, \047live\047: True, \047inconsistent\047: []}`.
- Matching top-level nonce, wrong `hold.nonce`: ACCEPTED — same pristine score output.
- Matching top-level nonce, wrong `captures.health.captured_at` (`wrong`): ACCEPTED — same pristine score output.

Falsification: the two accepted mutations demonstrate that the score does not validate the hold metadata nonce or capture timestamp. The nonce-stale family is rejected because `nonce_match` is recomputed against the module-level NONCE; the hold nonce and capture time are not graded fields.

No tools installed or updated.

Restoration: only the dedicated scratch was used for receipt/probes; no source files changed. Scratch removed after copying evidence. Counter tally: pending actual counter output.
