-- PBL智能助手 - 数据库Schema初始化脚本
-- 创建独立的schema以避免与现有应用冲突

-- 创建schema
CREATE SCHEMA IF NOT EXISTS pbl_core;

-- 设置schema权限
GRANT USAGE ON SCHEMA pbl_core TO postgres;
GRANT CREATE ON SCHEMA pbl_core TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA pbl_core TO postgres;

-- 注释
COMMENT ON SCHEMA pbl_core IS 'PBL智能助手核心数据Schema';

-- 为了确保后续的表和序列都在正确的schema中，设置搜索路径
SET search_path TO pbl_core, public;

-- 可选：创建一些扩展（如果需要）
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp" SCHEMA pbl_core;
-- CREATE EXTENSION IF NOT EXISTS "pgcrypto" SCHEMA pbl_core;

-- 输出确认信息
SELECT 'Schema pbl_core created successfully' AS status;