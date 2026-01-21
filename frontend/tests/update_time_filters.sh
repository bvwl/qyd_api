#!/bin/bash

# 批量为所有前端页面添加创建时间和更新时间查询条件的脚本
# 使用方法: chmod +x update_time_filters.sh && ./update_time_filters.sh

echo "开始批量更新前端页面，添加时间查询条件..."

# 需要更新的文件列表
files=(
  "src/views/User/UserList.tsx"
  "src/views/User/RoleList.tsx"
  "src/views/User/RouteList.tsx"
  "src/views/User/TokenList.tsx"
  "src/views/Project/ProjectAccount.tsx"
  "src/views/Project/ProjectBalance.tsx"
  "src/views/Project/ProjectWallet.tsx"
  "src/views/Server/ServerList.tsx"
  "src/views/Server/ServerAccount.tsx"
  "src/views/Server/CountryList.tsx"
  "src/views/Server/GroupList.tsx"
  "src/views/Mail/MailList.tsx"
)

echo "需要手动更新以下文件："
for file in "${files[@]}"; do
  echo "  - $file"
done

echo ""
echo "更新步骤："
echo "1. 在 import 中添加: import { DatePicker } from 'antd' 和 import dayjs, { Dayjs } from 'dayjs'"
echo "2. 添加 const { RangePicker } = DatePicker"
echo "3. 添加状态: const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)"
echo "4. 添加状态: const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)"
echo "5. 在搜索区域添加两个 RangePicker 组件"
echo "6. 在 fetchData 中添加时间参数"
echo "7. 在 handleReset 中重置时间范围"
echo ""
echo "参考 ProjectList.tsx 的实现"
