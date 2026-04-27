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
- A recycled pwntools scaffold can keep the wrong architecture. If the new target is 64-bit but the script still runs with a stale 32-bit context, `p32`/`p64`, shellcode, ROP gadgets, and syscall helpers can all go bad at once. Set `context.binary` and `context.arch` from the target before debugging the heap model.
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
- A modern `large_bin_attack` is not unlocked by largebin residency alone. If no UAF, overlap, or stale edit can still mutate the freed largebin chunk's nextsize metadata, drop the route and re-rank candidates.
- A successful largebin write does not imply the attacked largebin chunk is safe to reclaim. If its `bk_nextsize` still points into the write target, the next largebin walk may die before unlink; reclaim the smaller same-bin helper first and repair the survivor's nextsize self-loop.

## Version and technique selection

- `how2heap` file absence is a signal. If the exact version-technique pair is missing, assume allocator rules changed until proved otherwise.
- Leakless off-by-null overlap and `house_of_einherjar` are not interchangeable. If you do not start with a known fake-chunk base and only need overlap, the first proof target is usually `poison_null_byte`-style backward consolidation.
- A single `largebin attack` does not buy two stages. If that is your only arbitrary write, `_IO_list_all` retarget and fake-FILE placement must usually be the same heap-fengshui decision, not two separate steps.
- A writable FILE path does not automatically mean Apple2. If `_wide_data` corruption destabilizes the path but `_codecvt` remains writable, forcing Apple2 can be the wrong branch; preserve default `_wide_data` and compare Apple3.
- Old stdio-field tricks are not one family. `_fileno` retarget, stdin-backed arbitrary write, stdout-backed leak, and `_IO_str_jumps` FSOP each need different later calls and version windows; if the notes only say `FSOP`, split the route before choosing offsets.
- Safe-linking, tcache counts, and hook removal are route-selection constraints, not cleanup details to patch later.
- A no-`free` top-chunk route is not automatically `house_of_tangerine`. If all you proved is that `sysmalloc` freed the old wilderness into unsorted, smallbin, or another reusable bin, keep the route at `sysmalloc_int_free` until you also prove a reachable tcache-poison or chosen-pointer bridge.
- `house_of_tangerine` is version-shaped now. On `2.42+`, prime the landing target like a real chunk and re-check how the released wilderness reaches tcache; on `2.43`, prefer the maintained repeat-the-wilderness cycle over sneaking in helper `free(malloc(...))` inside a supposedly no-`free` solve.
- If a no-leak off-by-null layout fails only on newer libc, check alignment drift and tcache-metadata warmup before declaring a new version family. Local how2heap keeps the maintained `poison_null_byte` path alive on `2.42`; `2.43` is where the official example adds warmup.
- Known-base stability is not pointer-mangling stability. `setarch -R` or repeated `FILE *` addresses do not imply a stable TLS `pointer_guard`.
- `/proc/self/maps`, `/proc/self/mem`, debugger memory, or `io.libs()` are not leak primitives. They are acceptable to validate a local hypothesis, but if the challenge still needs PIE, libc, stack, or heap addresses, keep searching for an in-band recovery route instead of letting same-host metadata become the exploit plan.
- A fixed local offset is not the same as a remotely recovered target. If the exploit only works because the local stack slot, return address delta, or libc interior offset was copied from one host run, keep treating it as a local proof and remove that dependency.
- A guessed-base oracle must be costed, not admired. If the only non-local route still leaves about 24 bits of PIE or libc entropy and each full attempt is slow, classify it as blocked instead of calling it a brute-force fallback.
- If a draft exploit only works because `libc.address`, `elf.address`, heap base, or stack slots were filled from `/proc`, `io.libs()`, or a previous debugger run, it is still a draft. Convert that dependency into a target-derived leak or drop the route.
- Tcache is per-thread, not per-process. A chunk freed by a worker thread does not automatically become reusable by main-thread `malloc`; if a poison plan assumes that, prove the cross-thread bridge explicitly.
- A stale alias can still bridge threads. If a worker frees a chunk but the main thread can still `free` the same stale pointer once, that second free may be the shortest route into a main-thread tcache poison.
- Overwriting `mp_.tcache_bins` only widens which `tc_idx` values glibc accepts. It does not create a non-zero count, a second list node, or a bypass for target alignment.
- When an overlap reaches `tcache_perthread_struct`, separate raw counter repair from real freelist writes. `counts[]` can be zeroed directly, but any live `entries[]` link still has to satisfy safe-linking.
- If you forge `tcache_perthread_struct` into a larger chunk and free it into unsorted for a libc leak, remember that unsorted `fd` / `bk` overwrites the struct head. Treat post-leak tcache state as corrupted until `counts[]` and related metadata are repaired.
- TSU, TSU+, and TSU++ differ by smallbin position and target layout, not by a completely different allocator mechanism. Recompute `tcache_count + smallbin_tail_position` before changing payload bytes.
- `house_of_water` offsets are version-shaped. Local how2heap uses one shape for `2.32-2.41`, a different `tcache_perthread_struct` placement for `2.42`, and another warmup/drain shape for `2.43`.
- `smallbin attack` is not one proof target. Split it into House of Lore fake return, smallbin unlink write, TSU stash behavior, or backward-consolidation unsafe unlink before writing payloads.
- A slot that aliases memory inside a forged large chunk stops being a valid follow-up chunk once that larger chunk is freed. Rebuild the next poison from storage outside the freed span instead of trusting the stale alias.
- On poisoned OOB tcache returns, `tcache_get` clears `e->key`. If the goal is a pointer leak, target a shifted aligned address that keeps the real pointer field away from `target+0x8`.
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
- A pile of `leak.py`, `probe.py`, `gdb.py`, and `exp.py` files can hide unfinished work. Keep temporary probes while proving one step, then merge the winning leak, heap, and trigger logic into one authoritative remote exploit file before calling the challenge solved.
- Rejected paths should name the allocator check that failed. "Heap fengshui wrong" is not a reusable lesson.
