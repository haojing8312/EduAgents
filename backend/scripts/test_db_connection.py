#!/usr/bin/env python3
"""
测试数据库连接
验证PostgreSQL连接是否正常
"""

import asyncio
import sys

import asyncpg
from app.core.config import get_settings

async def test_basic_connection():
    """测试基本数据库连接"""
    settings = get_settings()

    # 不使用schema的基本连接URL
    basic_url = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )

    try:
        print(f"🔗 测试连接: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
        conn = await asyncpg.connect(basic_url)

        # 测试基本查询
        version = await conn.fetchval("SELECT version()")
        print(f"✅ 数据库连接成功!")
        print(f"📋 PostgreSQL版本: {version[:50]}...")

        # 检查当前用户
        current_user = await conn.fetchval("SELECT current_user")
        print(f"👤 当前用户: {current_user}")

        # 检查当前数据库
        current_db = await conn.fetchval("SELECT current_database()")
        print(f"🗄️  当前数据库: {current_db}")

        await conn.close()
        return True

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

async def test_schema_connection():
    """测试带schema的数据库连接"""
    settings = get_settings()

    try:
        print(f"\n🎯 测试Schema连接: {settings.POSTGRES_SCHEMA}")

        # 使用asyncpg兼容的URL格式
        conn = await asyncpg.connect(settings.ASYNCPG_URL)

        # 检查search_path
        search_path = await conn.fetchval("SHOW search_path")
        print(f"🔍 当前search_path: {search_path}")

        # 检查schema是否存在
        schema_exists = await conn.fetchval(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = $1",
            settings.POSTGRES_SCHEMA
        )

        if schema_exists:
            print(f"✅ Schema '{settings.POSTGRES_SCHEMA}' 存在")
        else:
            print(f"⚠️  Schema '{settings.POSTGRES_SCHEMA}' 不存在，需要创建")

        await conn.close()
        return bool(schema_exists)

    except Exception as e:
        print(f"❌ Schema连接失败: {e}")
        return False

async def list_existing_schemas():
    """列出现有的schema"""
    settings = get_settings()

    basic_url = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )

    try:
        conn = await asyncpg.connect(basic_url)

        # 获取所有schema
        schemas = await conn.fetch(
            """
            SELECT schema_name,
                   pg_size_pretty(sum(pg_total_relation_size(c.oid))) as size
            FROM information_schema.schemata s
            LEFT JOIN pg_class c ON c.relnamespace = (
                SELECT oid FROM pg_namespace WHERE nspname = s.schema_name
            )
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            GROUP BY schema_name
            ORDER BY schema_name
            """
        )

        print(f"\n📊 现有Schema列表:")
        print("-" * 40)
        for schema in schemas:
            size = schema['size'] or '0 bytes'
            print(f"  📁 {schema['schema_name']:<20} ({size})")

        await conn.close()

    except Exception as e:
        print(f"❌ 获取Schema列表失败: {e}")

async def main():
    """主函数"""
    print("🧪 PBL智能助手 - 数据库连接测试")
    print("=" * 50)

    # 1. 测试基本连接
    basic_ok = await test_basic_connection()
    if not basic_ok:
        print("💥 基本连接失败，请检查数据库配置!")
        sys.exit(1)

    # 2. 列出现有schema
    await list_existing_schemas()

    # 3. 测试schema连接
    schema_ok = await test_schema_connection()

    print("\n" + "=" * 50)
    if basic_ok and schema_ok:
        print("🎉 所有测试通过! 数据库配置正确")
        print("💡 可以开始运行应用了:")
        print("   uv run scripts/dev.py")
    elif basic_ok and not schema_ok:
        print("⚠️  基本连接正常，但需要初始化Schema")
        print("💡 请先运行Schema初始化:")
        print("   python scripts/init_schema.py")
    else:
        print("💥 数据库连接测试失败!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())