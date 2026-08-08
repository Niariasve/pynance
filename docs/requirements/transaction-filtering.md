# Transaction filtering requirements

Transaction filtering lets users narrow the existing transaction list by date,
account, category, or category type. This slice extends the current repository,
service, and Typer CLI flow without changing transaction persistence or account
balances.

## Scope

- Add optional filters to the transaction list operation.
- Support filtering by inclusive date range, account, category, and category type.
- Combine multiple filters using `AND` semantics.
- Preserve the existing deterministic transaction ordering.
- Keep the unfiltered list behavior unchanged.

## Functional requirements

| Area | Requirement |
|------|-------------|
| Date range | `from_date` includes transactions occurring on or after that date. |
| Date range | `to_date` includes transactions occurring on or before that date. |
| Date range | Either date boundary can be used independently. |
| Date validation | When both boundaries are provided, `from_date` cannot be later than `to_date`. |
| Account | `account_id` returns only transactions assigned to that account. |
| Category | `category_id` returns only transactions assigned to that category. |
| Category type | `category_type` returns transactions whose current category type is `income` or `expense`. |
| Composition | When multiple filters are provided, a transaction must satisfy every filter. |
| Empty result | A valid filter combination with no matches returns an empty list, not an error. |
| Missing reference | A missing filtered account returns `Account not found`. |
| Missing reference | A missing filtered category returns `Category not found`. |
| Ordering | Results are ordered by `occurred_on` descending, then `id` descending. |
| Compatibility | Listing without filters returns the same results and ordering as the existing command. |
| Balance | Filtering transactions does not modify `Account.balance` or any persisted entity. |

## CLI requirements

The existing `transactions list` command accepts optional filters:

```bash
pynance transactions list --from-date 2026-08-01 --to-date 2026-08-31
pynance transactions list --account-id 1
pynance transactions list --category-id 2
pynance transactions list --type expense

pynance transactions list \
  --from-date 2026-08-01 \
  --to-date 2026-08-31 \
  --account-id 1 \
  --type expense
```

`--from-date` and `--to-date` accept ISO calendar dates in `YYYY-MM-DD` format.
`--type` accepts only `income` or `expense`. Invalid values must produce clear CLI
validation errors.

The output keeps the existing transaction list columns:

- transaction id
- date
- description
- account name
- category name
- category type
- amount

When no transaction matches, the command displays the existing empty-table
representation and exits successfully.

## Acceptance checklist

- [ ] Repository filtering supports each filter independently.
- [ ] Repository filtering combines all supplied filters with `AND` semantics.
- [ ] Date boundaries are inclusive.
- [ ] Filtered results preserve deterministic ordering.
- [ ] Service rejects an inverted date range before querying transactions.
- [ ] Service reports missing filtered accounts and categories consistently.
- [ ] CLI accepts every filter independently and in combination.
- [ ] CLI rejects invalid dates and category types clearly.
- [ ] A valid filter with no matches succeeds with an empty result.
- [ ] Calling `transactions list` without filters remains backward compatible.
- [ ] Filtering is read-only and leaves all persisted data unchanged.

## Out of scope for this slice

- Free-text search over transaction descriptions.
- Pagination or result limits.
- Sorting options other than the existing deterministic order.
- Aggregations, totals, monthly summaries, or reports.
- Automatic account balance calculation or synchronization.
- Filtering by amount ranges.
- Category snapshots; filtering uses the category's current type.
