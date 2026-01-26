#!/usr/bin/env python3
"""
部署检查脚本
用于检查部署环境和配置是否正确

使用方法:
    python check_deployment.py
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))


class DeploymentChecker:
    """部署检查器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
    
    def check(self, name, condition, error_msg=None, warning_msg=None):
        """执行检查"""
        self.total_checks += 1
        
        if condition:
            print(f"  ✓ {name}")
            self.success_count += 1
            return True
        else:
            if error_msg:
                print(f"  ✗ {name}: {error_msg}")
                self.errors.append(f"{name}: {error_msg}")
            elif warning_msg:
                print(f"  ⚠ {name}: {warning_msg}")
                self.warnings.append(f"{name}: {warning_msg}")
            else:
                print(f"  ✗ {name}")
                self.errors.append(name)
            return False
    
    def check_python_version(self):
        """检查 Python 版本"""
        print("\n" + "=" * 60)
        print("1. 检查 Python 环境")
        print("=" * 60)
        
        version = sys.version_info
        self.check(
            f"Python 版本 {version.major}.{version.minor}.{version.micro}",
            version >= (3, 11),
            error_msg="需要 Python 3.11 或更高版本"
        )
    
    def check_dependencies(self):
        """检查依赖包"""
        print("\n" + "=" * 60)
        print("2. 检查依赖包")
        print("=" * 60)
        
        required_packages = [
            'fastapi',
            'uvicorn',
            'tortoise',
            'aerich',
            'redis',
            'jose',
            'passlib',
            'loguru',
            'httpx',
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                self.check(f"包 {package}", True)
            except ImportError:
                self.check(
                    f"包 {package}",
                    False,
                    error_msg="未安装，请运行: pip install -r requirements.txt"
                )
    
    def check_env_file(self):
        """检查环境变量文件"""
        print("\n" + "=" * 60)
        print("3. 检查环境变量")
        print("=" * 60)
        
        # 检查 .env 文件是否存在
        env_file = Path('.env')
        self.check(
            ".env 文件存在",
            env_file.exists(),
            error_msg="未找到 .env 文件，请复制 .env.example 并配置"
        )
        
        if not env_file.exists():
            return
        
        # 加载环境变量
        from dotenv import load_dotenv
        load_dotenv()
        
        # 检查必需的环境变量
        required_vars = {
            'DB_HOST': '数据库主机',
            'DB_PORT': '数据库端口',
            'DB_USER': '数据库用户',
            'DB_PASSWORD': '数据库密码',
            'DB_NAME': '数据库名称',
            'JWT_SECRET_KEY': 'JWT 密钥',
        }
        
        for var, desc in required_vars.items():
            value = os.getenv(var)
            self.check(
                f"{desc} ({var})",
                value is not None and value != '',
                error_msg="未配置或为空"
            )
            
            # 检查 JWT_SECRET_KEY 长度
            if var == 'JWT_SECRET_KEY' and value:
                self.check(
                    "JWT_SECRET_KEY 长度",
                    len(value) >= 32,
                    warning_msg=f"当前长度 {len(value)}，建议至少 32 字符"
                )
    
    async def check_database_connection(self):
        """检查数据库连接"""
        print("\n" + "=" * 60)
        print("4. 检查数据库连接")
        print("=" * 60)
        
        try:
            from tortoise import Tortoise
            from app.core.settings import TORTOISE_ORM
            
            # 尝试连接数据库
            await Tortoise.init(config=TORTOISE_ORM)
            self.check("数据库连接", True)
            
            # 检查表是否存在
            conn = Tortoise.get_connection("default")
            
            # 检查关键表
            tables = ['user', 'role', 'frontendroute']
            for table in tables:
                result = await conn.execute_query(
                    f"SHOW TABLES LIKE '{table}'"
                )
                self.check(
                    f"表 {table} 存在",
                    len(result[1]) > 0,
                    warning_msg="表不存在，请运行: aerich init-db"
                )
            
            await Tortoise.close_connections()
            
        except Exception as e:
            self.check(
                "数据库连接",
                False,
                error_msg=f"连接失败: {str(e)}"
            )
    
    async def check_redis_connection(self):
        """检查 Redis 连接"""
        print("\n" + "=" * 60)
        print("5. 检查 Redis 连接")
        print("=" * 60)
        
        redis_enabled = os.getenv("REDIS_ENABLED", "1") == "1"
        
        if not redis_enabled:
            print("  - Redis 已禁用，跳过检查")
            return
        
        try:
            import redis
            
            redis_host = os.getenv("REDIS_HOST", "127.0.0.1")
            redis_port = int(os.getenv("REDIS_PORT", "6379"))
            redis_password = os.getenv("REDIS_PASSWORD", "")
            redis_db = int(os.getenv("REDIS_DB", "0"))
            
            # 尝试连接 Redis
            r = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password if redis_password else None,
                db=redis_db,
                socket_connect_timeout=5
            )
            
            # 测试连接
            r.ping()
            self.check("Redis 连接", True)
            
            # 检查 Redis 版本
            info = r.info()
            redis_version = info.get('redis_version', 'unknown')
            print(f"  ℹ Redis 版本: {redis_version}")
            
        except Exception as e:
            self.check(
                "Redis 连接",
                False,
                warning_msg=f"连接失败: {str(e)}（如不需要 Redis，可在 .env 中设置 REDIS_ENABLED=0）"
            )
    
    def check_directories(self):
        """检查目录结构"""
        print("\n" + "=" * 60)
        print("6. 检查目录结构")
        print("=" * 60)
        
        required_dirs = [
            'app',
            'app/apis',
            'app/models',
            'app/crud',
            'app/utils',
            'logs',
        ]
        
        for dir_path in required_dirs:
            path = Path(dir_path)
            self.check(
                f"目录 {dir_path}",
                path.exists() and path.is_dir(),
                error_msg="目录不存在"
            )
        
        # 检查日志目录权限
        logs_dir = Path('logs')
        if logs_dir.exists():
            self.check(
                "日志目录可写",
                os.access(logs_dir, os.W_OK),
                error_msg="日志目录不可写，请检查权限"
            )
    
    def check_files(self):
        """检查必需文件"""
        print("\n" + "=" * 60)
        print("7. 检查必需文件")
        print("=" * 60)
        
        required_files = [
            'requirements.txt',
            'start.py',
            'deploy_init.py',
            'app/main.py',
            'app/core/settings.py',
            'app/core/database.py',
        ]
        
        for file_path in required_files:
            path = Path(file_path)
            self.check(
                f"文件 {file_path}",
                path.exists() and path.is_file(),
                error_msg="文件不存在"
            )
    
    async def check_initial_data(self):
        """检查初始数据"""
        print("\n" + "=" * 60)
        print("8. 检查初始数据")
        print("=" * 60)
        
        try:
            from tortoise import Tortoise
            from app.core.settings import TORTOISE_ORM
            from app.models.user import User, Role, FrontendRoute
            
            await Tortoise.init(config=TORTOISE_ORM)
            
            # 检查角色
            roles_count = await Role.all().count()
            self.check(
                f"角色数据 ({roles_count} 个)",
                roles_count >= 4,
                warning_msg="角色数据不完整，请运行: python deploy_init.py"
            )
            
            # 检查路由
            routes_count = await FrontendRoute.all().count()
            self.check(
                f"路由数据 ({routes_count} 个)",
                routes_count > 0,
                warning_msg="路由数据不存在，请运行: python deploy_init.py"
            )
            
            # 检查管理员用户
            admin = await User.filter(email='zhiyu').first()
            self.check(
                "管理员用户",
                admin is not None,
                warning_msg="管理员用户不存在，请运行: python deploy_init.py"
            )
            
            await Tortoise.close_connections()
            
        except Exception as e:
            print(f"  ⚠ 无法检查初始数据: {str(e)}")
            print(f"  提示: 请确保已运行 aerich init-db 和 python deploy_init.py")
    
    def print_summary(self):
        """打印检查摘要"""
        print("\n" + "=" * 60)
        print("检查摘要")
        print("=" * 60)
        
        print(f"\n总检查项: {self.total_checks}")
        print(f"通过: {self.success_count}")
        print(f"警告: {len(self.warnings)}")
        print(f"错误: {len(self.errors)}")
        
        if self.warnings:
            print("\n⚠️  警告:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if self.errors:
            print("\n❌ 错误:")
            for error in self.errors:
                print(f"  - {error}")
            print("\n请修复以上错误后重新检查")
            return False
        else:
            print("\n✅ 所有检查通过！")
            print("\n下一步:")
            print("  1. 启动服务: python start.py")
            print("  2. 访问 API 文档: http://localhost:6080/docs")
            print("  3. 使用管理员账号登录: zhiyu / 2201101122@qq.com")
            return True
    
    async def run(self):
        """运行所有检查"""
        print("=" * 60)
        print("QYD 后端部署检查")
        print("=" * 60)
        
        # 同步检查
        self.check_python_version()
        self.check_dependencies()
        self.check_env_file()
        self.check_directories()
        self.check_files()
        
        # 异步检查
        await self.check_database_connection()
        await self.check_redis_connection()
        await self.check_initial_data()
        
        # 打印摘要
        success = self.print_summary()
        
        return success


async def main():
    """主函数"""
    checker = DeploymentChecker()
    success = await checker.run()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())
