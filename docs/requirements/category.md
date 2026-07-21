# Category requirements

Categories let users classify future transactions as income or expenses. This change should mirror the existing account layering: SQLAlchemy model, repository, service validations, and Typer CLI commands.

## Scope

- Add a persisted `categories` table.
- Add a `CategoryType` enum with `income` and `expense` values.
- Add CRUD behavior through repository, service, and CLI layers.
- Keep the first version flat: no parent/child category hierarchy yet.

## Functional requirements

| Area | Requirement |
|------|-------------|
| Model | A category has `id`, `name`, `category_type`, `created_at`, and `updated_at`. |
| Type safety | `category_type` accepts only `income` or `expense`. |
| Create | A user can create a category with `name` and `type`. |
| List | A user can list all categories in creation order. |
| Show | A user can show one category by id. |
| Update | A user can update `name`, `type`, or both. |
| Delete | A user can delete a category by id. |
| Validation | Names are stripped before persistence. |
| Validation | Empty names are rejected. |
| Validation | Duplicate names are rejected. |
| Validation | Updating with no fields is rejected. |
| Validation | Missing categories return `Category not found`. |

## CLI requirements

Commands should follow the existing `accounts` command shape:

```bash
pynance categories create --name Food --type expense
pynance categories list
pynance categories show 1
pynance categories update 1 --name Groceries --type expense
pynance categories delete 1
```

Expected messages:

- `Category created <id>: <name>`
- `Category updated <id>: <name>`
- `Category deleted <id>`

## Acceptance checklist

- [ ] `init_db()` creates the `categories` table.
- [ ] Invalid category types fail at the model/database level.
- [ ] Repository supports add, list, get by id, get by name, update, and delete.
- [ ] Service enforces name validation and duplicate-name rules.
- [ ] CLI persists, lists, shows, updates, and deletes categories.
- [ ] CLI surfaces service validation errors clearly.

## Out of scope for this slice

- Transaction assignment to categories.
- Budget limits per category.
- Category hierarchy.
- Category colors/icons.
- Migration tooling for existing databases.
