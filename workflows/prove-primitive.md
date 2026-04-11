# Prove Primitive

Use this workflow when a candidate heap route exists but the allocator primitive is not yet stable.

## Read First

- `rules/heap-solving-principles.md`
- `rules/output-contract.md`
- `references/largebin-geometry-checklist.md`
- `references/gdb-mi-heap-proof-loop.md`
- `references/core-postmortem-validation.md`

## Steps

1. Define the exact proof target.
   - State the transition in allocator terms: `free(B)` survives, `A` reaches largebin, same-bin insertion performs the write, overlap becomes usable, or pointer recovery succeeds.
2. Build the invariant table.
   - Record field, required value, write source, write offset from edit base, and consume site.
   - For fake-free or same-write largebin chains, resolve `A->bk_nextsize`, forged `B.prev_size`, forged `B.size`, `B.end`, and the next real header.
3. Validate geometry before coding.
   - Check alignment, minimum chunk size, real-boundary landing point, coherent next-chunk metadata, and any tail chunk needed for forward consolidation.
   - If two required roles overlap and cannot share one value, treat that as a blocker.
4. Use the shortest deterministic probe.
   - Prefer a small script that proves one transition over a full exploit attempt.
   - Instrument with GDB MI or a core-based loop early instead of after repeated crashes.
5. Record the proof result precisely.
   - State what was proved, what remains unproved, and which assumption is next on the critical path.
   - If the probe failed, name the allocator check or geometry condition that failed.

## Completion Checklist

- [ ] Exact proof target written in allocator terms
- [ ] Invariant table exists for the chosen primitive
- [ ] Deterministic probe or debugger loop used
- [ ] Result clearly labeled as proved, disproved, or still inferred
- [ ] Next proof target identified

## Escape Conditions

- Switch to `workflows/debug-allocator-failure.md` if the blocker is a specific glibc abort or integrity check.
- Switch to `workflows/choose-endgame.md` once overlap, leak, or write is stable and the remaining problem is the finish.
- Rebuild the model immediately if observed chunk state contradicts the invariant table.
