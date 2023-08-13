Usage:

```bash
poetry install
```

```python
litestar --app litestar_test.app:app run --reload --debug
```

# Notes

- [SQLite foreign key support](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support) does *not*
include any constraint behavior by default. A `PRAGMA foreign_keys = ON` statement must be emitted on all connections.
