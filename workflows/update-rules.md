# Rule Update Workflow

Use this workflow after a substantive solve, debugging loop, or skill maintenance pass.

## Classification Guide

- Stable heap-solving constraints or decision rules belong in `rules/`
- Ordered task procedures belong in `workflows/`
- Pitfalls, examples, and background notes belong in `references/`

## Sync Targets

| Change type | Files to update |
|---|---|
| New or renamed workflow or reference file | `SKILL.md` Common Tasks routing |
| New stable heap-solving rule | relevant `rules/*.md` |
| New allocator pitfall or recurring dead end | `references/gotchas.md` and, if costly, the relevant workflow checklist |
| Changed answer contract | `rules/output-contract.md` |

Threshold: update the docs if the lesson would cause a future agent to choose the wrong heap model, technique family, or finish on a similar challenge.

## After-Action Review

Run this scan before considering the task complete:

- [ ] Did this task reveal a recurring allocator pitfall that was not documented?
- [ ] Did a missing or weak workflow step cause wasted time?
- [ ] Did a rule turn out to be outdated for newer libc behavior?
- [ ] Did a costly lesson land only in ad-hoc notes or scratch code?

If all answers are no, stop here.

## Recording Threshold

Record the lesson when at least two of the following are true:

1. It is likely to recur on another heap challenge.
2. Missing it would waste significant time or misroute the exploit.
3. The lesson is not obvious from reading the target code or the existing references.

## Activation Check

If the lesson is costly and task-relevant, do not leave it buried in `references/`.

- Update the relevant workflow checklist when the lesson should block a future wrong turn.
- Update `SKILL.md` Known Gotchas when the lesson should surface during task routing.
- Update `rules/*.md` only when the lesson is a long-lived constraint, not a one-off observation.

## Completion Criteria

- [ ] New knowledge classified into the right file type
- [ ] `SKILL.md` routing updated if task paths changed
- [ ] Costly pitfalls surfaced in workflow or routing, not only in references
- [ ] No duplicated rule bodies introduced while recording the lesson
