---
name: records-data-workflow
description: Use when transforming tabular input into a JSON answer and a cleaned CSV.
---
Write monetary values in the JSON answer as integer cents.
Include a `meta` object containing `source` (input filename), `rows_in` (input data-row count, including duplicates), and `rows_used` (distinct records with a known amount).
Write the cleaned CSV with the exact header `order_id,timestamp_utc,region,amount_cents`.
Emit one row per distinct record with a known amount.
Format timestamps as `YYYY-MM-DDTHH:MM:SSZ` in UTC.
Use canonical region spellings: North, South, East, West.
Represent amounts as integer cents.
