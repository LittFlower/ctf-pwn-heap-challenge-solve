# Known Heap-Solving Gotchas

Use this file for recurring pitfalls that are expensive and not obvious from the target alone.

## Transport and normalization

- Fixed-width menu parsing can invalidate exploit transport. If the target mixes `read(..., 0x10)` and `atoi`, prove the command protocol before debugging heap geometry.
- Do not assume line-based helpers are harmless. Short sends, padding, or delayed delimiters can change parser state before the heap logic even runs.
- A one-shot `show` primitive changes planning. Favor one-shot leak routes over long grooming plans when the leak surface cannot be revisited.

## Modeling errors

- The most common wrong turn is naming a technique before deriving the size algebra. If only a few alloc sizes exist, solve the equations first.
- Slot or handle state and physical chunk state are different models. A UAF-capable slot does not imply the corresponding chunk is still live.
- A stale slot may be more than a dangling pointer: if it still reaches a freed application struct with a callback, vtable, or function pointer, it can be a direct call primitive. Reoccupying that struct with attacker-controlled content may finish the challenge before any libc leak or allocator poisoning is needed.
- When a runtime knob changes chunk sizes, the first aesthetically pleasing layout is often the wrong one. Compare the whole legal range against leak, bin, and payload-placement needs.
- If dynamic results contradict the current geometry, replace the model quickly. Extending brute-force search around a broken model wastes time.

## Fake-free and largebin geometry

- Fake-free plans fail most often on boundary landing, next-chunk coherence, or overlapping metadata roles. Write the invariant table before building the payload.
- If two metadata roles need the same bytes and cannot share one valid value, treat that as a blocker rather than a payload-tuning problem.
- A forged chunk that is meant to coalesce later must still satisfy the metadata checks seen at the earlier `free` site.

## Version and technique selection

- `how2heap` file absence is a signal. If the exact version-technique pair is missing, assume allocator rules changed until proved otherwise.
- Safe-linking, tcache counts, and hook removal are route-selection constraints, not cleanup details to patch later.
- On modern libc, hook-centric thinking is often stale. Prefer stdout, stderr, FILE, or exit-linked routes when the trigger surface supports them.

## Validation and finish

- Live attach is not always the right proof tool. Alarms, short-lived children, and PTY-driven I/O often make core-based validation the faster route.
- If a modern FSOP chain prints the flag and then crashes, treat that crash as a post-execution validation problem first, not proof of failure.
- Rejected paths should name the allocator check that failed. "Heap fengshui wrong" is not a reusable lesson.
