import sys
body = "B" * 420
sys.stderr.write("could-not-evaluate: internal: RuntimeError: " + body + "\n")
sys.exit(2)
