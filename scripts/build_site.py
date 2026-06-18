import json, os, re
from datetime import date

today = date.today().isoformat()  # 动态日期，不再硬编码

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DOCS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')

# Load and validate data
alltime = json.load(open(os.path.join(DATA_DIR, 'alltime.json'), 'r', encoding='utf-8'))
recent = json.load(open(os.path.join(DATA_DIR, 'recent.json'), 'r', encoding='utf-8'))

# ─── Data integrity check ───
def validate_data(data, label):
    if not isinstance(data, list):
        raise ValueError(f"{label}: expected a list, got {type(data).__name__}")
    if len(data) == 0:
        raise ValueError(f"{label}: empty dataset, refusing to generate page")
    required = ['name', 'url', 'stars']
    for i, r in enumerate(data):
        for field in required:
            if field not in r or r[field] is None:
                raise ValueError(f"{label}[{i}]: missing required field '{field}'")
        if not isinstance(r.get('stars', 0), (int, float)):
            raise ValueError(f"{label}[{i}]: stars must be a number, got {type(r['stars']).__name__}")
    print(f"  [ok] {label}: {len(data)} repos validated")

validate_data(alltime, 'alltime')
validate_data(recent, 'recent')

# 领域自动分类：if-elif 链，按优先级顺序匹配关键词
# 优先匹配高特异性类别（AI Agent），再匹配通用类别（AI/ML）
# 修改关键词时注意顺序敏感，排前面的优先命中
def classify_field(item):
    name = item['name'].lower()
    desc = item.get('desc', '').lower()
    topics = [t.lower() for t in item.get('topics', [])]
    kw = name + ' ' + desc + ' ' + ' '.join(topics)
    if any(k in kw for k in ['agent skill','claude code','claude-code','codex cli','opencode','agent harness','agent-managed','agent skills','coding agent','skills for','skills framework','agentic','ai agent','ai-agents']):
        return 'ai-agent'
    if any(k in kw for k in ['machine learning','deep learning','tensorflow','pytorch','neural network','transformer','stable diffusion','llama','fine-tun','model training','nlp','huggingface','transformers','llm','gpt','chatgpt','openai','anthropic','ollama','diffusion','autogpt','ai enginee','ai coding','coding agent']):
        return 'ai-ml'
    if any(k in kw for k in ['react','vue','frontend','bootstrap','css framework','ui component','design system','tailwind css','html css','web app']):
        return 'web-frontend'
    if any(k in kw for k in ['backend framework','django','flask','spring','microservices','rest api','graphql','orm','database']):
        return 'backend'
    if any(k in kw for k in ['kubernetes','docker','container','linux kernel','shell framework','oh-my-zsh','zsh','devops','continuous','monitoring','cloud','deploy','linux']):
        return 'devops'
    if any(k in kw for k in ['learn','tutorial','course','education','curriculum','roadmap','guide','handbook','book','interview prep','coding interview','study plan','from scratch','100 days','computer science']):
        return 'education'
    if any(k in kw for k in ['security','hack','crypto','password','authentication']):
        return 'security'
    if any(k in kw for k in ['awesome','curated list','collection','resource list','.gitignore']):
        return 'collection'
    if any(k in kw for k in ['data science','analytics','data visualization','apache spark']):
        return 'data'
    return 'dev-tools'

FIELD_META = {
    'ai-agent':      {'label':'AI Agent','hue':250,'emoji':'\U0001f916'},
    'ai-ml':         {'label':'AI/ML','hue':180,'emoji':'\U0001f9e0'},
    'education':     {'label':'教育资源','hue':95,'emoji':'\U0001f4da'},
    'dev-tools':     {'label':'开发工具','hue':140,'emoji':'\U0001f527'},
    'collection':    {'label':'资源合集','hue':350,'emoji':'\U0001f4cb'},
    'web-frontend':  {'label':'Web前端','hue':25,'emoji':'\U0001f3a8'},
    'devops':        {'label':'DevOps','hue':210,'emoji':'\U0001f3d7\ufe0f'},
    'backend':       {'label':'后端框架','hue':280,'emoji':'\u2699\ufe0f'},
    'security':      {'label':'安全','hue':10,'emoji':'\U0001f512'},
}

INSIGHTS = {
    'codecrafters-io/build-your-own-x': {
        'insight': '不从零学，从"造"学。这不是教你写代码的教程——它是让你自己实现 Git、Docker、Redis、Shell。每造一个工具，你被迫理解那个工具背后的核心原理。这是编程教育中最彻底的反向工程路径。',
        'problem': '传统编程教学"先学语法再写项目"路径过长，且不触及底层原理。build-your-own-x 把学习顺序颠倒：先造工具，再造认知。',
        'features': '覆盖 100+ 技术主题的分步重造指南；从零实现 Git/Docker/Redis/Shell/数据库；项目难度分级，适合初中级开发者；社区维护的代码评测系统'
    },
    'sindresorhus/awesome': {
        'insight': 'GitHub 的"黄页"。在任何领域开始学习之前，awesome 列表是你第一个停靠站。它不是内容创造者，是内容策展引擎——每个条目都是经过社区投票的精选链接。',
        'problem': 'GitHub 信息过载，高质量资源散落在数百万仓库中。awesome 用人工策展 + 社区共识解决了"该从哪开始"的问题。',
        'features': '覆盖几乎所有技术领域的精选资源列表；社区贡献与维护机制；统一的列表格式便于浏览；广泛被搜索引擎索引，降低发现成本'
    },
    'freeCodeCamp/freeCodeCamp': {
        'insight': '编程教育界的"免费替代一切付费 bootcamp"。它用一套完整的交互式课程 + 实战项目 + 认证体系，证明了你不需要花 2 万美元学编程。核心不是"免费"，是"可执行的学习路径"。',
        'problem': '编程教育资源要么免费但零散，要么系统但昂贵。freeCodeCamp 找到了第三条路：开源社区驱动、系统化、可认证的免费教育。',
        'features': '11 个完整的认证课程（Web/数据/AI）；交互式编程练习环境；数千小时的视频教程和文章；全球最大的开源编程社区之一'
    },
    'public-apis/public-apis': {
        'insight': '开发者版的"电话黄页"。想在项目里加天气、支付、地图、翻译？先翻这里。它在"有一个想法"和"开始写代码"之间架了一座桥——知道什么是现成的，才知道该造什么。',
        'problem': '开发者经常为常见功能（天气、支付、地图等）重复造轮子，其实有大量免费/廉价的第三方 API 早已存在，只是缺乏集中发现渠道。',
        'features': '按类别组织的公共 API 列表；每项标注认证方式、HTTPS 支持、CORS 状态；社区持续维护更新；适合快速原型验证产品想法'
    },
    'affaan-m/ECC': {
        'insight': 'Claude Code 的"操作系统层"。Skills、Memory、Security、Research——这四个词构成了 agent 运行的完整底座。它不是另一个 skill 合集，是一套 agent 性能和安全的标准化体系。',
        'problem': 'Claude Code 的 Skills 各自为战，缺乏统一的性能监控、记忆管理和安全审计。ECC 提供了 agent harness 的标准化层——让所有 skills 跑在同一个经过优化的底座上。',
        'features': 'Agent 技能编排与性能优化系统；内置记忆管理与上下文压缩；安全审计与沙盒执行；支持 Claude Code / Codex / Opencode / Cursor 多平台'
    },
    'ultraworkers/claw-code': {
        'insight': '一个思想实验变成的现实：如果让 AI 代理完全自主地建造和维护一个项目，会发生什么？claw-code 就是这个实验的结果——全程无人类提交代码。它是 agent 自主编程能力的极限测试。',
        'problem': '我们不知道 AI 代理在零人类干预下能否交付可维护的软件。claw-code 是第一个大规模验证这个问题的开源实验。',
        'features': '全自主 AI 开发与维护 Rust 项目；Gajae-Code/LazyCodex 代理框架；零人类代码干预的实验设计；MIT 开源，可复现实验'
    },
    'multica-ai/andrej-karpathy-skills': {
        'insight': '一句话的价值：Karpathy 观察到自己用 Claude Code 时的常见错误模式，把它们编成一个 CLAUDE.md 文件。17 万 Star 不是因为复杂——是因为精准。最好的 prompt engineering 不是长，是对。',
        'problem': '开发者使用 Claude Code 时重复犯相同的编码错误。Karpathy 的系统化观察把这些 pitfalls 提炼成了可复用的行为约束文件。',
        'features': '单个 CLAUDE.md 文件优化 Claude Code 行为；基于 Karpathy 对 LLM 编码陷阱的观察；覆盖代码质量、架构决策、错误处理等维度；开源可自由修改适配'
    },
    'mattpocock/skills': {
        'insight': '来自"真实工程师"而不是"prompt engineer"的 skills。Matt Pocock 是 TypeScript 社区的权威声音——他的 skills 带着实用主义的温度。不是教你怎么问 AI 问题，是让 AI 学会怎么做工程。',
        'problem': '现有 AI coding skills 大多来自 prompt 专家而非一线工程师，缺乏真实工程场景的实用性验证。',
        'features': '来自真实工程工作流的 Skills 配置；TypeScript/React/Node.js 生态专属优化；开箱即用的 .claude 目录结构；持续更新维护'
    },
    'garrytan/gstack': {
        'insight': 'YC CEO 的 Claude Code 配置：23 个角色工具，把一个人变成一支团队。CEO、设计师、工程经理、发布经理、文档工程师、QA——六个角色封装在一个终端里。这是"一人公司"的技术实现。',
        'problem': '独立开发者和创业团队资源有限，无法雇佣完整的技术团队。gstack 用 agent roles 模拟了完整的软件工程团队结构。',
        'features': '23 个角色化工具（CEO/设计/工程/QA 等）；一套完整的 Claude Code 工作流；YC 创业公司验证的生产力方案；MIT 开源'
    },
    'VoltAgent/awesome-design-md': {
        'insight': '"设计系统"民主化的一次尝试。以前你要雇设计师才能有品牌级 UI——现在把你的品牌调性写进 DESIGN.md，coding agent 就能生成配套界面。这是 design token 的 agent 化。',
        'problem': '非设计师开发者难以产出品牌级 UI。DESIGN.md 模式将设计系统编码化为文本，让 coding agent 可以理解和复现视觉风格。',
        'features': '收集热门品牌 DESIGN.md 文件分析；设计系统文本化模板；支持 Figma/Google Stitch 等多源导入；Vibe Coding 友好的设计协作方案'
    },
    'karpathy/autoresearch': {
        'insight': 'Karpathy 的 AI 研究自动化实验：AI agents 自动在单 GPU 上跑 nanochat 训练的研究循环。这是"AI 做 AI 研究"的早期原型。',
        'problem': 'AI 研究中的大量工作（参数调优、实验记录、结果分析）是重复性的，理论上可以由 AI 代理自主完成。',
        'features': 'AI agent 自动运行的 nanochat 训练研究；单 GPU 友好；开源可复现；探索 AI 研究自动化的边界'
    },
    'JuliusBrussee/caveman': {
        'insight': '幽默背后是精准的经济学洞察。Claude Code 的 token 计费模式下，少说 65% 的话 = 省 65% 的钱。caveman 用"原始人说话"的伪装，实现了 prompt compression 的经济价值。',
        'problem': 'Claude Code 每次对话消耗大量 token，导致 API 费用快速累积。压缩 prompt 长尾部分可以显著降低成本而不影响输出质量。',
        'features': 'Claude Code Skill 减少 65% token 消耗；原始人语言风格压缩技巧；一个文件即插即用；已验证不影响核心任务完成度'
    },
    'pewdiepie-archdaemon/odysseus': {
        'insight': 'PewDiePie 的开源 AI 工作空间。这是自媒体顶流对"个人 AI 基础设施"的理解——自托管、私密、一体化。它代表了创作者群体对 AI 工具的需求：简单、强大、完全掌控。',
        'problem': '现有的 AI 工作空间要么是 SaaS（数据不安全），要么过于技术化（创作者用不了）。Odysseus 试图在两者间建立桥梁。',
        'features': '自托管 AI 工作空间；统一的 LLM/工具/数据管理；隐私优先的本地部署；适合创作者和个人用户'
    },
}

def auto_insight(item):
    desc_cn = item.get('desc_cn', '')
    if desc_cn:
        sentences = re.split(r'[.。!！]', desc_cn)
        for s in sentences:
            s = s.strip()
            if 10 < len(s) < 150:
                return s
        return desc_cn[:150] + '…'
    desc = item.get('desc', '')
    if desc:
        return desc[:120] + '…'
    return '暂无中文描述。'

def auto_features(item):
    desc = item.get('desc', '')
    topics = [t.lower() for t in item.get('topics', [])]
    fs = []
    tl = ' '.join(topics).lower() + ' ' + desc.lower()
    if 'claude-code' in tl or 'claude code' in tl: fs.append('集成 Claude Code 生态')
    if 'open-source' in tl or 'open source' in tl: fs.append('完全开源')
    if 'cli' in topics or 'cli' in desc.lower(): fs.append('命令行工具')
    if 'api' in topics: fs.append('提供 API 接口')
    if 'mcp' in topics: fs.append('支持 MCP 协议')
    if 'docker' in topics or 'container' in desc.lower(): fs.append('Docker 容器化部署')
    if 'rust' in topics or item.get('lang') == 'Rust': fs.append('Rust 实现，高性能')
    if item.get('license') == 'MIT': fs.append('MIT 许可，商业友好')
    if item.get('stars_month', 0) > 30000: fs.append('超高增速，社区活跃')
    if not fs: fs.append('详见 GitHub 项目页面')
    return ', '.join(fs[:5])

def auto_problem(item):
    desc_cn = item.get('desc_cn', '')
    if desc_cn:
        return desc_cn[:150].rstrip('. ') + '…'
    desc = item.get('desc', '')
    if desc:
        return desc[:150].rstrip('. ') + '…'
    return '详见项目描述。'

for lst in [alltime, recent]:
    for item in lst:
        item['field'] = classify_field(item)
        if item['name'] in INSIGHTS:
            item['insight_data'] = INSIGHTS[item['name']]
        else:
            item['insight_data'] = {
                'insight': auto_insight(item),
                'problem': auto_problem(item),
                'features': auto_features(item),
                'desc_en': item.get('desc', '')
            }

def fmt(n): return f"{n:,}"
def fK(n):
    if n >= 1e5: return str(round(n/1e3))+'K'
    return f"{n/1e3:.1f}K"

data_all = json.dumps(alltime, ensure_ascii=False)
data_rec = json.dumps(recent, ensure_ascii=False)
fj = json.dumps(FIELD_META, ensure_ascii=False)

# ─── Generate HTML ───
html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>GitHub Top 50 双榜 · 开源风向标</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="wrap">

<header>
<div class="eyebrow">GitHub Archive · 开源风向标</div>
<h1>最强开源项目 Top 50 双榜</h1>
<div class="subtitle">全期经典对照近半年爆发 · 点击卡片展开深度解析 · 每条可溯源</div>
<div class="src-line">
<svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
数据来自 GitHub Search API · 截至 {today}
</div>
</header>

<div class="stats-row" id="stats-all">
<div class="stat-card"><div class="stat-val">{fmt(sum(r['stars'] for r in alltime))}</div><div class="stat-label">全期总 Star</div></div>
<div class="stat-card"><div class="stat-val">{fmt(alltime[0]['stars'])}</div><div class="stat-label">最高 Star</div></div>
<div class="stat-card"><div class="stat-val">{fmt(sorted([r['stars'] for r in alltime])[25])}</div><div class="stat-label">中位 Star</div></div>
<div class="stat-card"><div class="stat-val">{len(set(r['lang'] for r in alltime))}</div><div class="stat-label">覆盖语言</div></div>
</div>
<div class="stats-row" id="stats-rec" style="display:none">
<div class="stat-card"><div class="stat-val">{fmt(sum(r['stars'] for r in recent))}</div><div class="stat-label">半年总 Star</div></div>
<div class="stat-card"><div class="stat-val">{fmt(recent[0]['stars'])}</div><div class="stat-label">最高 Star</div></div>
<div class="stat-card"><div class="stat-val">{fmt(sorted([r['stars'] for r in recent])[25])}</div><div class="stat-label">中位 Star</div></div>
<div class="stat-card"><div class="stat-val">{len(set(r['lang'] for r in recent))}</div><div class="stat-label">覆盖语言</div></div>
</div>

<div class="tab-bar">
<button class="tab-btn active" onclick="switchTab('all')" id="tab-all">全期 Top 50</button>
<button class="tab-btn" onclick="switchTab('rec')" id="tab-rec">近半年 Top 50 <span class="tab-sub">{date.today().strftime('%Y.01')}–{date.today().strftime('%m')}</span></button>
</div>

<div class="filter-bar">
<label>语言</label><select id="flang" onchange="apply()"><option value="all">全部</option></select>
<label>领域</label><select id="ffld" onchange="apply()"><option value="all">全部</option></select>
<button class="sort-chip active" onclick="setSort('stars')" id="sort-stars">Star</button>
<button class="sort-chip" onclick="setSort('month')" id="sort-month">月增速</button>
<button class="sort-chip" onclick="setSort('fresh')" id="sort-fresh">最近更新</button>
</div>

<nav class="sticky-nav" id="snav"></nav>
<div id="list"></div>

<footer>
数据来源 <a href="https://github.com" target="_blank" rel="noopener noreferrer">GitHub</a> Search API &middot; 排序 Star 降序 &middot; 洞察基于第一性原理分析 &middot; 手动触发更新 &middot; 生成 {today}
</footer>

</div>

<script>
const F={fj};
const ALLTIME={data_all};
const RECENT={data_rec};
let tab='all',srt='stars',data=ALLTIME;

function fn(n){{return n.toLocaleString()}}
function fK(n){{return n>=1e5?(n/1e3|0)+'K':(n/1e3).toFixed(1)+'K'}}
function da(d){{return Math.max(1,Math.floor((new Date('{today}')-new Date(d))/864e5))}}

function buildOpts(){{
  const L=new Set,R=new Set;data.forEach(r=>{{L.add(r.lang);R.add(r.field)}})
  document.getElementById('flang').innerHTML='<option value="all">全部</option>'+[...L].sort().filter(Boolean).map(v=>`<option>${{v}}</option>`).join('')
  document.getElementById('ffld').innerHTML='<option value="all">全部</option>'+[...R].sort().map(v=>`<option value="${{v}}">${{(F[v]||{{}}).label||v}}</option>`).join('')
  document.getElementById('snav').innerHTML=[...R].sort().map(v=>`<a href="#sec-${{v}}">${{(F[v]||{{}}).emoji}} ${{(F[v]||{{}}).label}}</a>`).join('')
}}

function doSort(){{
  if(srt==='stars')data.sort((a,b)=>b.stars-a.stars)
  else if(srt==='month')data.sort((a,b)=>b.stars_month-a.stars_month)
  else data.sort((a,b)=>new Date(b.pushed)-new Date(a.pushed))
  data.forEach((r,i)=>r.ri=i+1)
}}

function esc(s){{return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}}

function render(items){{
  if(!items.length){{document.getElementById('list').innerHTML='<div class="empty-hint">没有匹配项，试试放宽筛选条件</div>';return}}
  const cmx=Math.max(...items.map(r=>r.stars))
  const grp={{}};items.forEach(r=>{{const f=r.field;if(!grp[f])grp[f]=[];grp[f].push(r)}})
  const ord=[...new Set(items.map(r=>r.field))]
  let h=''
  for(const field of ord){{
    const rs=grp[field];if(!rs||!rs.length)continue
    const m=F[field]||{{label:field,hue:0,emoji:''}}
    const clr=`oklch(0.60 0.05 ${{m.hue}})`
    h+=`<div class="section-group" id="sec-${{field}}"><div class="sec-head"><h3 style="color:${{clr}}">${{m.emoji}} ${{m.label}}</h3><span class="sec-count">${{rs.length}}/items</span></div>`
    rs.forEach(r=>{{
      const d=da(r.pushed),pct=Math.round(r.stars/cmx*100)
      const ins=r.insight_data||{{}}
      h+=`<div class="repo-card">
        <div class="card-collapsed">
          <div class="rank-num ${{r.ri<=3?'t3':''}}" style="${{r.ri<=3?'color:'+clr+';':''}}">#${{r.ri}}</div>
          <div class="repo-info-c">
            <span class="repo-name-c">${{esc(r.name)}}</span>
            <div class="repo-one-liner">${{esc(ins.insight||ins.problem||r.desc||'')}}</div>
            ${{r.topics&&r.topics.length?'<div class="repo-tags-row">'+r.topics.slice(0,5).map(t=>`<span>${{esc(t)}}</span>`).join('')+'</div>':''}}
          </div>
          <div class="star-col">
            <span class="star-num" style="color:${{clr}}">${{fn(r.stars)}}</span>
            <div class="star-bar-w"><div class="star-bar-f" style="width:${{pct}}%;background:${{clr}}"></div></div>
          </div>
        </div>
        <button class="toggle-btn" onclick="event.stopPropagation();toggleCard(this.closest('.repo-card'))">展开详情</button>
        <div class="card-expanded" onclick="event.stopPropagation()">
          <div class="exp-insight">${{esc(ins.insight)}}</div>
          ${{ins.problem?'<div class="exp-section"><h4>🎯 解决的问题</h4><p>'+esc(ins.problem)+'</p></div>':''}}
          ${{ins.features?'<div class="exp-section"><h4>🔧 核心功能</h4><p>'+esc(ins.features)+'</p></div>':''}}
          ${{r.desc&&r.desc.length>10?'<div class="exp-section"><details class="exp-original"><summary>📝 英文原文</summary><p>'+esc(r.desc)+'</p></details></div>':''}}
          <div class="exp-meta">
            <span>${{d<=14?'● 近两周活跃':(d<=60?'● '+d+'天前':'○ '+d+'天前更新')}}</span>
            <span>Fork ${{fn(r.forks)}}</span>
            <span>创建 ${{r.created}}</span>
            <span>${{r.license||'No license'}}</span>
            <span>~${{fK(r.stars_month)}}/月</span>
          </div>
          ${{r.topics&&r.topics.length?'<div class="repo-tags-row" style="margin-top:8px">'+r.topics.slice(0,8).map(t=>`<span>${{esc(t)}}</span>`).join('')+'</div>':''}}
          <a class="exp-link" href="${{r.url}}" target="_blank" rel="noopener" onclick="event.stopPropagation()">${{r.url}} <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 17L17 7M7 7h10v10"/></svg></a>
          <button class="collapse-btn" onclick="event.stopPropagation();toggleCard(this.closest('.repo-card'))">收起 ▲</button>
        </div>
      </div>`
    }})
    h+='</div>'
  }}
  document.getElementById('list').innerHTML=h
}}

function toggleCard(card){{card.classList.toggle('open')}}

function apply(){{
  const lg=document.getElementById('flang').value,fd=document.getElementById('ffld').value
  let items=data;if(lg!=='all')items=items.filter(r=>r.lang===lg);if(fd!=='all')items=items.filter(r=>r.field===fd)
  render(items)
}}

function switchTab(t){{
  tab=t;document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'))
  document.getElementById('tab-'+t).classList.add('active')
  data=t==='all'?[...ALLTIME]:[...RECENT]
  document.getElementById('stats-all').style.display=t==='all'?'grid':'none'
  document.getElementById('stats-rec').style.display=t==='rec'?'grid':'none'
  document.getElementById('flang').value='all';document.getElementById('ffld').value='all'
  srt='stars';document.querySelectorAll('.sort-chip').forEach(c=>c.classList.remove('active'))
  document.getElementById('sort-stars').classList.add('active')
  doSort();buildOpts();render(data)
}}

function setSort(t){{
  srt=t;document.querySelectorAll('.sort-chip').forEach(c=>c.classList.remove('active'))
  document.getElementById('sort-'+t).classList.add('active')
  doSort();apply()
}}

doSort();buildOpts();render(data)
</script>
<button class="theme-toggle" onclick="var d=document.documentElement,m=matchMedia('(prefers-color-scheme:dark)').matches;d.dataset.theme=d.dataset.theme?null:(m?'light':'dark')" title="切换明暗模式">◐</button>
<a class="back-top" href="#" onclick="window.scrollTo({{top:0,behavior:'smooth'}});return false" title="回到顶部">▲</a>
<script>(function(){{var b=document.querySelector('.back-top');if(b){{window.addEventListener('scroll',function(){{b.classList.toggle('show',(window.pageYOffset||document.documentElement.scrollTop)>300)}},{{passive:true}})}}}})()</script>
</body>
</html>'''

out_path = os.path.join(DOCS_DIR, 'top50.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Generated: {out_path} ({len(html):,} bytes)")
print(f"All-time repos: {len(alltime)}, Recent repos: {len(recent)}")
