#!/bin/bash
# EduAgents 统一启停管理脚本
# 支持前后端一键启停，参数控制开发/生产模式

set -e

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
PID_DIR="$PROJECT_ROOT/.pids"

# 创建PID目录
mkdir -p "$PID_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
🚀 EduAgents 统一启停管理脚本

用法:
    $0 <命令> [选项]

命令:
    start           启动服务
    stop            停止服务
    restart         重启服务
    status          查看服务状态
    logs            查看服务日志
    cleanup         清理PID文件和日志

选项:
    --env <mode>    环境模式: dev|prod (默认: dev)
    --backend-only  只操作后端服务
    --frontend-only 只操作前端服务
    --port <port>   后端端口 (默认: 48284)
    --frontend-port <port> 前端端口 (默认: 48285)
    --help         显示此帮助信息

示例:
    $0 start                    # 启动前后端 (开发模式)
    $0 start --env prod         # 启动前后端 (生产模式)
    $0 start --backend-only     # 只启动后端
    $0 stop                     # 停止所有服务
    $0 restart --env prod       # 重启为生产模式
    $0 status                   # 查看服务状态

环境模式差异:
    dev   - 开发模式: 热重载、API文档、详细日志
    prod  - 生产模式: 多进程、禁用文档、优化性能
EOF
}

# 检查依赖
check_dependencies() {
    log_step "检查依赖..."

    # 检查uv
    if ! command -v uv &> /dev/null; then
        log_error "uv 未安装，请先安装: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi

    # 检查Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装，请先安装 Node.js 18+"
        exit 1
    fi

    # 检查npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装"
        exit 1
    fi

    log_info "✅ 依赖检查通过"
}

# 检查进程是否运行
is_running() {
    local pid_file="$1"
    if [[ -f "$pid_file" ]]; then
        local pid=$(cat "$pid_file")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            # PID文件存在但进程不存在，清理PID文件
            rm -f "$pid_file"
            return 1
        fi
    fi
    return 1
}

# 启动后端服务
start_backend() {
    local env_mode="$1"
    local port="$2"
    local pid_file="$PID_DIR/backend.pid"
    local log_file="$PID_DIR/backend.log"

    if is_running "$pid_file"; then
        log_warn "后端服务已在运行 (PID: $(cat $pid_file))"
        return 0
    fi

    log_step "启动后端服务 (${env_mode}模式, 端口:${port})..."

    cd "$BACKEND_DIR"

    # 确保依赖已安装
    if [[ ! -d ".venv" ]]; then
        log_step "首次运行，安装依赖..."
        uv sync
    fi

    # 构建启动命令
    if [[ "$env_mode" == "prod" ]]; then
        # 生产模式
        nohup uv run uvicorn app.main:app \
            --host 0.0.0.0 \
            --port "$port" \
            --workers 2 \
            > "$log_file" 2>&1 & echo $! > "$pid_file"
    else
        # 开发模式
        nohup uv run uvicorn app.main:app \
            --host 0.0.0.0 \
            --port "$port" \
            --reload \
            > "$log_file" 2>&1 & echo $! > "$pid_file"
    fi

    sleep 2

    if is_running "$pid_file"; then
        log_info "✅ 后端服务启动成功"
        log_info "📍 访问地址: http://localhost:${port}"
        log_info "📚 API文档: http://localhost:${port}/docs"
        log_info "📋 PID: $(cat $pid_file)"
    else
        log_error "❌ 后端服务启动失败"
        if [[ -f "$log_file" ]]; then
            log_error "错误日志:"
            tail -n 10 "$log_file"
        fi
        return 1
    fi
}

# 启动前端服务
start_frontend() {
    local port="$1"
    local pid_file="$PID_DIR/frontend.pid"
    local log_file="$PID_DIR/frontend.log"

    if is_running "$pid_file"; then
        log_warn "前端服务已在运行 (PID: $(cat $pid_file))"
        return 0
    fi

    log_step "启动前端服务 (端口:${port})..."

    cd "$FRONTEND_DIR"

    # 确保依赖已安装
    if [[ ! -d "node_modules" ]]; then
        log_step "首次运行，安装依赖..."
        npm install
    fi

    # 启动前端服务
    nohup npm run dev -- --port "$port" \
        > "$log_file" 2>&1 & echo $! > "$pid_file"

    sleep 3

    if is_running "$pid_file"; then
        log_info "✅ 前端服务启动成功"
        log_info "📍 访问地址: http://localhost:${port}"
        log_info "📋 PID: $(cat $pid_file)"
    else
        log_error "❌ 前端服务启动失败"
        if [[ -f "$log_file" ]]; then
            log_error "错误日志:"
            tail -n 10 "$log_file"
        fi
        return 1
    fi
}

# 停止服务
stop_service() {
    local service_name="$1"
    local pid_file="$PID_DIR/${service_name}.pid"

    if is_running "$pid_file"; then
        local pid=$(cat "$pid_file")
        log_step "停止${service_name}服务 (PID: $pid)..."

        # 优雅停止
        kill "$pid" 2>/dev/null || true
        sleep 2

        # 强制停止
        if ps -p "$pid" > /dev/null 2>&1; then
            kill -9 "$pid" 2>/dev/null || true
            sleep 1
        fi

        rm -f "$pid_file"
        log_info "✅ ${service_name}服务已停止"
    else
        log_warn "${service_name}服务未运行"
    fi
}

# 查看服务状态
show_status() {
    log_step "服务状态:"

    local backend_pid_file="$PID_DIR/backend.pid"
    local frontend_pid_file="$PID_DIR/frontend.pid"

    echo "后端服务:"
    if is_running "$backend_pid_file"; then
        local pid=$(cat "$backend_pid_file")
        local mem=$(ps -o rss= -p "$pid" 2>/dev/null | tr -d ' ' || echo "N/A")
        echo "  ✅ 运行中 (PID: $pid, 内存: ${mem}KB)"
    else
        echo "  ❌ 未运行"
    fi

    echo "前端服务:"
    if is_running "$frontend_pid_file"; then
        local pid=$(cat "$frontend_pid_file")
        local mem=$(ps -o rss= -p "$pid" 2>/dev/null | tr -d ' ' || echo "N/A")
        echo "  ✅ 运行中 (PID: $pid, 内存: ${mem}KB)"
    else
        echo "  ❌ 未运行"
    fi
}

# 查看日志
show_logs() {
    local service="$1"
    local lines="${2:-50}"

    case "$service" in
        "backend"|"")
            local log_file="$PID_DIR/backend.log"
            if [[ -f "$log_file" ]]; then
                log_info "后端服务日志 (最近${lines}行):"
                tail -n "$lines" "$log_file"
            else
                log_warn "后端日志文件不存在"
            fi
            ;;
        "frontend")
            local log_file="$PID_DIR/frontend.log"
            if [[ -f "$log_file" ]]; then
                log_info "前端服务日志 (最近${lines}行):"
                tail -n "$lines" "$log_file"
            else
                log_warn "前端日志文件不存在"
            fi
            ;;
        *)
            log_error "未知服务: $service"
            exit 1
            ;;
    esac
}

# 清理文件
cleanup() {
    log_step "清理PID文件和日志..."
    rm -f "$PID_DIR"/*.pid
    rm -f "$PID_DIR"/*.log
    log_info "✅ 清理完成"
}

# 主函数
main() {
    local command=""
    local env_mode="dev"
    local backend_only=false
    local frontend_only=false
    local backend_port="48284"
    local frontend_port="48285"

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            start|stop|restart|status|logs|cleanup)
                command="$1"
                shift
                ;;
            --env)
                env_mode="$2"
                shift 2
                ;;
            --backend-only)
                backend_only=true
                shift
                ;;
            --frontend-only)
                frontend_only=true
                shift
                ;;
            --port)
                backend_port="$2"
                shift 2
                ;;
            --frontend-port)
                frontend_port="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # 验证环境模式
    if [[ "$env_mode" != "dev" && "$env_mode" != "prod" ]]; then
        log_error "无效的环境模式: $env_mode (支持: dev, prod)"
        exit 1
    fi

    # 执行命令
    case "$command" in
        start)
            check_dependencies
            log_info "🚀 启动 EduAgents 服务 (${env_mode}模式)"

            if [[ "$frontend_only" == false ]]; then
                start_backend "$env_mode" "$backend_port"
            fi

            if [[ "$backend_only" == false ]]; then
                start_frontend "$frontend_port"
            fi

            echo
            show_status
            ;;
        stop)
            log_info "🛑 停止 EduAgents 服务"

            if [[ "$frontend_only" == false ]]; then
                stop_service "backend"
            fi

            if [[ "$backend_only" == false ]]; then
                stop_service "frontend"
            fi
            ;;
        restart)
            log_info "🔄 重启 EduAgents 服务"

            # 停止服务
            if [[ "$frontend_only" == false ]]; then
                stop_service "backend"
            fi

            if [[ "$backend_only" == false ]]; then
                stop_service "frontend"
            fi

            sleep 1

            # 启动服务
            check_dependencies

            if [[ "$frontend_only" == false ]]; then
                start_backend "$env_mode" "$backend_port"
            fi

            if [[ "$backend_only" == false ]]; then
                start_frontend "$frontend_port"
            fi

            echo
            show_status
            ;;
        status)
            show_status
            ;;
        logs)
            if [[ "$backend_only" == true ]]; then
                show_logs "backend"
            elif [[ "$frontend_only" == true ]]; then
                show_logs "frontend"
            else
                show_logs "backend"
                echo
                show_logs "frontend"
            fi
            ;;
        cleanup)
            stop_service "backend"
            stop_service "frontend"
            cleanup
            ;;
        "")
            log_error "请指定命令"
            show_help
            exit 1
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"