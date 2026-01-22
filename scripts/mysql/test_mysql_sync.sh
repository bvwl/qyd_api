#!/bin/bash
# MySQL数据同步测试脚本

echo "=========================================="
echo "  测试MySQL主从数据同步"
echo "=========================================="
echo ""

# 生成测试数据库名（带时间戳）
TEST_DB="test_sync_$(date +%Y%m%d_%H%M%S)"

echo "1. 在主库创建测试数据..."
docker exec mysql-master mysql -uroot -pzhiyu666 << EOF
CREATE DATABASE ${TEST_DB};
USE ${TEST_DB};
CREATE TABLE test_table (
    id INT PRIMARY KEY AUTO_INCREMENT,
    data VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO test_table (data) VALUES ('test1'), ('test2'), ('test3');
SELECT '主库数据：' as info;
SELECT * FROM test_table;
EOF

echo ""
echo "2. 等待3秒让数据同步..."
sleep 3

echo ""
echo "3. 在从库1查询数据..."
docker exec mysql-slave-1 mysql -uroot -pzhiyu666 -e "SELECT '从库1数据：' as info; SELECT * FROM ${TEST_DB}.test_table;" 2>/dev/null

echo ""
echo "4. 在从库2查询数据..."
docker exec mysql-slave-2 mysql -uroot -pzhiyu666 -e "SELECT '从库2数据：' as info; SELECT * FROM ${TEST_DB}.test_table;" 2>/dev/null

echo ""
echo "=========================================="
echo "测试完成！"
echo ""
echo "如果从库能查询到3条数据，说明同步正常。"
echo "测试数据库：${TEST_DB}"
echo ""
echo "清理测试数据："
echo "  docker exec mysql-master mysql -uroot -pzhiyu666 -e \"DROP DATABASE ${TEST_DB};\""
echo "=========================================="
