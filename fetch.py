# -*- coding: utf-8 -*-
"""
fetch.py — 抓取（20 个粗领域，每个领域 10~15 个细分龙头）
云端 GitHub Actions 每天自动跑，本地不用跑
"""
import os
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime


# 云端不填，GitHub Actions 自带 token
# 本地跑的话，可以填上你的 ghp_xxx
GITHUB_TOKEN = ""


# ============================================================
# 20 个粗领域，每个领域下 10~15 个细分关键词
# ============================================================
CATEGORIES = [
    {
        "label": "媒体处理",
        "keywords": [
            "image compression", "image watermark", "image format convert",
            "background removal", "image ocr", "image enhancement",
            "batch image", "video converter", "video compression",
            "video editing", "subtitle editor", "screen recorder",
            "audio extraction", "speech to text", "text to speech",
        ],
    },
    {
        "label": "软件开发",
        "keywords": [
            "code formatter", "linter", "api testing", "git tool",
            "dependency manager", "documentation gen", "debugger",
            "profiler", "static analysis", "unit test",
            "refactor tool", "code search",
        ],
    },
    {
        "label": "文件管理",
        "keywords": [
            "file rename", "file deduplication", "file sync",
            "disk usage", "file search", "backup tool",
            "file compare", "archive tool", "file hash",
            "duplicate finder", "file organizer",
        ],
    },
    {
        "label": "密码安全",
        "keywords": [
            "password manager", "password generator", "file encryption",
            "hash checker", "ssl certificate", "two factor auth",
            "secure delete", "port scanner", "cryptography library",
        ],
    },
    {
        "label": "文档办公",
        "keywords": [
            "pdf merger", "pdf splitter", "docx reader",
            "excel reader", "markdown editor", "ebook converter",
            "office automation", "document compare", "document scanner",
            "office converter",
        ],
    },
    {
        "label": "网络通信",
        "keywords": [
            "web scraper", "http client", "email sender",
            "ssh client", "ftp client", "websocket",
            "network scanner", "ping tool", "dns lookup",
            "proxy server", "rss reader",
        ],
    },
    {
        "label": "系统工具",
        "keywords": [
            "system monitor", "process manager", "clipboard manager",
            "screen capture", "task scheduler", "window manager",
            "hotkey tool", "system info", "hardware monitor",
            "battery monitor", "startup manager",
        ],
    },
    {
        "label": "游戏娱乐",
        "keywords": [
            "game save manager", "game trainer", "game automation",
            "minecraft mod", "steam library", "game launcher",
            "achievement tracker", "mod manager", "game tools",
        ],
    },
    {
        "label": "数据处理",
        "keywords": [
            "csv reader", "excel writer", "json parser",
            "xml parser", "data cleaner", "data converter",
            "data validation", "yaml parser", "sql parser",
            "data merge",
        ],
    },
    {
        "label": "数据可视化",
        "keywords": [
            "chart generator", "plotting library", "dashboard",
            "network graph", "heatmap", "3d visualization",
            "bar chart", "scatter plot", "interactive chart",
            "gantt chart",
        ],
    },
    {
        "label": "效率自动化",
        "keywords": [
            "keyboard automation", "mouse automation", "batch processing",
            "workflow automation", "auto clicker", "text expander",
            "gui automation", "macro recorder", "hotkey manager",
            "auto backup",
        ],
    },
    {
        "label": "Web 开发",
        "keywords": [
            "web framework", "api framework", "html parser",
            "web testing", "static site gen", "template engine",
            "web server", "graphql", "rest api", "url parser",
        ],
    },
    {
        "label": "数据库",
        "keywords": [
            "sqlite tool", "mysql client", "postgresql client",
            "mongodb client", "redis client", "orm library",
            "database migration", "query builder", "database backup",
            "database admin",
        ],
    },
    {
        "label": "AI 工具",
        "keywords": [
            "llm api", "prompt tool", "embedding",
            "image recognition", "speech recognition", "object detection",
            "face recognition", "chat bot", "machine learning",
            "deep learning", "model training", "ai assistant",
        ],
    },
    {
        "label": "文本处理",
        "keywords": [
            "text diff", "text translate", "text tokenizer",
            "regex tool", "text statistics", "text formatting",
            "text search", "text replace", "spell checker",
            "grammar check",
        ],
    },
    {
        "label": "图形绘制",
        "keywords": [
            "vector graphics", "svg tool", "flowchart",
            "diagram generator", "drawing library", "image annotation",
            "mind mapping", "uml tool", "canvas drawing", "graphviz",
        ],
    },
    {
        "label": "硬件控制",
        "keywords": [
            "usb device", "serial port", "bluetooth",
            "gpio control", "camera control", "printer control",
            "arduino", "raspberry pi", "sensor library",
            "game controller",
        ],
    },
    {
        "label": "科学计算",
        "keywords": [
            "numpy alternative", "symbolic math", "statistics",
            "physics sim", "data analysis", "linear algebra",
            "optimization", "numerical method", "signal processing",
            "scientific plot",
        ],
    },
    {
        "label": "生活学习",
        "keywords": [
            "todo list", "flashcard", "pomodoro",
            "weather", "personal finance", "language learning",
            "calendar", "habit tracker", "note taking",
            "bookmark manager",
        ],
    },
    {
        "label": "老龄照护",
        "keywords": [
            "medication reminder", "health monitoring", "fall detection",
            "elderly care", "cognitive training", "emergency call",
            "accessibility tool", "voice assistant", "blood pressure",
            "senior fitness",
        ],
    },
]


MIN_STARS = 300
MIN_FORKS = 30
MAX_MONTHS = 30
LICENSE_WHITELIST = ["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause"]


def months_ago(iso_str):
    if not iso_str:
        return 999
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return (datetime.now(dt.tzinfo) - dt).days / 30
    except Exception:
        return 999


def search_keyword(keyword, token):
    """搜一个关键词，返回 stars 最高的那个符合白名单的项目"""
    q = f"{keyword} language:python stars:>{MIN_STARS}"
    url = (
        f"https://api.github.com/search/repositories"
        f"?q={urllib.parse.quote(q)}"
        f"&sort=stars&order=desc&per_page=5"
    )
    headers = {
        "User-Agent": "PluginFetch/2.0",
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    for r in data.get("items", []):
        if r.get("archived") or r.get("fork"):
            continue
        lic = (r.get("license") or {}).get("spdx_id", "无") or "无"
        if lic not in LICENSE_WHITELIST:
            continue
        forks = r.get("forks_count", 0)
        if forks < MIN_FORKS:
            continue
        if months_ago(r.get("updated_at", "")) > MAX_MONTHS:
            continue

        pip_name = r["name"].lower().replace("-", "_").replace(".", "_")
        return {
            "name": r["full_name"],
            "pip_name": pip_name,
            "desc": (r.get("description") or "").strip(),
            "stars": r["stargazers_count"],
            "forks": forks,
            "license": lic,
            "url": r["html_url"],
            "updated": r.get("updated_at", ""),
            "keyword": keyword,
        }
    return None


def main():
    token = GITHUB_TOKEN.strip() or os.environ.get("GITHUB_TOKEN", "").strip()

    print("=" * 60)
    if token:
        print("  ✅ Token 已就绪")
    else:
        print("  ⚠️ 没有 Token，速率限制严")
    print("=" * 60)
    print()

    out = {
        "last_updated": datetime.now().isoformat(),
        "categories": [],
    }

    for i, cat in enumerate(CATEGORIES):
        print(f"[{i+1}/{len(CATEGORIES)}] {cat['label']}")
        plugins = []
        for kw in cat["keywords"]:
            try:
                result = search_keyword(kw, token)
                if result:
                    plugins.append(result)
                    print(f"    ✅ {kw} → {result['name']} (⭐{result['stars']})")
                else:
                    print(f"    ⚪ {kw} → 无符合项目")
            except urllib.error.HTTPError as e:
                if e.code == 403:
                    print(f"    ❌ {kw} → 速率限制，保存已有数据")
                    out["categories"].append({
                        "label": cat["label"],
                        "keywords": cat["keywords"],
                        "count": len(plugins),
                        "plugins": plugins,
                    })
                    save_and_exit(out)
                    return
                else:
                    print(f"    ❌ {kw} → HTTP {e.code}")
            except Exception as e:
                print(f"    ❌ {kw} → {type(e).__name__}: {e}")

            time.sleep(0.5)

        out["categories"].append({
            "label": cat["label"],
            "keywords": cat["keywords"],
            "count": len(plugins),
            "plugins": plugins,
        })

    save_and_exit(out)


def save_and_exit(out):
    with open("market_data.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    total = sum(c.get("count", 0) for c in out["categories"])
    print()
    print("=" * 60)
    print(f"  ✅ 抓取完成！共 {total} 个项目")
    print(f"  💾 已保存到 market_data.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
