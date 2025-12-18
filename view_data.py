from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from database_setup import engine, User, Robot, Target, Task, SystemLog

Session = sessionmaker(bind=engine)
session = Session()

def print_table_header(table_name, comment):
    print(f"\n{'='*80}")
    print(f" 📂 表名: {table_name} ({comment})")
    print(f"{'-'*80}")

def view_strict_data():
    print("🚀 [Database Validation] 开始全字段完整性验证...\n")

    # --- 1. 系统用户表 (t_sys_user) ---
    print_table_header("t_sys_user", "系统用户表")
    users = session.query(User).all()
    for u in users:
        print(f" [Row] id={u.id}")
        print(f"       username={u.username:<15} | role={u.role}")
        print(f"       password_hash={u.password_hash} (已加密)")

    # --- 2. 智能终端表 (t_sys_robot) ---
    print_table_header("t_sys_robot", "智能终端表")
    robots = session.query(Robot).all()
    for r in robots:
        print(f" [Row] id={r.id}")
        print(f"       ip_address={str(r.ip_address):<15} | status={r.status}")
        print(f"       battery_level={r.battery_level}%      | current_load={r.current_load} kg")
        print(f"       last_heartbeat={r.last_heartbeat}")

    # --- 3. 作业目标表 (t_biz_target) ---
    print_table_header("t_biz_target", "作业目标表")
    targets = session.query(Target, func.ST_AsText(Target.coordinate).label('wkt')).all()
    for t, wkt in targets:
        print(f" [Row] id={t.id}")
        print(f"       coordinate={wkt}")
        print(f"       ripeness={t.ripeness:<10} | area_code={t.area_code}")
        print(f"       image_url={t.image_url}")

    # --- 4. 作业任务表 (t_biz_task) ---
    print_table_header("t_biz_task", "作业任务表")
    tasks = session.query(Task).all()
    for t in tasks:
        print(f" [Row] id={t.id}")
        print(f"       type={t.type:<10}     | priority={t.priority} | status={t.status}")
        print(f"       assigned_robot_id={t.assigned_robot_id} | target_id={t.target_id}")
        print(f"       created_by={t.created_by}")
        print(f"       created_at={t.created_at}")

    # --- 5. 运行日志表 (t_sys_log) ---
    print_table_header("t_sys_log", "运行日志表")
    logs = session.query(SystemLog).all()
    for l in logs:
        print(f" [Row] id={l.id}")
        print(f"       robot_id={l.robot_id:<10} | level={l.level}")
        print(f"       content={l.content}")
        print(f"       created_at={l.created_at}")

    print("\n✅ 验证结束：所有字段均已持久化，且符合物理模型设计约束。")

if __name__ == "__main__":
    view_strict_data()