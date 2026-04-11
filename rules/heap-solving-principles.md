# Heap Solving Principles

These rules govern every use of this skill, regardless of glibc version or endgame.

## Core model

- Treat each challenge as three linked problems: recover allocator facts, prove one stable primitive, and choose an endgame that matches the shipped libc and trigger surface.
- Start from exact allocator facts, not from a favorite technique name.
- Treat `how2heap` as a versioned allocator-behavior atlas, not as copy-paste exploit stock.
- Prefer the smallest technique family that satisfies the challenge's observable constraints.

## Modeling rules

- Translate menu actions such as `add`, `delete`, `edit`, `show`, `calloc`, and `realloc` into exact allocator actions before naming a technique.
- Keep two models separate at all times:
  - slot or handle state
  - physical chunk state
- Do not conflate a stale pointer capability with a live allocated chunk.
- Write desired state transitions in allocator terms, not UI terms.

## Reasoning rules

- Solve size algebra before heap grooming when the menu exposes only a few alloc sizes.
- Prefer explicit equalities, overlaps, and chunk-size formulas over intuition-only layout search.
- If a runtime knob changes reachable sizes, enumerate the legal range before committing to one geometry.
- If the user provides a concrete layout hint, algebraic relation, or target size pair, test it before inventing alternatives.

## Commitment rules

- Prefer the technique that needs the fewest hidden assumptions.
- Prefer real-chunk routes over fake-free geometry when both satisfy the same leak and endgame needs.
- Before committing to libc hooks, tcache poisoning, or FSOP, check whether a stale heap object already contains a callable field such as a callback, vtable, or function pointer. If a same-size reuse can rewrite that object and a later program action calls the field, prefer the direct application-level control-flow route.
- If a plan depends on a heap leak, writable target offset, later `free` or `exit` trigger, or bin-ordering assumption, write that dependency down before coding.
- If dynamic results contradict the current model, replace the model quickly instead of brute-forcing around it.
- Do not move to full code execution until a primitive has been proved in isolation.
