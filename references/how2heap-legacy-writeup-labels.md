# how2heap Legacy Writeup Labels

Use this file when a challenge, blog post, or exploit note is still speaking in old community labels and you need to translate that wording into the current allocator corridor before choosing a local `how2heap` file.

## What this file is for

- Treat old labels as hints, not as final technique names.
- Separate historical naming from the first stable allocator proof target.
- Hand off quickly into the nearest specialized reference once the label is translated.

## Translation table

| Historical label | Translate it into | Read next | Why the label can mislead |
| --- | --- | --- | --- |
| `offbynull-heap` | null-byte overlap / consolidation bug label | `offbynull-heap.md`, then `how2heap-overlap-nullbyte.md` | It names the bug, not whether the route is `poison_null_byte` or `house_of_einherjar`. |
| `tcache_dup` | obsolete tcache duplicate-return route | `how2heap-freelist-primitives.md` | It only survives directly on the old `2.26-2.28` window; newer libc usually wants a bypass family such as `house_of_botcake`. |
| `house_of_io` | historical tcache-metadata arbitrary-return route | `how2heap-freelist-primitives.md` | Despite the name, this is not libio / FILE corruption in the route-selection sense. |
| `house_of_roman` | historical mixed leakless chain | `primitive-version-map.md`, then `leak-and-endgame-map.md` | It bundles fake fastbins, unsorted-bin writes, relative overwrites, and hook-era assumptions into one old chain. |
| `house_of_storm` | historical mixed-bin return route | `how2heap-bin-attacks.md`, then `how2heap-bin-write-primitives.md` | It is a mixed unsorted-plus-largebin old route, not just "another largebin attack." |

## Decision rules

- If the label names a bug shape such as `offbynull-heap`, translate the bug first and only then choose a family.
- If the label comes from old tcache writeups, verify the libc window before trusting it literally.
- If the label implies a bundled old chain such as `house_of_roman` or `house_of_storm`, prefer re-deriving the smallest current primitive instead of copying the whole chain.

## Reporting language

When you report the route, say both:

- the historical label you translated
- the allocator family you actually proved first

That keeps old writeups searchable without letting the old name drive the exploit model by itself.
