# MAINTENANCE.md — oss-top50 运维留档

> 写给未来的维护者（人或 AI）。读完就知道项目的当前状态、待升级清单、设计约定和已知问题。

---

## 一、项目定位

- **名称**：oss-top50
- **功能**：GitHub 开源项目双榜排行榜（全期 Top 50 + 近半年 Top 50），托管于 GitHub Pages
- **仓库**：https://github.com/QwX777MCC/oss-top50
- **在线**：https://qwx777mcc.github.io/oss-top50/top50.html
- **运维入口**：`cd Desktop/oss-top50`

---

## 二、当前版本状态（2026-06-18）

| 维度 | 状态 | 备注 |
|------|:--:|------|
| 数据 | ✅ | 100 条全量中文翻译 + 英文原文备查 |
| 构建 | ✅ | `build_site.py` 含数据校验层 |
| 部署 | ✅ | SSH 推送 + Pages 自动上线 |
| 安全 | ✅ | 审计 → 质询 → FMEA → 修复 四阶段完成 |
| 设计 | ✅ | 莫兰迪高级灰体系 · 六维设计需求落地 |
| 手机 | ✅ | 768/420 双断点适配 |

---

## 三、🔶 待升级清单（按优先级）

### P1 - 应尽快（下一轮运维）

| # | 项目 | 说明 |
|---|------|------|
| 1 | **Windows SSH 私钥权限** | Git Bash `chmod 600` 不生效，需 PowerShell `icacls` 真正限制。当前单用户系统风险极低但不符合安全规范 |
| 2 | **GitHub Actions 改用官方 deploy-pages** | 当前 `peaceiris/actions-gh-pages@v3` 是第三方 Action，应切到 `actions/deploy-pages` |
| 3 | **Pages 部署验证** | 推送后无自动检查 Pages 是否上线成功，建议 CI 增加 `curl` 验证步骤 |

### P2 - 可规划（时机合适时）

| # | 项目 | 说明 |
|---|------|------|
| 4 | **自定义域名** | 当前 `qwx777mcc.github.io/oss-top50`，可绑独立域名如 `oss-top50.dev` |
| 5 | **分支保护** | 如果仓库从单人变多人协作，需开 main 分支保护 + CODEOWNERS |
| 6 | **数据备份** | `data/` 目前无自动备份，建议 GitHub Actions 增加定时 snapshot 到 release |
| 7 | **翻译自动化** | `desc_cn` 目前全量人工翻译，新增仓库无翻译需手动补。可引入 AI 翻译脚本 |

### P3 - 长远优化

| # | 项目 | 说明 |
|---|------|------|
| 8 | **RSS 订阅** | 榜单变动时自动推送 |
| 9 | **历史趋势图** | 项目 Star 增长曲线可视化 |
| 10 | **搜索功能** | 前端关键词搜索（当前只有下拉筛选） |
| 11 | **国际化** | 英文版页面 |

---

## 四、安全审计留档（2026-06-18）

| 发现 | 严重度 | 质询后 | 修复状态 |
|------|:---:|:---:|:---:|
| SSH 私钥 644 | CRITICAL → HIGH | Windows 单用户无利用路径 | ⚠️ 待 icacls |
| 缺少 .gitignore | HIGH | 零成本保险 | ✅ 已添加 |
| git config 暴露路径 | HIGH → MEDIUM | 不推送到远端 | ✅ 已清理 |
| Actions 权限过宽 | MEDIUM → LOW | 手动触发 + 单人 | ✅ 可接受 |
| Token 日志泄露 | MEDIUM → LOW | requests 默认无日志 | ✅ 已抑制 |
| 分支保护缺失 | MEDIUM → LOW | 单人项目 | 🔶 P2-5 |
| 数据无校验 | FMEA 发现 | 坏数据静默生成坏页面 | ✅ 已添加 |

---

## 五、设计系统速查

| 变量 | 用途 |
|------|------|
| `--cvs #f5f3f0` | 画布底色（莫兰迪灰白） |
| `--crd / --crd-h / --crd-a` | 卡片三层底色 |
| `--tx / --tx-d / --tx-f` | 正文 / 次要 / 辅助文字 |
| 领域色 | `oklch(0.60 0.05 {hue})` 9 色统一饱和度明度 |
| 暗色模式 | `prefers-color-scheme: dark` 自动切换 |

**视觉权重阶梯（高→低）**：排名编号 > 项目名 > Star > 比例条 > 标签 > 收起 > 元数据 > 展开

---

## 六、运维命令速查

```bash
# 进入项目
cd Desktop/oss-top50

# 更新数据（手动编辑 data/*.json 后）
python scripts/build_site.py

# 推送到 GitHub（自动触发 Pages 部署）
git add -A && git commit -m "描述" && git push

# 查看状态
git status && git log --oneline -5

# 回滚到上一版
git revert HEAD --no-edit && git push
```

---

## 七、文件清单

```
oss-top50/
├── data/
│   ├── alltime.json          # 全期 Top 50，含 desc_cn + desc_cn_source
│   └── recent.json           # 近半年 Top 50
├── scripts/
│   ├── build_site.py         # 数据 → HTML（含校验层）
│   ├── fetch_data.py         # GitHub API → 数据（含日志抑制）
│   └── requirements.txt
├── docs/                     # GitHub Pages 源
│   ├── index.html
│   ├── top50.html            # 由 build_site.py 生成
│   ├── tech-stack.html       # 技术栈学习文档
│   └── assets/style.css
├── .github/workflows/
│   └── update.yml            # 手动触发 CI
├── .gitignore
├── AI-GUIDE.md               # 运维操作手册
├── MAINTENANCE.md             # 本文件
└── README.md
```
