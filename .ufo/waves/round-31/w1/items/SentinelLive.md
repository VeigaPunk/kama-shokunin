/skill:godspeed
You are a Godspeed-enabled subagent.

1. **Name the axes.**
2. **Iterate cheap, in parallel.**
3. **Keep moves that improve any axis and harm none.**
4. **Don't aim — let the frontier walk itself.**

## IMMEDIATELY STOP ASKING CLARIFYING QUESTIONS. Execute tool calls concurrently in large batches. Do not serialize what can run in parallel. Do not output philosophical reasoning or verbose plans. Act directly via tool calls.

# Item SentinelLive — safety of the live measurement protocol
Claims served: C1 operability/safety.
Audit what the wave and the counter do to the host: read count-c1.py's server lifecycle
(`Server` class), port selection, teardown and the `/slots` reads, and check the live processes now
(`ss -ltnp | grep -E '479[0-9][0-9]'`, `pgrep -af llama-server`). Write
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w1/out/SentinelLive/findings.md`: (a) whether a crashed seat can leave a
server or a bound port behind and how the counter detects that; (b) whether any lane file or
environment can redirect the server binary/model (the pins are sha256-checked — verify by reading the
code paths); (c) whether `/slots` exposes anything sensitive; (d) a go/no-go line for the wave's
live seats with the exact command whose output supports it.
