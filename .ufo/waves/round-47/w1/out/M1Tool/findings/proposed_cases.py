#!/usr/bin/env python3
"""Proposed selftest cases for the three C1 survivors (B2, K2, S1).

Additions to tools/append-only-audit.py's selftest() case list (suggested for a
future round; the round-47 counter is frozen and must not change). Each follows
the existing case pattern (lines(), Fixture, audit, asserts). Validation: each
case passes on the pristine tool and FAILS on the corresponding mutant.
"""

# ---- B2: CRLF line deleted in a >=20 event and restored byte-exact must count
def t_crlf_restore_exact():
    f = Fixture(root)
    plain = [f"p{i} {os.urandom(3).hex()}" for i in range(30)]
    crl = b"crlf line\r\n"
    base = ("\n".join(plain) + "\n").encode()
    f.commit({"LOG.md": base + crl}, raw=True)
    c = f.commit({"LOG.md": ("\n".join(plain[:10]) + "\n").encode()}, raw=True)
    t = f.commit({"LOG.md": base + crl}, raw=True)          # restore all byte-exact
    res = audit(f.d, t, files=F)
    e = res["events"]
    return (len(e) == 1 and e[0]["commit"] == c and e[0]["deleted"] == 21
            and e[0]["restored_max"] == 21 and e[0]["status"] == "restored"), str(e)


# ---- K2: 2 of 3 duplicate copies deleted in one event, kept copy must not count
def t_dup_kept_not_restored():
    f = Fixture(root)
    a = lines("a", 30) + ["dup"] * 3
    f.commit({"LOG.md": a})
    t = f.commit({"LOG.md": a[:10] + ["dup"]})              # 20 plain + 2 dup deleted
    res = audit(f.d, t, files=F)
    e = res["events"]
    return (len(e) == 1 and e[0]["deleted"] == 22 and e[0]["restored_max"] == 0
            and e[0]["status"] == "unrestored"), str(e)


# ---- S1: final-segment rule: only the split artifact after a last newline is dropped
def t_split_lines_final_segment():
    return (split_lines(b"x\n") == [b"x"] and split_lines(b"x") == [b"x"]
            and split_lines(b"a\n\n") == [b"a", b""] and split_lines(b"") == []
            and split_lines(b"a\r\n") == [b"a\r"]), ""
