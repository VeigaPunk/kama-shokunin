# Rev1 run notes (round 55, seat Rev1) — commands and artifacts

Everything below ran with `S=/fast/scratch/hyaku/kama-r55/w1/Rev1`, `TMPDIR=$S`,
inherited `GIT_*` unset. Frozen lane and counters read-only; no counter or preregistration
edited.

## Frozen inputs

    sha256sum kama-shokunin/tools/round54-replay-code-audit.py
    # c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af (== prereg C1 counter_sha256)
    sha256sum kama-shokunin/tools/round54-cited-path-check.py
    # d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c (== prereg C2)
    sed -n '2p' kama-shokunin/.ufo/waves/round-55/controls/base.c1.out
    # bind=1 ... newrow=0 ... met=False   (red base control)
    sed -n '2p' kama-shokunin/.ufo/waves/round-55/measured/c1-build.out
    # bind=1 ... newrow=1 ... met=True    (green build measurement at 9c60eae)

## Battery receipt headers (frozen directory)

    for f in control m-ldpreload m-text-flip m-member-flip m-ldaudit-foreign m-ldaudit-writable m-extra-in-tree; do
      printf '%-24s %s\n' "$f" "$(sed -n '2p' kama-shokunin/.ufo/waves/round-55/c1/battery/$f.out)"; done

    control.out              met=True
    m-ldpreload.out          envnames=0/3 met=False   (detail: env: server environment carries LD_PRELOAD)
    m-text-flip.out          code=0/3 rehash=3 met=False
    m-member-flip.out        rehash=3 met=False
    m-ldaudit-foreign.out    met=True     <-- frozen mutant expected to fail; passes
    m-ldaudit-writable.out   met=True     <-- stale arm, expected to fail; passes
    m-extra-in-tree.out      met=True     (not in the prereg mutant list)

## Probes (no archive, no network; the frozen counter imported as a module)

    python3 "$S/probe.py"    # probe.json   K1Cheat class (LD_PRELOAD + anon RWX), host-set gate, LD_AUDIT viability
    python3 "$S/probe2.py"   # probe2.json  LD_AUDIT is recorded but not in BAD_ENV; la_version + constructor run
    python3 "$S/probe3.py"   # probe3.json  clearenv()/unsetenv() does not remove LD_PRELOAD from /proc/pid/environ
    python3 "$S/probe4.py"   # probe4.json  root-owned in-set-basename audit plant is admitted (no problem line)
    python3 "$S/probe5.py"   # probe5.json  memfd-image emulation: envnames/hostlibs/anon/code all green with the plant

## End-to-end (frozen counter, own clone)

    git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
    git -C "$S/lane" reset --hard 9c60eae6f7ed84f7da93d219a406aadc30958c6c
    # fixture.patch: 3 lines in tools/kama-llamacpp-live.py child_env (LD_AUDIT + markers)
    git -C "$S/lane" -c user.name=fx -c user.email=fx@invalid commit -qam "fixture: ..."
    # tip 13d5ed99a8f4fa1220db4a66b3b5555e94a881ae
    python3 kama-shokunin/tools/round54-replay-code-audit.py --repo "$S/lane" \
      --tip 13d5ed99a8f4fa1220db4a66b3b5555e94a881ae --scratch "$S/ctr" --out "$S/c1-audit.out"
    # exit 0, met=True, envnames=3/3 hostlibs=3/3 anon=0, "14 root-owned host files"

Then the same tip with the plant rebuilt to also `mmap` an anonymous RWX page
(`audit_anon.c`, installed root-owned as `libzstd.so.1.5.7`):

    python3 kama-shokunin/tools/round54-replay-code-audit.py --repo "$S/lane" \
      --tip 13d5ed99a8f4fa1220db4a66b3b5555e94a881ae --scratch "$S/ctr2" --out "$S/c1-audit-anon.out"
    # exit 1, met=False, anon=6, code=0/3, hostlibs=3/3, envnames=3/3

## Cleanup

    sudo rm -f "$S/libzstd.so.1.5.7"; rm -rf "$S"
    pgrep -af llama-server   # only seat J5EnvNames' two processes; none from Rev1

No packages installed (pacman paused host-wide). System gcc (GCC 16.2.1) used to build the
probe libraries. `sudo` used only to chown/chmod and remove two scratch probe files.
