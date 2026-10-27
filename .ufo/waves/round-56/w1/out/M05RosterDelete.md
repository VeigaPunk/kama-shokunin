# M05RosterDelete — Round 56 C2 mutation probe

- **Mutation:** In the isolated scratch clone, deleted the single `round56-counter` entry (`designation=positive-control`, `expected=detected`) from `tools/round56-env-leg-battery.py`'s `ROSTER`. No lane source was intentionally changed; an accidental attempt to edit the lane was immediately restored from the freeze-tip blob, with original SHA-256 `79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c` and clean tracked status.
- **Expected detector:** `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round56-prereg-check.py --repo <scratch clone> --tip <tip>`; deleting a roster member should yield `roster_match=0`, `met=False`, exit 1.
- **Counter identity:** SHA-256 at freeze tip `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7` was `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853`, matching the frozen digest.

## Runs

1. **Pristine:** tip `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7`
   - Output: `tip=efc6b3ec6fb6ea308c15855e9b8b62856f4255b7\npresent=1 roster_match=1 kills=1 controls=2 met=True`
   - Exit: `0`.
2. **Mutated:** tip `f2d21d2a53cb690b247d260cba1ec7e8b565d7e1`; mutated file SHA-256 `7fbf1ae9d313763c96a564164b90f53e2983012940d224f2da73f1c90e5d2da1`.
   - Output: `tip=f2d21d2a53cb690b247d260cba1ec7e8b565d7e1\npresent=1 roster_match=0 kills=1 controls=2 met=False`
   - Exit: `1`.
3. **Restored bytes:** committed the exact freeze-tip battery bytes in scratch at tip `5f714a06ea11d763eb05e1dab4d60e58863a2bcb`.
   - Restored file SHA-256: `79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c`; blob ID matches the freeze tip (`9d51ffc3e6744b15ec31a9c247d1059666b11e16`).
   - Output: `tip=5f714a06ea11d763eb05e1dab4d60e58863a2bcb\npresent=1 roster_match=1 kills=1 controls=2 met=True`
   - Exit: `0`.

**Verdict:** KILLED — the roster-delete mutant is rejected by the checker, while pristine and restored bytes pass. Scratch directory removed. No tools installed.