import requests
import time
import os

from flask import Flask
from threading import Thread

# ===== 설정 =====
BOT_TOKEN = "8199900540:AAH9ffkY5CTo92FOy_KARJosELCtVQW0ulY"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ===== Flask =====
app = Flask('')


@app.route('/')
def home():
    return "Game Price Bot Running!"


# ===== Render 유지 =====
def run_web():

    app.run(
        host='0.0.0.0',
        port=int(os.environ.get("PORT", 10000))
    )


def keep_alive():

    t = Thread(target=run_web)

    t.start()


# ===== 서버 ID =====
SERVER_IDS = {

    "린델": "24613",

    "데포로쥬": "24487",

    "켄라우헬": "24488",

    "조우": "24491",

    "로엔그린": "25274",

    "하이네": "25273",

    "발라카스": "26022"
}


# ===== API URL =====
API_URL = (
    "https://gamebit.co.kr/"
    "jdata2/total_status.json"
)


# ===== 메시지 보내기 =====
def send_message(chat_id, text):

    url = f"{BASE_URL}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": text
        }
    )

    print(response.text)


# ===== API 데이터 가져오기 =====
def get_data():

    response = requests.get(
        API_URL,
        timeout=10
    )

    return response.json()


# ===== 단일 서버 시세 =====
def get_server_price(server_name):

    if server_name not in SERVER_IDS:

        return """❌ 지원하지 않는 서버입니다

지원 서버:
• 린델
• 데포로쥬
• 켄라우헬
• 조우
• 로엔그린
• 하이네
• 발라카스"""

    try:

        data = get_data()

        server_id = SERVER_IDS[server_name]

        server_data = data[server_id]

        price = server_data["price"]

        rate = server_data["rate"]

        update_time = server_data["last_update"]

        return f"""📊 {server_name} 서버

💰 현재 시세
{price:,.2f}

📈 변동률
{rate}%

🕒 업데이트
{update_time}

🌐 gamebit.co.kr"""

    except Exception as e:

        print(e)

        return "❌ 시세 조회 실패"


# ===== 전체 서버 시세 =====
def get_all_prices():

    try:

        data = get_data()

        result_text = "📊 전체 서버 시세\n\n"

        for server_name, server_id in SERVER_IDS.items():

            try:

                server_data = data[server_id]

                price = server_data["price"]

                rate = server_data["rate"]

                result_text += (
                    f"💰 {server_name}\n"
                    f"시세: {price:,.2f}\n"
                    f"변동: {rate}%\n\n"
                )

            except:

                result_text += (
                    f"❌ {server_name}: 실패\n\n"
                )

        return result_text

    except Exception as e:

        print(e)

        return "❌ 전체 시세 조회 실패"


# ===== 메시지 처리 =====
def handle_message(message):

    chat_id = message['chat']['id']

    text = message.get(
        'text',
        ''
    ).strip()

    print("입력값:")
    print(text)

    # ===== 전체 시세 =====
    if text == "전체시세":

        send_message(
            chat_id,
            "📡 전체 서버 시세 조회 중..."
        )

        result = get_all_prices()

        send_message(
            chat_id,
            result
        )

    # ===== 서버 시세 =====
    elif text.startswith("시세"):

        split_text = text.split()

        if len(split_text) < 2:

            send_message(
                chat_id,
                """📊 사용 방법

• 시세 린델
• 시세 켄라우헬
• 시세 발라카스
• 전체시세"""
            )

            return

        server_name = split_text[1]

        send_message(
            chat_id,
            f"📡 {server_name} 서버 시세 조회 중..."
        )

        result = get_server_price(
            server_name
        )

        send_message(
            chat_id,
            result
        )

    # ===== 기본 메시지 =====
    else:

        send_message(
            chat_id,
            """🎮 리니지 시세 봇

사용 방법:

• 시세 린델
• 시세 켄라우헬
• 시세 발라카스
• 전체시세"""
        )


# ===== 업데이트 =====
def get_updates(offset=None):

    url = f"{BASE_URL}/getUpdates"

    params = {
        "timeout": 10
    }

    if offset:

        params["offset"] = offset

    res = requests.get(
        url,
        params=params
    )

    return res.json()


# ===== 메인 =====
def main():

    offset = None

    while True:

        try:

            data = get_updates(offset)

            if (
                "result" in data
                and len(data["result"]) > 0
            ):

                for update in data["result"]:

                    if "message" in update:

                        try:

                            handle_message(
                                update["message"]
                            )

                        except Exception as e:

                            print(e)

                            send_message(
                                update["message"]["chat"]["id"],
                                f"오류 발생 😢\n{e}"
                            )

                    offset = (
                        update["update_id"] + 1
                    )

            time.sleep(1)

        except Exception as e:

            print(e)

            time.sleep(5)


# ===== 시작 =====
if __name__ == "__main__":

    print("게임 시세 봇 실행 중...")

    keep_alive()

    main()