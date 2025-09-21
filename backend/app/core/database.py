"""
数据库连接管理
配置SQLAlchemy异步数据库引擎和会话
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

# 获取配置
settings = get_settings()

# 创建异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 在开发环境中打印SQL语句
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=3600,  # 1小时重新创建连接
)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """获取数据库会话"""
    return AsyncSessionLocal()


async def get_db() -> AsyncSession:
    """FastAPI dependency for database sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    from app.models import Base
    from app.core.config import get_settings
    from sqlalchemy import text

    settings = get_settings()

    try:
        async with engine.begin() as conn:
            # Set the search path to our schema
            await conn.execute(text(f"SET search_path TO {settings.POSTGRES_SCHEMA}, public"))

            # Create all tables in the specified schema
            await conn.run_sync(Base.metadata.create_all)

            print(f"✅ Tables created successfully in schema: {settings.POSTGRES_SCHEMA}")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        # Try fallback approach using engine configuration
        try:
            # Configure engine with schema-specific connection events
            from sqlalchemy import event

            @event.listens_for(engine.sync_engine, "connect")
            def set_search_path(dbapi_connection, connection_record):
                with dbapi_connection.cursor() as cursor:
                    cursor.execute(f"SET search_path TO {settings.POSTGRES_SCHEMA}, public")

            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                print(f"✅ Tables created successfully using fallback method in schema: {settings.POSTGRES_SCHEMA}")
        except Exception as fallback_error:
            print(f"❌ Fallback method also failed: {fallback_error}")
            raise e