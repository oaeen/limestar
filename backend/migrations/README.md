# Database Migrations

This directory contains database migration scripts for LimeStar.

## Available Migrations

### `001_add_tag_hierarchy_fields.py`
Adds hierarchical tag support by adding these columns to the `tag` table:
- `parent_id`: Foreign key to parent tag (for sub-tags)
- `is_category`: Boolean flag to distinguish categories from tags
- `sort_order`: Integer for custom sorting

### `migrate.py`
Simple migration script that adds missing columns to existing database.

## Usage

### First-time Database Setup

If you have a fresh installation (no existing database), the database will be initialized automatically when you start the application. The models already include all necessary columns.

### Migrating an Existing Database

If you have an existing database that was created before the hierarchical tag feature was added, run:

```bash
cd backend
python migrations/migrate.py
```

This will add the missing `parent_id`, `is_category`, and `sort_order` columns to your existing `tag` table.

## Manual Database Initialization

If you need to manually initialize the database:

```bash
cd backend
python init_db.py
```

This creates all tables with the current schema.
