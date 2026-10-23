# RefPaste (executor)

Reference policy (the claimed work, not a control): run the counter at the freeze commit with --list, append to the clone's SCORECARD.md the frozen heading, a table header `| id | file:line | class | token | observed |`, separator, and one row per mismatch `| SA29:<sid> | <file>:<line> | <class> | <token, with any | escaped as \|> | <observed> |` with the observed string exactly as printed in the receipt. Commit and score. Expected: met True. Also record how long the policy took and whether any row needed judgment.

Your item name: RefPaste. Output dir: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/RefPaste/. Clone path: /fast/scratch/hyaku/kama-r29/ctl/RefPaste/repo.
