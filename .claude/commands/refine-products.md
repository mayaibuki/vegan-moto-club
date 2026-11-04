---
description: Run the VMC product enrichment pass now (same rules as the daily scheduled task) for the whole queue or for the Notion page ids given as arguments. Uses the Claude Code subscription, never the Anthropic API.
allowed-tools: Agent, Skill, WebFetch, WebSearch, Bash, Read, Write, mcp__a0fe616a-ee45-48ad-826a-40d1bb70fdfe__notion-fetch, mcp__a0fe616a-ee45-48ad-826a-40d1bb70fdfe__notion-query-data-sources, mcp__a0fe616a-ee45-48ad-826a-40d1bb70fdfe__notion-update-page, mcp__a0fe616a-ee45-48ad-826a-40d1bb70fdfe__notion-create-file-upload, mcp__a0fe616a-ee45-48ad-826a-40d1bb70fdfe__notion-get-file-download-urls
---

Read `~/.claude/scheduled-tasks/vmc-product-enrichment/SKILL.md` and follow its body as your instructions, with two differences:

1. The user is present. You may ask one clarifying question if a row is ambiguous, but prefer to decide and note it in the report.
2. If arguments were given (`$ARGUMENTS`), treat them as Notion page ids or URLs and process only those rows, skipping the queue query in step 2. Otherwise run the normal queue.

The rules, the agents (`.claude/agents/gear-researcher.md`, `gear-writer.md`, `gear-verifier.md`), the brand voice (`docs/brand-voice.md`), the green publish gate and the report location are all defined there. Do not keep a second copy of them here.
