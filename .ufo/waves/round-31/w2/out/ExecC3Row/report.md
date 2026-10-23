```RESULTS
$ mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecC3Row /tmp/kama-r31w2/ExecC3Row
exit=0
verbatim tail: (empty)

$ sha256sum .ufo/waves/round-29/count-c1.py  [cwd: /home/vgpnk/Projects/shokunin/kama-shokunin]
exit=0
fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383  .ufo/waves/round-29/count-c1.py

$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD
exit=0
addeb57c5d717785a94105a2e36cc8a76940fb6c

$ /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gate-registry-check.py --help
exit=0
usage: gate-registry-check.py [-h] [--repo REPO] [--rev REV]

Report tracked round counters that SKILL.md does not name.

options:
  -h, --help   show this help message and exit
  --repo REPO  repository to evaluate (default: .)
  --rev REV    git revision to evaluate (default: the working tree)

$ git clone --shared --no-hardlinks --branch master /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/ExecC3Row/gate-clone
exit=0
Cloning into '/tmp/kama-r31w2/ExecC3Row/gate-clone'...
done.

$ git clone --shared --no-hardlinks --branch master /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/ExecC3Row/counter-clone
exit=0
Cloning into '/tmp/kama-r31w2/ExecC3Row/counter-clone'...
done.

$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin log -1 --format='%H%n%P%n%s'
exit=0
addeb57c5d717785a94105a2e36cc8a76940fb6c
bda324bbc5c1d7db93553adb13c5f380492c3c93
round-31 attempt 2: C3 — SKILL instrument-registry row for the round-29 counter (gate 8/1 exit 1 -> 9/0 exit 0), round-31 re-run receipt

$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin cat-file -e 382d11b2107d335705875da1a4d889b074bd6fa6^{commit}
exit=0
verbatim tail: (empty)

$ git -C /tmp/kama-r31w2/ExecC3Row/gate-clone rev-parse HEAD && git -C /tmp/kama-r31w2/ExecC3Row/counter-clone rev-parse HEAD && git -C /tmp/kama-r31w2/ExecC3Row/counter-clone cat-file -e 382d11b2107d335705875da1a4d889b074bd6fa6^{commit}
exit=0
addeb57c5d717785a94105a2e36cc8a76940fb6c
addeb57c5d717785a94105a2e36cc8a76940fb6c

$ git -C /tmp/kama-r31w2/ExecC3Row/gate-clone checkout --detach 382d11b2107d335705875da1a4d889b074bd6fa6
exit=0
HEAD is now at 382d11b round-31: SOURCES repair — S180-S191 relocated into ## Registry (census E12 exit 1 -> exit 0), lesson Mistakes row 4, census start/end receipts, two late seat artifacts

$ /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gate-registry-check.py --repo /tmp/kama-r31w2/ExecC3Row/gate-clone  [baseline, before row]
exit=1
unregistered .ufo/waves/round-29/count-c1.py
registered 8 unregistered 1

$ cp /tmp/kama-r31w2/ExecC3Row/gate-clone/SKILL.md /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecC3Row/SKILL.md
exit=0
verbatim tail: (empty)

$ cp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecC3Row/SKILL.md /tmp/kama-r31w2/ExecC3Row/gate-clone/SKILL.md
exit=0
verbatim tail: (empty)

$ /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gate-registry-check.py --repo /tmp/kama-r31w2/ExecC3Row/gate-clone  [row-bearing scratch copy]
exit=0
registered 9 unregistered 0

$ /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py --repo /tmp/kama-r31w2/ExecC3Row/counter-clone --tip addeb57c5d717785a94105a2e36cc8a76940fb6c --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecC3Row/counter-tip.json
exit=0
statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip addeb57c5d71
```
FINDING: The five-cell round-29 row is drafted in the copied SKILL.md; the scratch gate changed from `registered 8 unregistered 1` (exit 1) to `registered 9 unregistered 0` (exit 0). The fresh-clone counter run at `addeb57c5d717785a94105a2e36cc8a76940fb6c` exited 0; its receipt is `counter-tip.json`. The counter hash matches the pin, and the existing round-29 receipts are `before/c1-base.json` and `final/c1-6de225c2.json`.
LIMITS: The registered gate compares path occurrence only; it does not validate the row's columns. The measured live HEAD was `addeb57c5d717785a94105a2e36cc8a76940fb6c`, while C3 was frozen at `382d11b2107d335705875da1a4d889b074bd6fa6`; the gate before/after comparison used a fresh scratch checkout of the frozen revision with only its working-tree SKILL.md copy modified. The counter's `met True` is the round-29 predicate, not evidence of C3 by itself. No LSP tool was exposed in this seat's tool inventory.
