# RevengerScope — round-35 w1 secret-bleed sweep

## Reconstructed contract

Search `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-35/w1` for AWS keys, tokens, Authorization headers, and writes proposed under `/home/vgpnk/.config` or systemd. Report hits, or a clean sweep command and its output. Do not read secret files. Do not mutate the lane Git index. Stop after this surface.

Judged axis: operability. A usable result is a re-runnable sweep that names hits without reprinting secret values.

## Result

Not a clean sweep. Assigned-class hits: 15. AWS key material, Authorization/Bearer values, and proposed local writes are a separate clean subset (counts below).

| class | count | disposition |
| --- | ---: | --- |
| marlin `apiKey` assignment | 4 | hit, value withheld |
| other assigned-class hits | 11 | see HIT rows |
| AWS key id or AWS assignment | 0 | clean |
| Authorization header or Bearer token value | 0 | clean |
| live token prefix | 11 | hit |
| PEM private-key block or JWT | 0 | clean |
| proposed write under `/home/vgpnk/.config`, `~/.config`, `$HOME/.config`, or a systemd unit path | 0 | clean |

Marlin hits share sha256_12 `8f3968219c02`, len `36`, shape `opaque`. Value not printed. Context is `window.__marlinConfig` in fetched HTML, not an operator credential file. Inference, not a registry check: a client analytics embed copied in by a fetch, not a lane-authored operator secret. Not an AWS access key id.

Hit paths:

- `out/ScribeGate/fetch/dockerfile.html`
- `out/ScribeGate/fetch/compose-services.html`
- `out/ScribeGate/fetch/docker-dockerfile.html`
- `out/ScribeGate/fetch/docker-compose-services.html`

Other hits (values already withheld in the sweep output):

- `token_prefix out/ScribeGate/fetch/hosted-s346.html:7215 prefix=hf_ rest_len=8`
- `token_prefix out/ScribeGate/fetch/hosted-s346.html:7368 prefix=hf_ rest_len=8`
- `token_prefix out/ScribeGate/fetch/hosted-s346.html:7454 prefix=hf_ rest_len=8`
- `token_prefix out/ScribeGate/fetch/hosted-s346.html:7593 prefix=hf_ rest_len=8`
- `token_prefix out/ScribeGate/fetch/hosted-s346.html:7594 prefix=hf_ rest_len=8`
- `token_prefix out/ScribeGate/fetch/hosted-s346.html:7674 prefix=hf_ rest_len=8`
- `token_prefix out/ScribeGate/fetch/hosted-s346.html:7678 prefix=hf_ rest_len=8`
- `token_prefix out/ScribeGate/fetch/hosted-s346.html:7679 prefix=hf_ rest_len=8`
- `token_prefix out/ScribeGate/fetch/hosted-s346.html:7809 prefix=hf_ rest_len=8`
- `token_prefix out/ScribeGate/fetch/hosted-s346.html:7821 prefix=hf_ rest_len=8`
- `token_prefix out/ScribeGate/fetch/hosted-s346.html:7871 prefix=hf_ rest_len=12`

False positives classified, not counted as hits: 2.

- `hf_path_slug out/ScribeGate/fetch/vllm-engine-args.html:5905 slug=hf_inference_endpoints`
- `bearer_prose out/ScribeGate/fetch/vllm-engine-args.html:15957 matched=authorization`

## Sweep command

Re-run from any cwd. It skips secret-named files unread, skips this report and `out/RevengerScope/` (assignment echo and this seat's trace), and never prints secret values. The tree is live; other seats were still writing, so `files_scanned` can move. Hit rows are the contract.

```bash
python3 - << 'PY'
import os, re, hashlib, datetime
root = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-35/w1"
exclude_prefix = "out/RevengerScope/"
exclude_rel = {"out/RevengerScope.md"}
secret_name = re.compile(r"(?i)^(\.env($|\..+)|id_rsa|id_ed25519|credentials|credentials\.json)$")
secret_suffix = (".pem", ".p12", ".pfx", ".kdbx")
aws_key = re.compile(r"(?<![A-Z0-9])(?:AKIA|ASIA|AIDA|AROA|AGPA|ANPA|ANVA)[A-Z0-9]{16}(?![A-Z0-9])")
aws_assign = re.compile(r"(?i)aws_(?:secret_access_key|access_key_id|session_token)\s*[=:]\s*\S+")
auth_hdr = re.compile(r"(?i)(?:^|[^A-Za-z])authorization\s*[:=]\s*[\"']?(?:bearer\s+)?([A-Za-z0-9._\-+/=]{8,})")
bearer = re.compile(r"(?i)\bBearer\s+([A-Za-z0-9._\-]{8,})")
tok = re.compile(r"(?<![A-Za-z0-9])(ghp_|gho_|ghu_|ghs_|ghr_|github_pat_|glpat-|xox[baprs]-|sk-ant-|sk-proj-|sk-live_|rk_live_|xai-|hf_)([A-Za-z0-9_\-]{8,})")
priv = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
jwt = re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\b")
apikey = re.compile(r"(?i)(?:api[_-]?key|secret[_-]?key|access[_-]?token)[\"']?\s*[:=]\s*[\"']?([A-Za-z0-9+/=_\-]{8,})")
config_path = re.compile(r"(?:/home/vgpnk/\.config|~/\.config|\$\{?HOME\}?/\.config)\S*")
unit_path = re.compile(r"(?i)(?:/etc/systemd/\S+|/\.config/systemd/\S+|systemd/(?:user|system)/\S+\.(?:service|timer|socket|mount))")
systemctl_write = re.compile(r"(?i)\bsystemctl\s+(?:edit|enable|disable|daemon-reload|start|stop)\b")
write_verb = re.compile(r"(?i)(write_text|write_bytes|\btee\b|\bcp\b|\binstall\b|>>)")

def echo_line(rel, line):
    if rel.startswith(exclude_prefix):
        return True
    if "writes proposed under" in line or "Authorization headers" in line:
        return True
    return False

print("when", datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
print("root", root)
files = 0
skipped_names = []
nul_names = []
echo_n = 0
hits, fp, config_mentions, systemd_mentions = [], [], [], []
for dirpath, _, filenames in os.walk(root):
    for name in filenames:
        path = os.path.join(dirpath, name)
        rel = os.path.relpath(path, root)
        if rel in exclude_rel:
            continue
        if secret_name.match(name) or name.endswith(secret_suffix):
            skipped_names.append(rel)
            continue
        files += 1
        raw = open(path, "rb").read()
        if b"\x00" in raw:
            nul_names.append(rel)
        text = raw.replace(b"\x00", b"\n").decode("utf-8", "replace")
        for i, line in enumerate(text.splitlines(), 1):
            if echo_line(rel, line):
                if config_path.search(line) or re.search(r"(?i)systemd|authorization", line):
                    echo_n += 1
                continue
            if aws_key.search(line):
                hits.append("aws_key_id %s:%d" % (rel, i))
            if aws_assign.search(line):
                hits.append("aws_assign %s:%d value_withheld" % (rel, i))
            for m in auth_hdr.finditer(line):
                val = m.group(1)
                if val.lower() in {"headers", "to", "for"} or val.lower().startswith("headers"):
                    fp.append("authorization_prose %s:%d" % (rel, i))
                else:
                    hits.append("authorization_header %s:%d val_len=%d" % (rel, i, len(val)))
            for m in bearer.finditer(line):
                val = m.group(1)
                if val.lower() in {"authorization", "token", "tokens"} or not re.search(r"\d", val):
                    fp.append("bearer_prose %s:%d matched=%s" % (rel, i, val.lower()[:24]))
                else:
                    hits.append("bearer_token %s:%d val_len=%d" % (rel, i, len(val)))
            for m in tok.finditer(line):
                full = m.group(1) + m.group(2)
                if full.startswith("hf_") and re.search(r"hf_[a-z0-9_]+/", line):
                    fp.append("hf_path_slug %s:%d slug=%s" % (rel, i, full[:40]))
                else:
                    hits.append("token_prefix %s:%d prefix=%s rest_len=%d" % (rel, i, m.group(1), len(m.group(2))))
            if priv.search(line):
                hits.append("private_key_block %s:%d" % (rel, i))
            if jwt.search(line):
                hits.append("jwt %s:%d" % (rel, i))
            for m in apikey.finditer(line):
                val = m.group(1)
                digest = hashlib.sha256(val.encode()).hexdigest()[:12]
                shape = "uuid-shaped" if re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", val) else "opaque"
                ctx = "marlinConfig" if "__marlinConfig" in line else "other"
                hits.append("api_or_secret_assign %s:%d ctx=%s shape=%s len=%d sha256_12=%s" % (rel, i, ctx, shape, len(val), digest))
            if config_path.search(line):
                proposed = bool(write_verb.search(line) or systemctl_write.search(line))
                config_mentions.append("%s:%d %s" % (rel, i, "proposed_write" if proposed else "mention"))
                if proposed:
                    hits.append("config_proposed_write %s:%d" % (rel, i))
            if unit_path.search(line) or systemctl_write.search(line):
                hits.append("systemd_proposed_write %s:%d" % (rel, i))
            elif re.search(r"(?i)\bsystemd\b|\bsystemctl\b", line):
                systemd_mentions.append("%s:%d %s" % (rel, i, line.strip()[:140]))
print("files_scanned", files)
print("secret_named_files_skipped_unread", len(skipped_names))
for s in skipped_names:
    print("SKIP", s)
print("nul_bearing_files_text_scanned", len(nul_names))
for s in nul_names:
    print("nul", s)
print("assignment_or_self_echo_lines_skipped", echo_n)
print("assigned_class_hits", len(hits))
for h in hits:
    print("HIT", h)
print("false_positives", len(fp))
for h in fp:
    print("FALSE_POSITIVE", h)
print("config_path_outside_echo", len(config_mentions))
for h in config_mentions:
    print("CONFIG", h)
print("systemd_mentions_outside_echo", len(systemd_mentions))
for h in systemd_mentions:
    print("SYSTEMD_MENTION", h)
print("aws_key_id", sum(h.startswith("aws_key_id") for h in hits))
print("authorization_header", sum(h.startswith("authorization_header") or h.startswith("bearer_token") for h in hits))
print("proposed_writes", sum("proposed_write" in h for h in hits))
PY
```

## Sweep output

Recorded at 2026-10-25T00:30:29Z. Secret values were not printed. `out/RevengerScope/` lines that repeat the search brief were counted only as echo, not as hits.

```
when 2026-10-25T00:30:29Z
root /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-35/w1
files_scanned 129
secret_named_files_skipped_unread 0
nul_bearing_files_text_scanned 0
assignment_or_self_echo_lines_skipped 77
assigned_class_hits 15
HIT api_or_secret_assign out/ScribeGate/fetch/dockerfile.html:18 ctx=marlinConfig shape=opaque len=36 sha256_12=8f3968219c02
HIT api_or_secret_assign out/ScribeGate/fetch/compose-services.html:18 ctx=marlinConfig shape=opaque len=36 sha256_12=8f3968219c02
HIT api_or_secret_assign out/ScribeGate/fetch/docker-dockerfile.html:18 ctx=marlinConfig shape=opaque len=36 sha256_12=8f3968219c02
HIT api_or_secret_assign out/ScribeGate/fetch/docker-compose-services.html:18 ctx=marlinConfig shape=opaque len=36 sha256_12=8f3968219c02
HIT token_prefix out/ScribeGate/fetch/hosted-s346.html:7215 prefix=hf_ rest_len=8
HIT token_prefix out/ScribeGate/fetch/hosted-s346.html:7368 prefix=hf_ rest_len=8
HIT token_prefix out/ScribeGate/fetch/hosted-s346.html:7454 prefix=hf_ rest_len=8
HIT token_prefix out/ScribeGate/fetch/hosted-s346.html:7593 prefix=hf_ rest_len=8
HIT token_prefix out/ScribeGate/fetch/hosted-s346.html:7594 prefix=hf_ rest_len=8
HIT token_prefix out/ScribeGate/fetch/hosted-s346.html:7674 prefix=hf_ rest_len=8
HIT token_prefix out/ScribeGate/fetch/hosted-s346.html:7678 prefix=hf_ rest_len=8
HIT token_prefix out/ScribeGate/fetch/hosted-s346.html:7679 prefix=hf_ rest_len=8
HIT token_prefix out/ScribeGate/fetch/hosted-s346.html:7809 prefix=hf_ rest_len=8
HIT token_prefix out/ScribeGate/fetch/hosted-s346.html:7821 prefix=hf_ rest_len=8
HIT token_prefix out/ScribeGate/fetch/hosted-s346.html:7871 prefix=hf_ rest_len=12
false_positives 2
FALSE_POSITIVE hf_path_slug out/ScribeGate/fetch/vllm-engine-args.html:5905 slug=hf_inference_endpoints
FALSE_POSITIVE bearer_prose out/ScribeGate/fetch/vllm-engine-args.html:15957 matched=authorization
config_path_outside_echo 3
CONFIG out/ConnSibling/seat.log:314 mention
CONFIG out/MutC2Junk/scratch-repo/corpus/README.md:51 mention
CONFIG out/MutC2Junk/scratch-repo/corpus/README.md:52 mention
systemd_mentions_outside_echo 4
SYSTEMD_MENTION out/ScribeGate/fetch/blackbox-readme.md:268 run a caching DNS resolver next to the exporter, such as systemd-resolved,
SYSTEMD_MENTION out/ScribeGate/fetch/blackbox-readme.md:270 systemd-resolved stub (`127.0.0.53`) or NodeLocal DNSCache on Kubernetes work
SYSTEMD_MENTION out/ConnSibling/seat.log:314 OMP route resolution and fallback selection are refused to kumitate. Flag changes, service restoration, and `~/.config` or systemd writes ar
SYSTEMD_MENTION out/MutC2Junk/scratch-repo/corpus/README.md:58 Installing/enabling a systemd user timer remains operator-owned.
aws_key_id 0
authorization_header 0
proposed_writes 0
```

## Evidence chain

1. Walked every file under `.ufo/waves/round-35/w1` except this report. No filename matched a secret store (`.env`, `credentials`, `id_rsa`, `id_ed25519`, `.pem`, `.p12`, `.pfx`, `.kdbx`), so nothing was skipped unread for that reason. `~/.config`, credential stores, and endpoint-admin state were not opened.
2. AWS key-id pattern and AWS assignment names: see `aws_key_id` in the output.
3. Authorization / Bearer: prose matches are `FALSE_POSITIVE bearer_prose` or `authorization_prose`. A header value would be `authorization_header` or `bearer_token`.
4. Token prefixes: an `hf_` docs path containing `hf_<slug>/` is `hf_path_slug`, not a Hugging Face token. A live prefix would be `token_prefix`.
5. `apiKey` / `secret_key` / `access_token` assignments are `api_or_secret_assign` with a 12-hex sha256 fingerprint, not the value.
6. A path mention is a proposed write only if the same line has a write verb (`tee`, `cp`, `install`, `>>`, `write_text`) or `systemctl edit|enable|disable|daemon-reload|start|stop`, or a systemd unit path. A refusal sentence is a mention.
7. Assignment text in `plan.json`, `spec.json`, `run.json`, and this seat's prompt names the search. That is echo, not a write proposal.
8. Lane Git index was not touched. No `git add`, commit, or jj mutation.

## Divergences

- The wave brief also names C1/C2 corpus work and `MISSION.md` axis wording. This seat's task is the bleed sweep only. Predicates were not retargeted. `MISSION.md` was not edited. Axis authority was not touched.
- A workspace content search that reports no matches for `AKIA` / `Authorization` is not this sweep. It does not see an `apiKey` assignment. The command above is the evidence.
- The tree moved during the seat (file count changed; a scratch git under `out/CriticC1Rewrite/` was present in an earlier pass and absent by the time of later runs). That earlier pass text-scanned those NUL git objects and found no AWS key, Authorization header, or token prefix. It is prior observation, not part of the recorded output.
- A naive grep for `/home/vgpnk/.config` or `systemd` hits the assignment echo and any refusal sentence. Those are not proposed writes.

## Confidence

- AWS key ids, AWS secret assignments, Authorization/Bearer values, proposed local writes: high. Patterns are specific and the walk covered the tree at the recorded timestamp.
- Token class: high that the listed live prefixes are absent when `token_prefix` is 0. An `apiKey` row is a real token-shaped hit; calling a `marlinConfig` row a public docs embed is inference from the fetch path and the JS object name, not a vendor lookup.
- Stability of `files_scanned`: low. Other seats were still writing. Re-run the command for a later count; do not treat a changed file count alone as a new secret.
