# V2Live evidence — round 48, kama C2 live tool v5 code review

Seat: V2Live-2. Lane commit under review: 380bcdff9c8af06997c482f6eb03db926a794a2b (base 33e005827742b29772b153cda036ec9f27f653be).
All commands run read-only against the lane or against my own clone
(`git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`, checkout of the tip commit, verified
`git rev-parse --show-toplevel` = the clone). No tool installs were needed (none performed).

## 1. Diff under review

    git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff 33e005827742b29772b153cda036ec9f27f653be \
        380bcdff9c8af06997c482f6eb03db926a794a2b -- tools/kama-llamacpp-live.py
    => 1 file changed, 128 insertions(+), 6 deletions(-)

Hunks (all reviewed): module docstring v5 paragraph (lines 30-43 at tip); SCHEMA_V5 + PINNED_MODEL_URL
constants (:70-71); verify_archive_member() (:193-219); parser description/help text (:1143, :1169-1182);
_provenance_selftest() (:1271-1305) wired into _selftest() (:1308-1311); argument-rule block in main()
(:1456-1479); v5 verify + schema bump in main() (:1556-1566).

## 2. Selftest at tip

    python3 $S/lane/tools/kama-llamacpp-live.py --selftest
    => selftest: ok; closed tcp6 listeners ::1:41287, ::ffff:127.0.0.1:40473   (exit 0)

## 3. Negative probes (stub server/model/archive in scratch; no server can start: every failing
case exits before install_tree/port pick/Popen — code order :1556 verify → :1567 install_tree → :1648 Popen)

Driver: scratch `driver.py` (deleted with scratch; transcript below). Stub server bytes `#!/bin/sh\nexit 0\n`,
stub model `model-bytes\n`, `good.tar.gz` = tar.gz whose member `llama-b/llama-server` holds the stub server
bytes, `other.tar.gz` = same member name holding `other-bytes\n`.

    == A-together: exit=2 receipt=False   stderr: provenance flags --server-asset-url, --server-asset-sha256, --server-member and --model-url must be given together   [one v4 flag alone]
    == B-https: exit=2 receipt=False      stderr: --server-asset-url must be an https:// URL   [http:// asset URL, other three flags present]
    == C-member: exit=2 receipt=False     stderr: --server-member must be a relative path without ..   [--server-member ../evil]
    == D-unpinned: exit=2 receipt=False   stderr: --model-url must be pinned to a 40-hex /resolve/<commit>/ revision (v5)   [--server-archive + resolve/main URL]
    == I-archive-alone: exit=2 receipt=False  stderr: provenance flags ... must be given together   [--server-archive with none of the four]
    == E-archmismatch: exit=2 receipt=True    schema=kama-llamacpp-live/v4 outcome=setup-error setup_error=provenance-archive-digest-mismatch port=None child_pid=None ownership=unproven
    == F-membermismatch: exit=2 receipt=True  schema=kama-llamacpp-live/v4 outcome=setup-error setup_error=provenance-member-digest-mismatch port=None child_pid=None ownership=unproven
    == J-v4-rules-ok: exit=2 receipt=True     schema=kama-llamacpp-live/v4 outcome=setup-error setup_error=model-digest-mismatch   [all four flags, https, safe member, NO --server-archive, unpinned model URL: argument rules ACCEPTED, run proceeds to the model-digest check]
    SUMMARY: 8 / 8 passed

E/F receipts (copied here as neg-run-E-archmismatch.json / neg-run-F-membermismatch.json): server.realpath
null, no server.sha256, no provenance.verified, no provenance.model.commit — i.e. the schema label "v4" on a
v5-attempt setup-error receipt matches the receipt's actual shape, and kama-live-replay.py:227-229 refuses
receipts whose server.sha256 is not a digest string, so such a receipt cannot enter a v5 replay.

## 4. Receipts vs code (receipt-1..3.json, copied here)

Code writes (tip lines): schema v5 only after verify succeeds (:1562); provenance.model.commit from the
PINNED_MODEL_URL group (:1563); provenance.verified {at: record, archive_sha256, member_sha256,
model_sha256} (:1564-1566); provenance.server/model recorded verbatim from argv (:1493-1498).

Checks performed:
- schema = kama-llamacpp-live/v5 in all three; outcome pass; setup_error null; internal_fault null.
- provenance.model.commit = 499bc8821c6b12b4e53c5bffcb21ec206f212d81 == the /resolve/<commit>/ segment of
  provenance.model.url (regex group semantics match).
- provenance.verified.archive_sha256 = bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b =
  frozen asset digest (counter docstring line 36-37) = install.txt archive hash.
- provenance.verified.member_sha256 = 35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0 =
  receipt server.sha256 = my own `sha256sum /home/vgpnk/.local/opt/llama-b11909/llama-server` (independent
  recompute) = install.txt server hash.
- provenance.verified.model_sha256 = provenance.model.sha256 = model.sha256 = model_sha256_post =
  270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d (frozen model digest).
- tool.sha256 = 1e5ea0fde985367d9d6335eae3825068e64063f032bbbc59fc8909e7b7f9a6d2 = sha256 of the tool file at
  tip (recomputed on my clone) — receipts were recorded with the committed tool bytes.
- captures.props.fields.build_info = "b11909-caa8191df..." (counter receipts leg: starts with `b11909-`).
- 11/11 checks passed in each receipt; stable fields identical across the three; instance fields differ
  (ports 33779/41891/45023, child pids 611093/612878/615051, started/ended utc).
- argv = child server argv (server binary, -m model, --alias kama-r48-live, --host 127.0.0.1, --port, -c 256,
  -t 1, --no-webui, --offline) — matches the code's server_argv construction.

## 5. Round-47 v4 compatibility

Round-47 receipt-1 (.ufo/waves/round-47/c2/live/): schema v4; provenance has all four fields; asset and
model URLs are https; member `llama-b11909/llama-server` is relative without `..`; model URL is the
unpinned `resolve/main/...`. Under the new argument rules this passes in v4 mode (probe J), and
kama-live-replay.py:240-241 passes --server-archive only for schema-v5 receipts — v4 replay is unaffected,
as the tool docstring (:42-43) claims.

## 6. Contract cross-check that produced finding F1

C2 counter docstring (tools/round48-live-replay-v5-audit.py:41-47) says: "given any provenance flag, the
live tool requires all of --server-asset-url, --server-asset-sha256, --server-member, --model-url and
--server-archive; https:// URLs; a model URL pinned to a 40-hex /resolve/<commit>/; ...". The code
(tools/kama-llamacpp-live.py:1459-1479) requires --server-archive, the pinned URL and the digest checks only
when --server-archive is given; the four v4 flags alone are accepted as an unverified v4 recording (probe J).
The preregistration claim (.ufo/waves/round-48/preregistration.json, C2 statement/predicate: "the four v4
provenance flags must come together with https URLs; --server-archive selects v5") matches the code. The
counter's recordcheck legs (counter :313-320: unpinned-with-archive, archive-digest-wrong, http-asset-url,
partial-flags = single flag, member-not-server, all-right-control) never drive all-four-without-archive, so
the executable legs pass under both readings.
