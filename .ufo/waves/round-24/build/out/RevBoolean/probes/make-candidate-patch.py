#!/usr/bin/env python3
"""Generate the candidate classification fragment as a real unified diff.

Reads the base file, applies the fragment, writes the candidate and the
diff, then checks that the diff applies to the base tree.  Nothing in the
lane tree is modified.
"""
import difflib
import shutil
import subprocess
from pathlib import Path

BASE_REPO = Path("/fast/scratch/hyaku/kama-r24/RevBoolean")
REL = "tools/report-landing-audit.py"
BASE = BASE_REPO / REL
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/"
           "build/out/RevBoolean")

OLD_BLOCK = '''    listing = git(repo, "config", "--null", "--list",
                  errors="surrogateescape")
    for entry in filter(None, listing.split("\\0")):
        key, _, value = entry.partition("\\n")
        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\\..+\\.promisor", key)
                and git_bool(value)):
            raise EvalError(f"{repo}: partial clone ({key})")
'''

NEW_BLOCK = '''    # r23 refused every promisor-marked repository here, which turned
    # complete local clones into could-not-evaluate.  The repository is
    # classified instead (promisor_backed); what a missing required object
    # means in a promisor-backed repository is the caller's decision.
'''

HELPERS = '''

def config_entries(repo):
    """(key, value) pairs from `git config --null --list`.

    git prints `key\\nvalue\\0` for a valued key and `key\\0` for a bare key
    (git's NULL value).  The distinction matters: a bare key is boolean
    true, an empty value is boolean false.  Every config scope git uses is
    included (repo-local, worktree, include.path files); global and system
    config are neutralized by git_env()."""
    listing = git(repo, "config", "--null", "--list",
                  errors="surrogateescape")
    for entry in filter(None, listing.split("\\0")):
        key, sep, value = entry.partition("\\n")
        yield key, (value if sep else None)


def git_bool_value(value):
    """git's boolean spelling (config.c git_parse_maybe_bool_text, then
    git_parse_int).  True, False, or None when git itself rejects the value
    (git dies with "bad boolean config value"); None must never be read as
    false: an unreadable boolean is unknown, not a denial."""
    if value is None:
        return True          # git's NULL value: a bare key is true
    if value == "":
        return False         # git_parse_maybe_bool_text("") is 0
    low = value.lower()
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    if re.fullmatch(r"[+-]?(0[xX][0-9a-fA-F]+|0[0-7]*|[1-9][0-9]*)", value):
        try:
            return int(value, 0) != 0
        except ValueError:
            return None
    return None


def promisor_backed(repo):
    """True when git would treat this repository as having a promisor
    remote, i.e. when a missing object might still be obtainable and its
    absence is therefore not evidence.

    git registers a promisor remote when
      * remote.<name>.promisor is a true boolean
        (promisor-remote.c promisor_remote_config, promisor_remote_new),
      * remote.<name>.partialclonefilter is set, even without
        remote.<name>.promisor (same function, filter branch), or
      * extensions.partialclone names a remote and
        core.repositoryformatversion is present (promisor_remote_init;
        setup.c read_repository_format discards the extension when the
        format version key is absent).

    Returns (promisor_backed, reasons).  An unreadable boolean yields
    promisor_backed True with the reason recorded: unknown is not absence.
    """
    reasons = []
    promisor = False
    format_version = False
    partialclone = None
    for key, value in config_entries(repo):
        if key == "core.repositoryformatversion":
            format_version = True
        elif key == "extensions.partialclone":
            if value is None:
                raise EvalError(f"{repo}: extensions.partialclone needs a "
                                "value; git rejects this repository")
            partialclone = value
        elif re.fullmatch(r"remote\\..+\\.promisor", key):
            state = git_bool_value(value)
            if state is None:
                reasons.append(f"{key}: unreadable boolean {value!r}")
                promisor = True
            elif state:
                reasons.append(key)
                promisor = True
        elif re.fullmatch(r"remote\\..+\\.partialclonefilter", key):
            reasons.append(key)
            promisor = True
    if partialclone is not None and format_version:
        reasons.append(f"extensions.partialclone={partialclone}")
        promisor = True
    return promisor, reasons

'''

text = BASE.read_text()
assert OLD_BLOCK in text, "base block not found"
new_text = text.replace(OLD_BLOCK, NEW_BLOCK, 1)
# insert the helpers right before grafts_effective
anchor = "\ndef grafts_effective(path):"
assert anchor in new_text
new_text = new_text.replace(anchor, HELPERS + anchor, 1)

cand = OUT / "candidate" / REL
cand.parent.mkdir(parents=True, exist_ok=True)
cand.write_text(new_text)

diff = difflib.unified_diff(
    text.splitlines(keepends=True), new_text.splitlines(keepends=True),
    fromfile=f"a/{REL}", tofile=f"b/{REL}", n=3)
body = "".join(diff)
header = (
    "CANDIDATE PATCH FRAGMENT — round-24, lane RevBoolean (reviewer).\n"
    "NOT APPLIED to the lane tree; L1 owns production files.\n"
    "Base: 0df800e896f6bce285a81e794ad4ae1d1e6c3a71 (tools/report-landing-audit.py)\n"
    "\n"
    "What this fragment does\n"
    "  * a git-faithful reader of `git config --null --list` entries that keeps\n"
    "    git's NULL value (a bare key) distinct from an empty value;\n"
    "  * a git-faithful boolean parser that returns None for a value git itself\n"
    "    rejects (git dies on it) instead of coercing it to false/true;\n"
    "  * promisor_backed(repo): the classification git itself uses (does the\n"
    "    repository have at least one promisor remote);\n"
    "  * removal of the r23 wholesale refusal of promisor-marked repositories.\n"
    "\n"
    "What this fragment deliberately does NOT do\n"
    "  * the policy for a missing required object in a promisor-backed\n"
    "    repository (exit 2 vs. verdict) is left to the integrator under\n"
    "    preregistration.json expected_after[2..4];\n"
    "  * GIT_ISOLATION, fetch/signature suppression, deadlines and everything\n"
    "    outside the classification are untouched.\n"
    "\n"
    "Evidence: .ufo/waves/round-24/build/out/RevBoolean/ (see advice/RevBoolean.md).\n"
    "\n")
(OUT / "candidate-classification-fragment.patch").write_text(header + body)

# verify the diff applies to the base tree
check = BASE_REPO / "applycheck"
if check.exists():
    shutil.rmtree(check)
shutil.copytree(BASE_REPO, check, symlinks=True,
                ignore=shutil.ignore_patterns(".git"))
p = subprocess.run(["git", "apply", "--check", "-p1",
                    str(OUT / "candidate-classification-fragment.patch")],
                   cwd=check, capture_output=True, text=True)
print("git apply --check rc:", p.returncode, p.stderr.strip()[:300])
print("patch bytes:", len(header + body))
