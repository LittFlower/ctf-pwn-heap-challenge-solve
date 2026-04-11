# Debug Allocator Failure

Use this workflow when glibc integrity checks, abort strings, or unexplained heap crashes block progress.

## Read First

- `rules/heap-solving-principles.md`
- `rules/allocator-version-rules.md`
- `references/version-delta.md`
- `references/gdb-mi-heap-proof-loop.md`
- `references/core-postmortem-validation.md`

## Steps

1. Name the failure precisely.
   - Capture the abort string, failing function, and last trusted heap action.
   - Prefer allocator-check names over vague descriptions.
2. Map the failure to invariant classes.
   - `largebin double linked list corrupted (nextsize)` usually means nextsize ordering or linkage is wrong.
   - `double free or corruption (!prev)` usually means forged boundary or `prev_inuse` geometry is wrong.
   - `invalid pointer` usually means alignment or chunk-boundary landing is wrong.
3. Inspect the exact consume site.
   - Break at `_int_free`, `_int_malloc`, or the failing check.
   - Dump chunk headers around the forged region and inspect bin or nextsize state.
4. Update the model, not just the payload.
   - Rewrite the violated invariant explicitly.
   - Decide whether the failure means bad geometry, bad transport, wrong version assumption, or a dead technique family.
5. Record the rejected path briefly.
   - Keep one or two lines on what failed at the allocator-check level and why that route is no longer preferred.

## Completion Checklist

- [ ] Abort string or failure site identified
- [ ] Violated invariant class named
- [ ] Heap state inspected near the consume site
- [ ] Model updated or route rejected
- [ ] Failure reason captured in allocator terms

## Escape Conditions

- Switch back to `workflows/prove-primitive.md` after the violated invariant is corrected.
- Switch to `workflows/solve-heap-challenge.md` if the failure exposed a wrong top-level primitive classification.
