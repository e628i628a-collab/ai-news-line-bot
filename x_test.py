import os
import json
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

if not BEARER_TOKEN:
    print("X_BEARER_TOKEN が見つかりません")
    exit(1)

if not LINE_CHANNEL_ACCESS_TOKEN:
    print("LINE_CHANNEL_ACCESS_TOKEN が見つかりません")
    exit(1)

ACCOUNTS = {
    "OpenAI": "🤖 OpenAI",
    "GoogleDeepMind": "🧠 DeepMind",
    "xAI": "🚀 xAI",
    "huggingface": "🤗 Hugging Face",
    "cursor_ai": "💻 Cursor"
}

JST = ZoneInfo("Asia/Tokyo")

today_jst = datetime.now(JST).date()
yesterday_jst = today_jst - timedelta(days=1)

start_jst = datetime.combine(yesterday_jst, datetime.min.time(), tzinfo=JST)
end_jst = start_jst + timedelta(days=1)

start_utc = start_jst.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
end_utc = end_jst.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

print("対象期間 JST:", start_jst, "〜", end_jst)
print("対象期間 UTC:", start_utc, "〜", end_utc)

results = []

for username, label in ACCOUNTS.items():
    try:
        user_url = f"https://api.x.com/2/users/by/username/{username}"

        user_req = urllib.request.Request(
            user_url,
            headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
        )

        with urllib.request.urlopen(user_req) as response:
            user_data = json.loads(response.read().decode("utf-8"))

        user_id = user_data["data"]["id"]

        tweet_url = (
            f"https://api.x.com/2/users/{user_id}/tweets"
            f"?max_results=100"
            f"&start_time={start_utc}"
            f"&end_time={end_utc}"
            f"&tweet.fields=public_metrics,created_at"
            f"&exclude=retweets,replies"
        )

        tweet_req = urllib.request.Request(
            tweet_url,
            headers={"Authorization": f"Bearer {BEARER_TOKEN}"}
        )

        with urllib.request.urlopen(tweet_req) as response:
            tweet_data = json.loads(response.read().decode("utf-8"))

        tweets = tweet_data.get("data", [])

        if not tweets:
            print(f"{username}: 前日の投稿なし")
            continue

        best_tweet = None
        best_score = -1

        for tweet in tweets:
            metrics = tweet.get("public_metrics", {})

            score = (
                metrics.get("like_count", 0)
                + metrics.get("retweet_count", 0) * 2
                + metrics.get("reply_count", 0)
                + metrics.get("quote_count", 0) * 2
            )

            if score > best_score:
                best_score = score
                best_tweet = tweet

        if best_tweet:
            tweet_text = best_tweet["text"]
            tweet_id = best_tweet["id"]
            tweet_link = f"https://x.com/{username}/status/{tweet_id}"

            results.append(
                f"""{label}

{tweet_text}

{tweet_link}
"""
            )

    except Exception as e:
        print(f"{username} エラー:", e)

if results:
    message_text = f"🔥 Yesterday's Trending AI X Posts\n対象日: {yesterday_jst}\n\n"
    message_text += "\n-------------------\n\n".join(results)

    LINE_API_URL = "https://api.line.me/v2/bot/message/broadcast"

    payload = {
        "messages": [
            {
                "type": "text",
                "text": message_text[:5000]
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

else:
    print("前日の送信対象投稿なし")
