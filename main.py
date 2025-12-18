import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from geoalchemy2.elements import WKTElement
import json
import uuid
import hashlib

# 导入数据库模型
from database_setup import engine, Robot, Task, Target, SystemLog, User

# --- 初始化 ---
app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 数据库会话
DBSession = sessionmaker(bind=engine)

def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic 模型 ---
class TaskCreate(BaseModel):
    priority: int
    type: str = "PICKING"
    target_area: str
    assigned_robot_id: Optional[str] = None

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[int] = None
    assigned_robot_id: Optional[str] = None

class RobotCreate(BaseModel):
    id: str
    ip_address: str
    battery_level: float = 100.0
    current_load: float = 0.0
    status: str = "OFFLINE"

class RobotUpdate(BaseModel):
    battery_level: Optional[float] = None
    current_load: Optional[float] = None
    status: Optional[str] = None

class TargetCreate(BaseModel):
    x: float
    y: float
    z: float = 1.5
    ripeness: float = 0.5
    area_code: str
    image_url: Optional[str] = None

# --- API 接口 ---

@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_robots = db.query(Robot).count()
    online_robots = db.query(Robot).filter(Robot.status == "ONLINE").count()
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).filter(Task.status == "COMPLETED").count()
    task_rate = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    avg_battery = db.query(func.avg(Robot.battery_level)).scalar()
    avg_battery = int(avg_battery) if avg_battery else 0
    return {
        "online_count": online_robots, "total_robots": total_robots,
        "task_rate": task_rate, "battery_avg": avg_battery
    }

@app.get("/api/tasks")
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    result = []
    for t in tasks:
        target_area = t.target.area_code if t.target else "Unknown"
        result.append({
            "id": t.id[-6:], "full_id": t.id,
            "target": f"{target_area}",
            "priority": "High" if t.priority == 2 else ("Medium" if t.priority == 1 else "Low"),
            "priority_val": t.priority,
            "assigned_to": t.assigned_robot_id if t.assigned_robot_id else "--",
            "status": t.status
        })
    return result

@app.get("/api/robots")
def get_robots(db: Session = Depends(get_db)):
    robots = db.query(Robot).all()
    result = []
    for r in robots:
        result.append({
            "id": r.id, "ip_address": str(r.ip_address),
            "battery_level": r.battery_level, "current_load": r.current_load,
            "status": r.status
        })
    return result

@app.get("/api/map/objects")
def get_map_objects(db: Session = Depends(get_db)):
    robots = db.query(Robot).all()
    robot_list = []
    for r in robots:
        h = int(hashlib.sha256(r.id.encode('utf-8')).hexdigest(), 16)
        robot_list.append({
            "id": r.id, "type": "UGV", "status": r.status,
            "x": h % 80 + 10, "y": (h // 100) % 60 + 20
        })
    
    targets = db.query(Target, func.ST_X(Target.coordinate), func.ST_Y(Target.coordinate)).all()
    target_list = []
    for t, x, y in targets:
        target_list.append({"id": t.id, "type": "Target", "x": x, "y": y})
    
    return {"robots": robot_list, "targets": target_list}

@app.post("/api/tasks")
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    try:
        target = Target(
            coordinate=WKTElement(f'POINT Z(10.5 20.0 1.5)', srid=4326),
            ripeness=0.8, area_code=task_data.target_area, image_url=""
        )
        db.add(target)
        db.flush()
        
        admin = db.query(User).filter(User.username=="admin").first()
        creator_id = admin.id if admin else None

        new_task = Task(
            id=str(uuid.uuid4()), priority=task_data.priority, status="PENDING",
            type=task_data.type, created_by=creator_id,
            assigned_robot_id=task_data.assigned_robot_id, target_id=target.id
        )
        db.add(new_task)
        db.commit()
        return {"success": True, "message": "Task created"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/tasks/{task_id}")
def update_task(task_id: str, task_data: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task: raise HTTPException(status_code=404, detail="Not found")
    if task_data.status: task.status = task_data.status
    if task_data.priority is not None: task.priority = task_data.priority
    if task_data.assigned_robot_id: task.assigned_robot_id = task_data.assigned_robot_id
    db.commit()
    return {"success": True}

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        if task.target: db.delete(task.target)
        db.delete(task)
        db.commit()
    return {"success": True}

@app.post("/api/robots")
def create_robot(robot_data: RobotCreate, db: Session = Depends(get_db)):
    if db.query(Robot).filter(Robot.id == robot_data.id).first():
        raise HTTPException(status_code=400, detail="Robot ID exists")
    new_robot = Robot(
        id=robot_data.id, ip_address=robot_data.ip_address,
        battery_level=robot_data.battery_level, current_load=robot_data.current_load,
        status=robot_data.status, last_heartbeat=datetime.now()
    )
    db.add(new_robot)
    db.commit()
    return {"success": True}

@app.delete("/api/robots/{robot_id}")
def delete_robot(robot_id: str, db: Session = Depends(get_db)):
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    if robot:
        db.query(Task).filter(Task.assigned_robot_id == robot_id).update({Task.assigned_robot_id: None})
        db.delete(robot)
        db.commit()
    return {"success": True}

# --- 核心：托管前端页面 ---
@app.get("/")
def read_root():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "01.html")
    
    if not os.path.exists(file_path):
        return HTMLResponse(content=f"<h1>错误：找不到文件</h1><p>程序试图加载：{file_path}</p><p>请确认 01.html 是否在同一目录下。</p>")
    
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    print("🚀 正在启动服务...")
    print("👉 请访问: http://localhost:8000")
    # 直接传入 app 对象，而不是字符串，避免循环导入
    uvicorn.run(app, host="0.0.0.0", port=8000)