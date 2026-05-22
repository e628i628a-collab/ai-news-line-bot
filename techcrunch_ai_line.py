import os
import json
import urllib.request
import xml.etree.ElementTree as ET

# .env 読み込み
env_path = r"C:\Users\ek090\.hermes\.env"

LINE_CHANNEL_ACCESS_TOKEN = None

with open(env_path, "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("LINE_CHANNEL_ACCESS_TOKEN="):
            LINE_CHANNEL_ACCESS_TOKEN = line.strip().split("=", 1)[1]

if not LINE_CHANNEL_ACCESS_TOKEN:
    print("LINE_CHANNEL_ACCESS_TOKEN が見つかりません")
    exit()

# RSS URL
RSS_URL = "https://techcrunch.com/category/artificial-intelligence/feed/"

# RSS取得
req = urllib.request.Request(
    RSS_URL,
    headers={"User-Agent": "Mozilla/5.0"}
)

with urllib.request.urlopen(req) as response:
    content = response.read()

root = ET.fromstring(content)

items = root.findall(".//item")

# LINEへ送るメッセージ
message_text = "Latest TechCrunch AI Articles:\n\n"

for item in items[:3]:
    title = item.find("title").text
    link = item.find("link").text

    message_text += f"- {title}\n{link}\n\n"

# LINE Messaging API
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

with urllib.request.urlopen(req) as response:
    print("LINE送信成功！")
    print(response.read().decode("utf-8"))