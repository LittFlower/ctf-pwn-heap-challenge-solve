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
   - Record whether the program really exposes `free`, `calloc`, or `realloc`, or whether the route is fundamentally a no-`free` (`no free`) surface.
   - If the write primitive targets a long-lived libc or application object such as `FILE`, `_IO_wide_data`, or `_codecvt` instead of chunk user data, switch immediately from chunk-grooming language to object-layout and trigger-path modeling.
   - Record real requested sizes, real chunk sizes, edit width, truncation behavior, pointer lifetime after `free`, whether `show` is one-shot (`single-shot show`), and what later action can trigger corruption.
   - Record whether any attacker-relevant allocation or free happens in a worker thread and whether the first worker startup is lazy.
   - Prove command transport if the target mixes fixed-width `read` calls with `atoi`-style parsing, including whether a short send returns early or blocks until the width is filled.
   - Record byte-alphabet constraints such as `NUL` or newline rejection before choosing overwrite targets.
   - Identify heap-resident application objects, especially structs that pair user data pointers with callbacks, vtables, or function pointers.
   - If a live stream object is writable, map the reachable offset window to exact libc fields and embedded substructures before choosing a technique family.
   - If a live stream object, `_IO_wide_data`, or `_codecvt` state is writable, open `references/libio-object-corruption.md` before continuing with heap-family selection.
   - If the writable stream state favors `_wide_data` or `_codecvt` but not both, open `references/house-of-apple-family.md` before committing to an Apple2-style fake FILE layout.
   - Identify global slot tables or pointer arrays that may be writable later through a heap primitive. A stale `.bss` slot table can become a known-address read/write router.
   - If a slot table may become a router, record not only the pointer fields it can repoint but also which slot will still drive the next `edit` or `show`, whether its tracked size can drop to zero, and the exact write width that survives the retarget.
   - If attacker-relevant chunks cross worker threads or lazy thread startup perturbs layout, open `references/threaded-allocator-pitfalls.md` before trusting same-thread tcache reuse or poisoning.
2. Build the allocator profile.
   - Identify the exact glibc version when possible.
   - If exact version is unclear, keep a short candidate set and note version-sensitive differences.
   - Record tcache, safe-linking, hook availability, per-thread allocator ownership for relevant chunks, and useful exit, stdio, or assert trigger surfaces.
   - Keep local validation aids separate from the real route. `/proc`, debugger bases, `io.libs()`, and fixed same-host offsets can prove a hypothesis locally, but they do not replace an in-band leak or dynamic recovery step when the challenge still needs runtime addresses on a remote target.
   - Default to a remotely viable exploit chain. Do not call the challenge solved while critical targets still depend on local-only base recovery, debugger-visible state, or offsets that were not recovered from the challenge surface itself.
3. Translate the bug into allocator primitives.
   - Classify the corruption precisely: UAF, edit-after-free, double free, overlap, off-by-one/null overwrite, metadata overwrite, arbitrary free, or leakless route.
   - Separate controllable state from merely observable state.
   - Record whether the challenge already gives a heap leak, only a libc leak, only one read via `show`, or no useful leak at all before ranking `leakless` or `no leak` families.
   - Do not route to `large_bin_attack` unless the challenge gives a post-free metadata write into the largebin chunk, usually through UAF, overlap, or stale edit that reaches `bk_nextsize` or equivalent nextsize fields.
   - If the surface is a writable live libc object rather than a freed chunk, state that explicitly as an object-corruption primitive and name the consumer path that will later read the corrupted fields.
   - If a stale slot still points to a freed struct with a callable field, model the stale slot as a call capability and the freed struct as the overwrite target.
   - If a stale or global slot table can be repointed to attacker-chosen addresses, model it explicitly as a pointer-routing primitive (`pointer router`), not just as a convenience for later reads.
4. Solve the size algebra before naming the technique.
   - Derive real chunk-size formulas, overlap deltas, and consolidation targets.
   - If a runtime knob changes sizes, enumerate the legal range before locking a geometry.
   - If the current blocker is still address recovery rather than allocator geometry, open `references/heap-address-leaks.md` before adding another heap-stage hypothesis.
   - If the challenge notes, writeup, or exploit skeleton is still using old community names instead of allocator-first language, open `references/how2heap-legacy-writeup-labels.md` before trusting the label literally.
   - If the challenge notes or prior writeup call the bug `offbynull-heap`, open `references/offbynull-heap.md` before deciding whether the local match is `poison_null_byte` or `house_of_einherjar`.
   - If the route depends on one null byte, `prev_inuse`, `prev_size`, or backward consolidation, open `references/how2heap-overlap-nullbyte.md` before deciding whether the local match is `poison_null_byte`, `house_of_einherjar`, `overlapping_chunks`, or `overlapping_chunks_2`.
   - If the route depends on huge mmapped allocations and overlap comes from corrupting mmap-chunk `size` or `prev_size` before `munmap`, open `references/how2heap-mmap-overlap.md` before forcing an ordinary heap-bin overlap family.
   - If the route depends on freeing attacker-controlled non-heap memory or a fake chunk header, open `references/how2heap-fake-free-primitives.md` before deciding between `house_of_spirit` and `tcache_house_of_spirit`.
   - If the route depends on fastbin, tcache, freed-`fd`, protected `next`, or tcache metadata semantics, open `references/how2heap-freelist-primitives.md` before choosing between duplication, poisoning, and metadata-side families.
   - If the route is already narrowed to a modern freelist family but the real uncertainty is protected-pointer recovery, production, or avoidance, open `references/how2heap-safe-linking.md` before forcing plain `tcache_poisoning`.
   - If the route depends on unsorted `bk`, smallbin freelists, largebin `bk_nextsize`, or stash motion through `calloc`, open `references/how2heap-bin-attacks.md` first, then `references/how2heap-bin-write-primitives.md` before choosing a technique.
   - If the route has only one `largebin attack` and the intended finish is FILE-based, open `references/largebin-geometry-checklist.md` and `references/house-of-apple2.md` early. Treat target selection and fake-FILE carrier placement as one heap-fengshui problem.
   - If the route depends on top chunk growth, `sysmalloc`, `NON_MAIN_ARENA`, fake `heap_info`, or arena-list behavior, open `references/how2heap-wilderness-and-arena.md` before choosing a technique.
   - If there is no meaningful allocator geometry, solve reachable field offsets, partial-overwrite budget, and trigger invariants before consulting `how2heap`.
5. Build the first candidate set.
   - Use `references/primitive-version-map.md`, `references/how2heap-taxonomy.md`, and `references/how2heap-selector.md` to list plausible families.
   - Use `scripts/find_how2heap_examples.py` to locate exact or nearby local examples.
   - Order candidates by hidden-assumption count, not aesthetics.
   - If a candidate entered the list through an old label such as `house_of_roman`, `house_of_storm`, `tcache_dup`, or `house_of_io`, rewrite it into current allocator terms before ranking it against simpler families.
   - If several candidates all end in overlap, separate them by first stable proof target: overlap only, chosen-pointer return, or fake-free consolidation.
   - If several candidates all live in fake-free space, separate them by first stable proof target: direct tcache admission, classic fastbin admission past nextsize checks, or the later chosen-pointer return.
   - If several candidates all live in fastbin / tcache space, separate them by first stable proof target: duplicate return, chosen-pointer return, allocator writeback, or metadata control.
   - If several candidates all live in unsorted / smallbin / largebin space, separate them by first stable proof target: large-value write, fake-chunk return, or stash-assisted mixed effect.
   - If a candidate is a single-write `largebin attack` feeding `apple2`, rank it by whether the inserted chunk itself can be the fake FILE carrier. If not, it is probably spending the only write too early.
   - If several candidates all live in wilderness / arena space, separate them by first stable proof target: freed wilderness, evil-size walk, or fake-arena write.
   - Rank direct stale-struct callback overwrite before hook or poisoning routes when it needs only same-size tcache reuse and an existing call trigger.
   - Rank direct libc-object call paths such as `_codecvt`, wide vtable, or other already-live stream dispatch before fake-`FILE` placement when the write window already reaches those fields.
   - Between Apple-family candidates, rank the branch that preserves more default libc state: `_wide_data`-first when that member is cleanly writable, `_codecvt`-first when `_wide_data` should stay default.
   - On threaded targets, rank same-thread reuse or explicit cross-thread bridge plans ahead of poison routes that silently assume process-wide tcache behavior.
6. Route around common dead ends early.
   - If there is no direct `free`, prioritize top-chunk or `sysmalloc` paths such as `house_of_tangerine`.
   - If `calloc` is reachable, value stash-dependent paths such as `fastbin_reverse_into_tcache`.
   - If there is no heap leak on `2.32+`, avoid plain `tcache_poisoning` unless you can decode safe-linking or pivot through metadata or leakless routes.
   - If `show` is single-shot, value single-chunk unsorted / largebin leaks and stdout-based leaks above long grooming plans.
   - If there is no `edit` but repeated UAF or reallocation exists, create overlap or a self-edit pattern first, then poison.
7. Choose the first proof target.
   - Pick the smallest claim that can be validated deterministically: overlap, pointer recovery, arbitrary allocation, arbitrary write, or stable leak.
   - Prefer proving pointer-table routing into a known target such as `stdout`, `stderr`, `environ`, or a stack slot before escalating to a heavier finish. It often validates primitive strength faster than a full FSOP chain.
   - If a local-only proof used `/proc`, debugger memory, helper metadata, or fixed local offsets to recover addresses, set the next proof target to the smallest in-band leak or dynamic targeting step that replaces one of those dependencies.
   - For stream-object routes, prefer proving the exact libc consumer path with breakpoints in the shipped libc before building the final endgame payload.
   - If the candidate depends on fake-free or largebin geometry, switch to `workflows/prove-primitive.md` with the required invariant table.
   - For one-write largebin FILE routes, the first proof target is not just "_IO_list_all changed." Prove that the written heap address already names a usable carrier chunk for the fake FILE.
8. Validate against the right versioned example.
   - Check the exact `glibc_<version>/technique.c` file first.
   - If the technique is missing for that version, inspect the nearest older and newer versions to identify what patch or check invalidated it.
   - Treat file absence as a signal. `how2heap` only keeps variants that still make sense for that version.
   - Name failed allocator checks explicitly: count>0, cleared `key`, `target+0x18` writability, fake-size equality, 0x100 overlap alignment, or 0x1000 top-chunk alignment.
9. Choose the finish only after the primitive is stable.
   - Once the heap phase yields leak, arbitrary allocation, arbitrary write, or overlap, pivot into the binary-specific control path.
   - Do not force an outdated `__malloc_hook` or `__free_hook` plan on modern libc.
   - Prefer the most stable modern finish that matches the trigger surface: stdout leak recovery, `house of apple2`, `house of cat`, `house of kiwi` as a trigger only, or exit-linked targets such as `tls_dtor_list` and `link_map`.
   - If leak or endgame routing is the hard part, switch to `workflows/choose-endgame.md`.
   - If the process aborts inside glibc, switch to `workflows/debug-allocator-failure.md`.

## Decision Rules

- Prefer the technique that needs the fewest hidden assumptions.
- Prefer exact-version examples over classic writeups from older libc.
- Treat safe-linking, alignment, and tcache fill/drain counts as first-class constraints.
- If a technique depends on a heap leak, say so explicitly and stop pretending it is leakless.
- If the challenge does not expose direct `free`, consider top-chunk and `sysmalloc` paths before overfitting to bin attacks.
- If the plan depends on `target+0x18` being writable, `count[idx] > 0`, or a later call to `fflush`, `puts`, `scanf`, `exit`, or `free`, write that dependency down before coding.
- If the plan still depends on local-only bases or fixed same-host offsets, it is not the final route yet. Keep the dependency explicit and keep solving.
- If a primitive only works because of a bypass in `how2heap`, copy the invariant, not the prose.

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
