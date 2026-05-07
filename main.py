"""
AviRec - FastAPI 主应用
"""
from fastapi import FastAPI, Request, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
import os
import uuid
from datetime import date
from pathlib import Path

from database import init_db, get_db, Airline, Aircraft, UserPhoto, User

# ─── 应用初始化 ─────────────────────────────────────────────

app = FastAPI(title="AviRec", description="飞机拍摄记录器")

# 静态文件
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 运行时挂载静态目录（FastAPI 挂载在根路径下需要放到最后，这里在 startup 后注册）


@app.on_event("startup")
def startup():
    init_db()
    # 确保有默认用户
    db = next(get_db())
    if not db.query(User).first():
        db.add(User(display_name="飞友"))
        db.commit()
    db.close()


# ─── 模板渲染辅助 ───────────────────────────────────────────

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_default_user(db: Session) -> User:
    """获取默认用户（MVP 阶段单用户）"""
    user = db.query(User).first()
    if not user:
        user = User(display_name="飞友")
        db.add(user)
        db.commit()
    return user


def get_spotted_ids(db: Session, user_id: int) -> set:
    """获取用户已拍摄的飞机 ID 集合"""
    rows = db.query(UserPhoto.aircraft_id).filter(UserPhoto.user_id == user_id).all()
    return {r[0] for r in rows}


# ─── 页面路由 ───────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    user = get_default_user(db)
    airlines = db.query(Airline).filter(Airline.is_active == True).order_by(Airline.name).all()
    total_aircraft = db.query(func.count(Aircraft.id)).filter(Aircraft.is_active == True).scalar()
    total_spotted = db.query(func.count(UserPhoto.id)).filter(UserPhoto.user_id == user.id).scalar()
    special_count = db.query(func.count(Aircraft.id)).filter(
        Aircraft.is_special_livery == True, Aircraft.is_active == True
    ).scalar()
    spotted_special = db.query(func.count(UserPhoto.id)).join(Aircraft).filter(
        UserPhoto.user_id == user.id,
        Aircraft.is_special_livery == True
    ).scalar()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "airlines": airlines,
        "total_aircraft": total_aircraft,
        "total_spotted": total_spotted,
        "special_count": special_count,
        "spotted_special": spotted_special,
    })


@app.get("/airlines", response_class=HTMLResponse)
async def airlines_list(request: Request, country: str = "", db: Session = Depends(get_db)):
    user = get_default_user(db)
    query = db.query(Airline).filter(Airline.is_active == True)
    if country:
        query = query.filter(Airline.country == country)
    airlines = query.order_by(Airline.name).all()
    spotted_ids = get_spotted_ids(db, user.id)

    # 每个航司的统计
    airline_stats = []
    for a in airlines:
        fleet = db.query(Aircraft).filter(Aircraft.airline_id == a.id, Aircraft.is_active == True).all()
        fleet_ids = [ac.id for ac in fleet]
        spotted = sum(1 for sid in fleet_ids if sid in spotted_ids)
        special = sum(1 for ac in fleet if ac.is_special_livery)
        airline_stats.append({
            "airline": a,
            "total": len(fleet),
            "spotted": spotted,
            "special": special,
        })

    countries = db.query(Airline.country).filter(Airline.is_active == True).distinct().order_by(Airline.country).all()

    return templates.TemplateResponse("airlines.html", {
        "request": request,
        "user": user,
        "airline_stats": airline_stats,
        "countries": [c[0] for c in countries],
        "current_country": country,
    })


# ─── 机型排序映射 ────────────────────────────────────────────
# 值越小越靠前，用于同类别内按"大→小"排列
TYPE_SORT_ORDER = {
    # Airbus (宽体 → 窄体)
    "A380": 10, "A350": 20, "A340": 25, "A330": 30,
    "A321": 40, "A320": 50, "A319": 55, "A318": 56, "A220": 60,
    # Boeing (宽体 → 窄体)
    "B747": 10, "B777": 20, "B787": 30, "B767": 35, "B757": 40, "B737": 50, "B717": 55,
    # COMAC
    "C919": 40, "ARJ21": 60,
    # Embraer
    "ERJ": 70, "E170": 70, "E175": 70, "E190": 65, "E195": 65,
    # Bombardier
    "CRJ": 70, "CRJ200": 70, "CRJ700": 70, "CRJ900": 70,
    # 俄制 / 其他宽体
    "An-124": 5, "An-225": 1, "Il-96": 15, "Il-76": 5,
    "Tu-204": 35, "Tu-154": 50, "SSJ100": 65,
    # 特殊
    "MD-11": 20, "MD-80": 55, "MD-90": 55,
    "Concorde": 1,
}

CATEGORY_ORDER = {"wide_body": 1, "narrow_body": 2, "regional": 3, "cargo": 4, "other": 5}

CATEGORY_LABELS = {
    "wide_body": "宽体机",
    "narrow_body": "窄体机",
    "regional": "支线机",
    "cargo": "货机",
    "other": "其他",
}


def get_type_family(aircraft_type: str) -> str:
    """从机型字符串中提取系列名，如 'B737-8 MAX' → 'B737'"""
    if not aircraft_type:
        return ""
    t = aircraft_type.strip()
    for sep in (" ", "-"):
        idx = t.find(sep)
        if idx > 0:
            return t[:idx]
    return t


def get_sort_key(ac: Aircraft) -> tuple:
    """生成排序键：(类别序, 值得关注序, 机型大小序, 注册号)"""
    cat_order = CATEGORY_ORDER.get(ac.category or "narrow_body", 5)
    notable_order = 0 if ac.notable else 1
    family = get_type_family(ac.aircraft_type)
    type_order = TYPE_SORT_ORDER.get(family, 100)
    reg = ac.registration or ""
    return (cat_order, notable_order, type_order, reg)


@app.get("/airlines/{airline_id}", response_class=HTMLResponse)
async def airline_detail(
    request: Request,
    airline_id: int,
    search: str = "",
    type_filter: str = "",
    category: str = "",
    notable_filter: str = "",
    status: str = "",
    db: Session = Depends(get_db),
):
    user = get_default_user(db)
    airline = db.query(Airline).filter(Airline.id == airline_id).first()
    if not airline:
        raise HTTPException(status_code=404, detail="航司不存在")

    # 构建查询
    query = db.query(Aircraft).filter(
        Aircraft.airline_id == airline_id, Aircraft.is_active == True
    )

    # 注册号搜索
    if search:
        query = query.filter(Aircraft.registration.ilike(f"%{search}%"))

    # 机型筛选
    if type_filter:
        query = query.filter(Aircraft.aircraft_type.ilike(f"%{type_filter}%"))

    # 类别筛选
    if category and category in CATEGORY_ORDER:
        query = query.filter(Aircraft.category == category)

    # 值得关注筛选
    if notable_filter == "notable":
        query = query.filter(Aircraft.notable == True)
    elif notable_filter == "special_livery":
        query = query.filter(Aircraft.is_special_livery == True)
    elif notable_filter == "normal_only":
        query = query.filter(Aircraft.notable == False, Aircraft.is_special_livery == False)

    aircraft_all = query.all()

    # 拍摄状态筛选（在 Python 中过滤，需要 spotted_ids）
    spotted_ids = get_spotted_ids(db, user.id)
    if status == "spotted":
        aircraft_all = [ac for ac in aircraft_all if ac.id in spotted_ids]
    elif status == "unspotted":
        aircraft_all = [ac for ac in aircraft_all if ac.id not in spotted_ids]

    # 排序
    aircraft_all.sort(key=get_sort_key)

    # 按类别分组
    grouped = {}  # category_label → [aircraft]
    for ac in aircraft_all:
        cat = ac.category or "narrow_body"
        label = CATEGORY_LABELS.get(cat, "其他")
        if label not in grouped:
            grouped[label] = []
        grouped[label].append(ac)

    # 用户照片映射
    ac_photos = {}
    for ac in aircraft_all:
        photo = db.query(UserPhoto).filter(
            UserPhoto.user_id == user.id, UserPhoto.aircraft_id == ac.id
        ).order_by(UserPhoto.created_at.desc()).first()
        ac_photos[ac.id] = photo

    # 该航司所有机型（供筛选下拉）
    all_types = db.query(Aircraft.aircraft_type).filter(
        Aircraft.airline_id == airline_id, Aircraft.is_active == True
    ).distinct().order_by(Aircraft.aircraft_type).all()

    # 类型系列列表（提取前缀去重）
    type_families = sorted(set(get_type_family(t[0]) for t in all_types if t[0]), key=lambda x: TYPE_SORT_ORDER.get(x, 100))

    # 统计
    total_active = len(aircraft_all)
    spotted_count = sum(1 for ac in aircraft_all if ac.id in spotted_ids)
    special_count = sum(1 for ac in aircraft_all if ac.is_special_livery)
    notable_count = sum(1 for ac in aircraft_all if ac.notable)

    return templates.TemplateResponse("airline_detail.html", {
        "request": request,
        "user": user,
        "airline": airline,
        "grouped": grouped,
        "spotted_ids": spotted_ids,
        "ac_photos": ac_photos,
        "total": total_active,
        "spotted": spotted_count,
        "special_total": special_count,
        "notable_total": notable_count,
        # 筛选参数回传
        "search": search,
        "type_filter": type_filter,
        "category": category,
        "notable_filter": notable_filter,
        "status": status,
        # 筛选选项
        "type_families": type_families,
        "all_types": [t[0] for t in all_types],
        "category_options": [("", "全部类别")] + [(k, v) for k, v in CATEGORY_LABELS.items()],
    })


@app.get("/aircraft/{aircraft_id}", response_class=HTMLResponse)
async def aircraft_detail(request: Request, aircraft_id: int, db: Session = Depends(get_db)):
    user = get_default_user(db)
    aircraft = db.query(Aircraft).filter(Aircraft.id == aircraft_id).first()
    if not aircraft:
        raise HTTPException(status_code=404, detail="飞机不存在")

    photos = db.query(UserPhoto).filter(
        UserPhoto.user_id == user.id, UserPhoto.aircraft_id == aircraft_id
    ).order_by(UserPhoto.created_at.desc()).all()

    return templates.TemplateResponse("aircraft_detail.html", {
        "request": request,
        "user": user,
        "aircraft": aircraft,
        "photos": photos,
        "is_spotted": len(photos) > 0,
    })


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str = "", db: Session = Depends(get_db)):
    user = get_default_user(db)
    results = []
    if q:
        results = db.query(Aircraft).filter(
            Aircraft.is_active == True,
            Aircraft.registration.ilike(f"%{q}%")
        ).order_by(Aircraft.registration).all()
        if not results:
            results = db.query(Aircraft).filter(
                Aircraft.is_active == True,
                Aircraft.aircraft_type.ilike(f"%{q}%")
            ).order_by(Aircraft.registration).all()

    spotted_ids = get_spotted_ids(db, user.id)
    return templates.TemplateResponse("search.html", {
        "request": request,
        "user": user,
        "query": q,
        "results": results,
        "spotted_ids": spotted_ids,
    })


# ─── API 路由 ────────────────────────────────────────────────

@app.post("/api/toggle-spotted/{aircraft_id}")
async def toggle_spotted(aircraft_id: int, db: Session = Depends(get_db)):
    """切换拍摄状态：有记录则删除，无记录则创建"""
    user = get_default_user(db)
    existing = db.query(UserPhoto).filter(
        UserPhoto.user_id == user.id, UserPhoto.aircraft_id == aircraft_id
    ).first()

    if existing:
        # 删除文件
        if existing.image_url:
            img_path = BASE_DIR / existing.image_url.lstrip("/")
            try:
                img_path.unlink(missing_ok=True)
            except Exception:
                pass
        db.delete(existing)
        db.commit()
        return {"status": "removed", "spotted": False}

    else:
        photo = UserPhoto(
            user_id=user.id,
            aircraft_id=aircraft_id,
            taken_date=date.today(),
        )
        db.add(photo)
        db.commit()
        return {"status": "added", "spotted": True, "photo_id": photo.id}


@app.post("/api/upload-photo/{photo_id}")
async def upload_photo(photo_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """上传照片到已有的拍摄记录"""
    photo = db.query(UserPhoto).filter(UserPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="记录不存在")

    # 保存文件
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else "jpg"
    if ext not in ("jpg", "jpeg", "png", "webp"):
        ext = "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = UPLOAD_DIR / filename

    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    # 更新记录
    photo.image_url = f"/uploads/{filename}"
    db.commit()

    return {"status": "ok", "image_url": photo.image_url}


@app.post("/api/update-photo/{photo_id}")
async def update_photo(
    photo_id: int,
    taken_date: str = Form(""),
    taken_location: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    """更新拍摄记录的元数据"""
    photo = db.query(UserPhoto).filter(UserPhoto.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404)
    if taken_date:
        try:
            photo.taken_date = date.fromisoformat(taken_date)
        except ValueError:
            pass
    photo.taken_location = taken_location
    photo.notes = notes
    db.commit()
    return {"status": "ok"}


# ─── 挂载静态文件 ───────────────────────────────────────────

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
