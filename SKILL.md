---
name: ctf-pwn-heap-challenge-solve
description: >
  Use for Linux glibc heap-pwn tasks when the user asks to "solve this heap challenge",
  "analyze/debug glibc heap exploit", "route UAF/double free/off-by-null", or
  "find leakless/no-free heap path"; covers primitive proof, FILE/libio, leaks, and endgames.
---
# CTF Pwn Heap Challenge Solve
Version-aware workflow for glibc heap CTF challenges: normalize the surface, prove one allocator
primitive, then finish with a compatible leak or endgame. Optimize for solving speed only when the
same proof and validation standard is preserved. A completed solve should converge into one remotely
usable `exp` file that recovers any required addresses from the challenge itself.
## Always Read
These files apply to every heap-solving task. Read them first:
1. `rules/heap-solving-principles.md`
2. `rules/allocator-version-rules.md`
3. `rules/output-contract.md`
## Common Tasks
Each task lists the exact files to read before acting:

- First-pass challenge solve or unclear surface → read `references/challenge-observation-checklist.md`, `references/solver-fast-paths.md`, `references/version-delta.md`, and `references/primitive-version-map.md`; follow `workflows/solve-heap-challenge.md`
- Normalize noisy writeup labels or pick the nearest `how2heap` corridor (`tcache dup`, `house_of_roman`, `unsafe unlink`, `no leak`, `no free`) → read `references/how2heap-selector.md`, `references/how2heap-legacy-writeup-labels.md`, `references/primitive-version-map.md`, and `references/version-delta.md`; use `scripts/find_how2heap_examples.py` when the family is stated in allocator terms
- Route overlap, null-byte, mmap-overlap, or fake-free families (`offbynull-heap`, `house_of_einherjar`, `poison_null_byte`, `house_of_spirit`) → read `references/offbynull-heap.md`, `references/how2heap-overlap-nullbyte.md`, `references/how2heap-mmap-overlap.md`, `references/how2heap-fake-free-primitives.md`, and `references/version-delta.md`; follow `workflows/solve-heap-challenge.md` or `workflows/prove-primitive.md`
- Route fastbin, tcache, metadata, or safe-linking families (`double free`, `house_of_io`, `house_of_botcake`, `house_of_water`, `tcache_perthread_struct`) → read `references/how2heap-freelist-primitives.md`, `references/how2heap-safe-linking.md`, `references/house-water-and-stash-fengshui.md` when metadata fengshui matters, `references/heap-address-leaks.md`, and `references/version-delta.md`; follow `workflows/solve-heap-challenge.md`
- Route unsorted, smallbin, largebin, or stash families (`house_of_lore`, `large_bin_attack`, `unsorted_bin_attack`, `tcache stash unlink`) → read `references/how2heap-bin-attacks.md`, `references/smallbin-techniques.md` when same-size smallbin return/write/stash behavior matters, `references/how2heap-bin-write-primitives.md`, `references/house-water-and-stash-fengshui.md` for stash count algebra, `references/largebin-geometry-checklist.md`, and `references/version-delta.md`; follow `workflows/solve-heap-challenge.md`, `workflows/prove-primitive.md`, or `workflows/route-mp-tcache-bins-to-oob-tcache.md`
- Route no-`free` wilderness, top-chunk, or fake-arena families (`house_of_tangerine`, `sysmalloc_int_free`, `house_of_force`, `house_of_orange`) → read `references/how2heap-wilderness-and-arena.md`, `references/primitive-version-map.md`, and `references/version-delta.md`; follow `workflows/solve-heap-challenge.md`
- Route live `FILE`, stdio, or libio object corruption (`_fileno`, stdin/stdout arbitrary read/write, wide stream, `_codecvt`) → read `references/libio-object-corruption.md`, `references/libio-stdio-primitives.md`, `references/leak-and-endgame-map.md`, and `references/house-of-apple-family.md` when the branch is still Apple-family-sensitive; follow `workflows/solve-heap-challenge.md`, then `workflows/choose-endgame.md`
- Prove a primitive or decode allocator aborts → read `references/largebin-geometry-checklist.md`, `references/gdb-mi-heap-proof-loop.md`, `references/core-postmortem-validation.md`, and `references/version-delta.md`; follow `workflows/prove-primitive.md` or `workflows/debug-allocator-failure.md`
- Choose an in-band leak, final endgame, or collapse local proof into one remote `exp` → read `references/heap-address-leaks.md`, `references/leak-and-endgame-map.md`, `references/house-of-apple2.md`, and `rules/output-contract.md`; follow `workflows/choose-endgame.md`
- Reroute a stuck solve after wrong-corridor reading or proof drift → read `references/solver-fast-paths.md`, `references/challenge-observation-checklist.md`, `references/version-delta.md`, and `rules/output-contract.md`; follow `workflows/reroute-stuck-solve.md`
- Benchmark whether routing changes actually improved real solve behavior → read `references/solver-fast-paths.md`, `references/solver-benchmark-suite.md`, and `workflows/update-rules.md`; follow `workflows/run-solver-regression.md`
- Record new lessons or reshape the docs after live solve feedback → read `references/gotchas.md`, `workflows/update-rules.md`, and `workflows/maintain-docs.md`; follow `workflows/update-rules.md`, then `workflows/maintain-docs.md` if routing or file boundaries should change
- Other / unlisted heap task → read `references/solver-fast-paths.md` first, then match the nearest grouped task above instead of scanning every reference manually
## Known Gotchas
- Menu transport can invalidate the heap model. Verify fixed-width `read` plus `atoi` parsing before blaming chunk geometry.
- A heap label does not guarantee allocator gameplay. If the live writable object is `FILE` / libio state, switch to object-layout and trigger-path modeling before touching `how2heap`.
- A no-`free` top-chunk route is not automatically `house_of_tangerine`; keep it at `sysmalloc_int_free` until the freed wilderness becomes a reachable chosen-pointer bridge.
- `house_of_tangerine` is version-shaped now: `2.32+` needs a safe-linking-compatible plan, and `2.42+/2.43` need the maintained local example checked before copying older scripts.
- If a largebin write targets `mp_.tcache_bins`, remember that widening the valid `tc_idx` range does not create a spare tcache entry. Plan the out-of-range poison with at least two same-size frees and account for `tcache_get` clearing `target+0x8`.
- For `house_of_water` and `tcache stash unlink` variants, write the stash count and metadata-role table before coding. Wrong tcache drain count or a stale `2.42+` metadata offset is usually a model error, not payload bad luck.
- Do not route to `large_bin_attack` just because a chunk can be sorted into largebin. Modern largebin write routes need attacker-controlled post-free metadata mutation on the largebin chunk, typically a UAF, overlap, or stale edit that reaches `bk_nextsize`.
- Leakless off-by-null overlap is usually `poison_null_byte`, not `house_of_einherjar`; if you only need overlap, prove backward-consolidation overlap first.
- A stale slot table can become the cleanest pointer router in the challenge, but only if the surviving slot still has enough logical size and write width.
- Do not let `/proc`, a debugger, or `io.libs()` become the leak plan. They are acceptable for local validation, but a real solve still needs an in-band address-recovery route unless the challenge environment itself fixes the bases.
- Default to a remotely viable exploit path. Treat fixed local offsets, `/proc`, debugger memory, and same-host helper metadata as validation aids unless the challenge is explicitly local-only or the remote environment guarantees the same bases.
- Do not let helper-script sprawl become the deliverable. Temporary leak probes, geometry checkers, and debugger harnesses are fine, but a completed solve must collapse back into one remote-capable `exp` file.
- If the route needs PIE, libc, heap, stack, or pointer-guard state, write those address classes down explicitly and recover each one from the target or prove they are unnecessary.
- Tcache is thread-local. If worker threads free or allocate the target chunks, prove allocator ownership before assuming reuse or poisoning from the main thread.
- A freed heap object with a callable field can be the endgame. Before planning hook writes or poisoning, check whether tcache reuse can overwrite a stale struct's callback, vtable, or function pointer and whether the binary already has a stable call target.
- For largebin or fake-free geometry, write the invariant table before coding. If two metadata roles overlap, treat it as a blocker.
- If clean `exit` already walks stdio state, compare that trigger before spending time on heavier exit-linked surfaces.
- If you have opened several corridor references and still cannot name one proof target, stop and reroute instead of reading more and coding blindly.
## Rule Priority
1. `SKILL.md`
2. `rules/`
3. `workflows/`
4. `references/`
5. `scripts/`
## Project Boundaries
- This skill covers Linux glibc heap-pwn solving, not generic web, crypto, kernel, or non-heap exploit work.
- It still applies when a heap-labeled glibc challenge collapses into `FILE` / libio object corruption instead of classic allocator grooming, as long as the exploit surface and finish are still libc-heap-oriented.
- Use `ctf-reverse` first if the main blocker is understanding what the binary does rather than allocator behavior.
- Treat `how2heap` as a versioned behavior atlas, not as exploit stock to paste blindly.
- Prefer the smallest provable primitive and the most stable finish over aesthetically pleasing but assumption-heavy chains.
