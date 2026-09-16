# Create a migration
```sh
poetry run alembic revision --autogenerate -m "create initial tables"

```
# run a migration
```sh
poetry run alembic upgrade head
# undo
poetry run alembic downgrade -1
# redo
poetry run alembic upgrade +1
# undo everything (removes whole db!)
poetry run alembic downgrade base
```
# info about the current migration in the db
```sh
poetry run alembic current
```