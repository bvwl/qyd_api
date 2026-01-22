#!/bin/bash
# MySQL快速连接脚本

case "$1" in
    master|m)
        echo "连接到主库（端口3307）..."
        docker exec -it mysql-master mysql -uroot -pzhiyu666
        ;;
    slave1|s1|1)
        echo "连接到从库1（端口3308）..."
        docker exec -it mysql-slave-1 mysql -uroot -pzhiyu666
        ;;
    slave2|s2|2)
        echo "连接到从库2（端口3309）..."
        docker exec -it mysql-slave-2 mysql -uroot -pzhiyu666
        ;;
    *)
        echo "用法: $0 {master|slave1|slave2}"
        echo "简写: $0 {m|s1|s2|1|2}"
        echo ""
        echo "示例："
        echo "  $0 master   # 连接主库"
        echo "  $0 m        # 连接主库（简写）"
        echo "  $0 slave1   # 连接从库1"
        echo "  $0 s1       # 连接从库1（简写）"
        echo "  $0 1        # 连接从库1（数字简写）"
        exit 1
        ;;
esac
