#!/usr/bin/env python3
"""
直接连接到Supabase数据库容器进行测试
绕过Supavisor连接池
"""

import asyncio
import asyncpg

async def test_direct_connection():
    """测试直接连接数据库容器"""

    # 直接连接数据库容器，绕过连接池
    db_config = {
        'host': '172.18.0.4',  # 数据库容器IP
        'port': 5432,
        'user': 'postgres',
        'password': 'Textloom2025',
        'database': 'postgres'
    }

    try:
        print(f"🔗 直接连接数据库容器: {db_config['host']}:{db_config['port']}")
        conn = await asyncpg.connect(**db_config)

        # 测试基本查询
        version = await conn.fetchval("SELECT version()")
        print(f"✅ 数据库连接成功!")
        print(f"📋 PostgreSQL版本: {version[:50]}...")

        # 检查当前用户和数据库
        current_user = await conn.fetchval("SELECT current_user")
        current_db = await conn.fetchval("SELECT current_database()")
        print(f"👤 当前用户: {current_user}")
        print(f"🗄️  当前数据库: {current_db}")

        # 列出现有schema
        schemas = await conn.fetch(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast') ORDER BY schema_name"
        )
        print(f"\n📊 现有Schema:")
        for schema in schemas:
            print(f"  📁 {schema['schema_name']}")

        # 测试创建schema
        schema_name = 'pbl_core'
        await conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
        print(f"\n✅ Schema '{schema_name}' 创建成功")

        # 验证schema
        schema_exists = await conn.fetchval(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = $1",
            schema_name
        )
        print(f"🔍 Schema验证: {'存在' if schema_exists else '不存在'}")

        await conn.close()
        return True, db_config

    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False, None

async def main():
    """主函数"""
    print("🧪 直接数据库容器连接测试")
    print("=" * 50)

    success, config = await test_direct_connection()

    if success:
        print("\n🎉 直接连接测试成功!")
        print("💡 建议的配置:")
        print(f"POSTGRES_SERVER={config['host']}")
        print(f"POSTGRES_PORT={config['port']}")
        print(f"POSTGRES_USER={config['user']}")
        print(f"POSTGRES_PASSWORD={config['password']}")
        print(f"POSTGRES_DB={config['database']}")
        print(f"POSTGRES_SCHEMA=pbl_core")
    else:
        print("\n💥 直接连接测试失败!")

if __name__ == "__main__":
    asyncio.run(main())