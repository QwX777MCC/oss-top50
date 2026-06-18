# AI-GUIDE.md — oss-top50 运维手册

> 这份文档写给任何人（包括未来的 AI 助手）。读完就知道这个项目的所有约定、如何更新数据、如何添加新功能。

---

## 项目简介

`oss-top50` 是一个托管在 GitHub Pages 上的开源项目排行榜。双榜（全期 Top 50 / 近半年 Top 50）自动聚合 GitHub 上最受欢迎的仓库，展示排名、洞察、链接。

**在线地址**：`https://{owner}.github.io/oss-top50`

---

## 目录结构

```
oss-top50/
├── data/
│   ├── alltime.json          ← 全期 Top 50 数据（手动或脚本生产）
│   └── recent.json           ← 近半年 Top 50 数据
├── scripts/
│   ├── build_site.py         ← 读取 data/ → 生成 docs/top50.html
│   ├── fetch_data.py         ← 调用 GitHub Search API → 写入 data/
│   └── requirements.txt      ← Python 依赖（仅 requests）
├── docs/                     ← GitHub Pages 发布目录
│   ├── index.html            ← 首页（导航入口）
│   ├── top50.html            ← 榜单主页面（build_site.py 生成，勿手动编辑！）
│   └── assets/
│       └── style.css         ← 共享样式（所有页面共用）
├── .github/workflows/
│   └── update.yml            ← 手动触发的 GitHub Actions：fetch → build → deploy
├── README.md                 ← 项目介绍（给人看）
└── AI-GUIDE.md               ← 你正在读的这份（给 AI 看）
```

---

## 数据约定

### `data/alltime.json` 和 `data/recent.json`

```json
[
  {
    "name": "owner/repo",
    "url": "https://github.com/owner/repo",
    "desc": "项目描述",
    "stars": 217341,
    "forks": 33361,
    "lang": "JavaScript",
    "created": "2026-01-18",
    "pushed": "2026-06-17",
    "issues": 31,
    "topics": ["ai-agents", "claude-code"],
    "license": "MIT",
    "stars_month": 43180
  }
]
```

**必填字段**：`name`, `url`, `stars`
**可选字段**：其余均可为 `null` 或空字符串

### 数据获取方式

1. **GitHub Search API**（推荐）：
   ```
   GET /search/repositories?q=stars:>10000&sort=stars&order=desc&per_page=50
   ```
   需要 `User-Agent` header。

2. **手动编辑**：直接修改 `data/*.json`，然后运行 `python scripts/build_site.py`。

---

## 构建流程

### 本地构建

```bash
cd oss-top50
pip install -r scripts/requirements.txt  # 只需要 requests
python scripts/build_site.py             # data/*.json → docs/top50.html
```

`build_site.py` 做的事情：
1. 读取 `data/alltime.json` 和 `data/recent.json`
2. 自动分类（按 Topics + 描述关键词 → AI Agent / AI-ML / 教育 / 工具...）
3. 匹配人工撰写洞察（`INSIGHTS` 字典中的 14 个重点仓库）
4. 为其余仓库自动生成描述
5. 输出 `docs/top50.html`（纯静态，可浏览器直接打开）

### GitHub Actions 构建（手动触发）

在 GitHub 仓库页面 → Actions → "Update Rankings" → Run workflow。

Actions 会自动：
1. 运行 `scripts/fetch_data.py` 拉最新数据
2. 运行 `scripts/build_site.py` 生成页面
3. 提交变更到 `docs/` 目录
4. GitHub Pages 自动部署（通常 1 分钟内生效）

---

## 洞察写作约定

`build_site.py` 中的 `INSIGHTS` 字典包含了人工撰写的项目洞察。每个条目结构：

```python
'repo-owner/repo-name': {
    'insight':  '一句话洞察（50-150字，基于第一性原理）',
    'problem':  '该项目解决的核心问题（用户视角）',
    'features': '核心功能列表（逗号分隔）'
}
```

**洞察写作原则**：
- 不重复项目描述（GitHub description）
- 回答"用户为什么需要它"而非"它是什么"
- 避免营销腔（"最好的"、"革命性的"）
- 中文优先，除非项目名是专有名词

**添加新洞察**：编辑 `build_site.py` 的 `INSIGHTS` 字典，重新运行 `build_site.py`。

---

## 样式维护

`docs/assets/style.css` 被所有 HTML 页面引用。样式体系：

| 变量 | 用途 |
|------|------|
| `--cvs` | 画布底色（亮灰 `#f5f3f0`） |
| `--crd` | 卡片底色 |
| `--crd-h` | 卡片 hover 态 |
| `--bd` | 边框色 |
| `--tx` | 正文色 |
| `--tx-d` | 次要文字 |
| `--tx-f` | 辅助文字 |

**颜色约束**：
- 明暗双模式：`prefers-color-scheme: dark` 自动切换
- 领域色统一使用 `oklch(0.60 0.05 {hue})`，确保同饱和度同明度
- 不使用投影、渐变、分割线

---

## 待优化项（Future Work）

- [ ] 支持自定义域名绑定（GitHub Pages Settings → Custom domain）
- [ ] 多语言支持
- [ ] 月度趋势图表
- [ ] RSS/邮件订阅

---

## FAQ

**Q: 这个文件谁更新？**
A: 任何人（包括 AI）。如果有新约定、新字段、新流程，直接追加到对应章节。

**Q: `data/` 里的 JSON 需要 Git 版本管理吗？**
A: 需要。每次更新后 commit，方便追溯历史版本。

**Q: 怎么添加新的 HTML 页面？**
A: 在 `docs/` 下创建新 HTML，引用 `assets/style.css`，然后从 `docs/index.html` 添加导航链接。
