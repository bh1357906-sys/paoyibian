# 跑一遍再说 — 个人站点

纯静态站点,零依赖(生成器只用 Hermes 自带的 python-markdown)。所有文件都可以直接
双击打开,但正式发布时用下面的方式。

```
index.html        首页(文章列表)
about.html        关于
posts/*.html      三篇文章
feed.xml          RSS 订阅源
assets/           样式、头像、背景图
build.py          生成器
```

---

## 一、发布(按摩擦从低到高)

### 方案 A:Netlify Drop —— **不需要注册任何账号**

1. 打开 <https://app.netlify.com/drop>
2. 把整个 `site` 文件夹**拖进浏览器窗口**
3. 等十几秒,它会给你一个网址,形如 `https://random-name-1234.netlify.app`

**这就是线上地址了。** 不填表单、不验证身份、不用邮箱。之后想保留这个网址,
再用邮箱注册一个账号把它"认领"下来即可(可选)。

> 注意:拖的是**文件夹本身**,不是里面的单个文件。

### 方案 B:GitHub Pages —— 需要邮箱注册,不需要身份证明

```bash
cd /Users/leo/site
git init && git add -A && git commit -m "site: initial"
# 在 github.com 新建一个仓库,然后把下面的地址换成你的
git remote add origin git@github.com:<你的用户名>/<仓库名>.git
git branch -M main && git push -u origin main
```

然后仓库 → Settings → Pages → Source 选 `main` 分支的 `/ (root)`。
网址会是 `https://<你的用户名>.github.io/<仓库名>/`。

### 方案 C:Vercel

```bash
cd /Users/leo/site && npx vercel deploy --prod
```

---

## 二、部署后必做一步:改网址

`build.py` 顶部有一行:

```python
SITE_URL = "https://example.netlify.app"   # ← 换成你的真实地址
```

把 Netlify/GitHub 给你的真实网址填进去,**然后重新生成**:

```bash
~/.hermes/hermes-agent/venv/bin/python build.py
```

然后重新上传。这一步不改的话,RSS 订阅源里的链接和分享到 X 时的卡片会指向错误的地址。

---

## 三、以后怎么加新文章

1. 把新的 `.md` 放进 `/Users/leo/articles/`
2. 在 `build.py` 的 `MANIFEST` 里加一条:

```python
dict(
    slug="url-friendly-slug",
    src="your-new-article.md",
    title="文章标题",
    date="2026-10-20",
    lang="zh-Hans",        # 英文文章用 "en"
    langtag="中文",         # 英文文章用 "EN"
    summary="一两句话的摘要,会显示在首页和 RSS 里。",
),
```

3. 重新跑 `~/.hermes/hermes-agent/venv/bin/python build.py`
4. 重新上传

**文章写法要求:** 用标准 Markdown。表格用 `|` 管道语法,代码用三个反引号。
文章第一行的 `# 标题` 会被自动去掉(标题由 MANIFEST 提供),所以别指望它显示。

---

## 四、本地预览

```bash
cd /Users/leo/site && python3 -m http.server 8787
```

然后打开 <http://localhost:8787>。改完文章重新 build,刷新即可。
