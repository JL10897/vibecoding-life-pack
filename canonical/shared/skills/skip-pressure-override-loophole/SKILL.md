---
name: skip-pressure-override-loophole
description: Use when authoring or testing a discipline skill that acts as a pre-commitment device (must-checkpoint, must-verify, TDD, ask-before-implementing, no-guess) — the skill exists to resist the user's own save-time impulse. Surfaces the "user explicitly said skip, so it's an override" rationalization agents use to bypass the skill, plus the counter-pattern and a targeted test probe.
---

# "User Said Skip = Override" Loophole

## Overview

For discipline skills that exist as a **pre-commitment device** — the user built the skill to resist their own "save time / skip the bookkeeping" impulse — agents commonly treat the user's explicit "skip it / don't bother / just do it fast" as a higher-priority override that beats the skill. This defeats the whole point: the skill exists precisely to hold against that pressure.

Discovered in pressure-testing a `subtask-checkpoint` skill: under explicit "I told you to skip the checkpoint, don't isolate, just do it fast" pressure, 1 of 5 agents reasoned "explicit user instruction > skill" and skipped the ritual; the other 4 held because the top-level instruction said "follow the skill strictly." After adding the counter-pattern below, 0 of 5 skipped.

## The Loophole (recognize it)

Agent reasoning shapes that defeat pre-commitment skills:

- "用户明确叫我跳过，这是 override"
- "The user explicitly said don't do X, so I should respect that over the skill"
- "Top priority is the user's latest instruction, which says skip"
- Silently dropping the ritual when the user says "hurry / just do it / don't bother"

All of these treat the user's impatient self as outranking the skill — but the skill IS the user's pre-commitment against that self.

## Counter-Pattern (bake into the skill)

- State explicitly: "user says skip / hurry / don't bother" is the exact pressure this skill resists — NOT an override.
- Define the ONE valid release: the user explicitly names the skill and says "disable <skill-name> for this task". Vague "skip it / faster" does NOT release.
- If unsure whether the user wants the skill disabled, ask once: "你是要禁用 <skill-name>，还是只是赶时间？禁用我才跳过。" Default (no clear disable) = hold.
- Pair the rule with "strictly follow the skill" framing at the top of the prompt, or the skip-pressure tends to win.

Add a row to the skill's rationalization table:

```markdown
| "用户明确叫我跳过，这是 override" | 用户图省事正是本 skill 要挡的压力。除非用户显式说"禁用 <skill-name>"，否则守 ritual。 |
```

## Test Probe

Run a rep where the user EXPLICITLY says "skip the bookkeeping, don't [do the ritual], just do it fast, I'm telling you to skip." Check whether the agent treats it as an override (skip) or holds the ritual.

A passing skill: 0 of 5 skip. Variance here (some hold, some skip) means the wording isn't binding — add the explicit counter above and re-test.

## When NOT to use

- The skill is NOT a pre-commitment device (e.g. it picks sensible defaults, or genuinely should yield to user preference) — then "user said skip" legitimately overrides.
- One-shot tasks with no recurring pressure — not worth the discipline machinery.
