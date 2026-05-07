# AviRec — 飞机拍摄记录器

面向航空摄影爱好者（plane spotter）的 Web 应用，用于记录和管理拍摄到的各航司飞机，彩绘机置顶展示，已拍/未拍一目了然。

## 功能

- **航司浏览** — 列表 + 国家筛选 + 拍摄进度条
- **机队视图** — 彩绘/特殊涂装飞机置顶高亮，普通飞机按注册号排列
- **图鉴收集** — 已拍摄彩色显示，未拍摄灰色滤镜（`grayscale`）
- **一键标记** — 在机队页面直接切换已拍/未拍
- **照片上传** — 拍摄后替换默认网络图片，支持 JPEG/PNG/WebP
- **搜索** — 按注册号或机型模糊搜索
- **统计** — 总拍摄数、彩绘收集进度、航司覆盖度

## 技术栈

| 层 | 技术 | 说明 |
|---|---|---|
| 后端 | Python 3.13 + FastAPI | 异步 Web 框架，自带 Swagger |
| 数据库 | SQLite | 零安装，标准库自带 |
| ORM | SQLAlchemy 2.0 | 关系映射，支持 SQLite |
| 前端 | Jinja2 + 原生 JS + CSS | 服务端渲染，无需 Node |
| 服务器 | Uvicorn | ASGI 服务器 |

## 快速开始

### 环境要求

- Python 3.10+

### 安装与运行

```bash
# 1. 克隆或进入项目目录
cd avi-rec

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动开发服务器
python main.py
```

浏览器访问 **http://localhost:8000**

- 首页 → 航司列表 → 点击"南航"进入机队
- 每架飞机卡片底部有"标记已拍"按钮
- 标记后自动出现照片上传入口

### 截图预览

待补充

## 项目结构

```
avi-rec/
├── main.py                # FastAPI 应用入口
├── database.py            # 数据库模型与连接
├── seed_data.py           # 种子数据导入脚本
├── requirements.txt       # Python 依赖
├── prd.md                 # 产品需求文档
├── templates/
│   ├── base.html          # 基础布局
│   ├── index.html         # 首页
│   ├── airlines.html      # 航司列表
│   ├── airline_detail.html # 航司机队
│   ├── aircraft_detail.html # 飞机详情
│   └── search.html        # 搜索页
├── static/
│   ├── css/style.css      # 样式表
│   └── js/app.js          # 交互逻辑
└── uploads/               # 用户上传照片（.gitignore）
```

## 路线图

| 阶段 | 内容 | 状态 |
|------|------|------|
| Phase 1 | 南航 MVP（当前） | 🚧 开发中 |
| Phase 2 | 广州航司扩展（国航/东航/海航等） | 📋 计划中 |
| Phase 3 | 外航 + 港澳台 + PWA 支持 | 📋 计划中 |

## 数据说明

