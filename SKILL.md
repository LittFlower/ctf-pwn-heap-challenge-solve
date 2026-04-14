---
name: ctf-pwn-heap-challenge-solve
description: >
  Use this skill when the user asks to "solve this heap challenge", "analyze this
  glibc heap exploit", "debug this largebin corruption", or "map this UAF to a
  working technique". Activate when the main task is a Linux glibc heap-pwn
  challenge and Codex must recover allocator facts, prove one stable primitive,
  compare version-compatible how2heap families, and choose a leak or endgame
  route that matches the shipped libc and trigger surface.
---

# CTF Pwn Heap Challenge Solve

Version-aware workflow for glibc heap CTF challenges: normalize the surface,
prove one allocator primitive, then finish with a compatible leak or endgame.
Optimize for solving speed only when the same proof and validation standard is preserved.

## Always Read

These files apply to every heap-solving task. Read them first:
1. `rules/heap-solving-principles.md`
2. `rules/allocator-version-rules.md`
3. `rules/output-contract.md`

## Common Tasks

Each task lists the exact files to read before acting:

- First-pass challenge solve → read `references/challenge-observation-checklist.md`, `references/version-delta.md`, and `references/primitive-version-map.md`; follow `workflows/solve-heap-challenge.md`
- Heap-labeled target with writable `FILE` / libio object or wide-stream trigger → read `references/challenge-observation-checklist.md`, `references/libio-object-corruption.md`, and `references/leak-and-endgame-map.md`; follow `workflows/solve-heap-challenge.md`, then `workflows/choose-endgame.md`
- Threaded heap target or cross-thread tcache suspicion → read `references/challenge-observation-checklist.md`, `references/threaded-allocator-pitfalls.md`, and `references/leak-and-endgame-map.md`; follow `workflows/solve-heap-challenge.md`, then `workflows/choose-endgame.md` if the finish depends on same-size reuse or poisoning
- Prove or debug a heap primitive → read `references/largebin-geometry-checklist.md`, `references/gdb-mi-heap-proof-loop.md`, and `references/core-postmortem-validation.md`; follow `workflows/prove-primitive.md`
- Decode an allocator abort or corruption check → read `references/version-delta.md` and `references/gdb-mi-heap-proof-loop.md`; follow `workflows/debug-allocator-failure.md`
- Choose a leak, FSOP, or exit-linked finish → read `references/leak-and-endgame-map.md` and `references/house-of-apple2.md`; follow `workflows/choose-endgame.md`
- Audit a local-only known-base or debugger-assisted finish and convert it into an in-band leak route → read `references/challenge-observation-checklist.md`, `references/leak-and-endgame-map.md`, and `rules/output-contract.md`; follow `workflows/choose-endgame.md`
- Search local `how2heap` coverage → read `references/how2heap-taxonomy.md`; use `scripts/find_how2heap_examples.py`
- Record a new lesson after solving a challenge → read `references/gotchas.md`; follow `workflows/update-rules.md`
- Optimize this skill from live solve feedback → read `references/gotchas.md`, `workflows/update-rules.md`, and `workflows/maintain-docs.md`; follow `workflows/update-rules.md`, then `workflows/maintain-docs.md` if routing or file boundaries should change
- Reshape this skill when docs drift or bloat → read `workflows/maintain-docs.md`
- Other or unclear heap task → read the Always Read files, then pick the closest workflow above before improvising

## Known Gotchas

- Menu transport can invalidate the heap model. Verify fixed-width `read` plus `atoi` parsing before blaming chunk geometry.
- Fixed-width `read` does not imply a full-width write. Prove whether short sends return early or block; that difference can create a low-clobber transport or kill a planned overwrite.
- A heap label does not guarantee allocator gameplay. If the live writable object is `FILE` / libio state, switch to object-layout and trigger-path modeling before touching `how2heap`.
- Once `ELF.address` / `libc.address` is set in pwntools, `ELF.sym[...]` is already absolute. Re-adding the base yields non-canonical targets and fake primitive failures such as `EFAULT` on the final write.
- For Apple2 and other libio routes, do not start from inherited fake-FILE templates such as `stderr-0x10`, `fp+0x68`, or copied callback slots. Reverse the shipped libc consumer path first, then derive the exact indirect-call slot from that path.
- Keep slot/handle state separate from physical chunk state. A stale alias is not a live chunk.
- If a stale slot table lives in `.bss` and can be retargeted through a heap primitive, treat it as a pointer router immediately. It may produce arbitrary known-address read/write, `environ` leaks, or a stack-return finish before any heavier FSOP plan.
- A pointer router is constrained by UI state too. Before planning follow-up `edit` or `show` calls through a repointed slot table, prove which slot still has non-zero tracked size and enough write width; the prettiest retarget can still be a logical no-op.
- Do not let `/proc`, a debugger, or `io.libs()` become the leak plan. They are acceptable for local validation, but a real solve still needs an in-band address-recovery route unless the challenge environment itself fixes the bases.
- Before spending time on heavier exit-linked surfaces such as `__exit_funcs`, `tls_dtor_list`, or `link_map`, inventory whether clean exit already gives a stdio walk. Prefer the lower-assumption trigger first.
- Tcache is thread-local. If worker threads free or allocate target chunks, do not assume main-thread reuse or poisoning until allocator ownership is proved.
- The first worker-thread startup can perturb heap layout. If thread creation is lazy, warm it up before trusting a leak or remainder geometry.
- A freed heap object with a callable field can be the endgame. Before planning hook writes or poisoning, check whether tcache reuse can overwrite a stale struct's callback, vtable, or function pointer and whether the binary already has a stable call target.
- For largebin or fake-free plans, write the invariant table before coding. If two metadata roles overlap, treat it as a blocker.
- If live attach is flaky because of alarms, short-lived children, or PTYs, switch early to core-based validation.

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
