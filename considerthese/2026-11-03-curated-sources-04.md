# kama: fourth curated source to consider after hyaku

Date: 2026-11-03

**Status: unassimilated future reading after hyaku.** No host inspection, monitor registration, configuration change or workload execution was performed.

## Linux PSI: resource stalls beside endpoint health

**Primary source:** The Linux kernel's [Pressure Stall Information documentation](https://github.com/torvalds/linux/blob/ffc253263a1375a65fa6c9f62a893e9767fbebfa/Documentation/accounting/psi.rst), pinned to v6.6 commit ffc253263a1375a65fa6c9f62a893e9767fbebfa. The [commit record](https://github.com/torvalds/linux/commit/ffc253263a1375a65fa6c9f62a893e9767fbebfa) is dated 2023-10-30T02:31:08Z; the document header dates its origin April 2018. Read 2026-11-03. This historical contract does not identify the installed kernel.

**Source summary:** PSI reports CPU, memory and I/O stall time, including recent percentage averages and cumulative microseconds. “Some” measures periods with stalled tasks; “full” measures simultaneous stalls of all non-idle tasks. System-level CPU full is undefined and reported as zero for compatibility. Cgroup2 provides scoped pressure files. Trigger registration writes to an interface and is distinct from reading counters.

**Reading path:** Documentation/accounting/psi.rst, Pressure interface → Monitoring for pressure thresholds → Cgroup2 interface. Read scope before the example.

**New domain gap:** Blackbox health, offered-load metrics and DCGM cover different layers. PSI adds host-resource waiting evidence that GPU utilization and a successful HTTP response cannot supply. Existing Linux references do not make this a new publisher; the pressure-stall contract is the new subject.

**Bounded future question, original proposal:** After hyaku, can a serving diagnosis distinguish a stalled workload from a merely busy host? Design four fictional windows combining endpoint latency, cumulative stall deltas and system-versus-service scope. Include healthy HTTP with rising stalls, slow HTTP without observed stalls, missing counters and the CPU-full compatibility zero. Require matching measurement intervals and a stated scope before drawing an association; reserve causal claims for additional evidence.

**Limits and rights:** Availability and scope require verification; no universal alert threshold follows. The [COPYING file](https://github.com/torvalds/linux/blob/ffc253263a1375a65fa6c9f62a893e9767fbebfa/COPYING) states GPL-2.0-only with Linux syscall exception and possible additional licenses. This note links and summarizes rather than copying example code. PSI aliases and exact documentation URLs were absent from reviewed contexts and prior batches.
