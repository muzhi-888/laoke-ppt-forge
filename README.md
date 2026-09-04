# 演示文稿一键生成器（laoke-ppt-forge）

> 局内人·老K · 专注实体老板 / 职场人 AI 落地实战

把主题、大纲或零散要点，整理成结构专业、视觉干净、可直接演示或转 PDF 的幻灯片。管三件事：内容策划（讲什么）、版式规范（长什么样）、一键生成（怎么出）。不堆花哨模板，只做干净、专业、能用的片子。

## 解决什么

- 拿到主题大脑空白 → 五步成片法把「讲什么」定死
- 内容堆成段落观众懒得看 → 极简版式规范锁死配色字体对齐
- 不想装 Office 调格式 → 脚本一键出自包含 HTML 幻灯片（浏览器放映、可打印 PDF）
- 路演/融资片怕编数据 → 护栏强制真实数据，缺口标待补

## 核心能力

- 五步成片法 + 分场景骨架库（汇报/产品/培训/路演/分享）
- 极简版式规范（三套安全配色、字体对齐纪律、禁区清单）
- 图表与配图规范、演讲备注与节奏、页标题改写库
- 配套脚本 `scripts/deck_from_md.py`：Markdown 大纲 → 自包含 HTML 幻灯片，纯标准库零依赖
- 合规护栏：不编数据、不侵权、不冒充

## 目录结构

```
laoke-ppt-forge/
├── SKILL.md                 # 完整手册（五步法+骨架+版式+图表+自检）
├── _meta.json
├── references/             # 5 份：骨架库/版式/图表/备注节奏/标题改写
├── scripts/
│   └── deck_from_md.py     # 大纲 → HTML 幻灯片（stdlib，离线）
├── hooks/
│   └── guardrail.md
└── icon.png
```

## 快速开始

```bash
# 内置示例自检
python scripts/deck_from_md.py --demo --output deck.html

# 用你的大纲生成
python scripts/deck_from_md.py --input outline.md --title "产品介绍" --output deck.html
```

浏览器打开 `deck.html` 即放映：方向键/空格翻页，按 `n` 看演讲备注，打印可存 PDF。

把主题/大纲丢给支持 SKILL.md 的 Agent（WorkBuddy / SkillHub / Claude Code / Cursor），它会自动走五步法产出片子并生成 HTML。

## 相关资源（同域推荐）

- ima 知识库《WorkBuddy实战案例200+》：200+ 真实办公提效实战打法
- ima 知识库《WorkBuddy官方·ima知识库200篇》：AI 工具落地用法
- SkillHub 作者主页：搜索「局内人·老K」
- 落地页：https://muzhi-888.github.io/ju-nei-ren-lao-k/

## License

MIT —— 可自由使用、修改、再分发。

## 免责声明

本工具仅供学习与研究使用，产出为用户自有内容的整理，**不构成任何业绩承诺或法律/财务建议**。路演/融资等对外材料请人工复核真实数据与权威来源，最终责任由使用者承担。
