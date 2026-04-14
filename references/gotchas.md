# Known Heap-Solving Gotchas

Use this file for recurring pitfalls that are expensive and not obvious from the target alone.

Use it for reusable failure patterns and anti-assumptions, not for one challenge's raw first-pass facts. Put target-specific surface notes in `challenge-observation-checklist.md` instead.

## Transport and normalization

- Fixed-width menu parsing can invalidate exploit transport. If the target mixes `read(..., 0x10)` and `atoi`, prove the command protocol before debugging heap geometry.
- Do not assume line-based helpers are harmless. Short sends, padding, or delayed delimiters can change parser state before the heap logic even runs.
- Fixed-width `read` may still return after a short send. If you silently assume a full-width overwrite, you can miss a low-clobber read primitive or misdiagnose why a partial overwrite appears to "stick."
- A heap-labeled target may not be an allocator target. If the menu only performs bounded writes into a live `FILE` or other libc object, stop naming bin techniques and map reachable object fields plus consumer calls first.
- A one-shot `show` primitive changes planning. Favor one-shot leak routes over long grooming plans when the leak surface cannot be revisited.

## Modeling errors

- The most common wrong turn is naming a technique before deriving the size algebra. If only a few alloc sizes exist, solve the equations first.
- Byte-alphabet limits matter early. If the write primitive rejects `NUL` or newline, treat the target as a constrained partial-overwrite problem before choosing a field or sink.
- A crashing final write is not automatically a heap-model failure. If a computed target looks non-canonical or absurdly high, check for a double rebase first; after `ELF.address` / `libc.address` is set in pwntools, `ELF.sym[...]` is already absolute.
- Slot or handle state and physical chunk state are different models. A UAF-capable slot does not imply the corresponding chunk is still live.
- A writable global slot table is more than metadata. Once a heap primitive can retarget it, the table may become the cleanest known-address read/write primitive in the challenge.
- A repointed slot table can still fail at the menu layer. If the slot you use for the next `edit` or `show` has size zero, a cleared state bit, or a narrower width than the routed object needs, the exploit quietly becomes a no-op even though the pointer target is correct.
- Libio templates age badly. Copying fake-FILE base shifts like `stderr-0x10` or assuming a nearby callback slot such as `fp+0x68` can waste hours when the shipped libc actually dispatches through `wide_data->_wide_vtable` or another version-specific path. Reverse the consumer path first, then place fields.
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
- Known-base stability is not pointer-mangling stability. `setarch -R` or repeated `FILE *` addresses do not imply a stable TLS `pointer_guard`.
- `/proc/self/maps`, `/proc/self/mem`, debugger memory, or `io.libs()` are not leak primitives. They are acceptable to validate a local hypothesis, but if the challenge still needs PIE, libc, stack, or heap addresses, keep searching for an in-band recovery route instead of letting same-host metadata become the exploit plan.
- A guessed-base oracle must be costed, not admired. If the only non-local route still leaves about 24 bits of PIE or libc entropy and each full attempt is slow, classify it as blocked instead of calling it a brute-force fallback.
- Tcache is per-thread, not per-process. A chunk freed by a worker thread does not automatically become reusable by main-thread `malloc`; if a poison plan assumes that, prove the cross-thread bridge explicitly.
- A stale alias can still bridge threads. If a worker frees a chunk but the main thread can still `free` the same stale pointer once, that second free may be the shortest route into a main-thread tcache poison.
- On modern libc, hook-centric thinking is often stale. Prefer stdout, stderr, FILE, or exit-linked routes when the trigger surface supports them.
- Exotic exit-linked targets are not free wins. If clean `exit` already walks stdio state, do not sink time into `__exit_funcs` or similar surfaces before comparing the simpler trigger.

## Threaded heaps and lazy startup

- The first `pthread_create` often perturbs heap state through thread-startup allocations. If a challenge lazily starts its worker, trigger that startup before committing to a layout that depends on clean unsorted or tcache geometry.
- When a background worker allocates and frees attacker-influenced chunks, track allocator ownership and trigger timing together. A correct bin-size model can still fail if the wrong thread consumes or frees the chunk.

## Validation and finish

- Live attach is not always the right proof tool. Alarms, short-lived children, and PTY-driven I/O often make core-based validation the faster route.
- A visible `fflush` call is not required for stdio-triggered finishes. Clean `exit`, menu quit, or abort-linked paths can still walk corrupted stdio state and are worth inventorying early.
- `_codecvt` / gconv direct-call paths can self-clobber. Prove which bytes of the fake step survive until the indirect call before storing command strings or arguments there.
- If a modern FSOP chain prints the flag and then crashes, treat that crash as a post-execution validation problem first, not proof of failure.
- If bases came from `/proc`, a debugger, or local process metadata, the resulting stack or stdio finish is a local validation path, not yet the intended remote route. Keep the distinction explicit.
- Rejected paths should name the allocator check that failed. "Heap fengshui wrong" is not a reusable lesson.
