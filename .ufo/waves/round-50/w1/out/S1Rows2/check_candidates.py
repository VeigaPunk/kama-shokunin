import html, re, pathlib
R = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50")
def norm(t): return re.sub(r"\s+", " ", t).strip()
PDE = norm((R/"c1/PR_SET_PDEATHSIG.2const.txt").read_text())
MAPS = norm((R/"c1/proc_pid_maps.5.txt").read_text())
CM = norm((R/"c2/commonmark-0.31.2-s4.5.txt").read_text())
cands = {
 "PDE-a": (PDE, "The parent-death signal is sent upon subsequent termination of the parent thread and also upon termination of each subreaper process"),
 "PDE-b": (PDE, "The parent-death signal setting is cleared for the child of a fork(2)."),
 "PDE-c": (PDE, "The parent-death signal is process-directed (see signal(7))"),
 "CM-a": (CM, "A fenced code block begins with a code fence, preceded by up to three spaces of indentation."),
 "CM-b": (CM, "The content of a code fence is treated as literal text, not parsed as inlines."),
 "CM-c": (CM, "The closing code fence must use the same character as the opening fence:"),
 "CM-d": (CM, "The closing code fence must be at least as long as the opening fence:"),
 "CM-e": (CM, "A code fence is a sequence of at least three consecutive backtick characters (`) or tildes (~)."),
 "MAPS-a": (MAPS, "0 indicates that no inode is associated with the memory region"),
}
for k,(hay,q) in cands.items():
    print(f"{k:7} words={len(q.split()):>2} verbatim={q in hay} :: {q}")
# entity form decodes to CM-e?
ent = html.unescape("A code fence is a sequence of at least three consecutive backtick characters (&#96;) or tildes (~).")
print("entity-decodes-equal:", ent == cands["CM-e"][1], "words=", len(ent.split()))
