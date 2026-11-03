# kama: second curated source to consider after hyaku

Date: 2026-11-03

**Status: unassimilated future candidate after hyaku.** Reading proposal only: no training, execution, assimilation, dependency adoption or external changes. Earlier notes remain unchanged.

## AIPerf: offered load, queue delay and metric populations

- Primary source: <https://github.com/ai-dynamo/aiperf/tree/bb79be22fdc8ce7860e7b81eda1e7765474d568c>
- Domain fit and new gap: Moves beyond readiness and reachability to whether a healthy endpoint’s latency measurement omits load-generator waiting. Documentation distinguishes arrival scheduling from concurrency ceilings, full-window versus active-phase metrics, and success-only from error-adjusted latency.
- Precise reading: docs/tutorials/request-rate-concurrency.md — How It Works; Quick Reference; docs/reference/effective-vs-active-metrics.md — effective_latency; Failed requests; Effective metrics.
- Future question: Could the same endpoint look healthy because the generator throttles arrivals or excludes failed requests?
- Proposed later evaluation (original lane-specific design): After hyaku, draft a synthetic timestamp ledger containing queue waits, idle gaps, one timeout and completed streams. Hand-calculate success latency and offered-load coverage, retaining failed-request counts separately. Specify required endpoint, tokenizer, workload, warmup and generator pins before considering a separately authorized load test; keep model-quality conclusions with kengaku.
- Limitations: The technical brief’s equal-mean example actually gives 1.09 s and 1.99 s; its ramp-to-capacity guidance needs service-time and load conditions. Treat equations and implementation as review targets, not adopted authority. Success-only latency can conceal errors; no capacity or local compatibility claim.
- License/reuse: Apache-2.0; official pinned license read at <https://raw.githubusercontent.com/ai-dynamo/aiperf/bb79be22fdc8ce7860e7b81eda1e7765474d568c/LICENSE>. Preserve applicable notices; dependencies and external data need separate review.
- Version/timestamp: Official API returned bb79be22fdc8ce7860e7b81eda1e7765474d568c with committer timestamp 2026-11-03T09:17:47Z. Commit snapshot, not a release assertion or proof of latest maintenance. Fetched 2026-11-03.
- Deduplication: All supplied lane existing-context files, including published first-batch notes, and existing-urls.json. Repository aliases and source-family names checked. Not a claim about unprovided historical files. No exact-URL or source-family match found.

### Verification links

- <https://api.github.com/repos/ai-dynamo/aiperf/commits/bb79be22fdc8ce7860e7b81eda1e7765474d568c>
- <https://raw.githubusercontent.com/ai-dynamo/aiperf/bb79be22fdc8ce7860e7b81eda1e7765474d568c/README.md>
- <https://raw.githubusercontent.com/ai-dynamo/aiperf/bb79be22fdc8ce7860e7b81eda1e7765474d568c/LICENSE>
- <https://raw.githubusercontent.com/ai-dynamo/aiperf/bb79be22fdc8ce7860e7b81eda1e7765474d568c/docs/tutorials/request-rate-concurrency.md>
- <https://raw.githubusercontent.com/ai-dynamo/aiperf/bb79be22fdc8ce7860e7b81eda1e7765474d568c/docs/reference/effective-vs-active-metrics.md>

