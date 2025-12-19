"""Simple database migration script

Adds parent_id, is_category, and sort_order columns to tag table
"""

import sqlite3
import os

# 数据库文件路径（相对于 backend 目录）
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "limestar.db")


def migrate():
    """Execute the migration"""
    print(f"Database path: {os.path.abspath(DB_PATH)}")

    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        return False

    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 检查所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\nExisting tables: {tables}")

        if "tag" not in tables:
            print("Error: 'tag' table does not exist")
            return False

        # 检查现有列
        print("\nChecking existing columns...")
        cursor.execute("PRAGMA table_info(tag)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        print(f"Existing columns: {existing_columns}")

        # 需要添加的列
        columns_to_add = []

        if "parent_id" not in existing_columns:
            columns_to_add.append(("parent_id", "INTEGER DEFAULT NULL"))

        if "is_category" not in existing_columns:
            columns_to_add.append(("is_category", "BOOLEAN DEFAULT 0"))

        if "sort_order" not in existing_columns:
            columns_to_add.append(("sort_order", "INTEGER DEFAULT 0"))

        if not columns_to_add:
            print("\n✓ All columns already exist. No migration needed.")
            return True

        print(f"\nAdding {len(columns_to_add)} missing column(s)...")

        # 添加缺失的列
        for col_name, col_def in columns_to_add:
            sql = f"ALTER TABLE tag ADD COLUMN {col_name} {col_def}"
            print(f"  Executing: {sql}")
            cursor.execute(sql)

        # 为 parent_id 添加索引
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
    import sys
    success = migrate()
    sys.exit(0 if success else 1)
