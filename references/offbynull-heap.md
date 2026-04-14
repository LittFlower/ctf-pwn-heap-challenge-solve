# offbynull-heap

Use this file when the challenge, writeup hint, or exploit notes call the bug `offbynull-heap` or `off-by-null`, but the actual allocator family has not been translated yet.

If the source material is mixing `offbynull-heap` with other old community labels, open `how2heap-legacy-writeup-labels.md` first, then return here to finish the null-byte-specific split.

## What this label really means

`offbynull-heap` is a bug label, not a final technique name.

In the local `how2heap` tree it usually maps to one of these first-proof routes:

- `poison_null_byte`
- `house_of_einherjar`
- older overlap families only when the single null byte is not the real deciding fact anymore

Use this file to decide what the one-byte null actually proves first, then hand off to `how2heap-overlap-nullbyte.md` for the deeper family details.

## Repo-backed anchors

The local `README.md` records these challenge-facing anchors for the modern off-by-null corridor:

- `poison_null_byte`: PlaidCTF `2015 plaiddb`, BalsnCTF `2019 PlainNote`
- `house_of_einherjar`: SECCON `2016 tinypad`

Treat them as family anchors, not as exploit templates.

## Family map

This bridge stays split by what the one-byte null actually proves first, and the quick routing table below is the fastest way to decide whether the label really means overlap, fake-chunk return, or an older overlap family.

## Fast split

| Observable off-by-null outcome | Best first local files to open | First thing to prove |
| --- | --- | --- |
| One null byte clears size metadata and the main goal is overlap through backward consolidation | `poison_null_byte`, then `how2heap-overlap-nullbyte.md` | fake chunk can survive unlink checks and create a reusable overlap |
| One null byte clears `prev_inuse`, and a known or recoverable fake-chunk base exists | `house_of_einherjar`, then `how2heap-overlap-nullbyte.md` | backward consolidation lands on the staged fake chunk and later `malloc` can return controlled data |
| Solver notes say `offbynull`, but the actual corruption is a wider size rewrite or historical overlap trick | `how2heap-overlap-nullbyte.md` plus `overlapping_chunks` / `overlapping_chunks_2` if the version is old enough | the family is really overlap-first, not modern null-byte-first |

## Decision rules

- If the only attacker-controlled byte is a trailing `\\x00` into the next chunk metadata, start here before saying `einherjar`.
- If the solve already has a heap leak or a known fake-chunk base, bias toward `house_of_einherjar`.
- If the solve still needs only a reusable overlap and not an immediate chosen-pointer return, bias toward `poison_null_byte`.
- If the challenge label says `offbynull`, but the live overwrite is not literally one null byte, leave this file and reclassify the primitive in allocator terms first.
- If the route depends on protected-pointer handling after the overlap is built, keep the off-by-null classification here, then open `how2heap-safe-linking.md` for the follow-up poisoning stage.

## Reporting language

When you report the route, say which of these was proved first:

- off-by-null backward-consolidation overlap
- off-by-null fake-chunk return bridge
- historical overlap mislabeled as off-by-null

That phrasing is more reusable than saying only `offbynull-heap`.
