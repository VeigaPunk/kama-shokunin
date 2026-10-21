VERDICT: partial - source-only census; L1 transcribed the scout's final response.

Original seat: CloseKama18.KillCensus-2. The scout declined to ship a file;
this is a durable L1 transcription, not an original report written by that seat.
Base 37bd4c5. Source inspection only, no tests executed by this seat.

- [INFERENCE] install-tree-grid.py:106–129 calls any gate exit1 rejected,
  signal -9 accepted. citation-provenance.py:94–108 maps bad git-blob lookup
  to mismatch; missing git executable/non-git lane is a different error path.
- [INFERENCE] round18/c2/survivors.py:897–899 accepts exit1 as kill in one
  historical arm; :931–956 may count partial FAIL+target as killed.
- [INFERENCE] round18/c1/measure.py:1051–1079 calls nonzero mutant-selftest
  exit killed; round17/c1/mutants.py:947–998 kills on observable differences.
- controls.py:1023–1069 requires receipt/target evidence; fault-controls.py:
  685–750 requires exit1 and targeted parsed row. Independent ControlsCrash
  seat later reproduced targeted-rejection credit on crashes, so this source
  inventory is not a dynamic adequacy proof.
- runs/run.py:22–31 grades expected exit only. count-verdicts.py:64–86
  checks first nonempty VERDICT line. Neither is a universal subject oracle.

Other inspected surfaces: kama-llamacpp-live.py:873–885; kama-probe.sh:
40–41,462–493; receipt gate:2213–2243; kama-ollama-evidence.py:413–443;
ollama-corpus-guard/check.py:529–605; test-snapshot.sh:35–37,187–194.
Clone/status/cleanup commands exit0; no installs. Original final at
history://CloseKama18.KillCensus-2 (navigation only; this file is durable).
