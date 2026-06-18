# oss-top50

开源项目 Top 50 双榜 · 全期经典 vs 近半年爆发 · 可筛选 / 点击展开 / 可溯源。

**在线地址** → `https://{owner}.github.io/oss-top50`

## 这是什么

每天 GitHub 上有成千上万个新仓库诞生。哪些真正值得关注？oss-top50 用 Star 数 + 领域分类 + 自然语言洞察，帮你 3 秒内知道"最近半年 GitHub 火什么"。

## 功能

- **双榜对照**：全期 Top 50（历史经典）vs 近半年 Top 50（当前爆发）
- **多维筛选**：语言 × 领域 × Star/月增速/活跃度排序
- **点击展开**：默认紧凑卡片，点击展开获取深度洞察、问题分析、核心功能
- **可溯源**：每条项目名可点击跳转 GitHub 原仓库，附带许可证和创建元数据
- **明暗双模**：自动跟随系统主题

## 如何贡献

1. 编辑 `data/alltime.json` 或 `data/recent.json`
2. 运行 `python scripts/build_site.py` 重新生成页面
3. 提交 PR

详见 [AI-GUIDE.md](AI-GUIDE.md)（给 AI 和运维人员看）。

## 技术栈

- Python 3（数据生成脚本）
- 纯静态 HTML + CSS + 原生 JS（无框架依赖）
- GitHub Pages（部署）
- GitHub Actions（手动触发更新）

## 许可

MIT — 数据来自 GitHub Search API，归 GitHub 所有。
