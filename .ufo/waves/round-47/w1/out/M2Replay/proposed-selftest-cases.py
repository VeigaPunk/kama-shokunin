# Proposed --selftest additions for tools/kama-live-replay.py (round-47, M2Replay).
#
# The tool is FROZEN for this wave; this file is a proposal, not an applied edit.
# Each case kills a mutant that survived the current 10-case selftest AND the
# frozen round47-live-replay-audit.py counter (see M2Replay.md).
#
# Line references are to kama-live-replay.py at lane commit
# 3a09a1d93dcc16799cf6c4b48786e6440af134c4 (pristine sha256
# 39cd387a3a95b47865d81484ffe30664e653d5016c4c75d47abf6e855e43fdd0).

# ---------------------------------------------------------------------------
# Change 1: make run() able to assert that nothing was extracted on refusal
# (kills m02: model digest verified only after extract(archive, tree), L143-144)
# ---------------------------------------------------------------------------
# In _selftest(), extend the local run() helper:
#
#   def run(name, rp, want_exit, want_refused=None, live=fake_live, no_extract=False):
#       w = os.path.join(d, f"w-{len(cases)}")
#       res, code = replay(rp, w, live=live)
#       ok = code == want_exit and (want_refused is None or (res["refused"] or "").startswith(want_refused))
#       if no_extract and os.path.exists(os.path.join(w, "server")):
#           ok = False  # something was extracted before the digest was verified
#       cases.append((name, ok, f"exit={code} refused={res['refused']} mism={res['mismatches']}"))
#
# and set no_extract=True on the two existing digest-refusal cases:
#   run("model-digest-wrong", ..., 2, "digest-mismatch:m.gguf", no_extract=True)
#   run("asset-digest-wrong", ..., 2, "digest-mismatch:srv", no_extract=True)

# ---------------------------------------------------------------------------
# Change 2: new case — digest refusal must win over extraction even when the
# downloaded bytes are not a tar at all
# (kills m03: archive extracted before its digest is verified, L141-144)
# ---------------------------------------------------------------------------
#   bad = os.path.join(d, "not-a-tar.bin")
#   with open(bad, "wb") as fh:
#       fh.write(b"this is not a tar archive, deliberately")
#   run("asset-digest-wrong-unextractable",
#       receipt(**{"provenance.server.asset_url": "file://" + bad,
#                  "provenance.server.asset_sha256": "1" * 64}),
#       2, "digest-mismatch:srv", no_extract=True)
# Pristine: refused digest-mismatch before tarfile.open. m03: extraction first ->
# could-not-run:ReadError (prefix mismatch) and the case fails.

# ---------------------------------------------------------------------------
# Change 3: new case — a traversal member inside the archive must be refused by
# the extraction filter
# (kills m07: tf.extractall(into, filter=None) at L100)
# ---------------------------------------------------------------------------
#   arc_trav = os.path.join(d, "trav.tar.gz")
#   with tarfile.open(arc_trav, "w:gz") as tf:
#       tf.add(os.path.join(d, "src", "build"), arcname="build")
#       esc = os.path.join(d, "escape.txt")
#       with open(esc, "w") as fh:
#           fh.write("x")
#       tf.add(esc, arcname="../escape.txt")   # parent traversal member
#   run("traversal-member-refused",
#       receipt(**{"provenance.server.asset_url": "file://" + arc_trav}),
#       2, "could-not-run")
# Pristine: tarfile.data_filter raises (OutsideDestinationError) -> refused.
# m07: escape.txt extracted, replay matches -> exit 0 -> case fails.

# ---------------------------------------------------------------------------
# Change 4: new case — the executed member must resolve inside the extraction
# tree (combo guard for m07+m08)
# ---------------------------------------------------------------------------
#   arc_sym = os.path.join(d, "sym.tar.gz")
#   bindir = os.path.join(d, "sym", "build", "bin")
#   os.makedirs(bindir)
#   os.symlink("/bin/sh", os.path.join(bindir, "llama-server"))  # absolute symlink
#   with tarfile.open(arc_sym, "w:gz") as tf:
#       tf.add(os.path.join(d, "sym", "build"), arcname="build")
#   run("symlink-member-refused",
#       receipt(**{"provenance.server.asset_url": "file://" + arc_sym,
#                  "provenance.server.member": "build/bin/llama-server"}),
#       2, None)   # pristine: could-not-run (data_filter); m07+m08: exit 0 match
# Kills only the combination m07 (filter disabled) + m08 (realpath gate removed,
# L146); each single mutant is still caught by Change 3 / stays latent.

# ---------------------------------------------------------------------------
# Change 5: make the fake live tool's emitted receipt configurable, then add
# five compare-rule cases (kills m10-m14, compare() L108-124)
# ---------------------------------------------------------------------------
# Replace the fixed fake_live string with one that honours an env spec:
#
#   spec_path = os.path.join(d, "fake-spec.json")
#   with open(spec_path, "w") as fh:
#       json.dump({}, fh)
#   fake_live = os.path.join(d, "fake-live.py")
#   with open(fake_live, "w") as fh:
#       fh.write(
#           "import json,sys,hashlib,os\n"
#           "a=sys.argv;o=a[a.index('--out')+1];s=a[a.index('--server')+1];m=a[a.index('--model')+1]\n"
#           "h=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()\n"
#           "sp=json.load(open(os.environ['KLR_FAKE_SPEC']))\n"
#           "json.dump({'schema':sp.get('schema','kama-llamacpp-live/v4'),'outcome':sp.get('outcome','pass'),"
#           "'server':{'sha256':h(s) if not sp.get('server_sha') else sp['server_sha']},"
#           "'model':{'sha256':h(m) if not sp.get('model_sha') else sp['model_sha']},"
#           "'checks':sp.get('checks',[{'id':'health_ready','passed':True,'evaluated':True}])},open(o,'w'))\n")
#
# and pass env={"KLR_FAKE_SPEC": spec_path} through replay() into the live
# subprocess (replay() already builds env; expose an optional env override
# parameter). Then the five cases:
#
#   def spec(**kv):
#       with open(spec_path, "w") as fh:
#           json.dump(kv, fh)
#
#   spec(schema="kama-llamacpp-live/v3")
#   run("rerun-schema-differs", receipt(), 1, None)          # wants mismatch "schema:..."
#   spec(outcome="fail")
#   run("rerun-outcome-differs", receipt(), 1, None)         # wants mismatch "outcome:..."
#   spec(server_sha=msha)
#   run("rerun-server-sha-differs", receipt(), 1, None)      # wants "server.sha256:..."
#   spec(model_sha=asha)
#   run("rerun-model-sha-differs", receipt(), 1, None)       # wants "model.sha256:..."
#   spec(checks=[])
#   run("rerun-missing-check", receipt(), 1, None)           # wants "check:health_ready:not-evaluated"
#   spec()  # restore default
#
# Pristine: each exits 1 with the named mismatch. m10/m11/m12/m13/m14 each omit
# exactly one comparison -> exit 0 -> case fails. (Tighten by asserting the
# mismatch prefix in res["mismatches"][0] if desired.)

# ---------------------------------------------------------------------------
# Change 6: new case — non-hex digest in provenance must be refused before any
# fetch (distinguishes m23: HEX64 loop removed, L78-80)
# ---------------------------------------------------------------------------
#   run("non-hex-digest-refused",
#       receipt(**{"provenance.model.sha256": "z" * 64, "model.sha256": "z" * 64}),
#       2, "provenance-bad-digest")
# Pristine: refused provenance-bad-digest:model.sha256 without network I/O.
# m23: fetches the model first, then refuses digest-mismatch (prefix mismatch).
# Behavioural delta beyond the prefix: the mutant performs a network fetch on
# malformed provenance before refusing.
