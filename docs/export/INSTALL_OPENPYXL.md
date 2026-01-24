# 安装 openpyxl 依赖

## 快速安装

```bash
cd backend
pip install openpyxl
```

## 验证安装

```bash
python -c "import openpyxl; print('openpyxl version:', openpyxl.__version__)"
```

## 如果安装失败

### 方法1：使用国内镜像源

```bash
pip install openpyxl -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 方法2：升级 pip 后重试

```bash
pip install --upgrade pip
pip install openpyxl
```

### 方法3：使用 conda（如果你使用 conda 环境）

```bash
conda install openpyxl
```

## 安装完成后

重启后端服务：

```bash
cd backend
python start.py
```

## 测试导出功能

1. 使用 ADMIN 或 GM 账号登录前端
2. 访问：http://localhost:3000/project/account
3. 点击"导出所有项目统计"按钮
4. 检查是否成功下载 Excel 文件

## 常见问题

### Q: 提示 "No module named 'openpyxl'"
A: 确保在正确的 Python 环境中安装了 openpyxl

```bash
# 查看当前 Python 路径
which python

# 查看已安装的包
pip list | grep openpyxl
```

### Q: 导出时报错 "导出失败"
A: 检查后端日志，可能是权限问题或数据库连接问题

```bash
# 查看后端日志
tail -f backend/logs/api.log
```

### Q: Excel 文件打不开
A: 确保使用的是 Microsoft Excel 2007 或更高版本，或者使用 WPS、LibreOffice 等支持 .xlsx 格式的软件
