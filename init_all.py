#!/usr/bin/env python3
"""
一键初始化脚本：自动完成数据库表创建、数据填充和验证
"""

def main():
    print("="*60)
    print("CitrusLink 系统初始化")
    print("="*60)

    # 步骤 1: 初始化数据库表
    print("\n📦 步骤 1/3: 初始化数据库表结构...")
    try:
        from database_setup import init_db
        init_db()
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print("\n请检查:")
        print("1. PostgreSQL 是否运行")
        print("2. 数据库 'citrus_link' 是否存在")
        print("3. 用户 'admin' 是否有权限")
        return False

    # 步骤 2: 填充测试数据
    print("\n📝 步骤 2/3: 填充测试数据...")
    try:
        from populate_data import add_fake_data
        add_fake_data()
    except Exception as e:
        print(f"❌ 数据填充失败: {e}")
        return False

    # 步骤 3: 验证数据
    print("\n🔍 步骤 3/3: 验证数据...")
    try:
        from view_data import view_strict_data
        view_strict_data()
    except Exception as e:
        print(f"❌ 数据验证失败: {e}")
        return False

    print("\n" + "="*60)
    print("✅ 初始化完成！")
    print("="*60)
    print("\n现在可以启动服务器:")
    print("  python3 main.py")
    print("\n然后在浏览器访问:")
    print("  http://localhost:8000")
    print("="*60)

    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
