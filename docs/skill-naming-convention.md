# Skill Naming Convention

This repo's skills are named **object-first** (`<object>-<verb>` / `<object>-<noun>`): the prefix is the **thing being acted on**, the suffix is the **action**. A flat alphabetical skill list then clusters every skill that works on the same object — so you can see "all paper skills" or "all citation skills" in one glance.

## Core rules

1. **Object-first.** Prefix = the object/domain; suffix = the verb or narrow noun. `paper-read` (read a paper), `citation-find` (find a citation), `text-humanize` (humanize text).
2. **One prefix per object family.** All skills sharing an object share a prefix. Don't invent a new prefix if an existing object-family fits; fold the skill in (e.g. `paper-moc`, `paper-network`).
3. **Don't encode pipeline order in names.** Sequence lives in the relationship map / description, not in the id. Use a secondary prefix for a sub-family instead: the review→revision pipeline is `paper-review → paper-revise-plan → paper-revise-paragraph → paper-revise-abstract → paper-revise-verify` (the `paper-revise-*` group signals "revision stages" without numbering).
4. **English ids, lowercase, hyphen-separated.** Ids are slash-command friendly (`/paper-read`). Trigger words (often Chinese) live in the `description`, not the id.
5. **Keep file-format / brand / code identifiers untouched.** A skill about `.pptx` is named `visual-slides`, but the `.pptx` extension, `markitdown[pptx]` pip extra, `pptx.writeFile()`, and `transcriptapi.com` URLs stay as-is inside the skill body — only the *skill id* renames.
6. **Memorable exceptions allowed, sparingly.** A name with strong recall can keep a distinctive token, e.g. `paper-feynman` (keeps "feynman" + groups under `paper-`).
7. **Pull agent-meta skills out.** A skill that serves the agent/planning layer (not a content domain) stands alone with its own object prefix, e.g. `plan-revise` (keep a plan doc self-consistent) — deliberately distinct from `paper-revise-plan` (plan revisions for a paper).

## Prefixes in use

| Prefix | Object | Skills |
|--------|--------|--------|
| `paper-` | 论文 | paper-daily, paper-search, paper-read, paper-feynman, paper-survey, paper-review, paper-revise-plan, paper-revise-paragraph, paper-revise-abstract, paper-revise-verify, paper-moc |
| `citation-` | 引文 | citation-assistant, citation-find |
| `text-` | 通用文本/写作 | text-humanize, text-typeset, text-coauthor |
| `outreach-` | 外向输出（按目的） | outreach-network, outreach-xhs |
| `visual-` | 产出物/Visuals | visual-slides, visual-art, visual-theme, visual-report, visual-web |
| (standalone) | — | youtube-transcript (Tools), plan-revise (agent-meta), research-idea-refine (research ideation), claude-code-bypass (env util, claude-code-only) |

## Disambiguation pairs that look alike

- `paper-revise-plan` = plan how to revise **a paper** from review feedback (paper pipeline).
- `plan-revise` = revise **a plan document** to keep it self-consistent (agent-meta).
  Different object prefix (`paper-` vs `plan-`) → they sort into different clusters.

## Adding a new skill

1. Pick the object. Does it act on papers / citations / text / outreach-output / visuals? Use that prefix.
2. If it's a genuinely new object with no family and no fold candidate, a compound name is fine (`youtube-transcript`, `research-idea-refine`) — but prefer folding into an existing prefix when the object fits.
3. Name = `<prefix>-<verb>`. Keep it short and semantic; don't force it to equal a trigger word.
4. Update `manifest.yaml` (`skills:` list, `agent: shared` or platform), run `./install.sh` to fan out, then `bin/vibe-save`.
5. If the skill calls other skills by slash-command or relative path, those refs must use the current ids (see the cross-reference scan in the rename commit for the pattern).
