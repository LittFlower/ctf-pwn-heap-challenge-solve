# GDB MI Heap Proof Loop

Use this when the heap primitive is not fully trusted yet.

Goal:
- make heap validation reproducible
- avoid interactive debugger drift
- prove one allocator transition at a time

Prefer:
- `gdb --interpreter=mi3`
- `gdb --interpreter=mi4`

Use plain CLI only if MI mode is unavailable or the environment wrapper breaks MI output.
If live attach works inconsistently because the target is PTY-driven, alarm-limited, or launched from
another tool session, switch to a core-based proof loop instead of repeatedly fighting debugger transport.

## What to prove

Keep the proof loop narrow. For each candidate primitive, prove exactly:
- `free(B)` survives
- `A` enters unsorted, then largebin
- forged/coalesced `B` enters the intended largebin index
- the intended largebin write happens

Do not debug the whole exploit before these are stable.

## Minimal command plan

For one candidate layout, script a loop around:
- start program with fixed input
- break at `_int_free`
- break at `_int_malloc` if largebin sorting depends on later allocation
- when stopped:
  - dump chunk headers around `A`
  - dump chunk headers around fake `B`
  - print relevant arena/bin pointers
  - continue

Good stop points:
- just before `free(B)`
- first `_int_free` handling of `B`
- first `_int_malloc` that should sort unsorted into largebin
- the largebin insertion point that should perform the write

## Minimal data to dump every time

Record:
- `A` chunk header
  - `prev_size`
  - `size`
  - `fd`
  - `bk`
  - `fd_nextsize`
  - `bk_nextsize`
- fake `B` chunk header
  - `prev_size`
  - `size`
- next real chunk header after `B.end`
- any free tail chunk used for forward consolidation
- the target address expected to receive the largebin write

If you cannot say which addresses matter before launching GDB, the geometric model is incomplete.

## Suggested MI workflow

Treat this as a shape, not a mandatory exact script:

1. Launch under MI.
2. Set breakpoints on allocator internals or on challenge wrappers around `free`/`malloc`.
3. Run with deterministic input.
4. On each stop:
   - evaluate the relevant memory words
   - compare against the invariant table
   - continue or abort immediately

The key property is machine-checkable output. Avoid long interactive sessions that are hard to replay.

## When to abandon live attach

Switch away from live attach early if you see any of:
- attach succeeds but memory reads intermittently fail
- `info proc mappings` is incomplete or inconsistent
- the inferior dies to `alarm` before the intended stop point
- the target is being driven by another tool session and the debugger state drifts

In those cases:
1. keep a tiny deterministic exploit or proof harness
2. run it to a crash or deliberate stop
3. collect a core if possible
4. use `references/core-postmortem-validation.md` to close the proof loop

## What to conclude from failures

Map failures to model defects:

- stop never reaches the expected allocator path
  - grooming/order assumption is wrong
- fake header words are wrong before `free(B)`
  - stale handle / write-base model is wrong
- `_int_free` aborts before consolidation
  - fake-free geometry is wrong
- `A` never reaches largebin
  - unsorted-to-largbin trigger assumption is wrong
- largebin insertion aborts on nextsize corruption
  - same-bin/order invariant is wrong

Write the failed invariant down and revise the model. Do not just mutate the exploit and rerun.

- attach is successful but target memory still cannot be read reliably
  - debugger transport or inferior lifetime is unstable; stop spending time on live attach and pivot to core

## Keep a tiny proof harness

Per challenge, keep one minimal script whose only job is:
- build one candidate heap state
- trigger one allocator transition
- stop in GDB/MI
- dump the invariant words

That script is often more valuable than an early exploit draft.
