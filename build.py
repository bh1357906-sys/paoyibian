#!/usr/bin/env python3
"""Static site generator — no dependencies beyond python-markdown.

Usage:  ~/.hermes/hermes-agent/venv/bin/python build.py
Output: ./index.html, ./about.html, ./posts/*.html, ./feed.xml
"""
import html
import pathlib
import re
import shutil
from datetime import datetime, timezone

import markdown

ROOT = pathlib.Path(__file__).parent
ARTICLES = pathlib.Path("/Users/leo/articles")
POSTS = ROOT / "posts"
ASSETS = ROOT / "assets"

SITE_NAME = "跑一遍再说"
SITE_TAGLINE = "不转述官方博客。每个结论背后都有一张自己跑出来的表。"
SITE_DESC = "大模型 API 实测 · agent 工具链 · 价格与真实成本"
SITE_URL = "https://bh1357906-sys.github.io/paoyibian"  # 部署后如有自定义域名,改这里

# slug -> (source file, title, date, lang, summary)
MANIFEST = [
    dict(
        slug="deepseek-silent-downgrade-en",
        src="deepseek-silent-downgrade-EN.md",
        title="DeepSeek silently serves you a different model than the one you asked for",
        date="2026-10-16",
        lang="en",
        langtag="EN",
        summary="I asked for deepseek-reasoner. The API ran deepseek-flash and returned HTTP 200. Two layers of silent substitution, both invisible by default — and the only place the truth appears is a response field almost nobody reads.",
    ),
    dict(
        slug="us-treasury-etf-withholding-tax",
        src="us-treasury-etf-withholding-tax.md",
        title="美国国债 4%，为什么到你手上只剩 2.6%",
        date="2026-10-16",
        lang="zh-Hans",
        langtag="中文",
        summary="国债利息在美国税法下有免预扣的豁免，但这个豁免在你把国债装进 ETF 的那一刻就失效了。SGOV 这类产品的收益几乎 100% 来自分红——而那恰好是唯一会被扣税的部分。附自查方法。",
    ),
    dict(
        slug="deepseek-silent-downgrade",
        src="deepseek-silent-downgrade.md",
        title="你的配置写着 deepseek-reasoner，实际跑的是 flash —— 而且没有任何地方会报错",
        date="2026-10-15",
        lang="zh-Hans",
        langtag="中文",
        summary="服务端和客户端各有一层静默替换。你写的模型名和真正执行的模型名，可以在你完全不知情的情况下分道扬镳。附自查方法。",
    ),
    dict(
        slug="deepseek-v4pro-vs-flash",
        src="deepseek-v4pro-vs-flash.md",
        title="DeepSeek v4-pro 比 flash 贵 3 倍，但多花的钱买的不是「能力」",
        date="2026-10-13",
        lang="zh-Hans",
        langtag="中文",
        summary="同一道题跑两个模型：答案质量没有区别，耗时差 2.2 倍，花费差 2.4 倍。而 v4-pro 开到 high 推理档时，会把预算全部烧在思考上，一个字都不回答。",
    ),
    dict(
        slug="deepseek-v4pro-vs-flash-en",
        src="deepseek-v4pro-vs-flash-EN.md",
        title="DeepSeek v4-pro costs 3× more than Flash. You're not paying for intelligence.",
        date="2026-10-13",
        lang="en",
        langtag="EN",
        summary="Same prompt, both models, same effort. Equivalent answers. 2.2× the time, 2.4× the cost. And at high effort, v4-pro burns its whole budget on reasoning and returns nothing.",
    ),
]

MD_EXT = ["tables", "fenced_code", "sane_lists", "attr_list", "md_in_html"]


def md_to_html(text: str) -> str:
    return markdown.markdown(text, extensions=MD_EXT)


PAGE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="{ogtype}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{site}/assets/banner-1200x400.png">
<meta property="og:site_name" content="{sitename}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="{root}assets/style.css">
<link rel="alternate" type="application/rss+xml" title="{sitename}" href="{site}/feed.xml">
<link rel="icon" href="{root}assets/avatar-512.png">
</head>
<body>
<header class="site">
  <a class="brand" href="{root}index.html">{sitename}</a>
  <nav>
    <a href="{root}index.html">文章</a>
    <a href="{root}about.html">关于</a>
    <a href="{site}/feed.xml">RSS</a>
  </nav>
</header>
<main>
{body}
</main>
<footer>
  <p>{site_desc} · <a href="{site}/feed.xml">RSS 订阅</a></p>
  <p class="dim">© {year} {sitename}</p>
</footer>
</body>
</html>
"""


def page(*, title, desc, body, lang="zh-Hans", ogtype="website", root=""):
    return PAGE.format(
        title=html.escape(title), desc=html.escape(desc), body=body, lang=lang,
        ogtype=ogtype, root=root, site=SITE_URL, sitename=SITE_NAME,
        site_desc=SITE_DESC, year=datetime.now(timezone.utc).year,
    )


def strip_h1(md_text: str):
    lines = md_text.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith("# "):
            return "\n".join(lines[i + 1:]).lstrip("\n")
    return md_text


def build():
    POSTS.mkdir(exist_ok=True)
    ASSETS.mkdir(exist_ok=True)
    for f in ("avatar-512.png", "banner-1200x400.png"):
        src = ARTICLES / f
        if src.exists():
            shutil.copy(src, ASSETS / f)

    built = []
    for a in MANIFEST:
        raw = (ARTICLES / a["src"]).read_text(encoding="utf-8")
        body_md = strip_h1(raw)
        body_html = md_to_html(body_md)
        dt = datetime.strptime(a["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        article = f"""<article>
<h1>{html.escape(a['title'])}</h1>
<p class="meta"><time datetime="{a['date']}">{dt.strftime('%Y年%m月%d日') if a['lang'].startswith('zh') else dt.strftime('%d %b %Y')}</time> · {a['langtag']}</p>
{body_html}
</article>
<p class="back"><a href="../index.html">← 回到文章列表</a></p>"""
        out = POSTS / f"{a['slug']}.html"
        out.write_text(
            page(title=f"{a['title']} — {SITE_NAME}", desc=a["summary"],
                 body=article, lang=a["lang"], ogtype="article", root="../"),
            encoding="utf-8",
        )
        built.append((a, dt))
        print(f"  ✓ posts/{out.name}")

    # ---- index ----
    cards = []
    for a, dt in sorted(built, key=lambda t: t[1], reverse=True):
        date_str = dt.strftime("%Y-%m-%d")
        cards.append(f"""<li class="card">
  <p class="meta"><time datetime="{a['date']}">{date_str}</time> · {a['langtag']}</p>
  <h2><a href="posts/{a['slug']}.html">{html.escape(a['title'])}</a></h2>
  <p class="summary">{html.escape(a['summary'])}</p>
</li>""")
    index_body = f"""<section class="intro">
<h1>{SITE_NAME}</h1>
<p class="lede">{SITE_TAGLINE}</p>
<p class="dim">{SITE_DESC}</p>
</section>
<ul class="cards">
{chr(10).join(cards)}
</ul>"""
    (ROOT / "index.html").write_text(
        page(title=f"{SITE_NAME} — {SITE_DESC}", desc=SITE_DESC, body=index_body),
        encoding="utf-8")
    print("  ✓ index.html")

    # ---- about ----
    about_body = f"""<article class="about">
<h1>关于</h1>
<p class="lede">{SITE_TAGLINE}</p>
<p>{SITE_DESC}。</p>
<p>我只写自己真上手跑过的东西。每个数字、每张表，都来自实际调用、实际日志或实际账单 ——
不转述官方博客，不搬运别人的结论。如果某件事我没测，我会直接说没测。</p>
<h2>为什么</h2>
<p>因为大部分技术内容是在转述。而转述会丢东西：模型被静默换掉、价格快照过期、
连写兼容代码的人对现状的判断都可能已经不准。这些问题只有在真的跑一遍之后才会出现。</p>
<p>所以这里的东西通常长这样：先给结果，再给方法，最后给局限 —— 包括对我自己不利的那部分。</p>
<h2>联系</h2>
<p>如果你有具体的问题，或者想找我做点什么，欢迎来
<a href="https://x.com/">X</a> 上找我。公开的提问比私信更容易被我看到。</p>
</article>"""
    (ROOT / "about.html").write_text(
        page(title=f"关于 — {SITE_NAME}", desc=SITE_TAGLINE, body=about_body),
        encoding="utf-8")
    print("  ✓ about.html")

    # ---- rss ----
    items = []
    for a, dt in sorted(built, key=lambda t: t[1], reverse=True):
        url = f"{SITE_URL}/posts/{a['slug']}.html"
        body_html = md_to_html(strip_h1((ARTICLES / a["src"]).read_text(encoding="utf-8")))
        items.append(f"""  <item>
    <title>{html.escape(a['title'])}</title>
    <link>{url}</link>
    <guid isPermaLink="true">{url}</guid>
    <pubDate>{dt.strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
    <description>{html.escape(a['summary'])}</description>
    <content:encoded><![CDATA[{body_html}]]></content:encoded>
  </item>""")
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">
<channel>
  <title>{SITE_NAME}</title>
  <link>{SITE_URL}</link>
  <description>{SITE_DESC}</description>
  <language>zh-cn</language>
  <lastBuildDate>{datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')}</lastBuildDate>
{chr(10).join(items)}
</channel>
</rss>
"""
    (ROOT / "feed.xml").write_text(feed, encoding="utf-8")
    print("  ✓ feed.xml")


if __name__ == "__main__":
    print("building...")
    build()
    print("done.")
