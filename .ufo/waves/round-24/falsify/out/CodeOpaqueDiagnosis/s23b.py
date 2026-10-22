import importlib.util, json, subprocess, sys
from pathlib import Path
sys.path.insert(0, ".")
from probe import (AUDIT, ROOT, WORK, base_env, body_for, build, drop, g,
                   republish, FAKE)
SPEC = importlib.util.spec_from_file_location("a", AUDIT)
M = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(M)
d = WORK / "s23"
import shutil
if d.exists(): shutil.rmtree(d)
d.mkdir(parents=True)
lane, fleet, info = build(d)
tree = g(lane, "rev-parse", f"{info['first']}^{{tree}}")
gone = subprocess.run(["git", "-C", str(lane), "commit-tree", tree, "-m", "x"],
                      capture_output=True, text=True,
                      env=base_env(GIT_AUTHOR_DATE="@900 +0000",
                                   GIT_COMMITTER_DATE="@900 +0000")).stdout.strip()
g(lane, "tag", "-a", "-m", "hole", "v-hole", gone,
  env=base_env(GIT_AUTHOR_DATE="@910 +0000", GIT_COMMITTER_DATE="@910 +0000"))
tag = g(lane, "rev-parse", "v-hole")
drop(lane, gone)
body = body_for(info["required"]).replace("## Landed changes\n", "## Landed changes\n- `%s`\n" % tag)
republish(fleet, info, body)
env = base_env(); env["TMPDIR"] = str(WORK / "tmp")
p = subprocess.run([sys.executable, str(AUDIT), "--lane-repo", str(lane),
                    "--fleet-repo", str(fleet), "--branch", "master",
                    "--lane", "kama", "--rounds", "1", "--json"],
                   capture_output=True, text=True, env=env, cwd=str(WORK))
print("S23 known tag with unavailable target -> rc=", p.returncode)
print("   stderr:", p.stderr.strip())

