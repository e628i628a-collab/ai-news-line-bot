import os
import json
import urllib.request

# Secrets
BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

if not BEARER_TOKEN:
    print("X_BEARER_TOKEN が見つかりません")
    exit(1)

if not LINE_CHANNEL_ACCESS_TOKEN:
    print("LINE_CHANNEL_ACCESS_TOKEN が見つかりません")
    exit(1)

USERNAME = "OpenAI"

# OpenAIユーザー取得
user_url = f"https://api.x.com/2/users/by/username/{USERNAME}"

user_req = urllib.request.Request(
    user_url,
    headers={
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }
)

with urllib.request.urlopen(user_req) as response:
    user_data = json.loads(response.read().decode("utf-8"))

user_id = user_data["data"]["id"]

print("USER ID:", user_id)

# 最新ポスト取得
tweet_url = f"https://api.x.com/2/users/{user_id}/tweets?max_results=5"

tweet_req = urllib.request.Request(
    tweet_url,
    headers={
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }
)

with urllib.request.urlopen(tweet_req) as response:
    tweet_data = json.loads(response.read().decode("utf-8"))

latest_tweet = tweet_data["data"][0]

tweet_text = latest_tweet["text"]
tweet_id = latest_tweet["id"]

tweet_link = f"https://x.com/{USERNAME}/status/{tweet_id}"

# LINE送信用メッセージ
message_text = f"""🔥 OpenAI Latest Post

{tweet_text}

{tweet_link}
"""

print(message_text)

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

line_req = urllib.request.Request(
    LINE_API_URL,
    data=json.dumps(payload).encode("utf-8"),
    headers=headers,
    method="POST"
)

with urllib.request.urlopen(line_req) as response:
    print("LINE送信成功！")
    print(response.read().decode("utf-8"))
