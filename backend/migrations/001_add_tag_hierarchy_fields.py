"""Add hierarchical fields to tag table

This migration adds parent_id, is_category, and sort_order columns
to support hierarchical tag structure.

Run this script: python -m backend.migrations.001_add_tag_hierarchy_fields
"""

import sqlite3
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.config import settings


def get_db_path() -> str:
    """Extract database file path from DATABASE_URL"""
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite:///"):
        # Remove 'sqlite:///' prefix and handle relative paths
        db_path = db_url.replace("sqlite:///", "")
        if db_path.startswith("./"):
            # Relative path from backend directory
            return str(Path(project_root) / "backend" / db_path[2:])
        return db_path
    raise ValueError(f"Unsupported database URL: {db_url}")


def check_column_exists(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns


def migrate():
    """Execute the migration"""
    db_path = get_db_path()
    print(f"Database path: {db_path}")

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 检查 tag 表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tag'")
        if not cursor.fetchone():
            print("Error: 'tag' table does not exist")
            return False

        print("\nChecking existing columns...")
        cursor.execute("PRAGMA table_info(tag)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        print(f"Existing columns: {existing_columns}")

        # 需要添加的列
        columns_to_add = []

        if "parent_id" not in existing_columns:
            columns_to_add.append(("parent_id", "INTEGER", "NULL", "REFERENCES tag(id)"))

        if "is_category" not in existing_columns:
            columns_to_add.append(("is_category", "BOOLEAN", "DEFAULT 0", ""))

        if "sort_order" not in existing_columns:
            columns_to_add.append(("sort_order", "INTEGER", "DEFAULT 0", ""))

        if not columns_to_add:
            print("\n✓ All columns already exist. No migration needed.")
            return True

        print(f"\nAdding {len(columns_to_add)} missing column(s)...")

        # 添加缺失的列
        for col_name, col_type, default, extra in columns_to_add:
            sql = f"ALTER TABLE tag ADD COLUMN {col_name} {col_type} {default} {extra}".strip()
            print(f"  Executing: {sql}")
            cursor.execute(sql)

        # 为 parent_id 添加索引（如果列是新添加的）
        if "parent_id" in [col[0] for col in columns_to_add]:
            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_tag_parent_id ON tag(parent_id)")
                print("  Created index on parent_id")
            except sqlite3.Error as e:
                print(f"  Warning: Could not create index: {e}")

        # 提交更改
        conn.commit()
        print("\n✓ Migration completed successfully!")

        # 验证结果
        print("\nVerifying migration...")
        cursor.execute("PRAGMA table_info(tag)")
        new_columns = {row[1] for row in cursor.fetchall()}
        print(f"Updated columns: {new_columns}")

        required_columns = {"id", "name", "color", "parent_id", "is_category", "sort_order"}
        if required_columns.issubset(new_columns):
            print("✓ All required columns are present")
            return True
        else:
            missing = required_columns - new_columns
            print(f"✗ Still missing columns: {missing}")
            return False

    except sqlite3.Error as e:
        print(f"\n✗ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
