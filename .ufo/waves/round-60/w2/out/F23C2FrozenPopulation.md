# F23C2FrozenPopulation
- W1 artifact: C2 population predicate in `tools/round60-c2-counter.py`; frozen base `ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b`.
- Re-derived population from base blobs: replay file has 9 `inference` lines; other source files need inference + keyword on the same physical line.
- Counter uses split-line population and literal quote substring (3–25 words) on that exact line; neighboring-line context cannot bind.
- Counterexample: incidental quote substring on a qualifying line passes binding without establishing that it quotes the line’s actual claim; multiline semantics are not represented.
- Evidence command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b:corpus/knowledge/ollama-evidence-replay.md | nl -ba | grep -i inference`.
- Axis: C2 calibration; lexical line coverage can overstate claim-level coverage.
- Smallest safe correction: retain frozen predicate, constrain interpretation to line-level textual coverage; no predicate edit.
- Full evidence: `.ufo/waves/round-60/w2/out/F23C2FrozenPopulation/findings.md`.