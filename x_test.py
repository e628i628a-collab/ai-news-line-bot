import os
import json
import urllib.request

BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN")

if not BEARER_TOKEN:
    print("X_BEARER_TOKEN が見つかりません")
    exit(1)

USERNAME = "OpenAI"

# ユーザー情報取得
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

print(json.dumps(tweet_data, indent=2, ensure_ascii=False))
