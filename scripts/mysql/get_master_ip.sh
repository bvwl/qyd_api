#!/bin/bash
# 获取主库容器IP脚本

echo "=========================================="
echo "  MySQL主库容器信息"
echo "=========================================="
echo ""

# 检查主库容器是否运行
if ! docker ps | grep -q mysql-master; then
    echo "错误：主库容器未运行"
    exit 1
fi

# 获取容器IP
MASTER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql-master)

if [ -z "$MASTER_IP" ]; then
    echo "错误：无法获取主库容器IP"
    exit 1
fi

echo "主库容器名称: mysql-master"
echo "主库容器IP: ${MASTER_IP}"
echo "主库容器端口: 3306"
echo "宿主机映射端口: 3307"
echo ""
echo "=========================================="
echo "从库配置复制时使用："
echo "=========================================="
echo ""
echo "CHANGE REPLICATION SOURCE TO"
echo "    SOURCE_HOST='${MASTER_IP}',"
echo "    SOURCE_PORT=3306,"
echo "    SOURCE_USER='repl',"
echo "    SOURCE_PASSWORD='repl123',"
echo "    SOURCE_AUTO_POSITION=1;"
echo ""
echo "=========================================="
echo ""
echo "测试从从库连接主库："
echo "  docker exec mysql-slave-1 mysql -h${MASTER_IP} -P3306 -urepl -prepl123 -e \"SELECT 1;\""
echo ""

# 保存到文件
echo "${MASTER_IP}" > /tmp/mysql_master_ip.txt
echo "主库IP已保存到: /tmp/mysql_master_ip.txt"
