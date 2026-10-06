---
name: log-triage-output
description: Use when producing structured JSON output from application logs for triage.
---
Set the top-level `schema_version` to `2` and `generated_by` to `log-triage`.
Normalize service names to lowercase and replace `-` with `_`.
Sort `errors` by service, then by `timestamp_utc`, ascending.
