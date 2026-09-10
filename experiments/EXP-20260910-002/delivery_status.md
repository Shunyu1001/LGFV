# Delivery checkpoint

Recorded 2026-09-10 after candidate acceptance and local main integration.

## Local result

The accepted data and evidence changes are in `d24bb12`; research-state update
`9b8ea78d9f1a8444edb23126dfcec01a4ef27359` follows it. Both were fast-forwarded
into local `main`. The latest complete content tree at that point is
`e91a9b7b0f0871e5c1afbcf8b7824f5e8269d864`. The working tree is clean. Current
validation also passes using the durable ignored source archive, independently
of the temporary cache location. Manuscript, outcome files, and immutable
objects are unchanged relative to `9977dd7`.

## GitHub

An earlier push succeeded for `codex/validation-frame-freeze-execution` through
`4c0d5de64e159c4856a4b7e338ffdad2d60b9a03`. That remote checkpoint includes the
interrupted-run audit and registration of source renewal, not its final result.
The later fetch failed with a receive timeout. Two non-forced pushes of local
main and the work branch failed, first on the low-speed timeout and then on a
connection timeout. No successful final push is claimed.

The GitHub connector could list branches, but a blob-creation attempt returned
HTTP 403, `Resource not accessible by integration`. No tree, snapshot commit,
or alternate remote branch was created. Writing through that connector stopped
at the permission failure. Network or connection permissions must recover
before final publication can be completed; do not assume the remote main
contains the accepted candidate.

## Overleaf

The browser can list the project tabs but repeatedly times out when attaching
to either editor tab. The native Computer route explicitly disallows control
of the Codex app and was stopped. No Overleaf pull or compile occurred.

## Resumption

Inspect local and remote heads before a normal, non-forced push. Preserve any
subsequent user edits. Once GitHub main is confirmed current, use the permitted
Overleaf interface to pull the project and inspect compilation. This iteration
did not change the manuscript, and its older frame-progress paragraphs need a
separately scoped claim update. Final frame freeze and human coding remain
pending; do not convert the 94 Codex working references into human labels.
