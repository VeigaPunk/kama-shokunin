from pathlib import Path

src = Path("tools/report-landing-audit.py").read_text()

# 1) collect tokens whose PEEL failed, per store (not "the object is
#    present in some audited store").
old_a = (
    '            if line.endswith(" missing"):\n'
    '                if (bare is not None and bare[token] == "found"\n'
    '                        and status[token] == "absent"):\n'
    '                    unresolved.append(token)\n'
    '                continue\n'
)
new_a = (
    '            if line.endswith(" missing"):\n'
    '                unresolved.append(token)\n'
    '                continue\n'
)
assert old_a in src, "anchor A missing"
src = src.replace(old_a, new_a, 1)

# 2) before the deref probe, keep only the tokens THIS store holds bare.
old_b = (
    '        if unresolved:\n'
    '            # the object is here; ask whether what it dereferences to is\n'
)
new_b = (
    '        if unresolved:\n'
    '            # PER-STORE presence: the object must be present in THIS\n'
    '            # store before its peel failure makes this store\'s answer\n'
    '            # "unknown".  A token that only another audited store\n'
    '            # holds is that store\'s business (a proved wrong type),\n'
    '            # not an unavailable object here.\n'
    '            here = git(store.path, "cat-file", "--batch-check",\n'
    '                       stdin="".join(f"{t}\\n" for t in unresolved))\n'
    '            here_lines = here.split("\\n")[:len(unresolved)]\n'
    '            if len(here_lines) != len(unresolved):\n'
    '                raise EvalError(f"cat-file --batch-check in "\n'
    '                                f"{store.path}: short output")\n'
    '            unresolved = [t for t, l in zip(unresolved, here_lines)\n'
    '                          if not l.endswith(" missing")\n'
    '                          and not l.endswith(" ambiguous")\n'
    '                          and not l.endswith(" excluded")\n'
    '                          and not l.endswith(" dangling")]\n'
    '        if unresolved:\n'
    '            # the object is here; ask whether what it dereferences to is\n'
)
assert old_b in src, "anchor B missing"
src = src.replace(old_b, new_b, 1)

Path("probe/fixed-auditor.py").write_text(src)
print("patched")
