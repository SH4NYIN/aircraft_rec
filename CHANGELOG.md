# AviRec 开发日志

## 2026-05-07 — 项目初始化

### 需求分析
- 确定核心需求：飞机拍摄记录器，参考"飞哪"小程序交互模式
- 范围策略：广州优先，Phase 1 仅南航（CZ），后续扩展广州可拍摄航司
- 编写完整 PRD（`prd.md`），含用户故事、技术栈、API 调研、数据模型、路线图

### 技术栈决策
| 决策项 | 选择 | 理由 |
|--------|------|------|
| 后端框架 | Python FastAPI | 用户本地仅有 Python 环境，无 Node.js |
| 数据库 | SQLite | 标准库自带，零安装，单文件极简 |
| ORM | SQLAlchemy 2.0 | 与 SQLite 无缝适配，支持关系映射 |
| 前端 | 服务端模板 Jinja2 + 原生 JS | 无需 Node 构建，单进程部署 |
| 图片存储 | 本地文件系统 | MVP 阶段最简单，路径存 SQLite |

### 已交付物
- [x] `prd.md` — 需求文档（505 行，v1.0）
- [x] `requirements.txt` — Python 依赖清单（5 个包）
- [x] `database.py` — 4 张表模型（airlines / aircraft / user_photos / users）
- [x] `main.py` — FastAPI 应用（8 页面路由 + 3 API 端点）
- [x] `seed_data.py` — 南航种子数据 90 架（11 彩绘）
- [x] 6 个 Jinja2 模板（base / index / airlines / airline_detail / aircraft_detail / search）
- [x] `static/css/style.css` — 445 行响应式样式
- [x] `static/js/app.js` — 拍摄标记切换 + 照片上传逻辑

### 核心功能
- 航司列表 → 航司机队（彩绘置顶）→ 飞机详情 完整页面流
- 已拍/未拍 灰色滤镜 vs 彩色标记 视觉对比
- 一键切换拍摄状态（API 端点）
- 照片上传（单文件 10MB 限制，JPEG/PNG/WebP）
- 注册号/机型模糊搜索
- 首页统计卡片（总拍摄数 / 彩绘收集 / 航司数）

### 待验证
- [ ] 本地 `pip install` 依赖安装
- [ ] `python seed_data.py` 种子数据导入
- [ ] `python main.py` 启动服务，浏览器访问测试

### 下一步
- Phase 1 MVP：验证本地跑通 → 补充南航完整机队真实数据 → 打磨交互细节
- Phase 2：扩展国航/东航/海航等广州航司机队数据

---

## 2026-05-07 (晚间) — 高级筛选 & 机型分组 & 值得关注体系

### 新增「值得记录的飞机」判定标准
- 编写三层分类体系：普通 → 🌟值得关注（涂装/机型/身份/里程碑）→ 🎨彩绘
- 定义判定流程：入库时回答 5 个问题即可确定 notable 标签
- 写入 `prd.md` 5B 章节，含 UI 表现、分组排序、高级筛选选项表

### 数据模型变更
- `Aircraft` 表新增 3 个字段：
  - `category` — 机型类别（wide_body / narrow_body / regional / cargo / other）
  - `notable` — 是否值得关注（稀有型号/专机/里程碑等）
  - `notable_reason` — 关注原因（rare_type / vip / milestone / retro）
- 降序排序键：(类别序, 值得关注序, 机型大小序, 注册号)

### 后端变更 (`main.py`)
- 新增 `TYPE_SORT_ORDER` 映射表，覆盖 30+ 机型系列的大→小顺序
- 重写 `airline_detail` 路由，支持 5 个筛选参数：
  - `search` — 注册号模糊搜索
  - `type_filter` — 机型系列筛选
  - `category` — 类别筛选
  - `notable_filter` — 值得关注/仅彩绘/普通
  - `status` — 已拍/未拍
- 结果按类别分组 → 模板渲染

### 模板变更 (`airline_detail.html`)
- 移除旧的双 section（彩绘 + 普通），改为按类别分组 section
- 新增筛选栏：注册号输入 + 机型输入 + 类别下拉 + 关注下拉 + 状态下拉 + 重置
- 每张卡片显示 `card-tags`：涂装标签（黄色）+ 值得关注标签（颜色按原因区分）
- 注册号实时过滤（JS 前端过滤，无需提交表单）

### 种子数据升级 (`seed_data.py`)
- 全部 90 架飞机标注 category + notable + notable_reason
- 分类：宽体 33 架 / 窄体 41 架 / 区域 4 架 / 货机 2 架
- 4 种 notable_reason：rare_type（稀有） / milestone（里程碑） / retro（复古涂装） / vip（专机）
- A380、B777F、C919、ARJ21 标注为 rare_type

### 样式新增 (`style.css`)
- 筛选栏 sticky 吸附（导航栏下方）
- 类别分组 section 可折叠（点击标题）
- 5 色标签徽章：黄=涂装 / 蓝=稀有 / 红=专机 / 紫=里程碑 / 棕=复古
- 空状态提示样式
