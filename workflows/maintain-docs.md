# Documentation Health Maintenance

Keep this skill compact enough to activate correctly and detailed enough to prevent repeated heap-solving mistakes.

## When to Run

- After splitting or renaming files
- When `SKILL.md` starts collecting deep procedural content again
- When a rule, workflow, or gotcha file becomes hard to scan during a real solve

## Reference Ranges

| File type | Healthy range | Evaluate above | Fragment signal |
|---|---|---|---|
| `SKILL.md` | up to 100 lines | above 100 | not applicable |
| `rules/*.md` | 25 to 120 lines | above 150 | below 20 |
| `workflows/*.md` | 25 to 120 lines | above 150 | below 20 |
| `references/gotchas.md` | 10 to 60 lines | above 80 | below 8 |

These are signals, not automatic split commands.

## Split Test

Split a file only when all three are true:

1. It contains separable topics.
2. Readers struggle to find one topic quickly.
3. Each resulting file will still be meaningful on its own.

## Merge Test

Merge small files only when all three are true:

1. The topics are tightly related.
2. Readers usually need them together.
3. The merged file will still stay readable.

## Integrity Checks

- [ ] `SKILL.md` Always Read and Common Tasks point to existing files
- [ ] No workflow points to deleted references
- [ ] No rule text is duplicated across multiple files
- [ ] `references/gotchas.md` stays brief and scannable
- [ ] `agents/openai.yaml` still describes the skill accurately after structural changes

## Completion Criteria

- [ ] Any split or merge decision was made deliberately instead of by line count alone
- [ ] Routing still matches the actual file structure
- [ ] No orphaned file remains after maintenance
