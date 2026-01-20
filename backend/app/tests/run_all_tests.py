"""
运行所有测试的主入口
"""
import sys
import pytest


def main():
    """
    运行所有测试文件
    """
    test_files = [
        "test_server.py",
        "test_mail.py",
        "test_project.py",
        "test_user.py",
    ]
    
    print("=" * 60)
    print("开始运行所有接口测试")
    print("=" * 60)
    
    # 运行所有测试
    args = ["-v", "--tb=short"] + test_files
    exit_code = pytest.main(args)
    
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败，请检查上面的错误信息")
    print("=" * 60)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
