# Heap Solving Principles

These rules govern every use of this skill, regardless of glibc version or endgame.

## Core model

- Treat each challenge as three linked problems: recover allocator facts, prove one stable primitive, and choose an endgame that matches the shipped libc and trigger surface.
- Start from exact allocator facts, not from a favorite technique name.
- Treat `how2heap` as a versioned allocator-behavior atlas, not as copy-paste exploit stock.
- Prefer the smallest technique family that satisfies the challenge's observable constraints.
- Optimize for time-to-correct-model, not time-to-first-theory. Any speedup that skips allocator facts, primitive proof, or trigger validation is a regression, not an improvement.

## Modeling rules

- Translate menu actions such as `add`, `delete`, `edit`, `show`, `calloc`, and `realloc` into exact allocator actions before naming a technique.
- A heap-labeled target may expose no meaningful allocator mutation at all. If attacker input only corrupts a long-lived libc or application object such as `FILE`, `_IO_wide_data`, `_codecvt`, or a stream wrapper, switch from chunk-geometry modeling to object-layout and consumer-path modeling before consulting `how2heap`.
- Keep two models separate at all times:
  - slot or handle state
  - physical chunk state
- Do not conflate a stale pointer capability with a live allocated chunk.
- Do not conflate address reachability with editability. If a slot table or router can be repointed, prove separately which UI operation still has non-zero logical length and enough width to perform the next write.
- Write desired state transitions in allocator terms, not UI terms.

## Reasoning rules

- Solve size algebra before heap grooming when the menu exposes only a few alloc sizes.
- If there is no real heap-grooming surface, solve field-offset reachability, byte-alphabet constraints, and trigger invariants before naming a technique family.
- Prefer explicit equalities, overlaps, and chunk-size formulas over intuition-only layout search.
- If a runtime knob changes reachable sizes, enumerate the legal range before committing to one geometry.
- If the user provides a concrete layout hint, algebraic relation, or target size pair, test it before inventing alternatives.

## Commitment rules

- Prefer the technique that needs the fewest hidden assumptions.
- Prefer the workflow change that reduces repeated work without removing a validation step. Faster routing is good; weaker proof obligations are not.
- Do not substitute local process metadata for a challenge leak. `/proc`, debugger state, and helper-library base discovery are validation aids; if addresses still matter to the intended route, keep building an in-band leak plan.
- Prefer real-chunk routes over fake-free geometry when both satisfy the same leak and endgame needs.
- Before committing to libc hooks, tcache poisoning, or FSOP, check whether a stale heap object already contains a callable field such as a callback, vtable, or function pointer. If a same-size reuse can rewrite that object and a later program action calls the field, prefer the direct application-level control-flow route.
- If a plan depends on a heap leak, writable target offset, later `free` or `exit` trigger, or bin-ordering assumption, write that dependency down before coding.
- If dynamic results contradict the current model, replace the model quickly instead of brute-forcing around it.
- Do not move to full code execution until a primitive has been proved in isolation.
