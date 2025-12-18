import sys

def test_imports():
    """测试导入依赖"""
    print("1️⃣  测试 Python 依赖导入...")
    try:
        import fastapi
        print(f"   ✅ FastAPI {fastapi.__version__}")
    except ImportError as e:
        print(f"   ❌ FastAPI 未安装: {e}")
        return False

    try:
        import sqlalchemy
        print(f"   ✅ SQLAlchemy {sqlalchemy.__version__}")
    except ImportError as e:
        print(f"   ❌ SQLAlchemy 未安装: {e}")
        return False

    try:
        import geoalchemy2
        print(f"   ✅ GeoAlchemy2 已安装")
    except ImportError as e:
        print(f"   ❌ GeoAlchemy2 未安装: {e}")
        return False

    try:
        import psycopg2
        print(f"   ✅ psycopg2 已安装")
    except ImportError as e:
        print(f"   ❌ psycopg2 未安装: {e}")
        return False

    return True

def test_database_connection():
    """测试数据库连接"""
    print("\n2️⃣  测试数据库连接...")
    try:
        # 修复点：在这里必须导入 sqlalchemy，否则下面报错 NameError
        import sqlalchemy 
        from database_setup import engine
        
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text("SELECT 1"))
            print("   ✅ 数据库连接成功")
            return True
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {e}")
        print("\n   提示：请确保:")
        print("   1. PostgreSQL 服务已启动")
        print("   2. 数据库 'citrus_link' 已创建")
        print("   3. 用户 'admin' 有访问权限")
        return False

def test_postgis():
    """测试 PostGIS 扩展"""
    print("\n3️⃣  测试 PostGIS 扩展...")
    try:
        # 修复点：这里也确保导入
        import sqlalchemy
        from database_setup import engine
        
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text("SELECT PostGIS_Version()"))
            version = result.fetchone()[0]
            print(f"   ✅ PostGIS 版本: {version}")
            return True
    except Exception as e:
        print(f"   ❌ PostGIS 未启用: {e}")
        print("\n   提示：运行以下命令启用 PostGIS:")
        print("   sudo -u postgres psql -d citrus_link -c 'CREATE EXTENSION postgis;'")
        return False

def main():
    print("="*60)
    print("CitrusLink 系统环境测试")
    print("="*60)

    results = []

    # 测试导入
    results.append(test_imports())

    if not results[0]:
        print("\n❌ 依赖未安装，请运行: pip3 install -r requirements.txt")
        sys.exit(1)

    # 测试数据库连接
    results.append(test_database_connection())

    if not results[1]:
        print("\n建议操作：")
        print("1. 启动 PostgreSQL: sudo systemctl start postgresql")
        print("2. 创建数据库: sudo -u postgres psql -c \"CREATE DATABASE citrus_link;\"")
        print("3. 创建用户: sudo -u postgres psql -c \"CREATE USER admin WITH PASSWORD 'citrus_pass';\"")
        print("4. 授权: sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE citrus_link TO admin;\"")
        sys.exit(1)

    # 测试 PostGIS
    results.append(test_postgis())

    print("\n" + "="*60)
    if all(results):
        print("✅ 所有测试通过！系统准备就绪")
        print("\n下一步:")
        print("1. 初始化数据库: python3 database_setup.py")
        print("2. 填充数据: python3 populate_data.py")
        print("3. 启动服务: python3 main.py")
    else:
        print("⚠️  部分测试失败，请检查上述错误信息")
    print("="*60)

if __name__ == "__main__":
    main()