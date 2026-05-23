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

# 監視アカウント
ACCOUNTS = {
    "OpenAI": "🤖 OpenAI",
    "GoogleDeepMind": "🧠 DeepMind",
    "xAI": "🚀 xAI",
    "huggingface": "🤗 Hugging Face",
    "cursor_ai": "💻 Cursor"
}

results = []

for username, label in ACCOUNTS.items():

    try:
        # ユーザー取得
        user_url = f"https://api.x.com/2/users/by/username/{username}"

        user_req = urllib.request.Request(
            user_url,
            headers={
                "Authorization": f"Bearer {BEARER_TOKEN}"
            }
        )

        with urllib.request.urlopen(user_req) as response:
            user_data = json.loads(response.read().decode("utf-8"))

        user_id = user_data["data"]["id"]

        # 投稿取得
        tweet_url = (
            f"https://api.x.com/2/users/{user_id}/tweets"
            f"?max_results=5"
            f"&tweet.fields=public_metrics"
        )

        tweet_req = urllib.request.Request(
            tweet_url,
            headers={
                "Authorization": f"Bearer {BEARER_TOKEN}"
            }
        )

        with urllib.request.urlopen(tweet_req) as response:
            tweet_data = json.loads(response.read().decode("utf-8"))

        best_tweet = None
        best_score = -1

        for tweet in tweet_data["data"]:

            metrics = tweet["public_metrics"]

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

🔥 Score: {best_score}

{tweet_link}
"""
            )

    except Exception as e:
        print(f"{username} エラー:", e)

# LINE送信
if results:

    message_text = "🔥 Trending AI X Posts\n\n"

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
    print("送信する投稿なし")
