**Verdict:** by the attestation vocabulary the round-49 C1 witness is a local, unsigned, observer-nonce "background check" whose binary-identity evidence is the kernel's `/proc/<pid>/exe` (comparable to IMA measurement, but taken after the fact and not logged). It matches freshness-by-verifier-nonce, measurement of the running image and verifier-side appraisal against a frozen reference value. It does not match signed Evidence, a tamper-evident measurement log, or any binding of the nonce to the binary. Its own preregistered limit (a host copy of the same binary passes) is the missing build-provenance link (SLSA/in-toto). No defect in the frozen counter; four hardening proposals at the end.

Scope: prior-art only. I did not run the counters or any server (no llama-server started by this seat; `pgrep` showed three llama-server pids that belong to other seats). Source snapshots fetched 2026-10-26; the located excerpts are in `source-excerpts.txt` beside this file.

## Sources (quotes <=25 words, located)

**S-A. RFC 9334, RATS Architecture (IETF, Jan 2023)** https://www.rfc-editor.org/rfc/rfc9334
- §10.2 Implicit Timekeeping Using Nonces: "an unpredictable nonce is sent by the appraising entity and the nonce is then signed and included along with the Claims in the Evidence".
- §3.1 Two Types of Environments: Attesting Environments work by "taking measurements on code, memory, or other relevant assets of the Target Environment".
- §12.2 Conceptual Message Protection: "Generating and conveying unprotected Evidence always creates significant risk"; unprotected Evidence over a trusted channel makes the receiving entity vouch for "authenticity and freshness".

**S-B. TCG TPM 2.0 Library Part 3 Commands, rev 01.59, §18 attestation commands (TPM2_Quote, §18.4, Table 90)** https://trustedcomputinggroup.org/wp-content/uploads/TCG_TPM2_r1p59_Part3_Commands_code_pub.pdf
- §18.1 Attestation Commands introduction (p.168 section; located by text, not page): "this value will be placed in the TPMS_ATTEST.extraData parameter that is then hashed and signed" (the caller's `qualifyingData`; §18.4 TPM2_Quote, Table 90 describes it as "data supplied by the caller").
- tpm2-tools `tpm2_quote(1)` --qualification, https://tpm2-tools.readthedocs.io/en/latest/man/tpm2_quote.1/: "This is typically used to add a nonce against replay attacks."

**S-C. Linux IMA, kernel ABI doc `Documentation/ABI/testing/ima_policy`** https://raw.githubusercontent.com/torvalds/linux/master/Documentation/ABI/testing/ima_policy
- header: IMA "maintains a list of hash values of executables and other sensitive system files loaded into the run-time of this system".
- example policy: `measure func=BPRM_CHECK` (the exec hook); the same file lists `pcr=` options, i.e. measurements are extended into a TPM PCR so the list is verifiable against a quote.

**S-D. SLSA v1.0 Provenance and in-toto Attestation Framework**
- https://slsa.dev/spec/v1.0/provenance, Model: "Provenance is an attestation that a particular build platform produced a set of software artifacts through execution of the buildDefinition."
- https://slsa.dev/spec/v1.0/about: "SLSA's Build Track protects against tampering during or after the build" (scope ends at distribution; it says nothing about what a host later executes).
- https://github.com/in-toto/attestation/blob/main/spec/v1/README.md: the Statement layer "Binds the attestation to a particular subject and unambiguously identifies the types of the predicate."

**S-E. proc_pid_exe(5)** (lane's own S495) https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html: "this file is a symbolic link containing the actual pathname of the executed command"; if the file is unlinked it shows " (deleted)" appended; dereference is governed by a ptrace access-mode check.

## Mapping: round-49 C1 witness vs those standards

| Standard's requirement | Source | Round-49 witness | Verdict |
|---|---|---|---|
| Verifier supplies an unpredictable nonce, so Evidence cannot predate the challenge | S-A §10.2; S-B qualifyingData | counter generates `kama witness <16 hex>` itself and posts it to /tokenize + /detokenize | **Matches** the verifier-nonce freshness model. Freshness is real: replaying an old capture cannot echo a new nonce |
| Nonce is **signed together with the Claims** (bound to the attester's identity key and the measurement) | S-A §10.2; S-B "hashed and signed" | the nonce is only echoed by a deterministic tokenizer; exe digest, socket inode and `-m` are read from /proc in separate steps | **Does not match.** No signature and no binding: the nonce answer proves "something on that port runs a vocabulary-compatible tokenizer", not that the frozen binary produced it |
| Claims collected by an Attesting Environment from the Target Environment by measuring code | S-A §3.1 | the kernel is the Attesting Environment: /proc/<pid>/exe is the exec'd inode; counter hashes it | **Matches in kind** (measures the executing image, not the path string — S-E says the link holds the pathname actually executed) |
| Evidence is protected (signed by a key the target cannot use) or sent over a trusted channel whose receiver vouches (RATS UCCS) | S-A §12.2 | evidence is unprotected; verifier = counter on the same host/uid as the attester; the replay tool shares kernel and user | **Matches only the "unprotected over a trusted channel" row**, which S-A flags as "significant risk". The counter is its own relying party, which is acceptable for a regression gate but not a remote-attestation guarantee |
| Measure-before-use into an append-only log extended into a PCR, appraised later against reference values | S-C (IMA `BPRM_CHECK`, `pcr=`) | digest is computed by the counter after the process is already serving; nothing is logged; reference value is the frozen b11909 digest in the counter source | **Reference-value appraisal matches** (frozen digest = RATS reference value); **log/PCR chain absent**: no exec-time record, so a binary swapped, run and removed between observations leaves no trace |
| Liveness/challenge-response health check | S-A §10, RATS watchdog use case | /tokenize+/detokenize round trip against vocab the counter decoded itself, then confirms pid gone and port refused | **Matches** (a functional challenge-response, stronger than a bare `/health` 200) |
| Runtime evidence linked to build provenance: Statement binds a *subject digest* to a build | S-D (SLSA, in-toto subject) | the receipts record `server` digest and an archive member digest; the witness digest is matched to the frozen constant, not to a signed build statement | **Partial.** The frozen digest is the in-toto "subject" analogue. There is no build-platform attestation, so the b11909 binary's origin rests on the lane's earlier replay leg (digest of the downloaded archive member) |
| Join between the measured process and the endpoint that answered | not specified by these standards; RATS calls such a join a layered-attestation binding | /proc/<pid>/exe digest + LISTEN inode in pid's fd table + `-m` in cmdline + same port answers nonce | **Exceeds the usual health-check bar**: the inode join stops a stub or proxy that merely sits on the port. It is a lane-local construct, not a standard |

Net: of the three properties a TPM-quote-style attestation gives (freshness, authenticity of measurement, integrity-protected log), the witness gives freshness and a kernel-sourced measurement, and does not give authenticity (no signature) or a historical log. The preregistration limits already concede the largest consequence: "a replay that runs the same binary from a host copy still passes the witness". Under S-D that is expected: SLSA-style provenance would be needed to say the executed bytes were *built from or downloaded as* the recorded artifact; a runtime witness cannot establish that alone.

## Where the nonce is weaker than a quote nonce (observations, not defects in the frozen counter)
1. The tokenizer response is a pure function of (model vocab, input). Any llama.cpp build, or a Python reimplementation that loads the same GGUF, answers identically. The round-49 design therefore carries binary identity solely in the `/proc/<pid>/exe` digest and the inode join; the nonce adds freshness and model identity, not binary identity. [INFERENCE from the counter docstring's rule "every piece equal to the counter's own GGUF vocab decoding"; I did not run a stub.]
2. The digest, listener, cmdline and nonce reads are separate observations of a pid taken seconds apart; the docstring does not say the pid's start time is pinned between them. Same-uid pid reuse within the window is very unlikely but a quote-style protocol closes it by making one signed object cover all claims. [INFERENCE: docstring lines read, counter body not audited.]
3. `/proc/<pid>/exe` can be re-pointed by a process with CAP_SYS_RESOURCE (prctl PR_SET_MM_EXE_FILE) [from memory, not fetched; unverified]; the counter's own docstring already limits itself to "same-uid fail closed" cases. Not exploitable by an unprivileged replay tool.

## Proposed hardening (cheap, none reduces any axis; for the next counter version, since the frozen counter must not change)
1. Read `/proc/<pid>/stat` field 22 (starttime) before the digest and after the nonce round trip and require equality — closes the pid-reuse gap and makes the observations a single "epoch" in RFC 9334 terms.
2. Record `(st_dev, st_ino)` of `/proc/<pid>/exe` and the digest in the counter's own receipt so a later seat can re-derive which inode was measured (an IMA-like log line of its own: path, digest, inode, time).
3. Add a binary-specific challenge so the nonce stops being binary-agnostic: e.g. compare the server's `build_info`/version string from its status endpoint to the frozen build tag in the same round trip. [INFERENCE: I did not check that b11909's /props exposes it; verify against the README at caa8191d before relying on this.] It would still be unsigned; label it a liveness identity hint, not attestation.
4. State the standard in the corpus: describe the witness as "observer-nonce, unsigned, same-host, measurement by kernel" (RFC 9334 background-check without protected Evidence) rather than "attestation". This prevents the over-claim that an outside reader would infer from "execution witness".

## Commands and checks I ran
- `curl` of the S-A, S-B, S-C, S-D, S-E sources into my scratch; `grep -n` located each quote (line numbers in `source-excerpts.txt`); `pdftotext -layout` on the TPM Part 3 PDF; `sed -n` on lane `tools/kama-llamacpp-live.py:280-300` (`hold_for_witness`) and `round49-replay-witness-audit.py` docstring, and the preregistration `limits`.
- Not run: the counters, any llama-server, any replay. No tool installed. No lane/fleet writes.
