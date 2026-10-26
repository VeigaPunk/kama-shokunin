import os, shutil, subprocess, sys
LANE="/home/vgpnk/Projects/shokunin/kama-shokunin"; FREEZE="5790944350ae41bfe2ce50934bba59e086e747f4"
UP="/fast/scratch/hyaku/kama-r46/L1/llama.git"
D="/fast/scratch/hyaku/kama-r46/K1Cheat/lane-fix"
shutil.rmtree(D,ignore_errors=True)
subprocess.run(["git","clone","-q","--shared","--no-checkout",LANE,D],check=True)
subprocess.run(["git","-C",D,"checkout","-q","--detach",FREEZE],check=True)
top=subprocess.run(["git","-C",D,"rev-parse","--show-toplevel"],capture_output=True,text=True).stdout.strip()
assert os.path.realpath(top)==os.path.realpath(D), top
# ledger
os.makedirs(os.path.join(D,"registry"),exist_ok=True)
shutil.copy("ledger-all.tsv",os.path.join(D,"registry/release-recheck-b11906.tsv"))
# SOURCES: heading-only section + a newrow that only names the strings
src=open(os.path.join(D,"corpus/SOURCES.md")).read()
src += ("\n## Round-46 release re-verification\n\n"
        "| S999 | llama.cpp @ b11906 4d71b42fd87db24b8b7c808c151b713aa4459cfd |\n")
open(os.path.join(D,"corpus/SOURCES.md"),"w").write(src)
subprocess.run(["git","-C",D,"add","-A"],check=True)
subprocess.run(["git","-C",D,"-c","user.name=r46-k1cheat-fixture","-c","user.email=k1cheat@fixture.invalid",
                "-c","commit.gpgsign=false","commit","-qm","vacuous section + string-only newrow + mechanical ledger"],check=True)
tip=subprocess.run(["git","-C",D,"rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()
p=subprocess.run([sys.executable,os.path.join(D,"tools/round46-release-recheck-audit.py"),"--repo",D,"--tip",tip,
                  "--upstream",UP,"--out","/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K1Cheat/fixture-full.c1.out"],
                 capture_output=True,text=True)
print("tip",tip); print("rc",p.returncode); print(p.stdout[:1200]); print("STDERR",p.stderr[:300])
