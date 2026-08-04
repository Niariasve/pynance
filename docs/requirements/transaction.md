# Transaction requirements

Transactions let users record income and expenses against an existing account and category. This change should follow the same layering as accounts and categories: SQLAlchemy model, repository, service validations, and Typer CLI commands.

## Scope

- Add a persisted `transactions` table.
- Link every transaction to one existing account and one existing category.
- Add CRUD behavior through repository, service, and CLI layers.
- Treat the amount as a positive magnitude; the category type determines whether it is income or expense.
- Keep account balances independent from transactions in this first version.

## Functional requirements

| Area | Requirement |
|------|-------------|
| Model | A transaction has `id`, `account_id`, `category_id`, `amount`, `description`, `occurred_on`, `created_at`, and `updated_at`. |
| Relationships | `account_id` and `category_id` are required foreign keys. |
| Amount | `amount` uses fixed-point decimal storage with two fractional digits. |
| Amount | Zero, negative, infinite, and NaN amounts are rejected. |
| Description | Descriptions are stripped before persistence and cannot be empty. |
| Date | `occurred_on` is required and represents the calendar date on which the transaction occurred. |
| Create | A user can create a transaction for an existing account and category. |
| List | A user can list transactions ordered by `occurred_on` descending, then `id` descending. |
| Show | A user can show one transaction by id. |
| Update | A user can update account, category, amount, description, or date. |
| Delete | A user can delete a transaction by id. |
| Validation | Updating with no fields is rejected. |
| Validation | Missing accounts return `Account not found`. |
| Validation | Missing categories return `Category not found`. |
| Validation | Missing transactions return `Transaction not found`. |
| Referential integrity | Accounts and categories referenced by transactions cannot be deleted. |
| Balance | Creating, updating, or deleting a transaction does not modify `Account.balance`. |

## CLI requirements

Commands should follow the existing `accounts` and `categories` command shape:

```bash
pynance transactions create \
  --account-id 1 \
  --category-id 2 \
  --amount 24.50 \
  --description "Groceries" \
  --date 2026-07-28

pynance transactions list
pynance transactions show 1

pynance transactions update 1 \
  --amount 30.00 \
  --description "Weekly groceries"

pynance transactions delete 1
```

`--date` accepts ISO calendar dates in `YYYY-MM-DD` format. Invalid dates and decimal values must produce clear CLI validation errors.

Expected messages:

- `Transaction created <id>`
- `Transaction updated <id>`
- `Transaction deleted <id>`

List and show output should include:

- transaction id
- date
- description
- account name
- category name
- category type
- amount

## Acceptance checklist

- [ ] `init_db()` creates the `transactions` table.
- [ ] The database enforces required account and category foreign keys.
- [ ] SQLite foreign-key enforcement is enabled for every application connection.
- [ ] Repository supports add, list, get by id, update, and delete.
- [ ] Repository returns transactions in the required deterministic order.
- [ ] Service validates the transaction, account, and category before persistence.
- [ ] Service rejects updates that provide no fields.
- [ ] CLI persists, lists, shows, updates, and deletes transactions.
- [ ] CLI displays account and category names instead of only their ids.
- [ ] CLI surfaces service validation errors clearly.
- [ ] Referenced accounts and categories cannot be deleted.
- [ ] Transaction operations leave `Account.balance` unchanged.

## Out of scope for this slice

- Automatic account balance calculation or synchronization.
- Transfers between accounts.
- Split transactions with multiple categories.
- Recurring transactions.
- Attachments, notes, or tags.
- Transaction search, filtering, pagination, or reporting.
- Category snapshots; transactions use the category's current name and type.
- Migration tooling for existing databases.
