#!/usr/bin/env python3
"""
初始化PBL智能助手专用Schema
使用独立schema避免与现有Supabase应用冲突
"""

import asyncio
import sys
from pathlib import Path

import asyncpg
from app.core.config import get_settings

async def init_schema():
    """初始化数据库schema"""
    settings = get_settings()

    # 构建连接URL（不使用schema参数，直接连接数据库）
    connection_url = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )

    try:
        # 连接数据库
        print(f"连接数据库: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
        conn = await asyncpg.connect(connection_url)

        # 读取SQL脚本
        sql_file = Path(__file__).parent / "init_schema.sql"
        if not sql_file.exists():
            print(f"错误: SQL脚本文件不存在: {sql_file}")
            return False

        sql_content = sql_file.read_text(encoding="utf-8")

        # 执行SQL脚本
        print(f"创建Schema: {settings.POSTGRES_SCHEMA}")
        await conn.execute(sql_content.replace("pbl_core", settings.POSTGRES_SCHEMA))

        # 验证schema是否创建成功
        result = await conn.fetchval(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = $1",
            settings.POSTGRES_SCHEMA
        )

        if result:
            print(f"✅ Schema '{settings.POSTGRES_SCHEMA}' 创建成功!")
            return True
        else:
            print(f"❌ Schema '{settings.POSTGRES_SCHEMA}' 创建失败!")
            return False

    except Exception as e:
        print(f"❌ 数据库连接或执行失败: {e}")
        return False
    finally:
        if 'conn' in locals():
            await conn.close()

async def check_schema_exists():
    """检查schema是否已存在"""
    settings = get_settings()

    connection_url = (
        f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )

    try:
        conn = await asyncpg.connect(connection_url)
        result = await conn.fetchval(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = $1",
            settings.POSTGRES_SCHEMA
        )
        await conn.close()
        return bool(result)
    except:
        return False

async def main():
    """主函数"""
    settings = get_settings()
    print(f"PBL智能助手 Schema初始化工具")
    print(f"目标Schema: {settings.POSTGRES_SCHEMA}")
    print("-" * 50)

    # 检查schema是否已存在
    exists = await check_schema_exists()
    if exists:
        print(f"ℹ️  Schema '{settings.POSTGRES_SCHEMA}' 已存在")
        response = input("是否重新初始化? (y/N): ").lower()
        if response != 'y':
            print("取消操作")
            return

    # 初始化schema
    success = await init_schema()

    if success:
        print("\n🎉 Schema初始化完成!")
        print(f"现在可以运行 Alembic 迁移来创建表结构:")
        print(f"  uv run alembic upgrade head")
    else:
        print("\n💥 Schema初始化失败!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())