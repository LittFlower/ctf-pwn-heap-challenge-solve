# how2heap Safe-Linking

Use this file when the challenge already looks like a freelist problem, but the actual route selection is blocked by protected-pointer handling on `2.32+`.

## The split that matters

Do not collapse these into generic tcache poisoning:

- `decrypt_safe_linking`
- `safe_link_double_protect`
- metadata-side routes such as `house_of_water`
- out-of-range metadata writes such as `tcache_relative_write`

The right split is based on what you can prove first: recover a protected pointer, synthesize one without a leak, or route around pointer forging entirely through metadata control.

## Repo-backed anchors

The local `README.md` records these challenge-facing anchors or version cues for this corridor:

- `decrypt_safe_linking`: local `>= 2.32` pointer-recovery example with no challenge anchor in the README table
- `safe_link_double_protect`: `37c3 Potluck Tamagoyaki`
- `house_of_water`: `37c3 Potluck Tamagoyaki`
- `tcache_metadata_poisoning`: local metadata-control example with no challenge anchor in the README table
- `tcache_relative_write`: local `2.30-2.41` metadata-write example with no challenge anchor in the README table
- `tcache_metadata_hijacking`: local `>= 2.42` metadata-overflow example with no challenge anchor in the README table

Treat those as routing anchors, not as permission to skip the protected-pointer proof on the shipped libc.

## Family map

### `decrypt_safe_linking`

Use when:
- a poisoned `next` value is readable
- the first proof target is pointer recovery, not immediate arbitrary return
- same-page or known page-offset reasoning can recover the real pointer

This is the "understand the protected pointer" branch.

### `safe_link_double_protect`

Use when:
- you can feed a once-protected pointer back through the protection path
- the first proof target is a leakless arbitrary pointer link
- metadata control is already strong enough to reinsert or restage the protected value

This is the "cancel protection by protecting twice" branch.

### Metadata-side avoidance

Use `house_of_water`, `tcache_metadata_poisoning`, `tcache_metadata_hijacking`, or `tcache_relative_write` when:
- raw protected-pointer forging is the wrong battleground
- the real exploit surface is tcache metadata instead of a single `next` field
- the first proof target is metadata control, relative write, or leakless allocator steering

This is often the practical modern branch when no clean heap leak exists.

For `house_of_water`, continue into `house-water-and-stash-fengshui.md` before coding. The maintained examples are version-shaped: `2.32-2.41`, `2.42`, and `2.43` use different metadata placement and drain assumptions.

## Decision rules

- If you can read a mangled pointer and the route needs a real heap relation first, bias toward `decrypt_safe_linking`.
- If you need an arbitrary protected pointer without a heap leak and can recycle metadata through the same key, bias toward `safe_link_double_protect`.
- If the challenge has no clean heap leak and already offers overlap or metadata reach, bias away from plain `tcache_poisoning` and toward metadata-side routes.
- Out-of-range tcache poisoning after an `mp_.tcache_bins` write still obeys normal tcache return rules: aligned target, forged `next`, non-zero count, and `e->key = 0` at `target+0x8`.
- If the route is still mostly about duplicate return, stash behavior, or wilderness steering, leave this file and go back to the corridor selector that owns that primitive.

## Version guidance

- `2.32+`: safe-linking is now a first-class route-selection constraint.
- `2.34+`: hook-era finishes are gone, so protected-pointer handling often decides whether the heap phase remains worth pursuing.
- Post-`2.42`: metadata positioning changes can make metadata-side avoidance easier than raw pointer recovery.

## Reporting language

When you report the route, say which of these was proved first:

- protected pointer recovered
- protected pointer synthesized leaklessly
- pointer forging avoided through metadata control

That phrasing is more reusable than saying only "safe-linking bypass."
