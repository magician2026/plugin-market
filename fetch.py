import os
import json
import time
import requests

GITHUB_TOKEN = os.environ.get("GH_TOKEN", "").strip()
HEADERS = {"Accept": "application/vnd.github+json"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

# ========== 关键词库 ==========
KEYWORDS = [
    # 把你原来的 280 个关键词都贴在这里
    "media processing", "video editor", "image compressor",
    "audio converter", "pdf tool", "file manager",
    # ... 剩下的全部
]

STATE_FILE = "search_state.json"
DATA_FILE = "market_data.json"
BATCH_SIZE = 25          # 每次抓 25 个关键词
RATE_SLEEP = 2.0         # 每个关键词之间停 2 秒

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"done": [], "last_index": 0}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_market():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"items": [], "updated": ""}

def search_repos(keyword):
    url = "https://api.github.com/search/repositories"
    params = {"q": keyword, "sort": "stars", "order": "desc", "per_page": 10}
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if r.status_code == 403:
            print(f"[限流] {keyword} — 停一会")
            time.sleep(60)
            return None
        if r.status_code != 200:
            print(f"[失败] {keyword} — {r.status_code}")
            return []
        return r.json().get("items", [])
    except Exception as e:
        print(f"[异常] {keyword} — {e}")
        return []

def main():
    state = load_state()
    market = load_market()
    start = state["last_index"]
    end = min(start + BATCH_SIZE, len(KEYWORDS))

    print(f"本轮抓取：索引 {start} ~ {end-1}，共 {end-start} 个")

    new_items = []
    for i in range(start, end):
        kw = KEYWORDS[i]
        if kw in state["done"]:
            continue
        print(f"[{i+1}/{len(KEYWORDS)}] 搜索：{kw}")
        items = search_repos(kw)
        if items is None:
            break
        for item in items:
            new_items.append({
                "name": item.get("full_name", ""),
                "stars": item.get("stargazers_count", 0),
                "desc": item.get("description") or "",
                "url": item.get("html_url", ""),
                "keyword": kw,
            })
        state["done"].append(kw)
        time.sleep(RATE_SLEEP)

    state["last_index"] = end
    if state["last_index"] >= len(KEYWORDS):
        state["last_index"] = 0
        state["done"] = []

    market["items"].extend(new_items)
    market["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")

    save_state(state)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(market, f, ensure_ascii=False, indent=2)

    print(f"完成。本轮新增 {len(new_items)} 条，累计 {len(market['items'])} 条")

if __name__ == "__main__":
    main()
