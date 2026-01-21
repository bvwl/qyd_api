#!/usr/bin/env node

/**
 * 批量为前端页面添加时间查询条件
 * 使用方法: node batch_update_time_filters.js
 */

const fs = require('fs');
const path = require('path');

// 需要更新的文件列表
const files = [
  'src/views/User/RoleList.tsx',
  'src/views/User/RouteList.tsx',
  'src/views/User/TokenList.tsx',
  'src/views/Project/ProjectAccount.tsx',
  'src/views/Project/ProjectBalance.tsx',
  'src/views/Project/ProjectWallet.tsx',
  'src/views/Server/ServerList.tsx',
  'src/views/Server/ServerAccount.tsx',
  'src/views/Server/CountryList.tsx',
  'src/views/Server/GroupList.tsx',
  'src/views/Mail/MailList.tsx',
];

// 更新单个文件
function updateFile(filePath) {
  console.log(`\n处理文件: ${filePath}`);
  
  const fullPath = path.join(__dirname, filePath);
  if (!fs.existsSync(fullPath)) {
    console.log(`  ⚠️  文件不存在，跳过`);
    return;
  }
  
  let content = fs.readFileSync(fullPath, 'utf8');
  let modified = false;
  
  // 1. 添加 DatePicker 导入
  if (!content.includes('DatePicker')) {
    content = content.replace(
      /from 'antd'/,
      match => match.replace('antd', 'antd'\n').replace("'antd'\n", ", DatePicker } from 'antd'")
    );
    content = content.replace(
      /} from 'antd'/,
      ', DatePicker } from \'antd\''
    );
    modified = true;
  }
  
  // 2. 添加 dayjs 导入
  if (!content.includes('import dayjs')) {
    const importIndex = content.indexOf('import');
    const firstImportEnd = content.indexOf('\n', importIndex);
    content = content.slice(0, firstImportEnd + 1) + 
              "import dayjs, { Dayjs } from 'dayjs'\n" +
              content.slice(firstImportEnd + 1);
    modified = true;
  }
  
  // 3. 添加 RangePicker 解构
  if (!content.includes('const { RangePicker }')) {
    const componentStart = content.indexOf('const ') || content.indexOf('export default');
    content = content.slice(0, componentStart) +
              'const { RangePicker } = DatePicker\n\n' +
              content.slice(componentStart);
    modified = true;
  }
  
  // 4. 添加状态变量
  if (!content.includes('createTimeRange')) {
    // 找到最后一个 useState
    const lastUseState = content.lastIndexOf('useState');
    const lineEnd = content.indexOf('\n', lastUseState);
    content = content.slice(0, lineEnd + 1) +
              '  const [createTimeRange, setCreateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)\n' +
              '  const [updateTimeRange, setUpdateTimeRange] = useState<[Dayjs, Dayjs] | null>(null)\n' +
              content.slice(lineEnd + 1);
    modified = true;
  }
  
  if (modified) {
    fs.writeFileSync(fullPath, content, 'utf8');
    console.log(`  ✅ 已更新`);
  } else {
    console.log(`  ℹ️  无需更新`);
  }
}

// 主函数
function main() {
  console.log('开始批量更新前端页面...\n');
  console.log('=' .repeat(60));
  
  files.forEach(file => {
    try {
      updateFile(file);
    } catch (error) {
      console.log(`  ❌ 更新失败: ${error.message}`);
    }
  });
  
  console.log('\n' + '='.repeat(60));
  console.log('\n✅ 批量更新完成！');
  console.log('\n⚠️  注意: 此脚本只完成了部分更新，还需要手动：');
  console.log('  1. 在搜索区域添加 RangePicker 组件');
  console.log('  2. 在 fetchData 中添加时间参数');
  console.log('  3. 在 handleReset 中重置时间范围');
  console.log('\n请参考 TIME_FILTER_UPDATE_GUIDE.md 完成剩余步骤');
}

main();
