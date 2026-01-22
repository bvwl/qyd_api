#!/bin/bash
# MySQL主从状态检查脚本

echo "=========================================="
echo "  MySQL主从状态检查"
echo "=========================================="
echo ""

echo "=== 容器状态 ==="
docker ps | grep mysql
echo ""

echo "=== 主库状态 ==="
docker exec mysql-master mysql -uroot -pzhiyu666 -e "SHOW MASTER STATUS\G" 2>/dev/null
echo ""

echo "=== 从库1状态 ==="
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" 2>/dev/null | grep -E "(Replica_IO_Running|Replica_SQL_Running|Seconds_Behind_Source|Last_IO_Error|Last_SQL_Error)"
echo ""

echo "=== 从库2状态 ==="
docker exec mysql-slave-2 mysql -uroot -pzhiyu666 -e "SHOW REPLICA STATUS\G" 2>/dev/null | grep -E "(Replica_IO_Running|Replica_SQL_Running|Seconds_Behind_Source|Last_IO_Error|Last_SQL_Error)"
echo ""
