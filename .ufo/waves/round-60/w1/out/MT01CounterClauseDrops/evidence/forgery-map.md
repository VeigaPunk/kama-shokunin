| forgery | pristine verify() trips | mutants accepting (of 31) |
|---|---|---|
| stale-nonce | nonce capture-parse manifest | none |
| verdict=MODEL_KO | verdict | verdict |
| binary_sha256=0*64 | binary-sha | binary-sha |
| port=8080 | port log-listening | none |
| teardown.returncode=1 | teardown | teardown |
| check:binary-digest.passed=False | check:binary-digest | req-all,req-binary-digest |
| check:model-digest.passed=False | check:model-digest | req-all,req-model-digest |
| check:port-unregistered.passed=False | check:port-unregistered | req-all,req-port-unregistered |
| check:ready.passed=False | check:ready | req-all,req-ready |
| check:version.passed=False | check:version | req-all,req-version |
| check:running-exe-digest.passed=False | check:running-exe-digest | req-all,req-running-exe-digest |
| check:listener-owned.passed=False | check:listener-owned | req-all,req-listener-owned |
| check:tags-empty-before-create.passed=False | check:tags-empty-before-create | req-all,req-tags-empty-before-create |
| check:create.passed=False | check:create | req-all,req-create |
| check:tags-lists-model.passed=False | check:tags-lists-model | req-all,req-tags-lists-model |
| check:v1-models-lists-model.passed=False | check:v1-models-lists-model | req-all,req-v1-models-lists-model |
| check:evidence-before-load.passed=False | check:evidence-before-load | req-all,req-evidence-before-load |
| check:generate.passed=False | check:generate | req-all,req-generate |
| check:ps-lists-loaded.passed=False | check:ps-lists-loaded | req-all,req-ps-lists-loaded |
| check:evidence-after-load.passed=False | check:evidence-after-load | req-all,req-evidence-after-load |
| check:teardown.passed=False | check:teardown | req-all,req-teardown |
| v1-models body unsigned-flip | capture-sha:v1-models | capture-sha |
| tags re-signed duplicate-entry | tags-entry | tags-entry |
| ps-after re-signed digest-swap | ps-digest | ps-digest |
| version re-signed 0.40.10 | version | version |
| serve.log Listening line removed | log-listening | log-listening |
| serve.log POST /api/generate line removed | log-generate | log-generate |
| manifest file removed | manifest | manifest |
| manifest layer sha zeroed | manifest-layer | manifest-layer |
| blob byte appended | blob-sha | blob-sha |
