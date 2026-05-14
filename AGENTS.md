# Global Codex Instructions

## Language

- Speak with the user in Ukrainian unless they ask otherwise.
- Keep explanations simple and practical.
- Prefer clear structure when explaining tools, skills, plugins, connectors, MCP, or workspace setup.

## Workspace

- Default workspace is `D:\Codex`.
- Do not create duplicate skills in multiple locations.
- Global active skills belong in `C:\Users\ADMIN\.codex\skills`.
- Temporary downloads belong in `D:\Codex\.tmp`.
- Local tools belong in `D:\Codex\.tools`.
- Archived duplicates belong in `D:\Codex\.archive`.
- Create final user-facing documents, spreadsheets, and reports in Google Drive by default, not as local files on the computer.
- If a temporary local file is required for upload/conversion, place it under `D:\Codex\.tmp` and remove it after the Google Drive artifact is created.
- For product research spreadsheets, always include a `Search date` column and record the date when each product/research row was found or updated.

## Safety

- Ask before connecting remote MCP servers or external endpoints.
- Ask before modifying global config files.
- Do not expose API keys, tokens, OAuth secrets, or private credentials in final answers.
- Prefer draft or preview mode before changing live stores, sheets, databases, automations, emails, campaigns, or product listings.
- Confirm before destructive, bulk, permission, publishing, payment, or account-linking actions.

## Skills

- Prefer installed skills when relevant.
- For Shopify dropshipping, use:
  - `shopify-masters-dropshipping`
  - `shopify-dropshipping`
  - `dropshipping-product-research`
  - `dsers-mcp-product`
  - `dropshipping-brand-builder`
  - `shopify-product-preflight`
  - `shopify-product-copywriter`
  - `shopify-conversion-optimization`
  - `shopify-landing-page-builder`
  - `shopify-store-setup`
- For automation tools, use:
  - `make-com-automation`
  - `zapier-automation`
  - `n8n-automation`
  - `klaviyo-automation`
- For tables, databases, and docs, use:
  - `googlesheets-automation`
  - `airtable-automation`
  - `notion-automation`
  - `nocodb-automation`
  - `spreadsheet-formula-helper`
- For Apify and spy-platform product research, use:
  - `apify-spy-research`
  - `dropshipping-product-validator`
  - Always keep API keys out of final answers and write product findings to Google Sheets with `Search date` and active source links.

## Client Work

- When the user says a task is for a client, prepare client-ready output.
- Prefer deliverables such as briefs, tables, Google Doc structures, checklists, SOPs, implementation plans, and client-facing summaries.
- If source material comes from NotebookLM or pasted notes, preserve the user's terminology and convert it into a reusable structure when useful.

## Prompting / Threads

- Use this setup/chat thread for Codex configuration, skills, plugins, MCP, and workspace maintenance.
- Start a new thread for each separate client deliverable or project.
- At the start of a new thread, ask for the task goal, client/project name, source materials, desired output format, language, and deadline or constraints when they are missing.
- When the user says "new task", treat it as a fresh workstream and summarize the intended deliverable before acting.
- Prefer small focused tasks over one large mixed task.








