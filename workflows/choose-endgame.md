# Choose Endgame

Use this workflow after the heap phase yields a stable leak, overlap, arbitrary allocation, or arbitrary write.

## Read First

- `rules/allocator-version-rules.md`
- `rules/output-contract.md`
- `references/leak-and-endgame-map.md`
- `references/house-of-apple2.md`

## Steps

1. Inventory trigger surfaces.
   - Record whether the binary reliably reaches `free`, `exit`, `fflush`, stdout or stderr activity, assert paths, or another FILE-consuming path.
2. Choose the most stable compatible finish.
   - Prefer stdout or stderr recovery when it already solves the challenge.
   - Prefer modern FILE or exit-linked routes over outdated hook-based finishes on modern libc.
   - Treat `house of kiwi` as a trigger helper, not a full finish by itself.
3. Check placement needs before coding.
   - Record where fake FILE, ROP data, or target pointers must land.
   - Confirm any required writable offsets and later trigger calls.
4. Validate post-success behavior.
   - If the chain prints the flag and then crashes, treat cleanup as a validation issue, not proof that the route failed.
   - Use core-based validation when execution likely completed before the crash.
5. Report the chosen finish and rejected alternatives.
   - Say why the chosen route matches the version and trigger surface.
   - Say why one or two discarded finishes were less stable or version-incompatible.

## Completion Checklist

- [ ] Trigger surface inventory recorded
- [ ] Chosen finish tied to libc version and trigger surface
- [ ] Placement constraints written down
- [ ] Post-crash behavior interpreted correctly
- [ ] Rejected finishes summarized briefly

## Escape Conditions

- Switch back to `workflows/prove-primitive.md` if the endgame needs a stronger primitive than the one currently proved.
- Switch to `workflows/debug-allocator-failure.md` if the chosen finish dies inside a glibc integrity check before the intended trigger.
