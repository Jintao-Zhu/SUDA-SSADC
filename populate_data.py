from sqlalchemy.orm import sessionmaker
from geoalchemy2.elements import WKTElement
from database_setup import engine, User, Robot, Target, Task, SystemLog

Session = sessionmaker(bind=engine)
session = Session()

def add_fake_data():
    print("🚀 [Strict Mode] 开始填充全量测试数据...")

    try:
        # 1. 清理旧数据
        session.query(Task).delete()
        session.query(SystemLog).delete()
        session.query(Target).delete()
        session.query(Robot).delete()
        session.query(User).delete()
        session.commit()
    except Exception:
        session.rollback()

    # 2. 创建用户 (对应 4.3.4 t_sys_user)
    admin = User(
        username="admin", 
        password_hash="sha256:xxxx", 
        role="ADMIN"
    )
    session.add(admin)
    session.flush() 

    # 3. 创建机器人 (对应 4.3.2 t_sys_robot)
    ugv01 = Robot(
        id="UGV-01",
        ip_address="192.168.1.101", 
        battery_level=85.5, 
        current_load=12.5,  # 补全字段
        status="ONLINE"
    )
    session.add(ugv01)

    # 4. 创建目标 (对应 4.3.3 t_biz_target)
    target1 = Target(
        coordinate=WKTElement('POINT Z(10.5 20.0 1.5)', srid=4326),
        ripeness=0.95, 
        area_code="Area-A",
        image_url="/static/cam01_01.jpg" # 补全字段
    )
    session.add(target1)
    session.flush()

    # 5. 创建任务 (对应 4.3.1 t_biz_task)
    task1 = Task(
        priority=2, 
        status="IN_PROGRESS",
        type="PICKING",        # 补全字段
        created_by=admin.id,   # 补全字段
        assigned_robot_id=ugv01.id,
        target_id=target1.id
    )
    session.add(task1)

    # 6. 创建日志 (对应 4.3.5 t_sys_log) —— 新增！
    log1 = SystemLog(
        robot_id=ugv01.id,
        level="INFO",
        content="System initialized successfully."
    )
    session.add(log1)

    # 提交
    session.commit()
    print("✅ 全量数据填充完成 (覆盖5张核心表)")
    session.close()

if __name__ == "__main__":
    add_fake_data()