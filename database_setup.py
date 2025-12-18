import uuid
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, ForeignKey, text, BigInteger, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import INET  # 对应文档中的 INET 类型
from sqlalchemy.sql import func  # 用于生成数据库级的 DEFAULT NOW
from geoalchemy2 import Geometry

# --- 1. 数据库连接配置 ---
DATABASE_URL = "postgresql://admin:citrus_pass@localhost:5432/citrus_link"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# --- 2. 定义实体类 (严格对应 4.3 物理模型表格) ---

# ==========================================
# 4.3.4 系统用户表 (t_sys_user)
# ==========================================
class User(Base):
    __tablename__ = 't_sys_user'
    
    # id: VARCHAR(36), PK
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # username: VARCHAR(50), UNIQUE
    username = Column(String(50), unique=True)
    
    # password_hash: VARCHAR(255), NOT NULL
    password_hash = Column(String(255), nullable=False)
    
    # role: VARCHAR(20)
    role = Column(String(20))
    
    # (ORM关系映射)
    tasks = relationship("Task", back_populates="creator")

# ==========================================
# 4.3.2 智能终端表 (t_sys_robot)
# ==========================================
class Robot(Base):
    __tablename__ = 't_sys_robot'
    
    # id: VARCHAR(36), PK
    id = Column(String(36), primary_key=True)
    
    # ip_address: INET, UNIQUE
    ip_address = Column(INET, unique=True)
    
    # battery_level: FLOAT, CHECK(0-100)
    battery_level = Column(Float, CheckConstraint('battery_level >= 0 AND battery_level <= 100'))
    
    # current_load: FLOAT
    current_load = Column(Float)
    
    # status: VARCHAR(10)
    status = Column(String(10))
    
    # last_heartbeat: TIMESTAMP
    last_heartbeat = Column(DateTime)
    
    # (ORM关系映射)
    tasks = relationship("Task", back_populates="robot")
    logs = relationship("SystemLog", back_populates="robot")

# ==========================================
# 4.3.3 作业目标表 (t_biz_target)
# ==========================================
class Target(Base):
    __tablename__ = 't_biz_target'
    
    # id: BIGINT, PK (自增)
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # coordinate: GEOMETRY(POINTZ), NOT NULL
    coordinate = Column(Geometry(geometry_type='POINTZ', srid=4326), nullable=False)
    
    # ripeness: FLOAT, CHECK(0-1)
    ripeness = Column(Float, CheckConstraint('ripeness >= 0 AND ripeness <= 1.0'))
    
    # image_url: TEXT
    image_url = Column(Text)
    
    # area_code: VARCHAR(10)
    area_code = Column(String(10))
    
    # (ORM关系映射)
    task = relationship("Task", back_populates="target", uselist=False)

# ==========================================
# 4.3.1 作业任务表 (t_biz_task)
# ==========================================
class Task(Base):
    __tablename__ = 't_biz_task'
    
    # id: VARCHAR(36), PK
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # priority: INT, NOT NULL
    priority = Column(Integer, nullable=False)
    
    # status: VARCHAR(20), NOT NULL
    status = Column(String(20), nullable=False)
    
    # type: VARCHAR(20)
    type = Column(String(20))
    
    # created_at: TIMESTAMP, DEFAULT NOW (使用 server_default 对应数据库级默认值)
    created_at = Column(DateTime, server_default=func.now())
    
    # created_by: VARCHAR(36), FK
    created_by = Column(String(36), ForeignKey('t_sys_user.id'))
    
    # assigned_robot_id: VARCHAR(36), FK
    assigned_robot_id = Column(String(36), ForeignKey('t_sys_robot.id'))
    
    # target_id: BIGINT, FK, UNIQUE (注意这里必须是 BigInteger 以匹配 Target.id)
    target_id = Column(BigInteger, ForeignKey('t_biz_target.id'), unique=True)
    
    # (ORM关系映射)
    creator = relationship("User", back_populates="tasks")
    robot = relationship("Robot", back_populates="tasks")
    target = relationship("Target", back_populates="task")

# ==========================================
# 4.3.5 运行日志表 (t_sys_log)
# ==========================================
class SystemLog(Base):
    __tablename__ = 't_sys_log'
    
    # id: BIGINT, PK
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # robot_id: VARCHAR(36), FK
    robot_id = Column(String(36), ForeignKey('t_sys_robot.id'))
    
    # content: TEXT
    content = Column(Text)
    
    # level: VARCHAR(10)
    level = Column(String(10))
    
    # created_at: TIMESTAMP, DEFAULT NOW
    created_at = Column(DateTime, server_default=func.now())
    
    # (ORM关系映射)
    robot = relationship("Robot", back_populates="logs")


# --- 3. 执行建表 (带清理旧表功能) ---
def init_db():
    print("正在连接数据库...")
    try:
        # ⚠️ 警告：因为表结构变动严格，必须先删除旧表
        print("🗑️  清理旧表结构 (Drop All)...")
        Base.metadata.drop_all(engine)
        
        print("🔨 正在创建新表 (Strict Schema)...")
        Base.metadata.create_all(engine)
        
        print("✅ 建表成功！已严格匹配文档设计：")
        print("   - [Check] 电量(0-100) 与 成熟度(0-1) 约束")
        print("   - [Type]  IP地址使用 INET, ID使用 BigInteger")
        print("   - [Null]  优先级与状态字段已设为 NOT NULL")
        print("   - [Default] 时间字段已设为 DEFAULT NOW")
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    init_db()