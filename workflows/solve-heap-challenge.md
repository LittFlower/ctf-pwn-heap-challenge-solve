# Solve Heap Challenge

Use this workflow for first-pass solving of a Linux glibc heap-pwn challenge.

## Read First

- `rules/heap-solving-principles.md`
- `rules/allocator-version-rules.md`
- `rules/output-contract.md`
- `references/challenge-observation-checklist.md`
- `references/version-delta.md`
- `references/primitive-version-map.md`

## Steps

1. Normalize the challenge surface.
   - Translate menu verbs into exact allocator actions.
   - If the write primitive targets a long-lived libc or application object such as `FILE`, `_IO_wide_data`, or `_codecvt` instead of chunk user data, switch immediately from chunk-grooming language to object-layout and trigger-path modeling.
   - Record real requested sizes, real chunk sizes, edit width, truncation behavior, pointer lifetime after `free`, whether `show` is one-shot, and what later action can trigger corruption.
   - Record whether any attacker-relevant allocation or free happens in a worker thread and whether the first worker startup is lazy.
   - Prove command transport if the target mixes fixed-width `read` calls with `atoi`-style parsing, including whether a short send returns early or blocks until the width is filled.
   - Record byte-alphabet constraints such as `NUL` or newline rejection before choosing overwrite targets.
   - Identify heap-resident application objects, especially structs that pair user data pointers with callbacks, vtables, or function pointers.
   - If a live stream object is writable, map the reachable offset window to exact libc fields and embedded substructures before choosing a technique family.
   - Identify global slot tables or pointer arrays that may be writable later through a heap primitive. A stale `.bss` slot table can become a known-address read/write router.
   - If a slot table may become a router, record not only the pointer fields it can repoint but also which slot will still drive the next `edit` or `show`, whether its tracked size can drop to zero, and the exact write width that survives the retarget.
2. Build the allocator profile.
   - Identify the exact glibc version when possible.
   - If exact version is unclear, keep a short candidate set and note version-sensitive differences.
   - Record tcache, safe-linking, hook availability, per-thread allocator ownership for relevant chunks, and useful exit, stdio, or assert trigger surfaces.
   - Keep local validation aids separate from the real route. `/proc`, debugger bases, and `io.libs()` can prove a hypothesis locally, but they do not replace an in-band leak when the challenge still needs runtime addresses.
3. Translate the bug into allocator primitives.
   - Classify the corruption precisely: UAF, edit-after-free, overlap, off-by-one, metadata overwrite, arbitrary free, or leakless route.
   - Separate controllable state from merely observable state.
   - If the surface is a writable live libc object rather than a freed chunk, state that explicitly as an object-corruption primitive and name the consumer path that will later read the corrupted fields.
   - If a stale slot still points to a freed struct with a callable field, model the stale slot as a call capability and the freed struct as the overwrite target.
   - If a stale or global slot table can be repointed to attacker-chosen addresses, model it explicitly as a pointer-routing primitive, not just as a convenience for later reads.
4. Solve the size algebra before naming the technique.
   - Derive real chunk-size formulas, overlap deltas, and consolidation targets.
   - If a runtime knob changes sizes, enumerate the legal range before locking a geometry.
   - If there is no meaningful allocator geometry, solve reachable field offsets, partial-overwrite budget, and trigger invariants before consulting `how2heap`.
5. Build the first candidate set.
   - Use `references/primitive-version-map.md` and `references/how2heap-taxonomy.md` to list plausible families.
   - Use `scripts/find_how2heap_examples.py` to locate exact or nearby local examples.
   - Order candidates by hidden-assumption count, not aesthetics.
   - Rank direct stale-struct callback overwrite before hook or poisoning routes when it needs only same-size tcache reuse and an existing call trigger.
   - Rank direct libc-object call paths such as `_codecvt`, wide vtable, or other already-live stream dispatch before fake-`FILE` placement when the write window already reaches those fields.
   - On threaded targets, rank same-thread reuse or explicit cross-thread bridge plans ahead of poison routes that silently assume process-wide tcache behavior.
6. Choose the first proof target.
   - Pick the smallest claim that can be validated deterministically: overlap, pointer recovery, arbitrary allocation, arbitrary write, or stable leak.
   - Prefer proving pointer-table routing into a known target such as `stdout`, `stderr`, `environ`, or a stack slot before escalating to a heavier finish. It often validates primitive strength faster than a full FSOP chain.
   - If a local-only proof used `/proc`, debugger memory, or helper metadata to recover addresses, set the next proof target to the smallest in-band leak that replaces one of those dependencies.
   - For stream-object routes, prefer proving the exact libc consumer path with breakpoints in the shipped libc before building the final endgame payload.
   - If the candidate depends on fake-free or largebin geometry, switch to `workflows/prove-primitive.md` with the required invariant table.
7. Choose the finish only after the primitive is stable.
   - If leak or endgame routing is the hard part, switch to `workflows/choose-endgame.md`.
   - If the process aborts inside glibc, switch to `workflows/debug-allocator-failure.md`.

## Completion Checklist

- [ ] Normalized challenge surface recorded
- [ ] Allocator profile tied to exact or candidate libc version
- [ ] Bug primitive stated in allocator terms
- [ ] If the writable target is a live libc object, the reachable field window and consumer path were recorded explicitly
- [ ] Heap-resident callbacks, vtables, and function pointers checked as possible direct endgames
- [ ] Candidate technique chains ranked
- [ ] First proof target chosen
- [ ] Endgame deferred until the primitive is stable

## Escape Conditions

- Stop and switch workflows if the current blocker is an allocator abort, a fake-free geometry failure, or an endgame-selection problem.
- Stop and re-model if dynamic results contradict the chosen geometry.
- Stop and call out transport uncertainty if command parsing is not proved yet.
