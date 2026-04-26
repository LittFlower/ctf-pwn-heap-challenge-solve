# Libio / FILE Object Corruption

Use this reference when a heap-labeled challenge turns out to corrupt a live stream object rather than heap chunk metadata.

## Switch Conditions

- There is no meaningful attacker-controlled `malloc` / `free` workflow, but a write primitive reaches `FILE`, `_IO_wide_data`, `_codecvt`, or a stream wrapper.
- The interesting trigger is `rewind`, `fseek`, `fflush`, `fclose`, wide conversion, or another stdio helper instead of allocator reuse.
- Exact shipped libc layout matters more than bin geometry or `how2heap` coverage.
- If the writable seam is really stdin/stdout field corruption or the notes explicitly say `_fileno`, stdin/stdout arbitrary read/write, or old `FSOP`, split first into `libio-stdio-primitives.md` before treating the route as a generic modern FILE-object corruption problem.

## First-Pass Proof Loop

- Map the reachable write window to exact object fields and embedded substructures before naming a technique.
- Reconstruct the shipped libc consumer path first. Do not start from historical fake-FILE layouts, `stderr-0x10` base shifts, or copied offset tables from old Apple2 notes.
- Record byte-budget constraints such as fixed-width writes, offset range, and forbidden bytes like `NUL` or newline.
- Separate writable pointer fields from writable embedded storage. Direct-call routes often depend on both.
- Prove the real libc consumer path with breakpoints in the shipped libc, not just in the main binary.
- Prove the exact indirect-call slot that the shipped path reaches. On modern wide-file paths that may live under `wide_data->_wide_vtable`, not in a nearby `FILE` field you copied from an older writeup.
- If the route uses `_codecvt` / gconv state, prove which fake-step bytes are overwritten by `step_data` or conversion helpers before the indirect call.

## Finish Selection Notes

- Prefer already-live indirect-call sites such as `_codecvt`, wide vtables, or stream callbacks over full fake-`FILE` placement when the writable field window already reaches them.
- If `_wide_data` is the clean writable seam, compare Apple2-style routes first. If `_codecvt` is the cleaner seam and `_wide_data` should stay default, compare Apple3-style routes first.
- Treat pointer-mangled stdio finishes as separate from known-base stability. `setarch -R` fixing object addresses does not imply TLS `pointer_guard` stability.
- If the only working proof needs `ptrace`, `/proc`, `setarch`, `LD_PRELOAD`, or other same-host instrumentation, label it as local-only and state what blocks the intended remote path.
