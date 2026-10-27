# Q08CensusEnd — final-tip sources census

Observed final committed tip: `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7` (HEAD); the jj working-copy commit is `0f65f84856f3b89b91adb6c408422b5d91cd2c65`, whose parent is that tip. `corpus/SOURCES.md` has no worktree diff from HEAD. The census script is `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`, SHA-256 `3fb7261569f46423dd80ecc23e0a23789a7926f667c7a3fc559d2439d4a64e30`.

The wave has no census command pinned in preregistration. Following X06Census's exact reproduction, I ran the receipt-producing validate command:

```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
```

**Exit 0.** Stdout was 100 lines (98 W04, 1 W01, and the final `kama ok` line); stderr was empty. Exact stdout and stderr are saved at `w1/out/Q08CensusEnd/validate-end.out` and `validate-end.err`; stdout SHA-256 is `3eeea0f4be9d942913d0458d1ec47f5e2d963b2790b95afbfc44abc7fe9a267d`. This stdout hash matches X06Census's final-tip rerun. Compared with `census/start.out`, `diff` exited 1 for exactly one added line: `kama W04 S513 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes` (before the final `kama ok`). The complete diff is saved as `w1/out/Q08CensusEnd/start-vs-end.diff`.

For the row-count summary, I also ran:

```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama
```

**Exit 0.** Exact stdout is saved at `w1/out/Q08CensusEnd/census-end.out` (stderr empty). It reports `rows=254`, tier A/B/C `241/9/4`, status mined/queued/rejected `229/8/17`, invalid `0`, and missing `0` (lane and fleet counts agree). Exact command metadata and exit receipts are in `run-meta.txt` and `exits.txt`.

No shared lane files or jj state were changed. Scratch `/fast/scratch/hyaku/kama-r56/Q08CensusEnd/` was used with `TMPDIR` set explicitly and removed before handoff.
