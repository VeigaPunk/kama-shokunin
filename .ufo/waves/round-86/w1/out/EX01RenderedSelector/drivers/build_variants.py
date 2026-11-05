#!/usr/bin/env python3
"""EX01RenderedSelector fixture driver: commit one SCORECARD variant per
shadow construct in the scratch fixture repo and record the frozen selector's
verdict for each. Run with cwd = fixture repo; RECEIPTS env set; TMPDIR inside scratch."""
import os
import pathlib
import subprocess
import sys

RECEIPTS = pathlib.Path(os.environ["RECEIPTS"])
R = "c07e1f909414aafb2d8de5605a81fd3bd4e3550e"  # freeze commit, ancestor of every fixture commit

GATE85 = "PRE_REPORT round=85 arms=13 failed=1 uncommitted=0"
GATE84 = "PRE_REPORT round=84 arms=13 failed=0 uncommitted=0"
CMD85 = "`python3 tools/pre-report-gate.py --repo . --round 85 --tip master`"
CMD84 = "`python3 tools/pre-report-gate.py --repo . --round 84 --tip master`"
RCPT85 = "`.ufo/waves/round-85/measured/after/gate.out`"
RCPT84 = "`.ufo/waves/round-84/measured/after/gate-final-green.out`"
CLOSE85 = "`corpus/lessons/round-85-verifier-spotcheck.md`"
CLOSE84 = "`corpus/lessons/round-84-verifier-spotcheck.md`"

AUTH85 = (f"**Current authority (round 85):** assigned axes are operability + calibration; "
          f"Latest measured round: 85. Terminal gate measured at `{R}`: {CMD85} printed "
          f"`{GATE85}`, exit0; receipt {RCPT85}.")
AUTH84 = (f"**Current authority (round 84):** assigned axes are operability + calibration; "
          f"Latest measured round: 84. Terminal gate measured at `{R}`: {CMD84} printed "
          f"`{GATE84}`, exit0; receipt {RCPT84}.")
ROW85 = (f"| calibration | **7** | terminal `SELFRECORD_R85` at `{R}`; latest outside closure "
         f"{CLOSE85} (round85 rejected-honest-stop) | score round1 |")
ROW84 = (f"| calibration | **7** | terminal `SELFRECORD_R84` at `{R}`; latest outside closure "
         f"{CLOSE84} (round84 rejected-honest-stop) | score round1 |")

SUPPORT = {
    ".ufo/waves/round-85/measured/after/gate.out": GATE85 + "\n",
    ".ufo/waves/round-84/measured/after/gate-final-green.out": GATE84 + "\n",
    "corpus/lessons/round-85-verifier-spotcheck.md":
        "# kama round 85 verifier spot-check\n\nVerdict: rejected-honest-stop.\n",
    "corpus/lessons/round-84-verifier-spotcheck.md":
        "# kama round 84 verifier spot-check\n\nVerdict: rejected-honest-stop.\n",
}


def fence3(opener="```", closer=None):
    closer = closer if closer is not None else "```"
    return lambda text: f"{opener}\n{text}\n{closer}"


def comment_block():
    return lambda text: "<!--\nscratch filler line\n" + text + "\n-->"


def comment_tail():
    # closer line carries the cell flush after --> : the whole line is inside the
    # HTML block per CommonMark 4.6, but rendered() keeps the split tail at column 0
    return lambda text: "<!--\nscratch filler line\n-->" + text


def comment_inline():
    return lambda text: "Scratch preamble prose <!-- " + text + " --> scratch trailing prose."


def comment_inline_flush():
    return lambda text: "<!--scratch-->" + text


def indent4():
    return lambda text: "    " + text


def fence_in_comment():
    return lambda text: "<!--\n```\n" + text + "\n```\n-->"


def comment_in_fence():
    return lambda text: "```\n<!-- " + text + " -->\n```"


def unclosed_fence():
    return lambda text: "```\n" + text


def unclosed_comment():
    return lambda text: "<!--\n" + text


def wrong_char_close():
    return lambda text: "~~~\n" + text + "\n```"


def info_backtick_fence():
    return lambda text: "``` `x` \n" + text + "\n```"


# name, auth shadow wrap, row shadow wrap, live auth, live row, placement
VARIANTS = [
    ("V00-baseline-stale", None, None, AUTH84, ROW84, "plain"),
    ("V01-green-control", None, None, AUTH85, ROW85, "plain"),
    ("V02-fence3", fence3(), fence3(), AUTH84, ROW84, "plain"),
    ("V03-fence3-info", fence3("```markdown"), fence3("```markdown"), AUTH84, ROW84, "plain"),
    ("V04-fence4-info", fence3("````text", "````"), fence3("````text", "````"), AUTH84, ROW84, "plain"),
    ("V05-tilde", fence3("~~~", "~~~"), fence3("~~~", "~~~"), AUTH84, ROW84, "plain"),
    ("V06-fence3-closed-by-4", fence3("```", "````"), fence3("```", "````"), AUTH84, ROW84, "plain"),
    ("V07-unclosed-fence-before", unclosed_fence(), unclosed_fence(), AUTH84, ROW84, "plain"),
    ("V08-unclosed-fence-after", unclosed_fence(), unclosed_fence(), AUTH84, ROW84, "after"),
    ("V09-comment-multiline", comment_block(), comment_block(), AUTH84, ROW84, "plain"),
    ("V10-comment-single-line", comment_inline(), comment_inline(), AUTH84, ROW84, "plain"),
    ("V10b-comment-inline-flush", comment_inline_flush(), comment_inline_flush(), AUTH84, ROW84, "plain"),
    ("V11-indent4", indent4(), indent4(), AUTH84, ROW84, "plain"),
    ("V12-correction-section-eof", "correction-eof", None, AUTH84, ROW84, "correction-eof"),
    ("V12b-correction-before-live", "correction-eof", None, AUTH84, ROW84, "correction-before"),
    ("V13-fence-in-comment", fence_in_comment(), fence_in_comment(), AUTH84, ROW84, "plain"),
    ("V14-comment-in-fence", comment_in_fence(), comment_in_fence(), AUTH84, ROW84, "plain"),
    ("V15-blockquote", lambda t: "> " + t, lambda t: "> " + t, AUTH84, ROW84, "plain"),
    ("V16-comment-closer-tail", comment_tail(), comment_tail(), AUTH84, ROW84, "plain"),
    ("V17-unclosed-comment-before", unclosed_comment(), unclosed_comment(), AUTH84, ROW84, "plain"),
    ("V18-green-with-fenced-stale", fence3(), fence3(), AUTH85, ROW85, "stale-shadow"),
    ("V19-tilde-closed-by-backtick", wrong_char_close(), wrong_char_close(), AUTH84, ROW84, "plain"),
    ("V20-info-contains-backtick", info_backtick_fence(), info_backtick_fence(), AUTH84, ROW84, "plain"),
]

# the correctness bar each verdict is judged against (exit, mismatches, rationale)
EXPECT = {
    "V00-baseline-stale": (1, 3, "stale live cells, no shadow"),
    "V01-green-control": (0, 0, "valid live cells reach green"),
    "V02-fence3": (1, 3, "fenced shadow is not rendered"),
    "V03-fence3-info": (1, 3, "info-string fence shadow is not rendered"),
    "V04-fence4-info": (1, 3, "4-tick fence shadow is not rendered"),
    "V05-tilde": (1, 3, "tilde fence shadow is not rendered"),
    "V06-fence3-closed-by-4": (1, 3, "longer same-char run closes the fence"),
    "V07-unclosed-fence-before": (2, None, "unclosed fence swallows live cells; fail closed"),
    "V08-unclosed-fence-after": (1, 3, "trailing unclosed fence hides shadow only"),
    "V09-comment-multiline": (1, 3, "comment block shadow is not rendered"),
    "V10-comment-single-line": (1, 3, "one-line inline comment shadow is not rendered"),
    "V10b-comment-inline-flush": (1, 3, "flush one-line comment shadow is not rendered"),
    "V11-indent4": (1, 3, "indented code shadow is never a column-0 cell"),
    "V12-correction-section-eof": (1, 3, "correction-section shadow is history, not live"),
    "V12b-correction-before-live": (2, None, "correction section before live cells swallows them; fail closed"),
    "V13-fence-in-comment": (1, 3, "comment swallows the fence wholesale"),
    "V14-comment-in-fence": (1, 3, "fence swallows the comment wholesale"),
    "V15-blockquote": (1, 3, "blockquote is never a column-0 cell"),
    "V16-comment-closer-tail": (1, 3, "CommonMark 4.6: the whole closer line sits inside the comment"),
    "V17-unclosed-comment-before": (2, None, "unclosed comment swallows live cells; fail closed"),
    "V18-green-with-fenced-stale": (0, 0, "stale fence before valid live cells must not become live"),
    "V19-tilde-closed-by-backtick": (2, None, "wrong-char closer cannot close; runs to EOF"),
    # CommonMark 4.4: an info string containing a backtick is NOT a fence, the lines
    # render as paragraph/code-span text, so a fully valid shadow WOULD be live; the
    # instrument fences it away instead. Bar records the CommonMark reading; the run
    # shows the instrument's verdict and the note classifies the divergence.
    "V20-info-contains-backtick": (0, 0, "CommonMark 4.4: backtick in info string = no fence = rendered"),
}


def run(cmd, **kw):
    return subprocess.run(cmd, text=True, capture_output=True, **kw)


def main():
    rows = []
    for name, aw, rw, live_auth, live_row, placement in VARIANTS:
        parts = ["# fixture\n"]
        if placement == "correction-eof":
            parts += [live_auth, "", "## Axes\n", live_row, "",
                      "## round-85 correction\n\n" + AUTH85 + "\n\n" + ROW85, ""]
        elif placement == "correction-before":
            parts += ["## round-85 correction\n\n" + AUTH85, "", live_auth, "",
                      "## Axes\n", live_row, ""]
        elif placement == "after":
            parts += [live_auth, "", "## Axes\n", live_row, "",
                      aw(AUTH85), "", rw(ROW85), ""]
        elif placement == "stale-shadow":
            parts += [live_auth, "", aw(AUTH84), "", "## Axes\n", live_row, "", rw(ROW84), ""]
        else:
            if aw is not None:
                parts += [aw(AUTH85), ""]
            parts += [live_auth, "", "## Axes\n"]
            if rw is not None:
                parts += [rw(ROW85), ""]
            parts += [live_row, ""]
        score = "\n".join(parts).rstrip("\n") + "\n"

        pathlib.Path("SCORECARD.md").write_text(score)
        for path, text in SUPPORT.items():
            p = pathlib.Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        top = run(["git", "rev-parse", "--show-toplevel"])
        assert top.stdout.strip() == os.getcwd(), f"toplevel guard failed: {top.stdout.strip()!r} vs {os.getcwd()!r}"
        run(["git", "add", "-A"])
        c = run(["git", "-c", "user.name=EX01", "-c", "user.email=ex01@scratch.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-q", "-m", f"fixture {name}"])
        assert c.returncode == 0, f"commit failed for {name}: {c.stderr}"
        sha = run(["git", "rev-parse", "HEAD"]).stdout.strip()
        g = run([sys.executable, "tools/round86-rendered-cells.py", "--repo", ".", "--rev", sha])
        (RECEIPTS / f"{name}.out").write_text(g.stdout)
        (RECEIPTS / f"{name}.err").write_text(g.stderr)
        (RECEIPTS / f"{name}.sha").write_text(sha + "\n")
        lines = g.stdout.splitlines()
        line = lines[0] if lines else ""
        finding = lines[1] if len(lines) > 1 else ""
        mm = int(line.split("mismatches=")[1].split()[0]) if "mismatches=" in line else None
        want_exit, want_mm, why = EXPECT[name]
        ok = g.returncode == want_exit and (want_mm is None or mm == want_mm)
        rows.append((name, g.returncode, mm, ok, why))
        print(f"{'OK        ' if ok else 'DIVERGENT '} {name} exit={g.returncode} mismatches={mm} :: {line}")
        if finding:
            print(f"           finding: {finding}")
        if not ok:
            print(f"           bar: {why}")
    print("\n== summary (name, exit, mismatches, strict_ok) ==")
    for name, code, mm, ok, _ in rows:
        print(f"{name}\texit={code}\tmismatches={mm}\tstrict_ok={ok}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
