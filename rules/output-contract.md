# Output Contract

Every non-trivial use of this skill should produce a result the user can audit.

## Required outputs

- A normalized challenge surface summary.
- A short allocator profile tied to the shipped or candidate libc version.
- The exact bug primitives plus any missing assumptions.
- Two or three candidate technique chains ordered by plausibility when more than one route is live.
- The chosen chain with explicit version justification tied back to local `how2heap` coverage.
- For a real solve task, one authoritative remotely usable exploit file, or an explicit blocker statement if the solve is not remote-ready yet.

## Primitive-proof output

- Include a short invariant table for the chosen primitive with:
  - field
  - required value
  - where it is written
  - when it is consumed
- If the chosen route is really stdin/stdout field corruption or `_fileno` redirection rather than a generic fake-FILE chain, name the exact live stream object, the exact fields changed, and the later stdio helper that consumes them.
- If the chosen route is `_fileno` retarget, also state which already-open fd is being selected and why the later stdio helper still consumes the same live stream object after the field change in the intended read or write direction.
- If the chosen route is a stdin-backed arbitrary write, also state whether the later input path is stdio or raw fd input; raw `read` is not a valid consumer for staged `stdin FILE` state by itself.
- If the chosen route is a stdout-backed leak, also state whether the later output path is stdio or raw fd output, and name the effective buffering mode when that changes whether the controlling edge is `_IO_buf_end` or an `_IO_write_ptr`-collapsed path.
- If the chosen route is an output-stream leak through `stderr` or another non-stdout live stream, also state the actual consuming helper or assert/flush path instead of inheriting stdout-style newline/full-buffer assumptions.
- If the chosen route is historical `_IO_str_finish` / `_IO_str_overflow` dispatch, also state the exact old-libc window you are claiming and whether the route depends on old `_s._allocate_buffer` / `_s._free_buffer` assumptions rather than the modern `malloc/free` implementation.
- State the next validation step if full code execution is not complete yet.
- Prefer a minimal exploit or exploit scaffold over a long unvalidated script.
- A proof scaffold is an intermediate artifact, not the terminal deliverable. Before claiming the challenge solved, collapse the winning leak, heap, and trigger path into the final remote-capable exploit file.
- If helper libraries auto-rebase symbols, say whether each critical target is still an offset or is already an absolute address. Sanity-check final write targets are canonical before blaming the primitive.
- If a proof or finish depends on bases from `/proc`, a debugger, `io.libs()`, `ptrace`, `LD_PRELOAD`, `setarch`, TLS pointer-guard recovery, or other local process metadata, label it explicitly as a local-only validation path and state what still blocks the intended remote route.

## Final exploit expectations

- The final exploit may keep local or GDB modes, but the authoritative path must be the remote path.
- When the exploit uses pwntools, initialize `context.binary` and `context.arch` from the real target early in the file so packing, shellcode, ROP helpers, and pointer width do not silently fall back to the wrong architecture.
- If the finish needs PIE, libc, heap, stack, or other runtime bases, the final exploit must recover those values from the target itself or prove they are unnecessary.
- Do not ship an exploit that copies addresses from a debugger note, cached `/proc` output, `io.libs()`, or a previous local run into the remote path.
- If temporary helper scripts still exist, say which file is the authoritative remote exploit and which helpers remain proof-only.
- If the exploit cannot yet obtain the remote flag, say which missing in-band leak, primitive, or trigger still blocks convergence.

## Failure-reporting output

- Keep rejected hypotheses brief but explicit.
- When known, name the allocator check that killed the path rather than saying heap fengshui was wrong.
- If core-based validation was used, say what the core proved:
  - allocator write target
  - fake FILE or ROP placement
  - whether execution finished before the crash

## Style constraints

- Do not present speculative technique names as facts.
- Separate what is proved from what is inferred.
- Separate local validation from remote viability. A locally verified endgame that relies on debugger-assisted or `/proc`-assisted bases is not the same claim as a solved challenge path.
- If a plan depends on an unproved transport, parser, or trigger assumption, call that out directly.
- Prefer short, checkable claims that map back to glibc behavior, debugger output, or local reference files.
