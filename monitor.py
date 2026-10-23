"""东南大学教务处讲座专区更新提醒器。

公开列表检查：不会登录校内系统，也不尝试绕过校园网访问限制。
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup

BASE = "https://jwc.seu.edu.cn"
SECTIONS = {
    "课外研学讲座": f"{BASE}/kwyxjz/list.htm",
    "文化素质讲座": f"{BASE}/whszjz/list.htm",
    "学业辅导讲座": f"{BASE}/xyfdjz/list.htm",
}

# 文本链接对应的官方文章路径，例如 /2026/1023/c68657a587358/page.htm
ARTICLE_PATTERN = re.compile(
    r"/(?:_t\d+/)?\d{4}/\d{4}/c\d+a\d+/page\.(?:htm|psp)(?:$|[?#])",
    re.IGNORECASE,
)
DATE_PATTERN = re.compile(r"20\d{2}[-/.]\d{1,2}[-/.]\d{1,2}")
STATE_FILE = Path(__file__).resolve().parent / "data" / "seen.json"
MAX_SAVED_PER_SECTION = 300


def canonical_url(url: str) -> str:
    """站点的 /_t3454 模板页和普通页指向同一篇文章。"""
    parts = urlsplit(url)
    path = re.sub(r"^/_t\d+(?=/)", "", parts.path)
    path = re.sub(r"/page\.psp$", "/page.htm", path, flags=re.I)
    return urlunsplit((parts.scheme, parts.netloc.lower(), path, "", ""))


def parse_articles(html: str, list_url: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    found: list[dict[str, str]] = []
    urls: set[str] = set()

    for link in soup.find_all("a", href=True):
        href = str(link["href"]).strip()
        article_url = urljoin(list_url, href)
        if not ARTICLE_PATTERN.search(urlsplit(article_url).path):
            continue
        if urlsplit(article_url).netloc.lower() != "jwc.seu.edu.cn":
            continue

        title = (link.get("title") or link.get_text(" ", strip=True)).strip()
        title = re.sub(r"\s+", " ", title)
        if not title:
            continue

        article_url = canonical_url(article_url)
        if article_url in urls:
            continue
        urls.add(article_url)

        # 文章列表的日期通常与标题放在同一个 li/div 内。
        date = ""
        parent = link.parent
        for _ in range(4):
            if parent is None:
                break
            context = parent.get_text(" ", strip=True)
            if len(context) > 500:
                break
            match = DATE_PATTERN.search(context)
            if match:
                date = match.group().replace("/", "-").replace(".", "-")
                break
            parent = parent.parent

        found.append({"title": title, "date": date, "url": article_url})

    return found


def fetch_articles(name: str, url: str) -> list[dict[str, str]]:
    response = requests.get(
        url,
        timeout=25,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; SEULectureMonitor/1.0; public-list-only)",
            "Accept-Language": "zh-CN,zh;q=0.9",
        },
    )
    response.raise_for_status()
    response.encoding = response.apparent_encoding or response.encoding
    articles = parse_articles(response.text, response.url)
    # 文化素质讲座页面目前可能为空；其他两栏意外为空更可能是网页格式发生变化。
    if not articles and name != "文化素质讲座":
        raise RuntimeError(f"{name} 列表解析结果为空；暂不更新记录，避免漏报。")
    print(f"{name}：检查到 {len(articles)} 条列表通知")
    return articles


def read_state() -> tuple[bool, dict[str, dict[str, dict[str, str]]]]:
    if not STATE_FILE.is_file():
        return False, {}
    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("data/seen.json 格式有误")
    return True, data


def push_wechat(title: str, description: str) -> None:
    key = os.getenv("SERVERCHAN_SENDKEY", "").strip()
    if not key:
        raise RuntimeError("缺少 SERVERCHAN_SENDKEY，请在 GitHub 仓库 Actions secrets 中配置。")
    # 仅使用 Server酱 Turbo 的 SCT 格式，避免将密钥发给错误的第三方服务。
    if not re.fullmatch(r"SCT[a-zA-Z0-9_-]+", key):
        raise RuntimeError("当前程序支持 Server酱 Turbo 的 SCT 开头的 SendKey。")
    endpoint = f"https://sctapi.ftqq.com/{key}.send"
    response = requests.post(endpoint, data={"title": title, "desp": description}, timeout=25)
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != 0:
        # 服务响应可能包含不宜直接输出的内部数据，故只提示通用错误。
        raise RuntimeError("Server酱返回失败状态，请检查 SendKey、推送通道及每日配额。")
    print("微信推送请求已成功提交。")


def build_message(events: list[tuple[str, str, dict[str, str]]]) -> str:
    chunks = [f"共发现 {len(events)} 条新增或变更的讲座通知："]
    for name, change, article in events:
        suffix = f"（{article['date']}）" if article["date"] else ""
        chunks.append(f"- **[{name}·{change}]** {article['title']}{suffix}\n  {article['url']}")
    chunks.append("\n注：部分文章正文仅允许通过校园网络或学校官方 VPN 查看。")
    return "\n\n".join(chunks)


def save_state(state: dict[str, dict[str, dict[str, str]]]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    print(f"开始检查：{datetime.now().astimezone().isoformat(timespec='seconds')}")
    # 先抓取全部栏目。遇到异常不更新本地记录，下一轮继续检查。
    listings = {name: fetch_articles(name, url) for name, url in SECTIONS.items()}
    initialized, old = read_state()

    if os.getenv("SEND_TEST", "").lower() == "true":
        push_wechat("东南大学讲座监控测试成功", "这是你手动触发的测试消息。正式运行时只推送新增或变更的讲座通知。")

    updated = {name: dict(old.get(name, {})) for name in SECTIONS}
    events: list[tuple[str, str, dict[str, str]]] = []

    for name, articles in listings.items():
        for article in articles:
            url = article["url"]
            previous = old.get(name, {}).get(url)
            if initialized:
                if previous is None:
                    events.append((name, "新增", article))
                elif previous.get("title") != article["title"] or (
                    article["date"] and previous.get("date") and previous["date"] != article["date"]
                ):
                    events.append((name, "更新", article))
            updated[name][url] = {"title": article["title"], "date": article["date"]}
        # 列表倒序更新；把当前页链接留在前面，状态表只保留近期的 300 项。
        current_urls = [article["url"] for article in articles]
        remaining = [u for u in updated[name] if u not in current_urls]
        ordered_urls = (current_urls + remaining)[:MAX_SAVED_PER_SECTION]
        updated[name] = {u: updated[name][u] for u in ordered_urls}

    if not initialized:
        save_state(updated)
        print("首次运行：已建立现有通知的基线，不把历史通知当成新消息推送。")
    elif events:
        print(f"发现 {len(events)} 条新通知/标题变更。")
        push_wechat(f"东南大学教务处讲座更新（{len(events)}条）", build_message(events))
        save_state(updated)  # 必须在发送成功后记录，避免推送失败但永久漏报。
    else:
        print("暂无新的讲座通知。")
        if updated != old:
            save_state(updated)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (requests.RequestException, RuntimeError, ValueError, OSError) as exc:
        print(f"检查失败：{exc.__class__.__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
