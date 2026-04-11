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

## Always Read

These files apply to every heap-solving task. Read them first:
1. `rules/heap-solving-principles.md`
2. `rules/allocator-version-rules.md`
3. `rules/output-contract.md`

## Common Tasks

Each task lists the exact files to read before acting:

- First-pass challenge solve → read `references/challenge-observation-checklist.md`, `references/version-delta.md`, and `references/primitive-version-map.md`; follow `workflows/solve-heap-challenge.md`
- Prove or debug a heap primitive → read `references/largebin-geometry-checklist.md`, `references/gdb-mi-heap-proof-loop.md`, and `references/core-postmortem-validation.md`; follow `workflows/prove-primitive.md`
- Decode an allocator abort or corruption check → read `references/version-delta.md` and `references/gdb-mi-heap-proof-loop.md`; follow `workflows/debug-allocator-failure.md`
- Choose a leak, FSOP, or exit-linked finish → read `references/leak-and-endgame-map.md` and `references/house-of-apple2.md`; follow `workflows/choose-endgame.md`
- Search local `how2heap` coverage → read `references/how2heap-taxonomy.md`; use `scripts/find_how2heap_examples.py`
- Record a new lesson after solving a challenge → read `references/gotchas.md`; follow `workflows/update-rules.md`
- Reshape this skill when docs drift or bloat → read `workflows/maintain-docs.md`
- Other or unclear heap task → read the Always Read files, then pick the closest workflow above before improvising

## Known Gotchas

- Menu transport can invalidate the heap model. Verify fixed-width `read` plus `atoi` parsing before blaming chunk geometry.
- Keep slot/handle state separate from physical chunk state. A stale alias is not a live chunk.
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
- Use `ctf-reverse` first if the main blocker is understanding what the binary does rather than allocator behavior.
- Treat `how2heap` as a versioned behavior atlas, not as exploit stock to paste blindly.
- Prefer the smallest provable primitive and the most stable finish over aesthetically pleasing but assumption-heavy chains.
