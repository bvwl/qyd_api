#!/usr/bin/env python3
"""
检查API文件中的异常处理顺序
查找 except Exception 在 except HTTPException 之前的情况
"""

import os
import re

# 需要检查的文件列表
files_to_check = [
    'app/apis/v1/mail/outlook.py',
    'app/apis/v1/mail/info.py',
    'app/apis/v1/server/country.py',
    'app/apis/v1/server/group.py',
    'app/apis/v1/server/info.py',
    'app/apis/v1/server/account.py',
    'app/apis/v1/user/auth.py',
    'app/apis/v1/user/user.py',
    'app/apis/v1/user/user_role.py',
    'app/apis/v1/user/token.py',
    'app/apis/v1/user/log.py',
    'app/apis/v1/user/route.py',
    'app/apis/v1/user/role.py',
    'app/apis/v1/project/info.py',
    'app/apis/v1/project/balance.py',
    'app/apis/v1/project/account.py',
    'app/apis/v1/project/wallet.py',
]

def check_file(filepath):
    """检查单个文件的异常处理顺序"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # 查找模式：except ValueError ... except Exception ... except HTTPException
    # 这种顺序是错误的，因为Exception会捕获HTTPException
    pattern = r'except ValueError.*?except Exception.*?except HTTPException'
    if re.search(pattern, content, re.DOTALL):
        issues.append("❌ ValueError -> Exception -> HTTPException (错误顺序)")
    
    # 查找模式：except Exception ... except HTTPException
    pattern2 = r'except Exception.*?except HTTPException'
    if re.search(pattern2, content, re.DOTALL):
        issues.append("❌ Exception -> HTTPException (错误顺序)")
    
    # 查找正确的模式：except HTTPException ... except Exception
    pattern3 = r'except HTTPException.*?except Exception'
    correct_count = len(re.findall(pattern3, content, re.DOTALL))
    
    # 查找所有except Exception的数量
    exception_count = len(re.findall(r'except Exception', content))
    
    return issues, correct_count, exception_count

def main():
    """主函数"""
    print("检查API文件的异常处理顺序...\n")
    print("=" * 80)
    
    total_issues = 0
    files_with_issues = []
    
    for filepath in files_to_check:
        if not os.path.exists(filepath):
            print(f"⚠️  文件不存在: {filepath}")
            continue
        
        issues, correct_count, exception_count = check_file(filepath)
        
        if issues:
            print(f"\n📁 {filepath}")
            for issue in issues:
                print(f"   {issue}")
            total_issues += len(issues)
            files_with_issues.append(filepath)
        elif exception_count > 0:
            print(f"✅ {filepath} - {correct_count}/{exception_count} 处理正确")
    
    print("\n" + "=" * 80)
    if total_issues > 0:
        print(f"\n⚠️  发现 {total_issues} 个问题，涉及 {len(files_with_issues)} 个文件")
        print("\n需要修复的文件：")
        for f in files_with_issues:
            print(f"  - {f}")
    else:
        print("\n✅ 所有文件的异常处理顺序都正确！")

if __name__ == '__main__':
    main()
