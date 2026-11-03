# kama: third curated source to consider after hyaku

Date: 2026-11-03

**Status: unassimilated future reading after hyaku.** No installation, collection, service change or training was performed. This proposal does not establish that the current host has supported hardware.

## DCGM Exporter: GPU evidence beside endpoint health

**Primary source:** NVIDIA's [DCGM Exporter snapshot](https://github.com/NVIDIA/dcgm-exporter/tree/691c92762eb551313c825f6efe4ceeee20982801), commit 691c92762eb551313c825f6efe4ceeee20982801. The [commit record](https://github.com/NVIDIA/dcgm-exporter/commit/691c92762eb551313c825f6efe4ceeee20982801) is dated 2026-05-06T16:32:42Z and names DCGM-Exporter 4.5.3-4.8.2. Verified 2026-11-03; this historical snapshot is not asserted to be latest.

**Why this gap:** HTTP probes and offered-load measurements leave the accelerator layer largely unobserved. This exporter exposes NVIDIA GPU telemetry in Prometheus format. Its collector definitions distinguish temperatures, framebuffer memory, utilization and the last XID error; some other counters are commented out rather than enabled defaults.

**Reading path:** At the pinned revision, README.md sections Changing Metrics, Profiling Metrics and HPC job mapping; then [etc/default-counters.csv](https://github.com/NVIDIA/dcgm-exporter/blob/691c92762eb551313c825f6efe4ceeee20982801/etc/default-counters.csv). Inspect metric types, units, comments and label identity before studying dashboard examples.

**Domain question:** What hardware evidence would distinguish an endpoint slowdown from GPU memory pressure or device errors without treating correlation as causation?

**Possible later exercise, original proposal:** After hyaku, draft a telemetry contract joining request windows to GPU identity, measurement timestamps and exporter/DCGM versions. Explicitly separate missing, unsupported, stale and zero-valued measurements. Include a negative case where HTTP remains healthy while device evidence is unavailable. Specify what additional evidence would justify each diagnosis, without inventing thresholds or changing the serving configuration.

**Limits and rights:** Requires compatible NVIDIA/DCGM hardware and software; upstream examples request elevated container capability, not authorized here. Profiling on Ampere and earlier depends on a proprietary package. Exporter code is [Apache-2.0](https://github.com/NVIDIA/dcgm-exporter/blob/691c92762eb551313c825f6efe4ceeee20982801/LICENSE); preserve required notices and review dependency terms separately. No DCGM Exporter source-family match appeared in the reviewed registry or prior two batches.
