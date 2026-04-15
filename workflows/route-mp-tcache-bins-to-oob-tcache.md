# Route `_mp.tcache_bins` To OOB Tcache Poisoning

Use this workflow when a menu heap challenge:
- only exposes largebin-sized real chunks such as `0x4f0`, `0x500`, or `0x510`
- lacks a direct arbitrary-allocation primitive
- still gives overlap, UAF, or a stale edit into largebin metadata
- needs a returned-pointer primitive after a largebin write

The point is to convert a largebin write-first corridor into an out-of-range tcache-return corridor.

## Read First

- `rules/heap-solving-principles.md`
- `rules/allocator-version-rules.md`
- `references/how2heap-bin-write-primitives.md`
- `references/how2heap-safe-linking.md`
- `references/largebin-geometry-checklist.md`
- `references/heap-address-leaks.md`

## Steps

1. Confirm the route shape before coding.
   - Prove the menu can create at least two real chunks in the same largebin index.
   - Prove one stale or overlapping write can reach `A->bk_nextsize` after `A` reaches largebin.
   - Prove the intended post-write chunk size maps to a tcache index above the default `mp_.tcache_bins`.

2. Treat the route as two separate primitives.
   - Primitive 1: `large_bin_attack` writes a heap pointer into `mp_.tcache_bins`.
   - Primitive 2: freeing a chunk of that size now inserts it into an out-of-range tcache bin, enabling `tcache_poisoning`.
   - Do not treat the largebin write itself as the returned-pointer proof.

3. Build the largebin invariant table.
   - Record which chunk is the largebin resident `A`.
   - Record which later chunk `B` triggers the same-bin insertion write.
   - Record the exact write site: `A->bk_nextsize = &mp_.tcache_bins - 0x20`.
   - Record any coalescing hazard that would change `A` from `0x510` into a larger unsorted chunk before the attack.

4. Prove the largebin write with the shortest deterministic probe.
   - Stop after the trigger insertion and read `mp_.tcache_bins`.
   - If it still equals the default bin count, the route is not proved.
   - If reclaiming the remaining largebin chunk crashes, debug that before moving to tcache work.

5. Repair post-attack largebin state before reclaiming `A`.
   - If the attack leaves `A->bk_nextsize` pointing into `mp_`, do not request `A` immediately.
   - First reclaim the smaller same-bin helper chunk if one remains.
   - Then repair the surviving largebin chunk back to a singleton nextsize self-loop such as `fd_nextsize = bk_nextsize = A`.
   - Only after that request `A` back for the tcache phase.

6. Model the out-of-range tcache bin explicitly.
   - Overwriting `mp_.tcache_bins` only widens which `tc_idx` values are considered valid.
   - It does not manufacture a non-zero count or an extra list node.
   - Write down the exact out-of-range `tc_idx` for the chosen size and how many frees will populate it.

7. Stage the poison with at least two frees in that OOB bin.
   - Free a same-size helper chunk `C` first.
   - Free the overlap-reachable chunk `A` second so `A` becomes the head.
   - Poison `A->next` to the aligned target.
   - Reallocate once to pop `A`, then reallocate again to land on the target.
   - If only one chunk ever entered the OOB bin, the second allocation will not hit the target.

8. Respect tcache target constraints.
   - The returned target must satisfy the tcache alignment check.
   - `tcache_get` clears `e->key`, so expect a zero write at `target + 0x8`.
   - When leaking a pointer-bearing object, choose a shifted aligned target that preserves the field you actually want to read.

9. Pick the smallest in-band leak or finish from the returned pointer.
   - For stack routing, `environ` is often cheaper than a PIE-first plan when a pointer router is unnecessary.
   - For direct poisoning into a libc object, separate “target is readable” from “target survives `key = 0`”.
   - If the next step is stack ROP, identify the active return-address offset under the exact consumer call, not from an earlier stack snapshot.

## Completion Checklist

- [ ] `mp_.tcache_bins` overwrite proved in the live allocator state
- [ ] Remaining largebin chunk reclaim no longer crashes
- [ ] OOB `tc_idx` and free count written down explicitly
- [ ] Poison staged with two frees, not one
- [ ] Target alignment and `target+0x8` zero-write accounted for
- [ ] Leak or finish chosen from the returned pointer, not assumed

## Escape Conditions

- Switch to `workflows/debug-allocator-failure.md` if reclaiming `A` still dies in largebin traversal or unlink checks.
- Switch to `workflows/choose-endgame.md` once the OOB tcache route yields a stable target return and the remaining blocker is the finish.
