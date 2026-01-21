#!/bin/bash
# 批量修复所有API文件的异常处理
# 在 except ValueError 后面添加 except HTTPException (如果不存在)

files=(
    "app/apis/v1/mail/info.py"
    "app/apis/v1/server/country.py"
    "app/apis/v1/server/group.py"
    "app/apis/v1/server/info.py"
    "app/apis/v1/server/account.py"
    "app/apis/v1/user/auth.py"
    "app/apis/v1/user/token.py"
    "app/apis/v1/user/log.py"
    "app/apis/v1/user/role.py"
    "app/apis/v1/project/info.py"
    "app/apis/v1/project/balance.py"
    "app/apis/v1/project/account.py"
    "app/apis/v1/project/wallet.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        # 使用 awk 在 except ValueError 后添加 except HTTPException
        awk '
        /except ValueError as e:/ {
            print
            getline
            print
            # 检查下一行是否已经是 except HTTPException
            getline
            if ($0 !~ /except HTTPException:/) {
                print "    except HTTPException:"
                print "        raise"
            }
            print
            next
        }
        {print}
        ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
        echo "✅ 已修复: $file"
    fi
done

echo ""
echo "修复完成！"
