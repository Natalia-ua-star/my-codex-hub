# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

This is a personal AI workspace configuration hub for the Codex/Claude environment. It stores global AI assistant instructions, active skills, and application configuration. There are no build, test, or lint commands — this is a documentation and configuration repository.

## Language

Communicate with the user in **Ukrainian** unless they ask otherwise.

## Repository Structure

| Path | Purpose |
|---|---|
| `AGENTS.md` | Global AI assistant instructions (language, workspace layout, safety rules, skill lists) |
| `config.toml` | Codex application config: model, enabled plugins, Windows sandbox settings, MCP servers |
| `.codex/skills/` | Active custom skills loaded by the Codex app |
| `Skill.md/` | Upload staging area — skills pending review, migration, or installation |
| `docs/` | Project documentation: Apps Script specs, automation references |
| `.codex-global-state.json` | Codex UI state (managed by the app; do not edit manually) |
| `installation_id` | Codex installation UUID (do not modify) |
| `cap_sid` | Workspace SID mapping (do not modify) |

## Skills Architecture

Each skill lives in its own subdirectory under `.codex/skills/`:

```
.codex/skills/
  <skill-name>/
    SKILL.md        ← the skill definition
```

A `SKILL.md` file must begin with YAML frontmatter followed by the skill body:

```yaml
---
name: skill-name
description: "One-line trigger description used by the AI to decide when to invoke the skill."
risk: low | medium | high | unknown
source: community | local | <url>
date_added: "YYYY-MM-DD"
---
```

**Active skills currently installed (25 total):**

*Core/Utility:*
- `brainstorming` — Design facilitation before any implementation; enforces Understanding Lock gate before proposing solutions.
- `guimkt-make-blueprint-expert` — Create, edit, debug, and validate Make.com scenario blueprint JSON files; includes rules for `jsonStringBodyContent` double-encoding and Python-based blueprint manipulation.
- `business-analyst` — 7-step Excel/CSV analysis producing anomaly/pattern/forecast reports (Ukrainian/Russian).
- `invoice` — PDF invoice generator from a one-line command using `reportlab` (Ukrainian/Russian).
- `spreadsheet-formula-helper` — Google Sheets / Excel formula assistance.

*Shopify/Dropshipping:*
- `shopify-masters-dropshipping`, `shopify-dropshipping` — Full store setup and dropshipping workflows.
- `dropshipping-product-research`, `dropshipping-product-validator` — Product sourcing and validation.
- `dropshipping-brand-builder` — Brand identity for dropshipping.
- `dsers-mcp-product` — DSers product research via MCP.
- `shopify-product-preflight`, `shopify-product-copywriter` — Pre-publish checks and product copy.
- `shopify-conversion-optimization`, `shopify-landing-page-builder` — CRO and landing pages.
- `shopify-store-setup` — Initial store configuration.

*Automation:*
- `make-com-automation`, `zapier-automation`, `n8n-automation`, `klaviyo-automation` — Platform-specific automation helpers.

*Tables/Docs:*
- `googlesheets-automation`, `airtable-automation`, `notion-automation`, `nocodb-automation` — Spreadsheet and database automation.

*Research:*
- `apify-spy-research` — Competitor and market research via Apify.

**Skills staged in `Skill.md/` (pending review):** None — all staged skills have been activated.

## Key Conventions from AGENTS.md

**Workspace layout (local Windows machine):**
- Global skills: `C:\Users\ADMIN\.codex\skills`
- Workspace root: `D:\Codex`
- Temp files: `D:\Codex\.tmp` (delete after Google Drive artifact is created)
- Tools: `D:\Codex\.tools`
- Archives: `D:\Codex\.archive`

**Output defaults:**
- Create final documents (spreadsheets, reports, briefs) in **Google Drive**, not as local files.
- Product research spreadsheets always include a `Search date` column.

**Safety rules:**
- Ask before connecting remote MCP servers or modifying global config files.
- Use draft/preview mode before changing live stores, automations, or product listings.
- Confirm before bulk, destructive, publishing, or payment actions.

**Preferred skills by domain** (from AGENTS.md — use these when relevant instead of ad-hoc solutions):
- Shopify/dropshipping: `shopify-masters-dropshipping`, `shopify-dropshipping`, `dropshipping-product-research`, `dsers-mcp-product`, `dropshipping-brand-builder`, `shopify-product-preflight`, `shopify-product-copywriter`, `shopify-conversion-optimization`, `shopify-landing-page-builder`, `shopify-store-setup`
- Automation: `make-com-automation`, `zapier-automation`, `n8n-automation`, `klaviyo-automation`
- Tables/docs: `googlesheets-automation`, `airtable-automation`, `notion-automation`, `nocodb-automation`, `spreadsheet-formula-helper`
- Research: `apify-spy-research`, `dropshipping-product-validator`

## Make.com Blueprint Rules (from guimkt-make-blueprint-expert skill)

When working with Make.com blueprints, never use text find/replace on the JSON — always load with `json.load()`, modify programmatically, and encode `jsonStringBodyContent` with `json.dumps(obj, separators=(",", ":"))`. Escaped quotes inside Make expressions `{{}}` break the double-encoded body parser. Array indexing in Make is 1-based.

## MCP Servers

The `dsers` MCP server is configured in `config.toml`:
```toml
[mcp_servers.dsers]
command = "D:/Codex/.tools/node-v24.12.0-win-x64/npx.cmd"
args = ["-y", "@lofder/dsers-mcp-product"]
```

Active session MCP servers include Canva, Shopify, Make.com, Google Drive, and Notion — accessed via `mcp__*` tool prefixes.
