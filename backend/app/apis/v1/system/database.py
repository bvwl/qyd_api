"""
数据库管理API
"""
import os
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app.apis.deps import get_admin_user
from app.core.settings import (
    _slave_health_cache,
    check_slave_health,
    DB_READ_WRITE_SPLIT,
    DB_HOST,
    DB_PORT,
    DB_SLAVE1_HOST,
    DB_SLAVE1_PORT,
    DB_SLAVE2_HOST,
    DB_SLAVE2_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
)

app = APIRouter()

# 备份文件存储目录
BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)


@app.get("/health", description="获取数据库健康状态", summary="获取数据库健康状态")
async def get_database_health(
    admin_user: dict = Depends(get_admin_user)
):
    """
    获取数据库健康状态（仅管理员可用）
    
    返回：
    - 主库状态
    - 从库状态
    - 读写分离是否启用
    """
    try:
        result = {
            "read_write_split": DB_READ_WRITE_SPLIT,
            "master": {
                "host": DB_HOST,
                "port": DB_PORT,
                "status": "healthy"  # 主库默认健康
            }
        }
        
        if DB_READ_WRITE_SPLIT:
            # 检查从库健康状态
            slave1_healthy = check_slave_health("slave1")
            slave2_healthy = check_slave_health("slave2")
            
            result["slaves"] = [
                {
                    "name": "slave1",
                    "host": DB_SLAVE1_HOST,
                    "port": DB_SLAVE1_PORT,
                    "status": "healthy" if slave1_healthy else "unhealthy"
                },
                {
                    "name": "slave2",
                    "host": DB_SLAVE2_HOST,
                    "port": DB_SLAVE2_PORT,
                    "status": "healthy" if slave2_healthy else "unhealthy"
                }
            ]
        
        return {
            "code": 1,
            "message": "成功",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据库健康状态失败: {str(e)}")


@app.post("/health/clear-cache", description="清除健康检查缓存", summary="清除健康检查缓存")
async def clear_health_cache(
    admin_user: dict = Depends(get_admin_user)
):
    """
    清除健康检查缓存（仅管理员可用）
    
    用途：
    - 强制重新检查从库健康状态
    - 从库恢复后，立即生效
    """
    try:
        global _slave_health_cache
        _slave_health_cache.clear()
        
        return {
            "code": 1,
            "message": "健康检查缓存已清除"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除缓存失败: {str(e)}")


@app.get("/stats", description="获取数据库统计信息", summary="获取数据库统计信息")
async def get_database_stats(
    admin_user: dict = Depends(get_admin_user)
):
    """
    获取数据库统计信息（仅管理员可用）
    
    返回：
    - 连接池状态
    - 查询统计
    """
    try:
        from tortoise import Tortoise
        
        result = {
            "connections": {}
        }
        
        # 获取所有连接的状态
        for conn_name in ["default", "slave1", "slave2"]:
            try:
                conn = Tortoise.get_connection(conn_name)
                if conn:
                    result["connections"][conn_name] = {
                        "status": "connected",
                        "pool_size": getattr(conn._pool, 'size', 'unknown') if hasattr(conn, '_pool') else 'unknown'
                    }
                else:
                    result["connections"][conn_name] = {
                        "status": "not_configured"
                    }
            except Exception as e:
                result["connections"][conn_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "code": 1,
            "message": "成功",
            "data": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据库统计信息失败: {str(e)}")


@app.get("/export-database", description="导出数据库", summary="导出数据库（仅管理员）")
async def export_database(
    admin_user: dict = Depends(get_admin_user)
):
    """
    导出整个数据库并压缩为ZIP文件（仅管理员可用）
    
    功能：
    - 使用 mysqldump 导出数据库
    - 压缩为 ZIP 文件
    - 自动清理临时文件
    - 文件名包含时间戳
    
    返回：
    - ZIP 压缩包（包含 SQL 文件）
    """
    sql_file = None
    zip_file = None
    
    try:
        # 生成文件名（带时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sql_filename = f"database_backup_{timestamp}.sql"
        zip_filename = f"database_backup_{timestamp}.zip"
        
        sql_file = BACKUP_DIR / sql_filename
        zip_file = BACKUP_DIR / zip_filename
        
        # 设置环境变量传递密码（更安全）
        env = os.environ.copy()
        env['MYSQL_PWD'] = DB_PASSWORD
        
        # 尝试方法1：直接使用 mysqldump（适用于服务器本地或兼容的客户端）
        dump_command = [
            "mysqldump",
            f"--host={DB_HOST}",
            f"--port={DB_PORT}",
            f"--user={DB_USER}",
            "--protocol=TCP",  # 强制使用 TCP 协议
            "--single-transaction",  # 保证数据一致性
            "--quick",  # 快速导出
            "--lock-tables=false",  # 不锁表
            "--routines",  # 导出存储过程和函数
            "--triggers",  # 导出触发器
            "--events",  # 导出事件
            "--default-character-set=utf8mb4",  # 字符集
            "--set-gtid-purged=OFF",  # 禁用 GTID
            "--column-statistics=0",  # 禁用列统计（兼容性）
            DB_NAME,
        ]
        
        # 执行导出
        with open(sql_file, 'w', encoding='utf-8') as f:
            result = subprocess.run(
                dump_command,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                timeout=600,  # 10分钟超时
                env=env
            )
        
        # 检查是否成功
        if result.returncode != 0:
            error_msg = result.stderr if result.stderr else "未知错误"
            
            # 如果是认证插件问题，尝试使用 Docker 方式
            if "Authentication plugin" in error_msg or "cannot be loaded" in error_msg:
                # 清理失败的文件
                if sql_file.exists():
                    sql_file.unlink()
                
                # 尝试方法2：使用 Docker 中的 mysqldump（如果可用）
                docker_command = [
                    "docker", "run", "--rm",
                    "--network=host",  # 使用主机网络
                    "-e", f"MYSQL_PWD={DB_PASSWORD}",
                    "mysql:8.0",  # 使用 MySQL 8.0 镜像
                    "mysqldump",
                    f"--host={DB_HOST}",
                    f"--port={DB_PORT}",
                    f"--user={DB_USER}",
                    "--protocol=TCP",
                    "--single-transaction",
                    "--quick",
                    "--lock-tables=false",
                    "--routines",
                    "--triggers",
                    "--events",
                    "--default-character-set=utf8mb4",
                    "--set-gtid-purged=OFF",
                    "--column-statistics=0",
                    DB_NAME,
                ]
                
                with open(sql_file, 'w', encoding='utf-8') as f:
                    result = subprocess.run(
                        docker_command,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=600,
                        env=env
                    )
                
                if result.returncode != 0:
                    error_msg = result.stderr if result.stderr else "未知错误"
                    raise Exception(f"数据库导出失败（已尝试 Docker 方式）: {error_msg}")
            else:
                raise Exception(f"mysqldump 执行失败: {error_msg}")
        
        # 检查 SQL 文件是否有内容
        if not sql_file.exists() or sql_file.stat().st_size == 0:
            raise Exception("导出的 SQL 文件为空")
        
        # 压缩为 ZIP 文件
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(sql_file, sql_filename)
        
        # 删除临时 SQL 文件
        if sql_file.exists():
            sql_file.unlink()
        
        # 返回 ZIP 文件
        return FileResponse(
            path=str(zip_file),
            filename=zip_filename,
            media_type='application/zip',
            background=lambda: zip_file.unlink() if zip_file.exists() else None  # 下载后删除
        )
    
    except subprocess.TimeoutExpired:
        # 清理临时文件
        if sql_file and sql_file.exists():
            sql_file.unlink()
        if zip_file and zip_file.exists():
            zip_file.unlink()
        raise HTTPException(status_code=500, detail="数据库导出超时（超过5分钟）")
    
    except FileNotFoundError as e:
        # 清理临时文件
        if sql_file and sql_file.exists():
            sql_file.unlink()
        if zip_file and zip_file.exists():
            zip_file.unlink()
        
        # 判断是 mysqldump 还是 docker 不存在
        if "mysqldump" in str(e) or "No such file" in str(e):
            raise HTTPException(
                status_code=500, 
                detail="mysqldump 命令不存在。请安装 MySQL 8.0 客户端工具或确保 Docker 可用"
            )
        raise HTTPException(status_code=500, detail=f"命令执行失败: {str(e)}")
    
    except Exception as e:
        # 清理临时文件
        if sql_file and sql_file.exists():
            sql_file.unlink()
        if zip_file and zip_file.exists():
            zip_file.unlink()
        raise HTTPException(status_code=500, detail=f"数据库导出失败: {str(e)}")
