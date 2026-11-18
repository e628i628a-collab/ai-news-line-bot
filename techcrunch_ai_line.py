import os
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

if not LINE_CHANNEL_ACCESS_TOKEN:
    print("LINE_CHANNEL_ACCESS_TOKEN が見つかりません")
    exit(1)

RSS_URLS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://techcrunch.com/category/artificial-intelligence/rss/"
]

LAST_SENT_FILE = "last_sent.txt"

# 前回送信URL読み込み
sent_urls = set()

if os.path.exists(LAST_SENT_FILE):
    with open(LAST_SENT_FILE, "r", encoding="utf-8") as f:
        sent_urls = set(line.strip() for line in f)

# RSS取得
content = None

for rss_url in RSS_URLS:
    try:
        req = urllib.request.Request(
            rss_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept": "application/rss+xml, application/xml, text/xml, */*"
            }
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            root = ET.fromstring(response.read())
            if root.tag != "rss":
                raise ValueError("RSS形式ではありません")
            content = root
            print("RSS取得成功！")
            break

    except Exception as e:
        print(f"RSS取得失敗: {rss_url}")
        print(f"エラー内容: {e}")

# RSS取得失敗時
if content is None:
    print("RSSを取得できなかったため、今回はスキップします")
    exit(0)

# 記事取得
items = content.findall(".//item")

new_articles = []

for item in items[:5]:
    title = item.findtext("title")
    link = item.findtext("link")

    if title and link and link not in sent_urls:
        new_articles.append((title, link))

# 新記事なし
if not new_articles:
    print("新しい記事なし")
    exit(0)

# LINEメッセージ作成
message_text = "🤖 New TechCrunch AI Articles:\n\n"

for title, link in new_articles:
    message_text += f"- {title}\n{link}\n\n"

# LINE送信
LINE_API_URL = "https://api.line.me/v2/bot/message/broadcast"

payload = {
    "messages": [
        {
            "type": "text",
            "text": message_text
        }
    ]
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
}

req = urllib.request.Request(
    LINE_API_URL,
    data=json.dumps(payload).encode("utf-8"),
    headers=headers,
    method="POST"
)

with urllib.request.urlopen(req, timeout=30) as response:
    print("LINE送信成功！")
    print(response.read().decode("utf-8"))

# 送信済みURL保存
with open(LAST_SENT_FILE, "a", encoding="utf-8") as f:
    for _, link in new_articles:
        f.write(link + "\n")
