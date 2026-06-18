# oss-top50 项目收纳

## 在线地址
- 首页：https://qwx777mcc.github.io/oss-top50/
- 榜单：https://qwx777mcc.github.io/oss-top50/top50.html
- 技术栈：https://qwx777mcc.github.io/oss-top50/tech-stack.html
- 仓库：https://github.com/QwX777MCC/oss-top50

## 文件清单（15 文件 / ~280KB）

```
oss-top50/
├── data/
│   ├── alltime.json      全期 Top 50 仓库数据
│   └── recent.json       近半年 Top 50 仓库数据
├── scripts/
│   ├── fetch_data.py     GitHub Search API 数据获取
│   ├── build_site.py     数据校验 → 分类 → 洞察 → HTML 生成
│   └── requirements.txt  仅 requests>=2.28
├── docs/
│   ├── index.html        首页导航
│   ├── top50.html        榜单主页面（自动生成）
│   ├── tech-stack.html   技术栈教学文档
│   └── assets/style.css  共享样式
├── .github/workflows/
│   └── update.yml        手动触发 CI：fetch → build → deploy
├── .gitignore
├── LICENSE               MIT
├── README.md             项目介绍
├── AI-GUIDE.md           运维操作手册（给 AI 和运维者）
└── MAINTENANCE.md        运维留档（状态 / 待升级 / 审计 / 命令）

共 15 个文件，约 280KB
```

## 技术栈

| 层 | 技术 |
|----|------|
| 数据 | GitHub Search API → Python requests |
| 构建 | Python 脚本：校验 → 分类 → 洞察 → 生成 HTML |
| 前端 | HTML + CSS + 原生 JS，零框架 |
| 部署 | GitHub Pages（docs/ 目录）|
| CI/CD | GitHub Actions，手动触发（workflow_dispatch）|
| 认证 | SSH ED25519 |
| 色彩 | oklch() 冷中性灰（hue 220°）+ 紫色强调（285°）|
| 响应式 | 380 / 420 / 768 / 1600 四个断点 |

## 设计系统

### 色彩（oklch 冷中性灰 hue 220° + 强调 hue 285°）
| 变量 | 亮色 | 用途 |
|------|------|------|
| --cvs | oklch(0.97 0.006 220) | 画布背景 |
| --crd | oklch(0.99 0.003 220) | 卡片背景 |
| --tx | oklch(0.25 0.008 220) | 正文 |
| --link | oklch(0.55 0.09 240) | 链接 |

### 响应式断点
| 名称 | 值 | 覆盖 |
|------|-----|------|
| bp-xs | 380px | 极小程序 |
| bp-sm | 420px | 手机 |
| bp-md | 768px | 平板 |
| bp-xl | 1600px | 大屏 |

### 9 个领域色（oklch hue 覆盖色环）
安全 10° · Web前端 25° · 教育 95° · 开发工具 140° · AI/ML 180° · DevOps 210° · AI Agent 250° · 后端 280° · 资源合集 350°

## 功能清单

| 功能 | 说明 |
|------|------|
| 双榜切换 | 全期 Top 50 ↔ 近半年 Top 50 |
| 筛选 | 语言 / 领域 下拉筛选 |
| 排序 | Star / 月增速 / 最近更新 |
| 卡片展开 | 点击展开深度洞察（问题/功能/原文/源码链接） |
| 源码溯源 | 展开区内链接到 GitHub 仓库（灰蓝色） |
| 统计面板 | 总 Star、最高、中位、覆盖语言 |
| 明暗主题 | 系统自动跟随 + 右下角 ◐ 手动切换 |
| 回到顶部 | 滚动 >300px 出现，CSS 纯几何三角形，平滑滚动 |
| 返回首页 | eyebrow 即链接，hover 装饰线延长+↩淡入 |
| 响应式 | 380/420/768/1600 四断点全覆盖 |
| 离线可用 | 数据内嵌 HTML，0 网络请求 |

## 运维命令

```bash
# 本地构建
cd "Desktop\AI资讯\项目2\oss-top50"
python scripts/build_site.py

# 数据更新 + 构建 + 部署（一条龙）
# 在 GitHub 网页 → Actions → Update Rankings → Run workflow

# 手动推送（CMD）
cd "Desktop\AI资讯\项目2\oss-top50"
git add -A
git commit -m "说明"
git push
```

## 待升级项

| 优先级 | 项目 |
|--------|------|
| P1 | Windows SSH 私钥权限（icacls） |
| P1 | Pages 部署后自动验证（curl 检查） |
| P2 | 自定义域名 |
| P2 | 数据自动备份 |
| P2 | 翻译自动化 |
| P3 | 搜索 / 趋势图 / RSS |

## 提交历史（45+ 次）

核心节点：
- 01-15：基础搭建 + 数据 + 翻译
- 16-22：平面构成优化（按钮/间距/手机端）
- 23-27：安全审计修复 + 文件整理 + LICENSE
- 28-34：大小屏适配 + 色彩重构 + 主题切换 + 回到顶部 + 架构修复
- 35-45+：毫秒透明度 + 色差根因诊断 + 几何替代 + 工作空间归整 + 导航重构
