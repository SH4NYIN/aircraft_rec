"""
种子数据脚本 — 中国南方航空（CZ）初始机队数据（v2：含类别+值得关注标注）

运行方式：python seed_data.py
"""
from database import init_db, SessionLocal, Airline, Aircraft
from datetime import date


def seed():
    init_db()
    db = SessionLocal()

    # 检查是否已有数据
    if db.query(Airline).filter(Airline.iata_code == "CZ").first():
        print("[skip] 南航数据已存在，跳过种子数据导入")
        db.close()
        return

    # ── 创建航司 ──
    cz = Airline(
        name="中国南方航空",
        name_short="南航",
        iata_code="CZ",
        icao_code="CSN",
        country="中国",
        region="Asia",
        logo_url="",
        is_active=True,
    )
    db.add(cz)
    db.flush()

    # ── 南航机队（注册号, 机型, 类别, 彩绘名, 彩绘?, 值得关注?, 关注原因）──
    fleet_data = [
        # === A320 系列 (窄体) ===
        ("B-1234", "A320-200", "narrow_body", None, False, False, None),
        ("B-1235", "A320-200", "narrow_body", None, False, False, None),
        ("B-1236", "A320-200", "narrow_body", None, False, False, None),
        ("B-1237", "A320-200", "narrow_body", None, False, False, None),
        ("B-1238", "A320-200", "narrow_body", None, False, False, None),
        ("B-1651", "A320neo", "narrow_body", None, False, False, None),
        ("B-1652", "A320neo", "narrow_body", None, False, False, None),
        ("B-1653", "A320neo", "narrow_body", None, False, False, None),
        ("B-1654", "A320neo", "narrow_body", "天合联盟涂装", True, True, "retro"),
        ("B-1655", "A320neo", "narrow_body", None, False, False, None),
        ("B-1656", "A320neo", "narrow_body", None, False, False, None),
        ("B-1840", "A321-200", "narrow_body", None, False, False, None),
        ("B-1841", "A321-200", "narrow_body", None, False, False, None),
        ("B-1842", "A321-200", "narrow_body", None, False, False, None),
        ("B-1843", "A321-200", "narrow_body", None, False, False, None),
        ("B-1844", "A321-200", "narrow_body", "贵州号彩绘", True, True, "retro"),
        ("B-3000", "A321neo", "narrow_body", None, False, False, None),
        ("B-3001", "A321neo", "narrow_body", None, False, False, None),
        ("B-3002", "A321neo", "narrow_body", None, False, False, None),
        ("B-3003", "A321neo", "narrow_body", None, False, False, None),
        ("B-3004", "A321neo", "narrow_body", "南航梦想之翼", True, True, "retro"),

        # === A330 系列 (宽体) ===
        ("B-8361", "A330-200", "wide_body", None, False, False, None),
        ("B-8362", "A330-200", "wide_body", None, False, False, None),
        ("B-8363", "A330-200", "wide_body", None, False, False, None),
        ("B-8364", "A330-200", "wide_body", "广州之路彩绘", True, True, "retro"),
        ("B-8365", "A330-300", "wide_body", None, False, False, None),
        ("B-8366", "A330-300", "wide_body", None, False, False, None),
        ("B-8367", "A330-300", "wide_body", None, False, False, None),
        ("B-8368", "A330-300", "wide_body", None, False, False, None),
        ("B-8369", "A330-300", "wide_body", None, False, False, None),
        ("B-8370", "A330-300", "wide_body", "世博会彩绘", True, True, "retro"),

        # === A350 系列 (宽体) ===
        ("B-308T", "A350-900", "wide_body", None, False, False, None),
        ("B-308U", "A350-900", "wide_body", None, False, False, None),
        ("B-308V", "A350-900", "wide_body", None, False, False, None),
        ("B-30AL", "A350-900", "wide_body", None, False, False, None),
        ("B-30AM", "A350-900", "wide_body", None, False, False, None),
        ("B-30AN", "A350-900", "wide_body", "第 600 架 A350 彩绘", True, True, "milestone"),
        ("B-32DR", "A350-900", "wide_body", None, False, False, None),
        ("B-32DS", "A350-900", "wide_body", None, False, False, None),

        # === A380 系列 (宽体，稀有) ===
        ("B-6136", "A380-800", "wide_body", None, False, True, "rare_type"),
        ("B-6137", "A380-800", "wide_body", None, False, True, "rare_type"),
        ("B-6138", "A380-800", "wide_body", None, False, True, "rare_type"),
        ("B-6139", "A380-800", "wide_body", None, False, True, "rare_type"),
        ("B-6140", "A380-800", "wide_body", None, False, True, "rare_type"),

        # === B737 系列 (窄体) ===
        ("B-1239", "B737-700", "narrow_body", None, False, False, None),
        ("B-1240", "B737-700", "narrow_body", None, False, False, None),
        ("B-1241", "B737-700", "narrow_body", None, False, False, None),
        ("B-1918", "B737-800", "narrow_body", None, False, False, None),
        ("B-1919", "B737-800", "narrow_body", None, False, False, None),
        ("B-1920", "B737-800", "narrow_body", None, False, False, None),
        ("B-1921", "B737-800", "narrow_body", None, False, False, None),
        ("B-1922", "B737-800", "narrow_body", None, False, False, None),
        ("B-1923", "B737-800", "narrow_body", "珠海航展彩绘", True, True, "retro"),
        ("B-1924", "B737-800", "narrow_body", None, False, False, None),
        ("B-1200", "B737-8 MAX", "narrow_body", None, False, False, None),
        ("B-1201", "B737-8 MAX", "narrow_body", None, False, False, None),
        ("B-1202", "B737-8 MAX", "narrow_body", None, False, False, None),
        ("B-1203", "B737-8 MAX", "narrow_body", None, False, False, None),
        ("B-1204", "B737-8 MAX", "narrow_body", "南航第 900 架飞机", True, True, "milestone"),
        ("B-1205", "B737-8 MAX", "narrow_body", None, False, False, None),
        ("B-1206", "B737-8 MAX", "narrow_body", None, False, False, None),
        ("B-2240", "B737-8 MAX", "narrow_body", None, False, False, None),
        ("B-2241", "B737-8 MAX", "narrow_body", None, False, False, None),
        ("B-2242", "B737-8 MAX", "narrow_body", None, False, False, None),
        ("B-2243", "B737-8 MAX", "narrow_body", None, False, False, None),

        # === B777 系列 (宽体) ===
        ("B-2008", "B777-300ER", "wide_body", None, False, False, None),
        ("B-2009", "B777-300ER", "wide_body", None, False, False, None),
        ("B-2010", "B777-300ER", "wide_body", None, False, False, None),
        ("B-2011", "B777-300ER", "wide_body", None, False, False, None),
        ("B-2012", "B777-300ER", "wide_body", None, False, False, None),
        ("B-2013", "B777-300ER", "wide_body", "天合联盟涂装", True, True, "retro"),
        ("B-2028", "B777-300ER", "wide_body", None, False, False, None),
        ("B-2029", "B777-300ER", "wide_body", None, False, False, None),

        # === B777 货机 ===
        ("B-7183", "B777-F", "cargo", None, False, True, "rare_type"),
        ("B-7184", "B777-F", "cargo", None, False, True, "rare_type"),

        # === B787 系列 (宽体) ===
        ("B-2725", "B787-8", "wide_body", None, False, False, None),
        ("B-2726", "B787-8", "wide_body", None, False, False, None),
        ("B-2727", "B787-8", "wide_body", None, False, False, None),
        ("B-2728", "B787-8", "wide_body", None, False, False, None),
        ("B-2729", "B787-8", "wide_body", "第 787 架 787 彩绘", True, True, "milestone"),
        ("B-2730", "B787-8", "wide_body", None, False, False, None),
        ("B-2731", "B787-8", "wide_body", None, False, False, None),
        ("B-2787", "B787-9", "wide_body", None, False, False, None),
        ("B-2788", "B787-9", "wide_body", None, False, False, None),
        ("B-2789", "B787-9", "wide_body", None, False, False, None),
        ("B-2790", "B787-9", "wide_body", None, False, False, None),
        ("B-2791", "B787-9", "wide_body", None, False, False, None),

        # === ARJ21 / C919 (窄体/支线，国产=值得关注) ===
        ("B-653Y", "ARJ21-700", "regional", None, False, True, "rare_type"),
        ("B-653Z", "ARJ21-700", "regional", None, False, True, "rare_type"),
        ("B-654A", "ARJ21-700", "regional", None, False, True, "rare_type"),
        ("B-654B", "ARJ21-700", "regional", None, False, True, "rare_type"),
        ("B-919A", "C919", "narrow_body", None, False, True, "rare_type"),
        ("B-919B", "C919", "narrow_body", None, False, True, "rare_type"),
        ("B-919C", "C919", "narrow_body", "C919 标准涂装", True, True, "milestone"),
    ]

    for reg, ac_type, cat, livery_name, is_livery, notable, notable_reason in fleet_data:
        db.add(Aircraft(
            registration=reg,
            airline_id=cz.id,
            aircraft_type=ac_type,
            category=cat,
            is_special_livery=is_livery,
            livery_name=livery_name,
            livery_description=livery_name if is_livery else None,
            notable=notable,
            notable_reason=notable_reason,
            is_active=True,
        ))

    db.commit()
    total = db.query(Aircraft).filter(Aircraft.airline_id == cz.id).count()
    special = db.query(Aircraft).filter(
        Aircraft.airline_id == cz.id, Aircraft.is_special_livery == True
    ).count()
    notable = db.query(Aircraft).filter(
        Aircraft.airline_id == cz.id, Aircraft.notable == True
    ).count()
    wide = db.query(Aircraft).filter(
        Aircraft.airline_id == cz.id, Aircraft.category == "wide_body"
    ).count()
    print(f"[done] 南航种子数据 v2：{total} 架 | 宽体 {wide} | 彩绘 {special} | 值得关注 {notable}")
    db.close()


if __name__ == "__main__":
    seed()
