PASS — the LOG restoration preserves the deleting history, including the actual round-50 loss, without presenting it as current policy.

## Evidence

- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show ed135b3cb869 -- LOG.md` confirms commit `ed135b3cb869c5d8a6c9d3b32dac02fb7e551ebd` is the revert of `33b167e...`; its patch deletes the 2026-10-13 HOURS ledger entry (the section heading and four body lines). The post-revert file no longer contains the heading (`show <commit>:LOG.md | grep ...` returned no match); its parent does. The restoration block at `LOG.md:2362-2370` identifies the revert and quotes those five lines verbatim in a fenced block. This is the real round-50 loss, not a hypothetical deletion.
- The round-52 framing at `LOG.md:2360` explicitly calls the material historical bytes, says later replacement text stands, and labels the section as restoration; `LOG.md:2362` attributes this first block to the reverting commit. Thus the withdrawn craft-hours rule is not reasserted as current policy. The preceding round-51 text at `LOG.md:2352` also records the correction/retraction context.
- The additional blocks at `LOG.md:2372-2422` are presented uniformly as deleted-by commit, fenced historical text under the same restoration framing. This inspection supports historical presentation; I did not independently enumerate all other deleting commits or search the contemporaneous repository for every line's possible re-addition elsewhere. No other actionable issue found in this scoped review.

## Verification gap

The assignment asks to establish for each restored line that its deleting commit did not re-add it elsewhere at the time. I verified the line group deleted by `ed135b3c` in the LOG diff and parent/post-commit versions, but did not establish that condition for every later block or search all paths at each historical commit. No finding is asserted on those unverified cases.