# -*- coding: utf-8 -*-
"""
fetch.py — 云端抓取 v6（动态扩展，永不空转）
· 20 个种子领域，每个 1~3 个宽泛种子词
· 抓到项目后，从 topics + description 里提取新关键词，加入待搜队列
· 队列存在 search_state.json，永远不空
· 每 3 小时跑一次，每次 25 个关键词
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
# 20 个大领域种子（每个 1~3 个宽泛词，不用写细）
# ============================================================
SEEDS = [
    ("媒体处理",   "media processing"),
    ("媒体处理",   "image tool"),
    ("媒体处理",   "video tool"),
    ("软件开发",   "developer tool"),
    ("软件开发",   "software development"),
    ("文件管理",   "file management tool"),
    ("文件管理",   "file utility"),
    ("密码安全",   "security tool"),
    ("密码安全",   "cryptography"),
    ("文档办公",   "document tool"),
    ("文档办公",   "office automation"),
    ("网络通信",   "network tool"),
    ("网络通信",   "http client"),
    ("系统工具",   "system tool"),
    ("系统工具",   "system utility"),
    ("游戏娱乐",   "game tool"),
    ("游戏娱乐",   "gaming utility"),
    ("数据处理",   "data processing"),
    ("数据处理",   "data tool"),
    ("数据可视化", "data visualization"),
    ("数据可视化", "chart tool"),
    ("效率自动化", "automation tool"),
    ("效率自动化", "productivity tool"),
    ("Web 开发",   "web development"),
    ("Web 开发",   "web framework"),
    ("数据库",     "database tool"),
    ("数据库",     "sql tool"),
    ("AI 工具",    "ai tool"),
    ("AI 工具",    "machine learning"),
    ("文本处理",   "text processing"),
    ("文本处理",   "text tool"),
    ("图形绘制",   "graphics tool"),
    ("图形绘制",   "drawing tool"),
    ("硬件控制",   "hardware tool"),
    ("硬件控制",   "iot tool"),
    ("科学计算",   "scientific computing"),
    ("科学计算",   "math tool"),
    ("生活学习",   "learning tool"),
    ("生活学习",   "productivity app"),
    ("老龄照护",   "elderly care"),
    ("老龄照护",   "health tool"),
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

# 单个关键词最多扩展出的新词数量（避免爆炸）
MAX_NEW_PER_KEYWORD = 6
# 待搜队列最大长度
MAX_QUEUE_SIZE = 8000
# 已经搜过的词不再进队列（上限）
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
    headers = {"User-Agent": "PluginFetch/6.0", "Accept": "application/vnd.github+json"}
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


# 常见停用词，提取短语时跳过
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
    """从一个项目里提取新搜索词（topics + description 短语）"""
    new_kws = []

    # 1. topics 标签（GitHub 官方标签，最准）
    for t in plugin.get("topics", []):
        t = (t or "").strip().lower()
        if 3 <= len(t) <= 30 and " " not in t and t not in STOP_WORDS:
            new_kws.append(t)

    # 2. description 里提取 2~3 词短语
    desc = (plugin.get("desc") or "").lower()
    # 去掉标点，切成单词
    for ch in ",.;:!?()[]{}<>/\\|":
        desc = desc.replace(ch, " ")
    tokens = [w for w in desc.split() if len(w) >= 3 and w not in STOP_WORDS]

    # 2 词短语
    for i in range(len(tokens) - 1):
        phrase = tokens[i] + " " + tokens[i + 1]
        if 8 <= len(phrase) <= 40:
            new_kws.append(phrase)
    # 3 词短语
    for i in range(len(tokens) - 2):
        phrase = tokens[i] + " " + tokens[i + 1] + " " + tokens[i + 2]
        if 12 <= len(phrase) <= 45:
            new_kws.append(phrase)

    # 去重 + 截断
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
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            if "queue" in state and "done" in state:
                return state
        except Exception:
            pass
    # 首次运行：用种子初始化队列
    return {
        "queue": [{"keyword": kw, "label": lbl} for lbl, kw in SEEDS],
        "done": [],
    }


def save_state(state):
    # done 太多就截断
    if len(state["done"]) > MAX_DONE:
        state["done"] = state["done"][-MAX_DONE:]
    # queue 太多就截断
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

            # ⭐ 从每个项目里提取新关键词，加入队列
            for p in plugins:
                for new_kw in extract_new_keywords(p):
                    if new_kw in done:
                        continue
                    if any(q["keyword"] == new_kw for q in queue):
                        continue
                    # 继承父级 label
                    queue.append({"keyword": new_kw, "label": label})
                    new_keywords_added += 1

        except urllib.error.HTTPError as e:
            if e.code == 403:
                print(f"  ❌ 遇到限流，保存进度后退出")
                queue.insert(0, item)  # 这个词塞回队列
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
