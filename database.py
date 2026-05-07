"""
AviRec - 飞机拍摄记录器
SQLite 数据库模型定义
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime, timezone
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'avirec.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI 依赖注入：获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """创建所有表（含自动迁移旧库）"""
    Base.metadata.create_all(bind=engine)
    # v2 迁移：新增 category / notable / notable_reason 列
    _migrate_v2()


def _migrate_v2():
    """为旧数据库添加 v2 新增字段"""
    import sqlite3
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'avirec.db'))
    cur = conn.cursor()
    # 检查列是否存在，不存在则添加
    cur.execute("PRAGMA table_info(aircraft)")
    cols = {row[1] for row in cur.fetchall()}
    for col, col_def in [
        ("category", "TEXT DEFAULT 'narrow_body'"),
        ("notable", "BOOLEAN DEFAULT 0"),
        ("notable_reason", "TEXT"),
    ]:
        if col not in cols:
            try:
                cur.execute(f"ALTER TABLE aircraft ADD COLUMN {col} {col_def}")
            except Exception:
                pass
    conn.commit()
    conn.close()


# ─── 模型定义 ───────────────────────────────────────────────

class Airline(Base):
    __tablename__ = "airlines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="航司全称")
    name_short = Column(String(50), comment="简称")
    iata_code = Column(String(2), comment="IATA 二字码")
    icao_code = Column(String(3), comment="ICAO 三字码")
    country = Column(String(50), default="中国")
    region = Column(String(50), default="Asia")
    logo_url = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    aircraft = relationship("Aircraft", back_populates="airline", order_by="Aircraft.registration")


class Aircraft(Base):
    __tablename__ = "aircraft"

    id = Column(Integer, primary_key=True, autoincrement=True)
    registration = Column(String(20), unique=True, nullable=False, comment="注册号，如 B-1234")
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False)
    aircraft_type = Column(String(50), comment="机型，如 B737-8 MAX")
    icao_type = Column(String(10), comment="ICAO 机型代码，如 B38M")
    msn = Column(String(20), comment="制造商序列号")
    delivery_date = Column(Date, comment="交付日期")
    category = Column(String(20), default="narrow_body", comment="机型类别: wide_body/narrow_body/regional/cargo/other")
    is_special_livery = Column(Boolean, default=False, comment="是否彩绘/特殊涂装")
    livery_name = Column(String(100), comment="彩绘名称")
    livery_description = Column(Text, comment="彩绘描述")
    notable = Column(Boolean, default=False, comment="是否值得关注（稀有型号/专机/里程碑等）")
    notable_reason = Column(String(50), comment="值得关注的原因: rare_type/vip/milestone/retro")
    default_image_url = Column(Text, comment="默认网络图片 URL")
    default_image_source = Column(Text, comment="图片来源标注")
    is_active = Column(Boolean, default=True, comment="是否在役")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    airline = relationship("Airline", back_populates="aircraft")
    photos = relationship("UserPhoto", back_populates="aircraft")


class UserPhoto(Base):
    __tablename__ = "user_photos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    aircraft_id = Column(Integer, ForeignKey("aircraft.id"), nullable=False)
    image_url = Column(Text, comment="用户上传图片路径")
    thumbnail_url = Column(Text, comment="缩略图路径")
    taken_date = Column(Date, comment="拍摄日期")
    taken_location = Column(String(200), comment="拍摄地点")
    notes = Column(Text, comment="备注")
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="photos")
    aircraft = relationship("Aircraft", back_populates="photos")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    display_name = Column(String(50), default="飞友")
    avatar_url = Column(Text, default="")
    bio = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    photos = relationship("UserPhoto", back_populates="user")
