VERDICT: Guard instrumentation has two ungradable parser failures; do not count either as agreement.

Ran v6 audit at 138af25b963450b6520794995605fa7dbbcd87e0 (exit 0; 22 SOURCES events) and sources-append-only.py on event pairs. The latest two events exit 2 with `corpus/SOURCES.md:251: unterminated table row (no closing pipe)`. Under KQ22 (`corpus/QUALITY.md:123`) and KQ87 (`:442`), only surviving-row status/recheck/used-by changes are permitted; parse failure yields no verdict. Contract row is `registry/append-only-contract.tsv:6`. Event counts are in table.md.
