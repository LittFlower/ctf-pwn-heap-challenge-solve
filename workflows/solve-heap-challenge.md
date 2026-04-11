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
   - Record real requested sizes, real chunk sizes, edit width, truncation behavior, pointer lifetime after `free`, whether `show` is one-shot, and what later action can trigger corruption.
   - Prove command transport if the target mixes fixed-width `read` calls with `atoi`-style parsing.
   - Identify heap-resident application objects, especially structs that pair user data pointers with callbacks, vtables, or function pointers.
2. Build the allocator profile.
   - Identify the exact glibc version when possible.
   - If exact version is unclear, keep a short candidate set and note version-sensitive differences.
   - Record tcache, safe-linking, hook availability, and useful exit, stdio, or assert trigger surfaces.
3. Translate the bug into allocator primitives.
   - Classify the corruption precisely: UAF, edit-after-free, overlap, off-by-one, metadata overwrite, arbitrary free, or leakless route.
   - Separate controllable state from merely observable state.
   - If a stale slot still points to a freed struct with a callable field, model the stale slot as a call capability and the freed struct as the overwrite target.
4. Solve the size algebra before naming the technique.
   - Derive real chunk-size formulas, overlap deltas, and consolidation targets.
   - If a runtime knob changes sizes, enumerate the legal range before locking a geometry.
5. Build the first candidate set.
   - Use `references/primitive-version-map.md` and `references/how2heap-taxonomy.md` to list plausible families.
   - Use `scripts/find_how2heap_examples.py` to locate exact or nearby local examples.
   - Order candidates by hidden-assumption count, not aesthetics.
   - Rank direct stale-struct callback overwrite before hook or poisoning routes when it needs only same-size tcache reuse and an existing call trigger.
6. Choose the first proof target.
   - Pick the smallest claim that can be validated deterministically: overlap, pointer recovery, arbitrary allocation, arbitrary write, or stable leak.
   - If the candidate depends on fake-free or largebin geometry, switch to `workflows/prove-primitive.md` with the required invariant table.
7. Choose the finish only after the primitive is stable.
   - If leak or endgame routing is the hard part, switch to `workflows/choose-endgame.md`.
   - If the process aborts inside glibc, switch to `workflows/debug-allocator-failure.md`.

## Completion Checklist

- [ ] Normalized challenge surface recorded
- [ ] Allocator profile tied to exact or candidate libc version
- [ ] Bug primitive stated in allocator terms
- [ ] Heap-resident callbacks, vtables, and function pointers checked as possible direct endgames
- [ ] Candidate technique chains ranked
- [ ] First proof target chosen
- [ ] Endgame deferred until the primitive is stable

## Escape Conditions

- Stop and switch workflows if the current blocker is an allocator abort, a fake-free geometry failure, or an endgame-selection problem.
- Stop and re-model if dynamic results contradict the chosen geometry.
- Stop and call out transport uncertainty if command parsing is not proved yet.
