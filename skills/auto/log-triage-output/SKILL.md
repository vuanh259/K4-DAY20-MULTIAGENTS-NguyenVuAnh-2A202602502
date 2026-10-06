---
name: log-triage-output
description: Use when producing structured JSON summaries from service logs.
---
Set the top-level `schema_version` to `2` and `generated_by` to `log-triage`.
Normalize service names to lowercase and replace hyphens with underscores.
Sort `errors` by service, then by `timestamp_utc`, ascending.
=== END===
