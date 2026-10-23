Verdict: Routed defect 5 is addressed in a candidate copy; both requested raw-hash mutants now report `bound False`, while the pristine lane-tip receipt remains bound. Candidate is not landed.

## Exact observations

- `corpus/lessons/round-25-verifier-spotcheck.md:223-225` routes defect 5: the prior counter accepted receipts without checking `cells[].raw` against files in `final/raw/`.
- `.ufo/waves/round-25/count-c2.py:137-140` showed the former receipt-level `bound` expression checked only server version and model SHA (and per-cell repeats); it had no raw-file hash check.
- `tools/kama-context-capacity.py:392-394,420-427` establishes the writer's raw names: `<id>.server.log`, `<id>.health.body`, `<id>.props.body`, `<id>.slots.body`, `<id>.models.body`; these are used by the candidate's key-to-file binding.
- Extracted frozen lane tip using `git archive a23c0e042114016a909eb15173aa6df74b5b7eb0 | tar -x -C /fast/scratch/hyaku/kama-r26/ExecC2RawBinding/extract`. The extracted `final/raw/` contained 70 files. The unpatched pristine run printed `registered 14 observed 14 bound True missing []`, exit 0.
- On the file-altered mutant (appended `\nMUTATED BY ExecC2RawBinding\n` to `K1.health.body`, receipt unchanged), unpatched printed `registered 14 observed 14 bound True missing []`, exit 0; patched printed `registered 14 observed 14 bound False missing []`, exit 0.
- On the receipt-hash mutant (`K1.raw.raw_health` changed to 64 zeroes, raw files unchanged), unpatched printed `registered 14 observed 14 bound True missing []`, exit 0; patched printed `registered 14 observed 14 bound False missing []`, exit 0.
- Patched copy on the committed receipt in the same frozen-tip scratch extract printed `registered 14 observed 14 bound True missing []`, exit 0.
- Full command lines and outputs, including an intermediate edit failure and its correction, are recorded in `out/ExecC2RawBinding/RUNS.txt`.

## Candidate behavior and boundaries

`out/ExecC2RawBinding/count-c2.py` adds SHA-256 reads for raw files and includes the resulting raw check in `bound`. Known raw keys must match the file belonging to that cell; other raw keys must match some file in the raw directory. Missing/empty raw objects, non-string values, changed hashes, missing expected files, and I/O errors make `bound` false. The counter retains its existing exit behavior: a parseable but unbound receipt prints `bound False` and exits 0.

Risk: the candidate resolves `final/raw/` relative to the counter's directory. That is correct when integrated at `.ufo/waves/round-25/count-c2.py`; testing used that placement inside the scratch extract. Running it from the round-26 output directory without placing it beside the round-25 `final/raw/` will produce `bound False`.

## Files written

- `.ufo/waves/round-26/w1-build/out/ExecC2RawBinding/count-c2.py`
- `.ufo/waves/round-26/w1-build/out/ExecC2RawBinding/diff.patch`
- `.ufo/waves/round-26/w1-build/out/ExecC2RawBinding/RUNS.txt`
- `.ufo/waves/round-26/w1-build/advice/ExecC2RawBinding.md`

No tools were installed. No lane production file was modified; the L1 decides whether to land the candidate.