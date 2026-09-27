# -*- coding: utf-8 -*-
"""
fetch.py — 云端抓取 v6.2（20 个宽泛种子，动态扩展，永不空转）
· 20 个大领域，每个 1 个宽泛种子词
· 抓到项目后，从 topics + description 自动提取新词，加入待搜队列
· 每 3 小时跑一次，每次 25 个关键词
· 状态全自动管理，不需要手动删任何文件
"""
import os
import sys
import json
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime

GITHUB_TOKEN = os.environ.get("GH_TOKEN", "").strip()

# ============================================================
# 20 个大领域，每个 1 个宽泛种子词
# ============================================================
SEEDS = [
    ("媒体处理",   "media"),
    ("软件开发",   "software development"),
    ("文件管理",   "file management"),
    ("密码安全",   "security"),
    ("文档办公",   "document"),
    ("网络通信",   "network"),
    ("系统工具",   "system utility"),
    ("游戏娱乐",   "game development"),
    ("数据处理",   "data processing"),
    ("数据可视化", "data visualization"),
    ("效率自动化", "automation"),
    ("Web 开发",   "web development"),
    ("数据库",     "database"),
    ("AI 工具",    "artificial intelligence"),
    ("文本处理",   "text processing"),
    ("图形绘制",   "computer graphics"),
    ("硬件控制",   "hardware"),
    ("科学计算",   "scientific computing"),
    ("生活学习",   "education"),
    ("老龄照护",   "elderly care"),
]

MIN_STARS = 100
MIN_FORKS = 10
MAX_MONTHS = 36
LICENSE_WHITELIST = ["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "MPL-2.0"]
TOP_N_PER_SUB = 5
BATCH_SIZE = 25
RATE_SLEEP = 0.5

STATE_FILE = "search_state.json"
DATA_FILE = "market_data.json"

MAX_NEW_PER_KEYWORD = 6
MAX_QUEUE_SIZE = 8000
MAX_DONE = 20000


def months_ago(iso_str):
    if not iso_str:
        return 999
    try:
        dt = datetime.strptime(iso_str[:10], "%Y-%m-%d")
        now = datetime.utcnow()
        return (now.year - dt.year) * 12 + (now.month - dt.month)
    except Exception:
        return 999


def search_keyword(keyword, token, top_n=5):
    q = f"{keyword} language:python stars:>{MIN_STARS}"
    url = (
        f"https://api.github.com/search/repositories"
        f"?q={urllib.parse.quote(q)}"
        f"&sort=stars&order=desc&per_page={top_n * 4}"
    )
    headers = {"User-Agent": "PluginFetch/6.2", "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    results = []
    for r in data.get("items", []):
        if r.get("archived") or r.get("fork"):
            continue
        stars = r.get("stargazers_count", 0)
        forks = r.get("forks_count", 0)
        if stars < MIN_STARS or forks < MIN_FORKS:
            continue
        lic = (r.get("license") or {}).get("spdx_id", "")
        if lic not in LICENSE_WHITELIST:
            continue
        if months_ago(r.get("updated_at", "")) > MAX_MONTHS:
            continue

        results.append({
            "name": r["full_name"],
            "desc": (r.get("description") or "").strip(),
            "stars": stars,
            "forks": forks,
            "license": lic,
            "url": r["html_url"],
            "updated": r.get("updated_at", ""),
            "keyword": keyword,
            "topics": r.get("topics", []) or [],
        })
        if len(results) >= top_n:
            break
    return results


STOP_WORDS = {
    "the", "and", "for", "with", "from", "that", "this", "your", "you",
    "are", "was", "were", "will", "can", "has", "have", "using", "use",
    "based", "into", "more", "than", "also", "all", "any", "simple",
    "easy", "fast", "light", "new", "open", "source", "free", "tool",
    "tools", "library", "python", "支持", "实现", "一个", "一款",
    "built", "made", "powered", "high", "low", "well", "very",
    "just", "like", "make", "makes", "made", "way", "ways",
}


def extract_new_keywords(plugin):
    new_kws = []
    for t in plugin.get("topics", []):
        t = (t or "").strip().lower()
        if 3 <= len(t) <= 30 and " " not in t and t not in STOP_WORDS:
            new_kws.append(t)

    desc = (plugin.get("desc") or "").lower()
    for ch in ",.;:!?()[]{}<>/\\|":
        desc = desc.replace(ch, " ")
    tokens = [w for w in desc.split() if len(w) >= 3 and w not in STOP_WORDS]

    for i in range(len(tokens) - 1):
        phrase = tokens[i] + " " + tokens[i + 1]
        if 8 <= len(phrase) <= 40:
            new_kws.append(phrase)
    for i in range(len(tokens) - 2):
        phrase = tokens[i] + " " + tokens[i + 1] + " " + tokens[i + 2]
        if 12 <= len(phrase) <= 45:
            new_kws.append(phrase)

    seen = set()
    out = []
    for k in new_kws:
        if k not in seen:
            seen.add(k)
            out.append(k)
        if len(out) >= MAX_NEW_PER_KEYWORD:
            break
    return out


def load_state():
    """自动检测旧格式，旧格式自动重建，不需要手动删"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            if isinstance(state, dict) and "queue" in state and "done" in state:
                return state
            print("检测到旧格式 search_state.json，自动重建为新格式")
        except Exception:
            print("search_state.json 损坏，自动重建")
    return {
        "queue": [{"keyword": kw, "label": lbl} for lbl, kw in SEEDS],
        "done": [],
    }


def save_state(state):
    if len(state["done"]) > MAX_DONE:
        state["done"] = state["done"][-MAX_DONE:]
    if len(state["queue"]) > MAX_QUEUE_SIZE:
        state["queue"] = state["queue"][:MAX_QUEUE_SIZE]
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_market():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"categories": [], "updated": ""}


def save_market(market):
    market["updated"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(market, f, ensure_ascii=False, indent=2)


def merge_into_market(market, cat_label, sub_label, plugins):
    cat_obj = None
    for c in market["categories"]:
        if c["label"] == cat_label:
            cat_obj = c
            break
    if cat_obj is None:
        cat_obj = {"label": cat_label, "count": 0, "plugins": []}
        market["categories"].append(cat_obj)

    existing_urls = {p["url"] for p in cat_obj["plugins"]}
    added = 0
    for p in plugins:
        if p["url"] in existing_urls:
            continue
        p["sub_label"] = sub_label
        p["cat_label"] = cat_label
        cat_obj["plugins"].append(p)
        existing_urls.add(p["url"])
        added += 1
    cat_obj["count"] = len(cat_obj["plugins"])
    return added


def main():
    token = GITHUB_TOKEN
    state = load_state()
    market = load_market()
    done = set(state["done"])
    queue = state["queue"]

    print(f"待搜队列：{len(queue)} 个关键词")
    print(f"已搜过：{len(done)} 个")
    print("  ✅ Token 已就绪" if token else "  ⚠️ 没有 Token")

    processed = 0
    new_added = 0
    new_keywords_added = 0

    while queue and processed < BATCH_SIZE:
        item = queue.pop(0)
        kw = item["keyword"]
        label = item["label"]

        if kw in done:
            continue
        done.add(kw)
        processed += 1

        try:
            plugins = search_keyword(kw, token, TOP_N_PER_SUB)
            n = merge_into_market(market, label, label, plugins)
            new_added += n
            print(f"  [{processed}/{BATCH_SIZE}] {label} · {kw} → {len(plugins)} 个（新增 {n}）")

            for p in plugins:
                for new_kw in extract_new_keywords(p):
                    if new_kw in done:
                        continue
                    if any(q["keyword"] == new_kw for q in queue):
                        continue
                    queue.append({"keyword": new_kw, "label": label})
                    new_keywords_added += 1

        except urllib.error.HTTPError as e:
            if e.code == 403:
                print(f"  ❌ 遇到限流，保存进度后退出")
                queue.insert(0, item)
                break
            print(f"  ❌ {kw} → HTTP {e.code}")
        except Exception as e:
            print(f"  ❌ {kw} → {type(e).__name__}: {e}")

        time.sleep(RATE_SLEEP)

    state["queue"] = queue
    state["done"] = list(done)

    save_state(state)
    save_market(market)
    print("=" * 60)
    print(f"本轮完成：搜了 {processed} 个词，新增项目 {new_added} 条，")
    print(f"新词进队 {new_keywords_added} 个，队列剩余 {len(queue)} 个")


if __name__ == "__main__":
    main()
