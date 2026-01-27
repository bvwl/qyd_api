#!/bin/bash
# Docker 容器代理测试脚本

echo "=== Docker 容器代理测试 ==="
echo ""

# 1. 检查宿主机代理是否运行
echo "1. 检查宿主机代理状态..."
if curl -x http://127.0.0.1:7890 -s --connect-timeout 3 https://iprust.io/ip.json > /dev/null 2>&1; then
    echo "✅ 宿主机代理正常运行"
else
    echo "❌ 宿主机代理未运行或无法访问"
    echo "   请确保代理监听在 0.0.0.0:7890 而不是 127.0.0.1:7890"
    exit 1
fi

# 2. 检查代理是否允许局域网访问
echo ""
echo "2. 检查代理配置..."
DOCKER_GATEWAY=$(docker network inspect bridge | grep -oP '(?<="Gateway": ")[^"]*' | head -1)
echo "   Docker 网关 IP: $DOCKER_GATEWAY"

# 3. 测试容器内代理
echo ""
echo "3. 在容器中测试代理..."
docker run --rm \
    -e HTTP_PROXY=http://172.17.0.1:7890 \
    -e HTTPS_PROXY=http://172.17.0.1:7890 \
    alpine/curl:latest \
    curl -s --connect-timeout 5 https://iprust.io/ip.json

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 容器代理测试成功！"
else
    echo ""
    echo "❌ 容器代理测试失败"
    echo ""
    echo "可能的原因："
    echo "1. 代理软件未监听 0.0.0.0，只监听了 127.0.0.1"
    echo "2. 防火墙阻止了 Docker 容器访问宿主机"
    echo "3. 代理端口不是 7890"
    echo ""
    echo "解决方案："
    echo "1. 修改代理软件配置，允许局域网连接"
    echo "2. 检查防火墙规则：iptables -L -n | grep 7890"
    echo "3. 或使用 host 网络模式（见下方说明）"
fi

echo ""
echo "=== 测试完成 ==="
