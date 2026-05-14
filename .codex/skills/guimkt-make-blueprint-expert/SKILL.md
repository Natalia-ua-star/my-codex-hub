---
name: guimkt-make-blueprint-expert
description: Interpret, create, edit, validate, and optimize Make.com (formerly Integromat) scenario blueprint JSON files, including Google Sheets modules such as google-sheets:addRow.
version: "1.0.0"
updated: "2026-03-17"
source: https://github.com/guilhermemarketing/esc-skills/tree/main/skills/guimkt-make-blueprint-expert
---

# Make.com Blueprint Expert

Create, edit, debug, and optimize Make.com scenario blueprints programmatically via JSON.

## Use When

Use this skill when the user wants to:

- Create a Make scenario from scratch via blueprint JSON.
- Modify an existing blueprint JSON, including field mappings, modules, body content, API endpoints, routers, filters, or webhooks.
- Debug Make execution errors such as `InvalidConfigurationError`, HTTP 400 responses, invalid field mappings, or `jsonStringBodyContent` encoding issues.
- Generate correct Make expressions like `{{module.field}}` inside JSON bodies.
- Work with Make HTTP modules, Google Sheets modules, webhooks, routers/filters, Facebook Lead Ads, CRM integrations, variables, roleta/round-robin assignment, or Make.com automation troubleshooting.

## Critical Rules

### 1. JSON Body Content: Never Use Quoted Strings Inside Make Expressions

The `jsonStringBodyContent` field is a double-encoded JSON string: a JSON string whose content is another JSON structure containing Make expressions `{{}}`. Make validates the body as JSON before evaluating expressions, so escaped quotes inside `{{}}` break the parser.

```json
// ❌ Breaks because quotes inside {{}} terminate JSON string parsing
{"name":"{{ifempty(1.field_name; \"fallback\")}}"}

// ✅ Works: direct value, no quoted fallback
{"name":"{{1.field_name}}"}

// ✅ Works: ifempty with another field reference, no quoted string literal
{"type":"{{ifempty(1.data.field_a[]; 1.data.field_b[])}}"}
```

If a string fallback is needed, set it in a **Set Variable** module before the HTTP module, then reference the variable.

### 2. Double-Encoding: Always Use Python `json.dumps()`

The `jsonStringBodyContent` blueprint value has two encoding layers:

- Layer 1: the body content itself is a JSON object with Make expressions as values.
- Layer 2: that JSON object is stored as a string value inside the blueprint JSON file.

Always use Python's `json.dumps()` to generate correctly escaped values:

```python
import json

body_obj = {
    "name": "{{1.data.full_name}}",
    "email": "{{1.data.email}}",
    "config": {"id": "{{25.my_variable}}"},
}

blueprint_value = json.dumps(body_obj, separators=(",", ":"))
```

### 3. Array Indexing Is 1-Based

Make uses 1-based indexing for arrays. Empty brackets `[]` do **not** select a single item; they flatten or iterate arrays into strings.

```text
// ❌ Wrong: does not select a single value
{{50.data.results[].id}}

// ✅ Correct: selects the first element
{{50.data.results[1].id}}

// ✅ Correct: flattens array to comma-separated string
{{1.data.tags[]}}
```

### 4. Never Edit Blueprints with Text-Based Find/Replace

Blueprint JSON files have very long lines with complex multi-level escaping. Text-based find-and-replace can corrupt the file. Always use Python to read, modify, and write blueprint JSON.

```python
import json

with open("blueprint.json", "r", encoding="utf-8") as f:
    bp = json.load(f)

for item in bp["flow"]:
    for route in item.get("routes", []):
        for module in route.get("flow", []):
            mapper = module.get("mapper", {})
            if "jsonStringBodyContent" in mapper:
                body = json.loads(mapper["jsonStringBodyContent"])
                body["name"] = "{{1.data.full_name}}"
                mapper["jsonStringBodyContent"] = json.dumps(body, separators=(",", ":"))

with open("blueprint.json", "w", encoding="utf-8") as f:
    json.dump(bp, f, indent=4, ensure_ascii=False)
```

## Blueprint Structure

### Top-Level Anatomy

```json
{
  "name": "Scenario Name",
  "flow": [
    {"id": 1, "module": "trigger-module:watch"},
    {"id": 2, "module": "google-sheets:addRow"},
    {"id": 25, "module": "util:SetVariable2"},
    {"id": 50, "module": "http:ActionSendData"},
    {
      "id": 60,
      "module": "builtin:BasicRouter",
      "routes": [
        {"flow": [{"id": 70}, {"id": 71}], "filter": {"conditions": []}},
        {"flow": [{"id": 80}, {"id": 81}], "filter": {"conditions": []}}
      ]
    }
  ],
  "metadata": {"instant": true, "version": 1}
}
```

### Module Types Reference

| Module string | Type |
| --- | --- |
| `facebook-lead-ads:watchLeads` | Facebook Lead Ads trigger |
| `google-sheets:addRow` | Google Sheets - Add Row |
| `http:ActionSendData` | HTTP - Make a request (POST/PATCH/PUT) |
| `http:ActionGetData` | HTTP - Get data (GET) |
| `util:SetVariable2` | Tools - Set Variable |
| `builtin:BasicRouter` | Router with routes and filters |
| `json:ParseJSON` | JSON - Parse |
| `builtin:BasicFeeder` | Iterator |
| `builtin:BasicAggregator` | Aggregator |
| `gateway:CustomWebHook` | Custom Webhook trigger |
| `util:FunctionSleep` | Tools - Sleep |

## HTTP Module Mapper Fields

```json
{
  "mapper": {
    "url": "https://api.example.com/v1/resource",
    "method": "post",
    "headers": [
      {"name": "Authorization", "value": "Bearer {{token}}"},
      {"name": "Content-Type", "value": "application/json"}
    ],
    "contentType": "json",
    "inputMethod": "jsonString",
    "jsonStringBodyContent": "{...encoded JSON...}",
    "parseResponse": true,
    "stopOnHttpError": true,
    "allowRedirects": true,
    "shareCookies": false,
    "requestCompressedContent": true
  }
}
```

## Router Filter Conditions

Filters use nested arrays with operator objects.

```json
{
  "filter": {
    "name": "Route Name",
    "conditions": [
      [
        {
          "a": "{{50.data.count}}",
          "b": "0",
          "o": "number:equal"
        }
      ]
    ]
  }
}
```

Common operators include `number:equal`, `number:notEqual`, `number:greater`, `number:less`, `text:equal`, `text:contain`, `text:startsWith`, `exist`, and `notExist`.

## Set Variable Module — Roleta / Round-Robin Distribution

A roleta is a common pattern for distributing leads, tasks, or tickets among team members. It uses a `Set Variable` module with `random` to assign items probabilistically.

Create a roleta when:

- The client needs to distribute leads or tasks among two or more agents.
- CRM APIs require an `attendantId` or `assigneeId` on creation.
- The user mentions roleta, round-robin, distribuição, or distributing leads.

Place the Set Variable module before any HTTP module that needs the assigned value.

```json
{
  "id": 25,
  "module": "util:SetVariable2",
  "version": 1,
  "parameters": {},
  "mapper": {
    "name": "roleta_crm",
    "scope": "roundtrip",
    "value": "{{if(random > 0.5; \"UUID-AGENT-A\"; \"UUID-AGENT-B\")}}"
  }
}
```

Reference the variable in downstream modules with `{{moduleId.variableName}}`:

```json
{
  "assigneeId": "{{25.roleta_crm}}",
  "attendant": {"id": "{{25.roleta_crm}}"}
}
```

## Debugging Common Make Errors

### `InvalidConfigurationError`: JSON Body Content Is Not Valid JSON

Cause: escaped quotes inside Make expressions in `jsonStringBodyContent`, such as `ifempty(val; "text")`.

Fix: remove `ifempty` or `if` calls that use string literals with quotes inside the body content. Use direct field references or pre-compute the value in a Set Variable module.

### HTTP 400: Required Field Is Empty

Cause: wrong field path, such as `1.data.full_name` when the internal field name is `1.data.nome`, or wrong module ID prefix.

Fix: check the trigger module's `interface.output` spec for correct internal field names.

### HTTP 400: Invalid Field Value

Cause: a fallback like `ifempty(field; "null")` sends the literal string `null` as a field value.

Fix: remove the fallback or use an empty string only if the receiving API accepts it.

### Incomplete Executions / DLQ

Make pauses sequential scenarios when errors accumulate. Items in the dead-letter queue carry the original request body, so retrying will not pick up new module mappings.

Fix: delete DLQ items, fix the module, reactivate the scenario, and reprocess data from an earlier source such as Google Sheets if needed.

### Module Output Not Available

Cause: referencing a module that has not run yet or is in a different router branch.

Fix: reference only modules that are guaranteed to have executed in the current flow path.

## Workflow: Creating a New Blueprint

1. Define the flow: list all modules in order with their connections.
2. Build body objects in Python as plain dictionaries with Make expressions as string values.
3. Generate the blueprint structure programmatically using Python.
4. Encode `jsonStringBodyContent` values with `json.dumps(obj, separators=(",", ":"))`.
5. Validate the final JSON with `json.load()` before delivering.
6. Test by importing into Make and running with a sample trigger.

## Workflow: Fixing an Existing Blueprint

1. Load the blueprint with `json.load()`.
2. Navigate to the target module through `bp["flow"]`, routes, flow, and mapper.
3. Parse existing body content with `json.loads(mapper["jsonStringBodyContent"])`.
4. Fix body fields, field names, paths, and broken expressions.
5. Write the body back with `mapper["jsonStringBodyContent"] = json.dumps(body, separators=(",", ":"))`.
6. Save using `json.dump(bp, f, indent=4, ensure_ascii=False)`.
7. Re-load the saved file with `json.load()` to confirm valid JSON.
8. Print module bodies for visual verification before delivering.

## Validation Script Pattern

```python
import json

with open("blueprint.json", "r", encoding="utf-8") as f:
    bp = json.load(f)

print("✅ Blueprint is valid JSON")

for item in bp["flow"]:
    for route in item.get("routes", []):
        for module in route.get("flow", []):
            mapper = module.get("mapper", {})
            body = mapper.get("jsonStringBodyContent", "")
            url = mapper.get("url", "")
            method = mapper.get("method", "post")
            if body:
                body_json = json.loads(body)
                print(f"\nModule {module['id']} ({method.upper()} {url}):")
                for k, v in body_json.items():
                    print(f"  {k}: {v}")
```

## Client-Facing HTML Output

When requested, generate an additional styled HTML document for client presentation or documentation. The primary output remains the Make blueprint JSON.

HTML rules:

1. Use gui.marketing visual style: Inter Tight/Inter, background `#f7f3ed`, accent `#864df9`.
2. Document modules, routers, filters, and connections in tables or cards.
3. Header link: `https://gui.marketing/?utm_source=esc-skills&utm_medium=deliverable&utm_campaign=guimkt-make-blueprint-expert&utm_content=header-logo`.
4. Footer link: `https://gui.marketing/?utm_source=esc-skills&utm_medium=deliverable&utm_campaign=guimkt-make-blueprint-expert&utm_content=footer`.
5. Save as `make-blueprint-{{CLIENTE}}.html`.
