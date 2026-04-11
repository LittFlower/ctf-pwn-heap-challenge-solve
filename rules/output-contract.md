# Output Contract

Every non-trivial use of this skill should produce a result the user can audit.

## Required outputs

- A normalized challenge surface summary.
- A short allocator profile tied to the shipped or candidate libc version.
- The exact bug primitives plus any missing assumptions.
- Two or three candidate technique chains ordered by plausibility when more than one route is live.
- The chosen chain with explicit version justification tied back to local `how2heap` coverage.

## Primitive-proof output

- Include a short invariant table for the chosen primitive with:
  - field
  - required value
  - where it is written
  - when it is consumed
- State the next validation step if full code execution is not complete yet.
- Prefer a minimal exploit or exploit scaffold over a long unvalidated script.

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
- If a plan depends on an unproved transport, parser, or trigger assumption, call that out directly.
- Prefer short, checkable claims that map back to glibc behavior, debugger output, or local reference files.
