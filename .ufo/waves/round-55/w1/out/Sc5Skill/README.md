# Sc5Skill — round-55 SKILL.md instrument-registry addition

Seat: Sc5Skill (round-55 w1, lane kama). Deliverable: the paste-ready
`## Round-55 instrument registry` section for the lane's SKILL.md, plus the
placement, the proposed diff, the integrity hashes and a fixture re-check of the
addition against the frozen round-55 C2 counter.

No lane file was written. Everything here is a proposal.

## Placement

Append **after `SKILL.md:1600`** (the file's last line is the `Seat-report immutability`
row). One blank line separates the new section from the Round-54 table. The anchor
header being appended after is `SKILL.md:1592`:

    ## Round-54 instrument registry (hardened code-identity and cited-path counters, seat-report immutability)

Its table header is `SKILL.md:1596` and its last row `SKILL.md:1600`; `wc -l SKILL.md`
= 1600 and the file ends with a newline.

## Files

| File | sha256 | What |
|---|---|---|
| `registry-round55.md` | `a4b682db6747b422d0e61db5497a238a71ea201d1a42a532bcf89e0db0bcf825` | paste-ready section (36 lines: header, preamble, 5-column table with 4 rows, two prose paragraphs) |
| `proposed-skill-append.diff` | — | `diff -u` of `SKILL.md` → `SKILL.md` + one blank line + the section (hunk `@@ -1598,3 +1598,40 @@`) |
| `proposed-harness-summary.diff` | — | optional, future-round only: tee the battery summary to `.ufo/waves/round-55/c1/battery/summary.out`; validates with `patch -p1 --dry-run` rc 0 against the committed harness |
| `receipts/` | see below | copies of every receipt the section cites, plus the addition re-check |

Row shape follows `SKILL.md:1596` (`| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |`); pipes inside cells are escaped `\|` as in the round-53/54 rows.

## Addition re-check (frozen C2 counter, fixture only)

    git clone --shared <lane> $S/lane
    cp registry-round55.md-append $S/lane/SKILL.md
    git -C $S/lane -c user.name=fx -c user.email=fx@invalid commit
    python3 tools/round54-cited-path-check.py --repo $S/lane --tip dd03f2b6 --scratch $S/c2check3 \
        --out receipts/c2-addition-check.out

    tip=dd03f2b6a8de7e8b0f0310c272574907ff944e98 fleet=666bc1efcddd4b711173f23def3278cfe54a418f
    fixture=1 lane=1 scenarios=15/15 cited=710 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
    rc=0

`cited` rises 693 → 710: the section adds 17 distinct cited tokens and none is
unresolved, undisclosed, bad, stale or dropped. `fleet=` is that repository's HEAD
(666bc1ef), not the build receipt's 6c4aba34 — see the limits paragraph in the section
and finding F4 in the report.

## Receipt copies

    d38418f908dc13de3ecc8ed882db341f74da2f620e727d505a9cd3a8e3a81b62  preregistration.json
    3d6736a39a5ef881c23e63da3e21cf6246aa4a37739d6d45cff0316f0fdf0794  base.c1.out
    d6a6f550e558156b16d69fb88196a51b61b913df043e68032172f3f6a5a53828  base.c2.out
    4f8f277b04b11861b5e45664db6c97fea9a078431c4e450ae89b846e893331b6  c1-build.out
    bc59e5e186c316a8f6783531d08cbd4c545de859cb4e1afac994357c396ed3bc  c2-build.out
    8f8bbf60bffd90a27c8e4ca6b844309026d2151fe534a5a762d64cc9b27a85b9  control.out
    ea80b60c8052a44b75cfd50485cc5e56a017226931f521c1c233b3a89d121c76  m-ldpreload.out
    a71864026f119c145cc847625e5fa6afaa6937516138a2fc3901ab55835d6e47  m-text-flip.out
    3177300bf5b984ff729f655e5e6b0bb33fe0b1b5a1771f3fb5043ee76a790036  m-member-flip.out
    4ef002955c60b91c0b0d7c57f27687fda00801d3e568654c86d65759eb589d35  m-ldaudit-foreign.out
    ead1173777919775974f517267c3c423c8045d4a04307f5f274f7a04395ab949  m-ldaudit-writable.out
    0ff496d245be1c4af01a80b255a1d69a17724e193a1c107cc793439234efefca  m-extra-in-tree.out
    b9dbec9dc83ad1fd19e34593613e58bf9fe58194fcedd8fe15d5c8d6cf009f15  c2-addition-check.out   (produced here)
