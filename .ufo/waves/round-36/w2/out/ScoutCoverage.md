kimi version 2.3.1
• Let me parse the task. I'm a Godspeed subagent, wave 2 (falsify wave), round 36, kama lane. My target:

  1. Read /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/README.md — say whether the coverage map already names any entry about a published native route that differs from the engine's current route, and quote the closest line if one exists.
  2. Read corpus/knowledge/runtime-health-surface-matrix.md and corpus/knowledge/sglang-docs-version-pinning.md if they exist. Say whether the ground the drafted entry covers is already held, or is new coverage-map ground.
  3. Do not edit any file, do not fetch anything.
  4. Report to .ufo/waves/round-36/w2/out/ScoutCoverage.md.

  So I need to read those files, plus probably the drafted entry at .ufo/waves/round-36/assimilation/sglang-native-route-deprecation.md to compare ground coverage.

  Axes: correctness (does README actually name such an entry), precision of quoting, scope discipline (no edits, no fetches), report quality.

  Plan: parallel reads of corpus/README.md, the two knowledge files, and the drafted entry. Also maybe glob the knowledge dir to check existence. All read-only. Then write the report to the seat-out path (my one allowed write).

  Let me do parallel reads: corpus/README.md, corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/sglang-docs-version-pinning.md, .ufo/waves/round-36/assimilation/sglang-native-route-deprecation.md, and .ufo/waves/round-36/assimilation/correction-lines.md maybe not needed. Also maybe the coverage audit tool to understand what the coverage block looks like — the README is the coverage map presumably. The task says "the coverage map" = corpus/README.md presumably, plus "the lane's own knowledge index". So also check for a knowledge index — maybe corpus/knowledge/README.md or an index file. Let me glob corpus/knowledge/*.

  Let me fire parallel tool calls:
  1. Read corpus/README.md
  2. Read corpus/knowledge/runtime-health-surface-matrix.md
  3. Read corpus/knowledge/sglang-docs-version-pinning.md
  4. Read .ufo/waves/round-36/assimilation/sglang-native-route-deprecation.md
  5. Glob corpus/knowledge/**

  That covers it. No web fetches. Then write report.

• Axes: (1) does corpus/README.md already name this ground, (2) do the two named knowledge files already hold it, (3) exact quoting, (4) scope discipline (no edits, no fetches). Firing parallel reads.

