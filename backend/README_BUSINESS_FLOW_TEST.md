# 业务穿越测试 - 使用说明

## 📋 概述

业务穿越测试脚本用于模拟前端业务流程，测试后端API接口的完整性和可用性。这是一个全面的端到端测试，确保系统在实际业务场景下能正常工作。

## 🎯 测试覆盖范围

### 核心业务流程
1. **系统健康检查** - 验证服务基础可用性
2. **系统能力查询** - 测试智能体能力接口
3. **模板功能测试** - 测试课程模板相关操作
4. **课程设计会话流程** - 完整的PBL课程设计流程
5. **课程迭代优化** - 基于反馈的课程改进
6. **课程导出功能** - 多格式导出测试
7. **质量检查功能** - 课程质量评估
8. **协作功能测试** - 多用户协作场景
9. **智能体性能指标** - 系统监控指标
10. **会话清理** - 资源管理测试

### API接口覆盖
- **智能体相关**: `/api/v1/agents/*`
- **模板相关**: `/api/v1/templates/*`
- **质量检查**: `/api/v1/quality/*`
- **协作功能**: `/api/v1/collaboration/*`
- **健康检查**: `/api/health`

## 🚀 快速使用

### 方式1: 通过主测试脚本（推荐）
```bash
# 进入后端目录
cd backend

# 运行业务流程测试
uv run scripts/test.py --business
```

### 方式2: 直接运行业务流程测试
```bash
# 进入后端目录
cd backend

# 直接运行业务流程测试（包含服务启动）
uv run scripts/run_business_flow_test.py
```

### 方式3: 独立测试脚本
```bash
# 进入后端目录
cd backend

# 如果后端服务已启动，可直接运行测试
uv run python tests/integration/test_business_flow.py
```

## 🔧 配置选项

### 环境变量
```bash
# 测试目标地址（默认: http://localhost:8000）
export TEST_BASE_URL="http://localhost:8000"

# 数据库配置（测试环境）
export DATABASE_URL="sqlite:///./test.db"
export REDIS_URL="redis://localhost:6379/1"

# AI API密钥（如果需要）
export OPENAI_API_KEY="your_key"
export ANTHROPIC_API_KEY="your_key"
```

### 测试配置
测试脚本支持以下配置：
- 超时设置: 60秒请求超时
- 健康检查: 30次重试，2秒间隔
- 模拟用户认证: 使用Bearer token
- 测试数据: 使用faker生成中文测试数据

## 📊 测试报告

### 报告格式
测试完成后会生成JSON格式的详细报告，保存在 `tests/integration/test_reports/` 目录下。

报告包含：
```json
{
  "summary": {
    "total_tests": 10,
    "successful_tests": 8,
    "failed_tests": 2,
    "success_rate": "80.0%",
    "test_time": "2024-01-01T12:00:00"
  },
  "results": {
    "测试名称": {
      "success": true,
      "timestamp": "2024-01-01T12:00:00",
      "details": {...}
    }
  },
  "session_data": {...},
  "execution_time_seconds": 45.2
}
```

### 控制台输出
测试执行过程中会实时显示：
- ✅ 成功的测试步骤
- ❌ 失败的测试步骤
- 📋 当前执行的测试名称
- 🎉 最终测试结果汇总

## 🛠️ 测试架构

### 核心类
```python
class BusinessFlowTester:
    """业务流程测试器"""

    def __init__(self, base_url: str = "http://localhost:8000")
    async def wait_and_check_health() -> bool
    async def test_course_design_session_flow() -> bool
    async def run_complete_business_flow() -> Dict[str, Any]
```

### 测试方法
每个测试方法负责特定的业务场景：
- `test_root_endpoint()` - 基础连通性
- `test_system_capabilities()` - 系统能力
- `test_course_design_session_flow()` - 核心业务流程
- `test_course_iteration_flow()` - 迭代优化
- `test_course_export_flow()` - 导出功能
- 等...

## 🔍 故障排除

### 常见问题

#### 1. 服务启动失败
```
❌ 后端服务器启动失败
```
**解决方案**:
- 检查端口8000是否被占用
- 确认uv环境配置正确
- 查看错误日志排查具体问题

#### 2. 健康检查超时
```
❌ 服务健康检查失败，测试终止
```
**解决方案**:
- 增加健康检查等待时间
- 检查网络连接
- 确认数据库和Redis服务可用

#### 3. API认证失败
```
❌ 401 Unauthorized
```
**解决方案**:
- 检查认证中间件配置
- 确认测试用的mock token有效
- 调整认证逻辑以支持测试环境

#### 4. 数据库连接失败
```
❌ 500 Internal Server Error - Database connection failed
```
**解决方案**:
- 检查DATABASE_URL环境变量
- 确认数据库服务运行正常
- 运行数据库迁移

### 调试技巧

#### 1. 启用详细日志
```bash
export LOG_LEVEL=DEBUG
uv run scripts/test.py --business
```

#### 2. 单独测试特定功能
修改 `test_business_flow.py` 中的测试流程，注释掉不需要的测试步骤。

#### 3. 检查API响应
在测试方法中添加调试信息：
```python
print(f"Response status: {response.status_code}")
print(f"Response body: {response.text}")
```

#### 4. 手动启动后端服务
```bash
# 终端1: 启动后端服务
cd backend
uv run uvicorn app.main:app --reload

# 终端2: 运行测试
cd backend
uv run python tests/integration/test_business_flow.py
```

## 🎯 最佳实践

### 1. 定期执行
建议在以下情况执行业务穿越测试：
- 重要功能开发完成后
- 代码合并到主分支前
- 发布新版本前
- 定期的回归测试

### 2. CI/CD集成
可以将测试集成到CI/CD流水线：
```yaml
# .github/workflows/backend-test.yml
- name: Run Business Flow Tests
  run: |
    cd backend
    uv run scripts/test.py --business
```

### 3. 测试数据管理
- 使用faker生成一致的测试数据
- 每次测试后清理会话和临时数据
- 使用独立的测试数据库

### 4. 结果监控
- 定期分析测试报告
- 跟踪成功率趋势
- 及时修复失败的测试用例

## 📈 性能基准

### 预期执行时间
- 完整业务流程测试: 30-60秒
- 服务启动等待: 5-10秒
- 单个API测试: 1-5秒

### 资源消耗
- 内存使用: < 200MB
- 磁盘空间: < 10MB（日志和报告）
- 网络请求: ~20-30个HTTP请求

## 🤝 贡献指南

### 添加新测试
1. 在 `BusinessFlowTester` 类中添加新的测试方法
2. 在 `run_complete_business_flow` 中注册测试
3. 更新文档说明

### 测试方法规范
```python
async def test_new_feature(self) -> bool:
    """测试新功能"""
    try:
        # 测试逻辑
        response = await self.client.get(f"{self.base_url}/api/v1/new-feature")
        success = response.status_code == 200

        self.log_test_result("新功能测试", success, {
            "status_code": response.status_code
        })
        return success

    except Exception as e:
        self.log_test_result("新功能测试", False, {"error": str(e)})
        return False
```

---

*更新时间: 2024年9月16日*
*版本: v1.0.0*