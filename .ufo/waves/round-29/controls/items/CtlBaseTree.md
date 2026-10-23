# CtlBaseTree (executor)

Policy: base-tree shortcut. Check every statement against the BASE tree 2aa46e24 (or the freeze commit) instead of the writing revision W: for P/H/N use the blob at base, for C test ancestry against base, for T compare with base's committer time, for Q grep the base tree with the same exclusions. Write correction rows (frozen heading, `SA29:<sid>`, observed string in the counter's format) for the statements that fail at base. Do not read before/c1-base.json or run the counter before scoring. Commit and score.

Your item name: CtlBaseTree. Output dir: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlBaseTree/. Clone path: /fast/scratch/hyaku/kama-r29/ctl/CtlBaseTree/repo.
