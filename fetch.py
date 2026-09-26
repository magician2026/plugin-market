# -*- coding: utf-8 -*-
"""
fetch.py — 云端抓取脚本
GitHub Actions 每天自动调用
"""
import os
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime


CATEGORIES = [
    # ============ 1. 媒体处理 ============
    {"keyword": "image compression", "label": "图片压缩"},
    {"keyword": "image watermark", "label": "图片水印"},
    {"keyword": "image format convert", "label": "图片格式转换"},
    {"keyword": "background removal", "label": "抠图去背景"},
    {"keyword": "image ocr", "label": "图片文字识别"},
    {"keyword": "image enhancement", "label": "图片增强修复"},
    {"keyword": "image stitching", "label": "图片拼接"},
    {"keyword": "image annotation", "label": "图片标注"},
    {"keyword": "batch image", "label": "批量图片处理"},
    {"keyword": "video converter", "label": "视频转码"},
    {"keyword": "video compression", "label": "视频压缩"},
    {"keyword": "video editing", "label": "视频剪辑"},
    {"keyword": "video downloader", "label": "视频下载"},
    {"keyword": "subtitle editor", "label": "字幕编辑"},
    {"keyword": "screen recorder", "label": "录屏"},
    {"keyword": "video to gif", "label": "视频转GIF"},
    {"keyword": "audio extraction", "label": "音频提取"},
    {"keyword": "audio converter", "label": "音频转码"},
    {"keyword": "audio denoise", "label": "音频降噪"},
    {"keyword": "speech to text", "label": "语音转文字"},
    {"keyword": "text to speech", "label": "文字转语音"},
    {"keyword": "photo library", "label": "照片库管理"},

    # ============ 2. 软件开发 ============
    {"keyword": "code formatter", "label": "代码格式化"},
    {"keyword": "linter", "label": "代码检查"},
    {"keyword": "api testing", "label": "API 测试"},
    {"keyword": "git tool", "label": "Git 工具"},
    {"keyword": "dependency manager", "label": "依赖管理"},
    {"keyword": "documentation gen", "label": "文档生成"},
    {"keyword": "code editor", "label": "代码编辑器"},
    {"keyword": "debugger", "label": "调试器"},
    {"keyword": "profiler", "label": "性能分析"},
    {"keyword": "static analysis", "label": "静态分析"},
    {"keyword": "code coverage", "label": "代码覆盖率"},
    {"keyword": "package manager", "label": "包管理"},
    {"keyword": "build tool", "label": "构建工具"},
    {"keyword": "unit test", "label": "单元测试"},
    {"keyword": "refactor tool", "label": "重构工具"},
    {"keyword": "code search", "label": "代码搜索"},
    {"keyword": "syntax highlight", "label": "语法高亮"},

    # ============ 3. 文件管理 ============
    {"keyword": "file rename", "label": "批量重命名"},
    {"keyword": "file deduplication", "label": "文件去重"},
    {"keyword": "file sync", "label": "文件同步"},
    {"keyword": "disk usage", "label": "磁盘分析"},
    {"keyword": "file search", "label": "文件搜索"},
    {"keyword": "backup tool", "label": "备份工具"},
    {"keyword": "file compare", "label": "文件对比"},
    {"keyword": "file split", "label": "文件分割"},
    {"keyword": "file merge", "label": "文件合并"},
    {"keyword": "archive tool", "label": "压缩归档"},
    {"keyword": "file hash", "label": "文件指纹"},
    {"keyword": "file metadata", "label": "文件元数据"},
    {"keyword": "folder sync", "label": "文件夹同步"},
    {"keyword": "duplicate finder", "label": "重复查找"},
    {"keyword": "file organizer", "label": "文件整理"},

    # ============ 4. 密码安全 ============
    {"keyword": "password manager", "label": "密码管理"},
    {"keyword": "password generator", "label": "密码生成"},
    {"keyword": "file encryption", "label": "文件加密"},
    {"keyword": "hash checker", "label": "哈希校验"},
    {"keyword": "ssl certificate", "label": "SSL 证书"},
    {"keyword": "two factor auth", "label": "双因素认证"},
    {"keyword": "vpn client", "label": "VPN 客户端"},
    {"keyword": "key derivation", "label": "密钥派生"},
    {"keyword": "secure delete", "label": "安全删除"},
    {"keyword": "steganography", "label": "隐写术"},
    {"keyword": "port scanner", "label": "端口扫描"},
    {"keyword": "packet sniff", "label": "抓包工具"},
    {"keyword": "vulnerability scan", "label": "漏洞扫描"},
    {"keyword": "penetration test", "label": "渗透测试"},
    {"keyword": "cryptography library", "label": "加密库"},

    # ============ 5. 文档办公 ============
    {"keyword": "pdf merger", "label": "PDF 合并"},
    {"keyword": "pdf splitter", "label": "PDF 拆分"},
    {"keyword": "pdf annotation", "label": "PDF 批注"},
    {"keyword": "docx reader", "label": "Word 读取"},
    {"keyword": "excel reader", "label": "Excel 读取"},
    {"keyword": "powerpoint tool", "label": "PPT 工具"},
    {"keyword": "markdown editor", "label": "Markdown 编辑"},
    {"keyword": "ebook converter", "label": "电子书转换"},
    {"keyword": "ebook reader", "label": "电子书阅读"},
    {"keyword": "office automation", "label": "办公自动化"},
    {"keyword": "document compare", "label": "文档对比"},
    {"keyword": "document scanner", "label": "文档扫描"},
    {"keyword": "text extraction", "label": "文本提取"},
    {"keyword": "office converter", "label": "Office 转换"},
    {"keyword": "spreadsheet tool", "label": "表格工具"},

    # ============ 6. 网络通信 ============
    {"keyword": "web scraper", "label": "网页爬虫"},
    {"keyword": "http client", "label": "HTTP 客户端"},
    {"keyword": "email sender", "label": "邮件发送"},
    {"keyword": "ssh client", "label": "SSH 客户端"},
    {"keyword": "ftp client", "label": "FTP 客户端"},
    {"keyword": "websocket", "label": "WebSocket"},
    {"keyword": "network scanner", "label": "网络扫描"},
    {"keyword": "ping tool", "label": "Ping 工具"},
    {"keyword": "dns lookup", "label": "DNS 查询"},
    {"keyword": "proxy server", "label": "代理服务器"},
    {"keyword": "api client", "label": "API 客户端"},
    {"keyword": "webhook", "label": "Webhook"},
    {"keyword": "chat bot", "label": "聊天机器人"},
    {"keyword": "notification", "label": "通知推送"},
    {"keyword": "rss reader", "label": "RSS 阅读"},

    # ============ 7. 系统工具 ============
    {"keyword": "system monitor", "label": "系统监控"},
    {"keyword": "process manager", "label": "进程管理"},
    {"keyword": "clipboard manager", "label": "剪贴板"},
    {"keyword": "screen capture", "label": "截图"},
    {"keyword": "task scheduler", "label": "定时任务"},
    {"keyword": "window manager", "label": "窗口管理"},
    {"keyword": "hotkey tool", "label": "快捷键"},
    {"keyword": "system tray", "label": "系统托盘"},
    {"keyword": "system info", "label": "系统信息"},
    {"keyword": "hardware monitor", "label": "硬件监控"},
    {"keyword": "battery monitor", "label": "电池监控"},
    {"keyword": "startup manager", "label": "启动管理"},
    {"keyword": "registry tool", "label": "注册表工具"},
    {"keyword": "driver tool", "label": "驱动工具"},
    {"keyword": "usb tool", "label": "USB 工具"},

    # ============ 8. 游戏娱乐 ============
    {"keyword": "game save manager", "label": "游戏存档"},
    {"keyword": "game trainer", "label": "游戏修改器"},
    {"keyword": "game automation", "label": "游戏自动化"},
    {"keyword": "minecraft mod", "label": "我的世界模组"},
    {"keyword": "steam library", "label": "Steam 库"},
    {"keyword": "game emulator", "label": "模拟器"},
    {"keyword": "game bot", "label": "游戏机器人"},
    {"keyword": "game launcher", "label": "游戏启动器"},
    {"keyword": "game config", "label": "游戏配置"},
    {"keyword": "achievement tracker", "label": "成就追踪"},
    {"keyword": "game stats", "label": "游戏统计"},
    {"keyword": "mod manager", "label": "模组管理"},
    {"keyword": "game patch", "label": "游戏补丁"},
    {"keyword": "game server", "label": "游戏服务器"},
    {"keyword": "game tools", "label": "游戏工具"},

    # ============ 9. 数据处理 ============
    {"keyword": "csv reader", "label": "CSV 读取"},
    {"keyword": "excel writer", "label": "Excel 写入"},
    {"keyword": "json parser", "label": "JSON 解析"},
    {"keyword": "xml parser", "label": "XML 解析"},
    {"keyword": "data cleaner", "label": "数据清洗"},
    {"keyword": "data converter", "label": "数据转换"},
    {"keyword": "data validation", "label": "数据校验"},
    {"keyword": "data pipeline", "label": "数据管道"},
    {"keyword": "etl tool", "label": "ETL 工具"},
    {"keyword": "data generator", "label": "数据生成"},
    {"keyword": "data masking", "label": "数据脱敏"},
    {"keyword": "yaml parser", "label": "YAML 解析"},
    {"keyword": "ini parser", "label": "INI 解析"},
    {"keyword": "sql parser", "label": "SQL 解析"},
    {"keyword": "data merge", "label": "数据合并"},

    # ============ 10. 数据可视化 ============
    {"keyword": "chart generator", "label": "图表生成"},
    {"keyword": "plotting library", "label": "绘图库"},
    {"keyword": "dashboard", "label": "仪表盘"},
    {"keyword": "network graph", "label": "网络图"},
    {"keyword": "heatmap", "label": "热力图"},
    {"keyword": "3d visualization", "label": "3D 可视化"},
    {"keyword": "data plot", "label": "数据绘图"},
    {"keyword": "bar chart", "label": "柱状图"},
    {"keyword": "pie chart", "label": "饼图"},
    {"keyword": "scatter plot", "label": "散点图"},
    {"keyword": "interactive chart", "label": "交互式图表"},
    {"keyword": "gantt chart", "label": "甘特图"},

    # ============ 11. 效率自动化 ============
    {"keyword": "keyboard automation", "label": "键盘自动化"},
    {"keyword": "mouse automation", "label": "鼠标自动化"},
    {"keyword": "batch processing", "label": "批量处理"},
    {"keyword": "workflow automation", "label": "工作流"},
    {"keyword": "auto clicker", "label": "自动点击"},
    {"keyword": "text expander", "label": "文本扩展"},
    {"keyword": "gui automation", "label": "GUI 自动化"},
    {"keyword": "macro recorder", "label": "宏录制"},
    {"keyword": "hotkey manager", "label": "热键管理"},
    {"keyword": "clipboard tool", "label": "剪贴板增强"},
    {"keyword": "auto fill", "label": "自动填充"},
    {"keyword": "auto save", "label": "自动保存"},
    {"keyword": "auto backup", "label": "自动备份"},
    {"keyword": "form filler", "label": "表单填写"},
    {"keyword": "task automation", "label": "任务自动化"},

    # ============ 12. Web 开发 ============
    {"keyword": "web framework", "label": "Web 框架"},
    {"keyword": "api framework", "label": "API 框架"},
    {"keyword": "html parser", "label": "HTML 解析"},
    {"keyword": "css parser", "label": "CSS 解析"},
    {"keyword": "web testing", "label": "网页测试"},
    {"keyword": "static site gen", "label": "静态站点生成"},
    {"keyword": "template engine", "label": "模板引擎"},
    {"keyword": "web server", "label": "Web 服务器"},
    {"keyword": "web socket", "label": "WebSocket"},
    {"keyword": "graphql", "label": "GraphQL"},
    {"keyword": "rest api", "label": "REST API"},
    {"keyword": "web browser", "label": "浏览器"},
    {"keyword": "web crawler", "label": "网页爬虫"},
    {"keyword": "url parser", "label": "URL 解析"},
    {"keyword": "http server", "label": "HTTP 服务器"},

    # ============ 13. 数据库 ============
    {"keyword": "sqlite tool", "label": "SQLite 工具"},
    {"keyword": "mysql client", "label": "MySQL 客户端"},
    {"keyword": "postgresql client", "label": "PostgreSQL 客户端"},
    {"keyword": "mongodb client", "label": "MongoDB 客户端"},
    {"keyword": "redis client", "label": "Redis 客户端"},
    {"keyword": "orm library", "label": "ORM 库"},
    {"keyword": "database migration", "label": "数据库迁移"},
    {"keyword": "query builder", "label": "查询构建"},
    {"keyword": "database backup", "label": "数据库备份"},
    {"keyword": "database admin", "label": "数据库管理"},
    {"keyword": "nosql database", "label": "NoSQL 数据库"},
    {"keyword": "database schema", "label": "数据库架构"},

    # ============ 14. AI 工具 ============
    {"keyword": "llm api", "label": "LLM 调用"},
    {"keyword": "prompt tool", "label": "提示词工具"},
    {"keyword": "embedding", "label": "向量嵌入"},
    {"keyword": "image recognition", "label": "图像识别"},
    {"keyword": "speech recognition", "label": "语音识别"},
    {"keyword": "text to speech", "label": "语音合成"},
    {"keyword": "object detection", "label": "目标检测"},
    {"keyword": "face recognition", "label": "人脸识别"},
    {"keyword": "chat bot", "label": "聊天机器人"},
    {"keyword": "machine learning", "label": "机器学习"},
    {"keyword": "deep learning", "label": "深度学习"},
    {"keyword": "neural network", "label": "神经网络"},
    {"keyword": "dataset tool", "label": "数据集工具"},
    {"keyword": "model training", "label": "模型训练"},
    {"keyword": "ai assistant", "label": "AI 助手"},

    # ============ 15. 文本处理 ============
    {"keyword": "text diff", "label": "文本对比"},
    {"keyword": "text translate", "label": "文本翻译"},
    {"keyword": "text tokenizer", "label": "分词"},
    {"keyword": "regex tool", "label": "正则工具"},
    {"keyword": "text statistics", "label": "文本统计"},
    {"keyword": "text formatting", "label": "文本格式化"},
    {"keyword": "text search", "label": "文本搜索"},
    {"keyword": "text replace", "label": "文本替换"},
    {"keyword": "text encryption", "label": "文本加密"},
    {"keyword": "text to markdown", "label": "转 Markdown"},
    {"keyword": "spell checker", "label": "拼写检查"},
    {"keyword": "grammar check", "label": "语法检查"},

    # ============ 16. 图形绘制 ============
    {"keyword": "vector graphics", "label": "矢量图"},
    {"keyword": "svg tool", "label": "SVG 工具"},
    {"keyword": "flowchart", "label": "流程图"},
    {"keyword": "diagram generator", "label": "图表生成"},
    {"keyword": "drawing library", "label": "绘图库"},
    {"keyword": "image annotation", "label": "图像标注"},
    {"keyword": "mind mapping", "label": "思维导图"},
    {"keyword": "uml tool", "label": "UML 工具"},
    {"keyword": "canvas drawing", "label": "画布绘图"},
    {"keyword": "graphviz", "label": "Graphviz"},

    # ============ 17. 硬件控制 ============
    {"keyword": "usb device", "label": "USB 设备"},
    {"keyword": "serial port", "label": "串口"},
    {"keyword": "bluetooth", "label": "蓝牙"},
    {"keyword": "gpio control", "label": "GPIO 控制"},
    {"keyword": "camera control", "label": "摄像头控制"},
    {"keyword": "printer control", "label": "打印机控制"},
    {"keyword": "arduino", "label": "Arduino"},
    {"keyword": "raspberry pi", "label": "树莓派"},
    {"keyword": "sensor library", "label": "传感器库"},
    {"keyword": "game controller", "label": "手柄控制"},

    # ============ 18. 科学计算 ============
    {"keyword": "numpy alternative", "label": "数值计算"},
    {"keyword": "symbolic math", "label": "符号数学"},
    {"keyword": "statistics", "label": "统计"},
    {"keyword": "physics sim", "label": "物理仿真"},
    {"keyword": "data analysis", "label": "数据分析"},
    {"keyword": "linear algebra", "label": "线性代数"},
    {"keyword": "optimization", "label": "优化算法"},
    {"keyword": "numerical method", "label": "数值方法"},
    {"keyword": "signal processing", "label": "信号处理"},
    {"keyword": "scientific plot", "label": "科学绘图"},

    # ============ 19. 生活学习 ============
    {"keyword": "todo list", "label": "待办"},
    {"keyword": "flashcard", "label": "闪卡"},
    {"keyword": "pomodoro", "label": "番茄钟"},
    {"keyword": "weather", "label": "天气"},
    {"keyword": "personal finance", "label": "记账"},
    {"keyword": "language learning", "label": "语言学习"},
    {"keyword": "calendar", "label": "日历"},
    {"keyword": "habit tracker", "label": "习惯追踪"},
    {"keyword": "note taking", "label": "笔记"},
    {"keyword": "bookmark manager", "label": "书签管理"},

    # ============ 20. 老龄照护 ============
    {"keyword": "medication reminder", "label": "用药提醒"},
    {"keyword": "health monitoring", "label": "健康监测"},
    {"keyword": "fall detection", "label": "跌倒检测"},
    {"keyword": "elderly care", "label": "养老护理"},
    {"keyword": "cognitive training", "label": "认知训练"},
    {"keyword": "emergency call", "label": "紧急呼叫"},
    {"keyword": "accessibility tool", "label": "无障碍工具"},
    {"keyword": "voice assistant", "label": "语音助手"},
    {"keyword": "blood pressure", "label": "血压监测"},
    {"keyword": "senior fitness", "label": "老人健身"},
]


MIN_STARS = 300
MIN_FORKS = 30
MAX_MONTHS = 30
LICENSE_WHITELIST = ["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause"]
RESULTS_PER_CATEGORY = 1


def months_ago(iso_str):
    if not iso_str:
        return 999
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return (datetime.now(dt.tzinfo) - dt).days / 30
    except Exception:
        return 999


def search_category(keyword, token):
    q = f"{keyword} language:python stars:>{MIN_STARS}"
    url = (
        f"https://api.github.com/search/repositories"
        f"?q={urllib.parse.quote(q)}"
        f"&sort=stars&order=desc&per_page=10"
    )
    headers = {
        "User-Agent": "PluginFetch/1.0",
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
        })
        if len(results) >= RESULTS_PER_CATEGORY:
            break
    return results


def main():
    token = os.environ.get("GITHUB_TOKEN", "")
    print(f"[启动] 开始抓取，共 {len(CATEGORIES)} 个分类")

    out = {
        "last_updated": datetime.now().isoformat(),
        "categories": [],
    }

    for i, cat in enumerate(CATEGORIES):
        print(f"[{i+1}/{len(CATEGORIES)}] {cat['label']}...")
        try:
            plugins = search_category(cat["keyword"], token)
            out["categories"].append({
                "label": cat["label"],
                "keyword": cat["keyword"],
                "count": len(plugins),
                "plugins": plugins,
            })
            print(f"    找到 {len(plugins)} 个")
        except urllib.error.HTTPError as e:
            err = "速率限制" if e.code == 403 else f"HTTP {e.code}"
            print(f"    失败：{err}")
            out["categories"].append({
                "label": cat["label"], "keyword": cat["keyword"],
                "count": 0, "plugins": [], "error": err,
            })
        except Exception as e:
            print(f"    失败：{e}")
            out["categories"].append({
                "label": cat["label"], "keyword": cat["keyword"],
                "count": 0, "plugins": [], "error": str(e),
            })
        time.sleep(0.5)

    with open("market_data.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    total = sum(c.get("count", 0) for c in out["categories"])
    print(f"[完成] 共 {total} 个项目")


if __name__ == "__main__":
    main()
