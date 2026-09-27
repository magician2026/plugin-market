# -*- coding: utf-8 -*-
"""
fetch.py — 云端抓取脚本 v3
· 20 个大领域
· 每个大领域 10~25 个细分关键词
· 每个细分关键词取 Top 5
· 云端不翻译，翻译留给本地
"""
import os
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime


GITHUB_TOKEN = os.environ.get("GH_TOKEN", "").strip()   # 云端不需要填，GitHub Actions 自带


# ============================================================
# 20 个大领域，每个大领域下细分关键词
# 格式：("英文关键词", "中文标签")
# ============================================================
CATEGORIES = [
    {
        "label": "媒体处理",
        "subs": [
            ("image compression", "图片压缩"),
            ("image watermark", "图片水印"),
            ("image format convert", "图片格式转换"),
            ("background removal", "抠图去背景"),
            ("image ocr", "图片文字识别"),
            ("image enhancement", "图片增强修复"),
            ("image stitching", "图片拼接"),
            ("image annotation", "图片标注"),
            ("batch image", "批量图片处理"),
            ("video converter", "视频转码"),
            ("video compression", "视频压缩"),
            ("video editing", "视频剪辑"),
            ("video downloader", "视频下载"),
            ("subtitle editor", "字幕编辑"),
            ("screen recorder", "录屏"),
            ("video to gif", "视频转GIF"),
            ("audio extraction", "音频提取"),
            ("audio converter", "音频转码"),
            ("audio denoise", "音频降噪"),
            ("speech to text", "语音转文字"),
            ("text to speech", "文字转语音"),
            ("photo library", "照片库管理"),
        ],
    },
    {
        "label": "软件开发",
        "subs": [
            ("code formatter", "代码格式化"),
            ("linter", "代码检查"),
            ("api testing", "API 测试"),
            ("git tool", "Git 工具"),
            ("dependency manager", "依赖管理"),
            ("documentation gen", "文档生成"),
            ("code editor", "代码编辑器"),
            ("debugger", "调试器"),
            ("profiler", "性能分析"),
            ("static analysis", "静态分析"),
            ("code coverage", "代码覆盖率"),
            ("package manager", "包管理"),
            ("build tool", "构建工具"),
            ("unit test", "单元测试"),
            ("refactor tool", "重构工具"),
            ("code search", "代码搜索"),
            ("syntax highlight", "语法高亮"),
        ],
    },
    {
        "label": "文件管理",
        "subs": [
            ("file rename", "批量重命名"),
            ("file deduplication", "文件去重"),
            ("file sync", "文件同步"),
            ("disk usage", "磁盘分析"),
            ("file search", "文件搜索"),
            ("backup tool", "备份工具"),
            ("file compare", "文件对比"),
            ("file split", "文件分割"),
            ("file merge", "文件合并"),
            ("archive tool", "压缩归档"),
            ("file hash", "文件指纹"),
            ("file metadata", "文件元数据"),
            ("folder sync", "文件夹同步"),
            ("duplicate finder", "重复查找"),
            ("file organizer", "文件整理"),
        ],
    },
    {
        "label": "密码安全",
        "subs": [
            ("password manager", "密码管理"),
            ("password generator", "密码生成"),
            ("file encryption", "文件加密"),
            ("hash checker", "哈希校验"),
            ("ssl certificate", "SSL 证书"),
            ("two factor auth", "双因素认证"),
            ("vpn client", "VPN 客户端"),
            ("key derivation", "密钥派生"),
            ("secure delete", "安全删除"),
            ("steganography", "隐写术"),
            ("port scanner", "端口扫描"),
            ("packet sniff", "抓包工具"),
            ("vulnerability scan", "漏洞扫描"),
            ("penetration test", "渗透测试"),
            ("cryptography library", "加密库"),
        ],
    },
    {
        "label": "文档办公",
        "subs": [
            ("pdf merger", "PDF 合并"),
            ("pdf splitter", "PDF 拆分"),
            ("pdf annotation", "PDF 批注"),
            ("docx reader", "Word 读取"),
            ("excel reader", "Excel 读取"),
            ("powerpoint tool", "PPT 工具"),
            ("markdown editor", "Markdown 编辑"),
            ("ebook converter", "电子书转换"),
            ("ebook reader", "电子书阅读"),
            ("office automation", "办公自动化"),
            ("document compare", "文档对比"),
            ("document scanner", "文档扫描"),
            ("text extraction", "文本提取"),
            ("office converter", "Office 转换"),
            ("spreadsheet tool", "表格工具"),
        ],
    },
    {
        "label": "网络通信",
        "subs": [
            ("web scraper", "网页爬虫"),
            ("http client", "HTTP 客户端"),
            ("email sender", "邮件发送"),
            ("ssh client", "SSH 客户端"),
            ("ftp client", "FTP 客户端"),
            ("websocket", "WebSocket"),
            ("network scanner", "网络扫描"),
            ("ping tool", "Ping 工具"),
            ("dns lookup", "DNS 查询"),
            ("proxy server", "代理服务器"),
            ("api client", "API 客户端"),
            ("webhook", "Webhook"),
            ("chat bot", "聊天机器人"),
            ("notification", "通知推送"),
            ("rss reader", "RSS 阅读"),
        ],
    },
    {
        "label": "系统工具",
        "subs": [
            ("system monitor", "系统监控"),
            ("process manager", "进程管理"),
            ("clipboard manager", "剪贴板"),
            ("screen capture", "截图"),
            ("task scheduler", "定时任务"),
            ("window manager", "窗口管理"),
            ("hotkey tool", "快捷键"),
            ("system tray", "系统托盘"),
            ("system info", "系统信息"),
            ("hardware monitor", "硬件监控"),
            ("battery monitor", "电池监控"),
            ("startup manager", "启动管理"),
            ("registry tool", "注册表工具"),
            ("driver tool", "驱动工具"),
            ("usb tool", "USB 工具"),
        ],
    },
    {
        "label": "游戏娱乐",
        "subs": [
            ("game save manager", "游戏存档"),
            ("game trainer", "游戏修改器"),
            ("game automation", "游戏自动化"),
            ("minecraft mod", "我的世界模组"),
            ("steam library", "Steam 库"),
            ("game emulator", "模拟器"),
            ("game bot", "游戏机器人"),
            ("game launcher", "游戏启动器"),
            ("game config", "游戏配置"),
            ("achievement tracker", "成就追踪"),
            ("game stats", "游戏统计"),
            ("mod manager", "模组管理"),
            ("game patch", "游戏补丁"),
            ("game server", "游戏服务器"),
            ("game tools", "游戏工具"),
        ],
    },
    {
        "label": "数据处理",
        "subs": [
            ("csv reader", "CSV 读取"),
            ("excel writer", "Excel 写入"),
            ("json parser", "JSON 解析"),
            ("xml parser", "XML 解析"),
            ("data cleaner", "数据清洗"),
            ("data converter", "数据转换"),
            ("data validation", "数据校验"),
            ("data pipeline", "数据管道"),
            ("etl tool", "ETL 工具"),
            ("data generator", "数据生成"),
            ("data masking", "数据脱敏"),
            ("yaml parser", "YAML 解析"),
            ("ini parser", "INI 解析"),
            ("sql parser", "SQL 解析"),
            ("data merge", "数据合并"),
        ],
    },
    {
        "label": "数据可视化",
        "subs": [
            ("chart generator", "图表生成"),
            ("plotting library", "绘图库"),
            ("dashboard", "仪表盘"),
            ("network graph", "网络图"),
            ("heatmap", "热力图"),
            ("3d visualization", "3D 可视化"),
            ("data plot", "数据绘图"),
            ("bar chart", "柱状图"),
            ("pie chart", "饼图"),
            ("scatter plot", "散点图"),
            ("interactive chart", "交互式图表"),
            ("gantt chart", "甘特图"),
        ],
    },
    {
        "label": "效率自动化",
        "subs": [
            ("keyboard automation", "键盘自动化"),
            ("mouse automation", "鼠标自动化"),
            ("batch processing", "批量处理"),
            ("workflow automation", "工作流"),
            ("auto clicker", "自动点击"),
            ("text expander", "文本扩展"),
            ("gui automation", "GUI 自动化"),
            ("macro recorder", "宏录制"),
            ("hotkey manager", "热键管理"),
            ("clipboard tool", "剪贴板增强"),
            ("auto fill", "自动填充"),
            ("auto save", "自动保存"),
            ("auto backup", "自动备份"),
            ("form filler", "表单填写"),
            ("task automation", "任务自动化"),
        ],
    },
    {
        "label": "Web 开发",
        "subs": [
            ("web framework", "Web 框架"),
            ("api framework", "API 框架"),
            ("html parser", "HTML 解析"),
            ("css parser", "CSS 解析"),
            ("web testing", "网页测试"),
            ("static site gen", "静态站点生成"),
            ("template engine", "模板引擎"),
            ("web server", "Web 服务器"),
            ("web socket", "WebSocket"),
            ("graphql", "GraphQL"),
            ("rest api", "REST API"),
            ("web browser", "浏览器"),
            ("web crawler", "网页爬虫"),
            ("url parser", "URL 解析"),
            ("http server", "HTTP 服务器"),
        ],
    },
    {
        "label": "数据库",
        "subs": [
            ("sqlite tool", "SQLite 工具"),
            ("mysql client", "MySQL 客户端"),
            ("postgresql client", "PostgreSQL 客户端"),
            ("mongodb client", "MongoDB 客户端"),
            ("redis client", "Redis 客户端"),
            ("orm library", "ORM 库"),
            ("database migration", "数据库迁移"),
            ("query builder", "查询构建"),
            ("database backup", "数据库备份"),
            ("database admin", "数据库管理"),
            ("nosql database", "NoSQL 数据库"),
            ("database schema", "数据库架构"),
        ],
    },
    {
        "label": "AI 工具",
        "subs": [
            ("llm api", "LLM 调用"),
            ("prompt tool", "提示词工具"),
            ("embedding", "向量嵌入"),
            ("image recognition", "图像识别"),
            ("speech recognition", "语音识别"),
            ("text to speech", "语音合成"),
            ("object detection", "目标检测"),
            ("face recognition", "人脸识别"),
            ("chat bot", "聊天机器人"),
            ("machine learning", "机器学习"),
            ("deep learning", "深度学习"),
            ("neural network", "神经网络"),
            ("dataset tool", "数据集工具"),
            ("model training", "模型训练"),
            ("ai assistant", "AI 助手"),
        ],
    },
    {
        "label": "文本处理",
        "subs": [
            ("text diff", "文本对比"),
            ("text translate", "文本翻译"),
            ("text tokenizer", "分词"),
            ("regex tool", "正则工具"),
            ("text statistics", "文本统计"),
            ("text formatting", "文本格式化"),
            ("text search", "文本搜索"),
            ("text replace", "文本替换"),
            ("text encryption", "文本加密"),
            ("text to markdown", "转 Markdown"),
            ("spell checker", "拼写检查"),
            ("grammar check", "语法检查"),
        ],
    },
    {
        "label": "图形绘制",
        "subs": [
            ("vector graphics", "矢量图"),
            ("svg tool", "SVG 工具"),
            ("flowchart", "流程图"),
            ("diagram generator", "图表生成"),
            ("drawing library", "绘图库"),
            ("image annotation", "图像标注"),
            ("mind mapping", "思维导图"),
            ("uml tool", "UML 工具"),
            ("canvas drawing", "画布绘图"),
            ("graphviz", "Graphviz"),
        ],
    },
    {
        "label": "硬件控制",
        "subs": [
            ("usb device", "USB 设备"),
            ("serial port", "串口"),
            ("bluetooth", "蓝牙"),
            ("gpio control", "GPIO 控制"),
            ("camera control", "摄像头控制"),
            ("printer control", "打印机控制"),
            ("arduino", "Arduino"),
            ("raspberry pi", "树莓派"),
            ("sensor library", "传感器库"),
            ("game controller", "手柄控制"),
        ],
    },
    {
        "label": "科学计算",
        "subs": [
            ("numpy alternative", "数值计算"),
            ("symbolic math", "符号数学"),
            ("statistics", "统计"),
            ("physics sim", "物理仿真"),
            ("data analysis", "数据分析"),
            ("linear algebra", "线性代数"),
            ("optimization", "优化算法"),
            ("numerical method", "数值方法"),
            ("signal processing", "信号处理"),
            ("scientific plot", "科学绘图"),
        ],
    },
    {
        "label": "生活学习",
        "subs": [
            ("todo list", "待办"),
            ("flashcard", "闪卡"),
            ("pomodoro", "番茄钟"),
            ("weather", "天气"),
            ("personal finance", "记账"),
            ("language learning", "语言学习"),
            ("calendar", "日历"),
            ("habit tracker", "习惯追踪"),
            ("note taking", "笔记"),
            ("bookmark manager", "书签管理"),
        ],
    },
    {
        "label": "老龄照护",
        "subs": [
            ("medication reminder", "用药提醒"),
            ("health monitoring", "健康监测"),
            ("fall detection", "跌倒检测"),
            ("elderly care", "养老护理"),
            ("cognitive training", "认知训练"),
            ("emergency call", "紧急呼叫"),
            ("accessibility tool", "无障碍工具"),
            ("voice assistant", "语音助手"),
            ("blood pressure", "血压监测"),
            ("senior fitness", "老人健身"),
        ],
    },
]


# ============================================================
# 过滤参数（放宽，尽量凑够 5 个）
# ============================================================
MIN_STARS = 100
MIN_FORKS = 10
MAX_MONTHS = 36
LICENSE_WHITELIST = ["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "MPL-2.0"]
TOP_N_PER_SUB = 5


def months_ago(iso_str):
    if not iso_str:
        return 999
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return (datetime.now(dt.tzinfo) - dt).days / 30
    except Exception:
        return 999


def search_keyword(keyword, token, top_n=5):
    """搜一个关键词，返回 Top N 符合条件的项目"""
    q = f"{keyword} language:python stars:>{MIN_STARS}"
    url = (
        f"https://api.github.com/search/repositories"
        f"?q={urllib.parse.quote(q)}"
        f"&sort=stars&order=desc&per_page=20"
    )
    headers = {
        "User-Agent": "PluginFetch/3.0",
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    results = []
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
        results.append({
            "name": r["full_name"],
            "pip_name": pip_name,
            "desc": (r.get("description") or "").strip(),
            "stars": r["stargazers_count"],
            "forks": forks,
            "license": lic,
            "url": r["html_url"],
            "updated": r.get("updated_at", ""),
            "keyword": keyword,
        })
        if len(results) >= top_n:
            break
    return results


def main():
    token = GITHUB_TOKEN.strip() or os.environ.get("GITHUB_TOKEN", "").strip()

    print("=" * 60)
    if token:
        print("  ✅ Token 已就绪")
    else:
        print("  ⚠️ 没有 Token，速率限制严（会中途停）")
    print("=" * 60)
    print()

    out = {
        "last_updated": datetime.now().isoformat(),
        "categories": [],
    }

    total_subs = sum(len(c["subs"]) for c in CATEGORIES)
    done_subs = 0
    stopped = False

    for i, cat in enumerate(CATEGORIES):
        print(f"[{i+1}/{len(CATEGORIES)}] {cat['label']}")
        all_plugins = []

        for kw, label in cat["subs"]:
            done_subs += 1
            try:
                plugins = search_keyword(kw, token, TOP_N_PER_SUB)
                for p in plugins:
                    p["sub_label"] = label      # 细分领域中文名
                all_plugins.extend(plugins)
                print(f"    [{done_subs}/{total_subs}] {label}  → {len(plugins)} 个")
            except urllib.error.HTTPError as e:
                if e.code == 403:
                    print(f"    ❌ 速率限制，保存已有数据后停止")
                    stopped = True
                    break
                else:
                    print(f"    ❌ {label} → HTTP {e.code}")
            except Exception as e:
                print(f"    ❌ {label} → {type(e).__name__}")

            time.sleep(0.5)

        out["categories"].append({
            "label": cat["label"],
            "count": len(all_plugins),
            "plugins": all_plugins,
        })

        if stopped:
            break

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
