# M18C2ManifestForger — manifest population probe

Scope: tested `canonical_rows()` plus the C2 counter's canonical coverage/prefix checks against two fabricated newest-round canonical sections. No lane source was edited; no tools installed.

- **Wrong row bodies, frozen prefixes preserved:** Replaced each of the 12 canonical row bodies with `fabricated | 999 |` after the exact frozen prefix. `canonical_rows()` returned round 62 and 12 rows; all slugs unique, all prefixes matched, and the population check accepted the forgery. **Accepted.** The counter does not compare content after the frozen prefix; its relevant predicate is `row_text.startswith(prefix)`.
- **Duplicate capability:** Inserted a second copy of one manifest row. The canonical list had 13 parsed rows and a duplicate slug; the counter's `len(slugs) != len(set(slugs))` predicate rejects it. **Rejected.**

Probe output:
```
wrong-body round= 62 rows= 12 unique= 12 prefix_mismatch= [] accepted= True
duplicate rows= 13 duplicate= True accepted= False
row-body compared beyond startswith: no; canonical_rows returns full row but coverage checks only startswith(frozen prefix).
```

This is a calibration coverage finding: the frozen row prefix constrains only the beginning of each table row, not its evidence cells or first-working round. No counter verdict or contract change asserted.

Scratch was removed after the probe. Report trailer: `.ufo/waves/round-62/M18C2ManifestForger.md`
