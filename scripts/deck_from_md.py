#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deck_from_md.py —— 演示文稿一键生成器 配套脚本

功能：把 Markdown 大纲转成「自包含 HTML 幻灯片」——浏览器打开即放映，
      方向键/空格/点击翻页，可按 n 切换演讲备注，可打印成 PDF。
      纯 Python 标准库，零依赖，离线可用，不引用任何外部资源。

大纲格式：
  # 页标题
  ## 副标题（可选，封面常用）
  - 要点
  > 引用
  [图：说明文字]        <- 渲染为图位占位
  <!-- 备注：演讲备注 -->  <- 按 n 显示，不在正片显示
  ---                    <- 分隔两页

用法：
  python deck_from_md.py --input outline.md --title "产品介绍"
  python deck_from_md.py                       # stdin
  python deck_from_md.py --demo                # 内置示例自检
  python deck_from_md.py --input outline.md --output deck.html

退出码：0 成功；非 0 参数错误或输入为空。
"""

import sys
import argparse
import html
import re

CSS = """
:root{--main:#1a2b4a;--accent:#d4af37;--ink:#222;--gray:#555;--bg:#f5f5f5;}
*{box-sizing:border-box;margin:0;padding:0;}
html,body{height:100%;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--ink);}
#deck{height:100vh;position:relative;overflow:hidden;}
.slide{position:absolute;inset:0;display:none;align-items:center;justify-content:flex-start;padding:6vh 8vw;}
.slide.active{display:flex;}
.slide-inner{max-width:1000px;width:100%;}
.slide h1{font-size:clamp(28px,4.2vw,44px);color:var(--main);line-height:1.25;margin-bottom:24px;border-left:8px solid var(--accent);padding-left:18px;}
.slide h2{font-size:clamp(18px,2.4vw,26px);color:var(--gray);font-weight:400;margin-bottom:20px;}
.slide ul{list-style:none;}
.slide li{font-size:clamp(18px,2.4vw,24px);line-height:1.7;padding:8px 0 8px 26px;position:relative;color:var(--ink);}
.slide li:before{content:"▍";color:var(--accent);position:absolute;left:0;}
.slide blockquote{border-left:6px solid var(--accent);background:#fff;padding:16px 20px;margin:18px 0;font-size:clamp(18px,2.4vw,24px);color:var(--main);font-style:italic;}
.slide p{font-size:clamp(16px,2vw,20px);line-height:1.7;color:var(--gray);margin:10px 0;}
.img-ph{border:2px dashed var(--accent);border-radius:10px;padding:30px;text-align:center;color:var(--gray);font-size:18px;margin:16px 0;background:#fff;}
.slide.cover{justify-content:center;text-align:center;}
.slide.cover .slide-inner{text-align:center;}
.slide.cover h1{border-left:none;padding-left:0;font-size:clamp(34px,5vw,56px);}
#bar{position:fixed;bottom:14px;right:20px;color:var(--gray);font-size:14px;background:rgba(255,255,255,.8);padding:4px 12px;border-radius:20px;}
#notes{position:fixed;left:0;right:0;bottom:0;background:var(--main);color:#fff;padding:18px 8vw;font-size:16px;display:none;line-height:1.6;}
#notes.show{display:block;}
#hint{position:fixed;top:14px;left:20px;color:var(--gray);font-size:12px;opacity:.7;}
"""

JS = """
let cur=0;const s=document.querySelectorAll('.slide');
function go(i){if(i<0)i=0;if(i>=s.length)i=s.length-1;cur=i;s.forEach((e,k)=>e.classList.toggle('active',k===cur));document.getElementById('bar').textContent=(cur+1)+' / '+s.length;localStorage&&localStorage.setItem('deck_cur',cur);}
function toggleNotes(){document.getElementById('notes').classList.toggle('show');}
document.addEventListener('keydown',e=>{
 if(e.key==='ArrowRight'||e.key===' '||e.key==='PageDown'){go(cur+1);e.preventDefault();}
 else if(e.key==='ArrowLeft'||e.key==='PageUp'){go(cur-1);e.preventDefault();}
 else if(e.key==='n'||e.key==='N'){toggleNotes();}
 else if(e.key==='Home'){go(0);} else if(e.key==='End'){go(s.length-1);}
});
document.getElementById('deck').addEventListener('click',()=>go(cur+1));
const saved=localStorage&&localStorage.getItem('deck_cur');go(saved?+saved:0);
"""


def esc(t):
    return html.escape(t, quote=True)


def parse_slides(md):
    lines = md.splitlines()
    slides, cur = [], []
    for ln in lines:
        if ln.strip() == "---":
            if cur:
                slides.append(cur)
                cur = []
        else:
            cur.append(ln)
    if cur:
        slides.append(cur)
    return slides


def render_slide(block, idx):
    title = subtitle = None
    bullets, quotes, notes, images, paras = [], [], [], [], []
    for ln in block:
        s = ln.rstrip()
        m = re.search(r"<!--\s*备注[:：]\s*(.*?)\s*-->", s)
        if m:
            notes.append(m.group(1))
            continue
        if s.startswith("# "):
            title = s[2:].strip()
        elif s.startswith("## "):
            subtitle = s[3:].strip()
        elif s.startswith("> "):
            quotes.append(s[2:].strip())
        elif s.startswith("- ") or s.startswith("* "):
            bullets.append(s[2:].strip())
        elif re.match(r"^\s*\[\s*图\s*[：:]", s):
            cm = re.search(r"\[\s*图\s*[：:]\s*(.*?)\s*\]", s)
            images.append(cm.group(1) if cm else "图")
        elif s.strip() == "":
            continue
        else:
            paras.append(s.strip())

    cls = "slide cover" if idx == 0 else "slide"
    parts = ['<div class="slide-inner">']
    if title:
        parts.append("<h1>%s</h1>" % esc(title))
    if subtitle:
        parts.append("<h2>%s</h2>" % esc(subtitle))
    for p in paras:
        parts.append("<p>%s</p>" % esc(p))
    if bullets:
        parts.append("<ul>" + "".join("<li>%s</li>" % esc(b) for b in bullets) + "</ul>")
    for q in quotes:
        parts.append("<blockquote>%s</blockquote>" % esc(q))
    for im in images:
        parts.append('<div class="img-ph">[ 图：%s ]</div>' % esc(im))
    parts.append("</div>")
    notes_html = (
        '<aside id="notes">📝 演讲备注：%s</aside>' % esc(" ｜ ".join(notes))
        if notes else ""
    )
    return '<section class="%s">%s</section>' % (cls, "".join(parts))


def build_html(title, slides):
    bodies = [render_slide(b, i) for i, b in enumerate(slides)]
    # notes are inside sections; move them out? keep inside, JS toggles #notes globally.
    # Simpler: collect all notes into one notes panel appended after deck.
    all_notes = []
    for b in slides:
        for ln in b:
            m = re.search(r"<!--\s*备注[:：]\s*(.*?)\s*-->", ln)
            if m:
                all_notes.append("P%d: %s" % (slides.index(b) + 1, m.group(1)))
    notes_panel = (
        '<aside id="notes">📝 演讲备注（按 n 显示/隐藏）：<br>%s</aside>'
        % esc("　".join(all_notes))
        if all_notes else '<aside id="notes"></aside>'
    )
    return """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title><style>%s</style></head>
<body><div id="deck">%s</div>%s
<div id="bar"></div><div id="hint">→ 翻页 · n 备注 · Home/End 首尾</div>
<script>%s</script></body></html>""" % (
        esc(title),
        CSS,
        "".join(bodies),
        notes_panel,
        JS,
    )


DEMO = """# 智能报价工具 · 让工厂报价从 2 小时变 5 分钟
## 面向全屋定制工厂的 AI 报价助手

---

# 报价是最大的隐形成本
- 老师傅手算一单要 2 小时，还常漏项
- 新人算错率 30%，亏了才知道
- 客户等报价等到跑单
> 报价慢 = 隐形丢单

<!-- 备注：开场用「你有没有报完价客户已经走了」反问钩子 -->

---

# 我们的解法：输入户型，输出报价
- 上传户型图，自动算投影面积与板材
- 内置你家的真实成本价，不拍脑袋
- 5 分钟出可发送报价单
[图：户型→报价的流程图]

---

# 实测：算得比人快，也不漏
- 100 单抽查：耗时 2h→5min，提速 24 倍
- 漏项率从 30% 降到 2%
- 3 家工厂在用，月省约 40 工时
[图：耗时对比柱状图]
"""


def main():
    ap = argparse.ArgumentParser(description="Markdown 大纲 → 自包含 HTML 幻灯片")
    ap.add_argument("--input", help="Markdown 大纲文件路径")
    ap.add_argument("--output", help="输出 HTML 路径（默认打印到 stdout）")
    ap.add_argument("--title", default="演示文稿", help="幻灯片标题")
    ap.add_argument("--demo", action="store_true", help="用内置示例运行（自检）")
    args = ap.parse_args()

    if args.demo:
        md = DEMO
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                md = f.read()
        except OSError as e:
            sys.stderr.write("[错误] 无法读取输入: %s\n" % e)
            return 2
    else:
        if sys.stdin.isatty():
            sys.stderr.write("[提示] 未给 --input 且非管道，使用 --demo 查看示例。\n")
            md = DEMO
        else:
            md = sys.stdin.read()

    slides = parse_slides(md)
    if not slides or all(not any(l.strip() for l in b) for b in slides):
        sys.stderr.write("[错误] 未解析到任何幻灯片，请检查大纲。\n")
        return 1

    out = build_html(args.title, slides)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        sys.stderr.write("[完成] 已生成 %d 页幻灯片 -> %s\n" % (len(slides), args.output))
    else:
        sys.stdout.write(out)
        sys.stderr.write("[完成] 已生成 %d 页幻灯片（自包含 HTML）。\n" % len(slides))
    return 0


if __name__ == "__main__":
    sys.exit(main())
