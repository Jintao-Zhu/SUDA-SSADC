#!/bin/bash

echo "=========================================="
echo "CitrusLink 后端系统初始化脚本"
echo "=========================================="

# 1. 检查 Python 版本
echo ""
echo "1️⃣  检查 Python 版本..."
python3 --version

# 2. 安装依赖
echo ""
echo "2️⃣  安装 Python 依赖..."
pip3 install -r requirements.txt

# 3. 检查 PostgreSQL 是否运行
echo ""
echo "3️⃣  检查 PostgreSQL 数据库..."
if ! sudo systemctl is-active --quiet postgresql; then
    echo "⚠️  PostgreSQL 未运行，正在启动..."
    sudo systemctl start postgresql
fi

# 4. 创建数据库和用户（如果不存在）
echo ""
echo "4️⃣  配置数据库..."
sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname='citrus_link'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE citrus_link;"

sudo -u postgres psql -c "SELECT 1 FROM pg_user WHERE usename='admin'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER admin WITH PASSWORD 'citrus_pass';"

sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE citrus_link TO admin;"

# 5. 启用 PostGIS 扩展
echo ""
echo "5️⃣  启用 PostGIS 扩展..."
sudo -u postgres psql -d citrus_link -c "CREATE EXTENSION IF NOT EXISTS postgis;"

# 6. 初始化数据库表结构
echo ""
echo "6️⃣  初始化数据库表结构..."
python3 database_setup.py

# 7. 填充测试数据
echo ""
echo "7️⃣  填充测试数据..."
python3 populate_data.py

# 8. 验证数据
echo ""
echo "8️⃣  验证数据..."
python3 view_data.py

echo ""
echo "=========================================="
echo "✅ 初始化完成！"
echo "=========================================="
echo ""
echo "现在可以运行以下命令启动服务器："
echo "  python3 main.py"
echo ""
echo "然后在浏览器中访问："
echo "  http://localhost:8000"
echo ""
