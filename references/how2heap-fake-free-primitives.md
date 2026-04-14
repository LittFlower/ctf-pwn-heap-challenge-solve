# how2heap Fake-Free Primitives

Use this file when the challenge can `free` attacker-controlled memory or a forged chunk header and the main question is whether the nearest local route is classic `house_of_spirit` or `tcache_house_of_spirit`.

If the notes use spaced forms such as `house of spirit`, treat them as the same fake-free family and keep the split focused on fastbin admission versus direct tcache admission.

## The split that matters

Do not file these under generic overlap or poisoning:

- `house_of_spirit`
- `tcache_house_of_spirit`

Both are fake-free routes, but they prove different allocator admissions first:

- fastbin admission with sane next-chunk geometry -> `house_of_spirit`
- direct tcache admission from a fake chunk -> `tcache_house_of_spirit`

## Repo-backed anchors

The local `README.md` records these challenge-facing anchors or version cues for this family:

- `house_of_spirit`: hack.lu CTF `2014 OREO`
- `tcache_house_of_spirit`: local `> 2.25` tcache-side variant with no challenge anchor in the current README table

## Family map

### Classic `house_of_spirit`

Use `house_of_spirit` when:
- the fake chunk must survive the older fastbin path rather than landing in tcache immediately
- the first proof target is "free accepts my fake chunk and a later allocation returns it"
- you can stage both the fake chunk size and a sane next fake-chunk size

The hidden requirement is usually not the fake pointer itself. It is the nextsize check on the following fake chunk header.

### `tcache_house_of_spirit`

Use `tcache_house_of_spirit` when:
- the size class reaches tcache directly
- the first proof target is "free accepts my fake chunk into tcache and the next malloc returns it"
- you can make the fake chunk aligned and give it a valid tcache-sized chunk header

This route is simpler because the local PoC does not need a second fake chunk for nextsize sanity.

## Decision rules

- If the program can directly free a pointer into stack, `.bss`, or another attacker-staged region, start here before ranking overlap or poisoning families.
- If the matching tcache bin is available, bias toward `tcache_house_of_spirit` first.
- If the matching tcache bin is already full, intentionally bypassed, or the target is pre-tcache, bias toward classic `house_of_spirit`.
- If the route depends on `prev_size`, `prev_inuse`, or backward consolidation, leave this file and open `how2heap-overlap-nullbyte.md`.
- If the route depends on raw protected-pointer forging after the fake free, keep the fake-free proof here, then open `how2heap-safe-linking.md` for the follow-up poisoning stage.
- If the route depends on fake arena state or top-chunk behavior rather than fake-free admission, leave this file and open `how2heap-wilderness-and-arena.md`.

## Version guidance

- Pre-tcache targets bias toward classic `house_of_spirit`.
- `2.26+` can often use `tcache_house_of_spirit` for request sizes that stay in the tcache range.
- On `2.32+`, safe-linking usually does not block the first fake-free proof because the allocator writes the protected `next` itself; it matters later if you continue into manual freelist corruption.
- In the local repo, `house_of_spirit` exists through `glibc_2.42`, while `glibc_2.43` keeps only `tcache_house_of_spirit`. Treat that as a warning to verify fastbin-side assumptions on the newest libc.

## Reporting language

When you report the route, say which of these was proved first:

- fake chunk admitted into tcache
- fake chunk admitted past fastbin nextsize checks
- chosen-pointer return after fake free

That wording is more reusable than saying only "House of Spirit."
