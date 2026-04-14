# Threaded Allocator Pitfalls

Use this file when a heap challenge routes attacker-controlled chunks through
worker threads, background queues, deferred callbacks, or lazy thread startup.

## Why this matters

glibc tcache is thread-local. A chunk freed by one thread does not become
directly reusable by `malloc` in another thread just because the process shares
one heap arena view in your notes.

## First-pass questions

- Which thread performs each attacker-relevant `malloc` and `free`?
- Does the first `pthread_create` happen lazily during a menu action?
- Does thread startup itself allocate enough metadata to perturb the layout you
  were about to rely on?
- Can a stale alias, duplicated handle, or secondary container still reach a
  chunk after a worker thread frees it?
- Is the intended poison consumer in the same thread that owns the tcache list?

## Common wrong assumptions

- A stale pointer to a worker-freed chunk implies main-thread `malloc` reuse.
- A readable freed chunk implies the same thread also owns the next allocation.
- A stable unsorted or remainder layout measured before worker startup will stay
  stable after the first task spawns the background thread.
- "Tcache poisoning is available" without proving the poisoned entry is consumed
  by the same thread that stores it.

## Useful bridge patterns

- Warm up lazy worker creation before committing to a precise unsorted, tcache,
  or remainder geometry.
- If the worker frees a chunk but the main thread still has a stale alias,
  test whether a second main-thread `free` can import that same chunk into the
  main thread's tcache.
- Prefer same-thread reuse or endgames that do not depend on cross-thread tcache
  consumption when the consumer thread is hard to drive deterministically.
- Track allocator ownership and trigger timing together. The right size class is
  not enough if the wrong thread later consumes the chunk.

## Reporting expectations

When thread ownership matters, write it down explicitly in the working notes:

1. which thread allocates the chunk,
2. which thread frees it,
3. which thread must later consume it,
4. what bridge, if any, moves the chunk between those thread-local tcaches.
