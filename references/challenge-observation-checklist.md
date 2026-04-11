# Challenge Observation Checklist

Use this file before naming any technique. Normalize the program surface first, then map it to allocator facts.

## Menu surface

- Record every operation and its real effect: `malloc`, `calloc`, `realloc`, `free`, show-only read, append, offset edit, or full rewrite.
- Record whether the index table lives in `.bss`, heap, stack, or mixed storage.
- Record whether freed pointers stay reachable through stale indexes, copied aliases, or secondary containers.
- Record whether allocation size, edit size, and shown length are independently controlled.
- Record whether a user-controlled knob such as `key` or difficulty changes all later allocation sizes.
- Record whether chunk reuse is immediate or gated by a state bit, reference count, or menu logic.

## I/O semantics

- Identify the actual input function: `read`, `fgets`, `gets`, `scanf("%s")`, `scanf("%c")`, `getline`, `memcpy`, `strcpy`, or custom parsing.
- Record whether newline, `NUL`, EOF, or spaces truncate or append bytes automatically.
- Record whether the command parser uses fixed-width short reads plus `atoi`-style parsing. If yes, verify whether `sendline` and fixed-width padded sends behave differently.
- Record whether partial writes, offset writes, or length confusion exist.
- Record whether output uses `puts`, `printf`, `write`, C++ streams, or buffered stdio.
- Record whether `show` is repeatable, single-shot, or format-string-like.

## Allocator surface

- Record every reachable size class, especially whether you can fill a tcache bin with 7 chunks.
- If a runtime knob changes sizes, write the exact real chunk sizes for the entire legal knob range, not just the first interesting candidate.
- Record whether `calloc` is reachable. `calloc` can skip normal tcache pops and make stash flows easier.
- Record whether `free` is reachable at all. If not, plan around top chunk or `sysmalloc`.
- Record whether you can create guard chunks to prevent consolidation.
- Record whether you can force large allocations that move unsorted chunks into large bins.

## Leak surface

- Record whether unsorted or large-bin pointers can be shown directly.
- Record whether freed tcache entries can be read back for heap leaks.
- Record whether stdout or stderr pointers are writable or re-pointable.
- Record whether stack, PIE, or libc pointers are already present in a printable structure.
- Record whether the program gives only one useful leak and whether it must recover both heap and libc.
- If the leak budget is tiny, prefer candidate size sets that make one read recover both heap and libc.

## Trigger surface

- Record whether the program exits cleanly through `exit`.
- Record whether later code still calls `free`, `malloc`, `calloc`, `puts`, `fflush`, `scanf`, or C++ flush routines after corruption.
- Record whether you can force one more `malloc` after corrupting top chunk metadata.
- Record whether a target address must satisfy side conditions such as `target+0x18` being writable.
- Record whether `alarm` or watchdog logic may make live attach or long debugger sessions unreliable.

## Version-sensitive notes

- Record whether the exact libc is known or only bracketed.
- Record whether hooks still exist.
- Record whether safe-linking applies.
- Record whether `tcache_key` is a heap pointer or randomized.
- Record whether a `kiwi`-style `__malloc_assert -> fflush(stderr)` trigger is even possible on this libc.

## Working notes format

Write the first pass in this structure:

1. Menu and input facts.
2. Allocator version and mitigations.
3. Primitive candidates.
4. Leak options.
5. Trigger options.
6. Hard preconditions and unknowns.
