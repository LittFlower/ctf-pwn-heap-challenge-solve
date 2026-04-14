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
   - Treat clean `exit(0)` and other normal-termination paths as possible implicit `fflush` triggers when the exploit plan targets stdio state.
   - Record whether `rewind`, `fseek`, `fclose`, wide-conversion helpers, or other stream operations can consume corrupted `FILE` / libio subfields directly.
   - Before committing to heavier exit-linked targets such as `__exit_funcs`, `tls_dtor_list`, or `link_map`, compare them against the clean-exit stdio walk and prefer the trigger with fewer hidden assumptions.
   - If the binary uses worker threads or lazy thread startup, record which thread performs each relevant `malloc` or `free` and whether the first thread creation perturbs the heap layout you plan to exploit.
2. Choose the most stable compatible finish.
   - Prefer stdout or stderr recovery when it already solves the challenge.
   - If a known-address read/write route can repoint a global slot table or stale pointer table, treat that structure as a `pointer router` and check `environ` and stack-return finishes before heavier FILE chains.
   - Do not freeze the plan at a debugger-assisted or `/proc`-assisted known-base finish unless the task is explicitly local-only. Use that proof to rank the next in-band leak or router step that removes the same-host dependency.
   - For FILE / libio routes, re-derive the actual consumer path in the shipped libc before choosing fields. Do not carry over `stderr-0x10`, `fp+0x68`, or historical callback-slot assumptions from older notes.
   - If an already-live stream object reaches a direct indirect-call site such as `_codecvt`, a wide vtable, or a callback-like field, rank that route ahead of full fake-`FILE` placement.
   - Prefer modern FILE or exit-linked routes over outdated hook-based finishes on modern libc.
   - If a stack pointer is reachable and a clean return site exists, value saved-RIP overwrite over more assumption-heavy FSOP when the version and trigger surface allow it.
   - Prefer `house of apple2` as the default modern FILE route when `_IO_list_all` or a FILE pointer is already writable.
   - Treat `house of cat` as a fallback only when `apple2` is blocked and the shipped libc still offers an acceptable seekoff-side trigger story.
   - Treat `house of emma` as higher-cost: require explicit point-guard control and stderr routing before ranking it above simpler FILE or exit-linked finishes.
   - Prefer `house of banana` when a `link_map` or fini-style exit-linked surface is already naturally reachable from the proved primitive.
   - Treat `house of kiwi` as a trigger helper, not a full finish by itself. If `__malloc_assert -> fflush(stderr)` still exists on the shipped libc, treat that assert path as the reason kiwi stays viable.
   - Treat `malloc_printerr -> strlen@GOT`-style abort routes as narrow old-target helpers only. Use them when GOT writes are truly available and the weak argument control is still enough for the challenge.
3. Check placement needs before coding.
   - Record where fake FILE, ROP data, or target pointers must land.
   - Confirm any required writable offsets and later trigger calls.
   - Sanity-check every computed absolute target before the final write. If `ELF.address` or `libc.address` is already set in pwntools, `ELF.sym[...]` is absolute; adding the base again can create non-canonical addresses and misleading `EFAULT` failures.
   - If a slot-table rewrite is part of the finish, confirm the slot that performs the follow-up `edit` still has non-zero logical size and enough width after the retarget. A correct pointer with a dead size field is not a write primitive.
   - For `_codecvt` / gconv routes, prove whether `step_data` or conversion helpers overwrite bytes in the fake step before the indirect call. Do not park command strings or arguments there unless that survival was tested.
   - If the finish depends on tcache poisoning or same-size reuse, confirm that the allocation consuming the poisoned entry runs in the same thread that owns that tcache list.
4. Validate post-success behavior.
   - If the chain prints the flag and then crashes, treat cleanup as a validation issue, not proof that the route failed.
   - Use core-based validation when execution likely completed before the crash.
5. Report the chosen finish and rejected alternatives.
   - Say why the chosen route matches the version and trigger surface.
   - Say whether the route is a real challenge path or only a local validation path that depends on bases from `/proc`, a debugger, `ptrace`, `LD_PRELOAD`, `setarch`, TLS pointer-guard recovery, or other local process metadata.
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
