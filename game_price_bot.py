import telebot
import requests
import time
import os

from flask import Flask
from threading import Thread

# ===== 설정 =====
BOT_TOKEN = "8199900540:AAH9ffkY5CTo92FOy_KARJosELCtVQW0ulY"
bot = telebot.TeleBot(BOT_TOKEN)

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ===== Flask =====
app = Flask(__name__)


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

    try:

        requests.post(
            url,
            data={
                "chat_id": chat_id,
                "text": text
            },
            timeout=10
        )

    except Exception as e:

        print("메시지 전송 오류:", e)


# ===== API 데이터 =====
def get_data():

    response = requests.get(
        API_URL,
        timeout=10
    )

    return response.json()


# ===== 서버 시세 =====
def get_server_price(server_name):

    if server_name not in SERVER_IDS:

        return None

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
{update_time}"""

    except Exception as e:

        print("서버 시세 오류:", e)

        return "❌ 시세 조회 실패"


# ===== 전체 시세 =====
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

            except Exception as e:

                print(f"{server_name} 오류:", e)

                result_text += (
                    f"❌ {server_name}: 실패\n\n"
                )

        return result_text

    except Exception as e:

        print("전체 시세 오류:", e)

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

    # ===== 전체시세 =====
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

        # 시세만 입력한 경우
        if len(split_text) < 2:

            send_message(
                chat_id,
                "사용법: 시세 서버이름"
            )

            return

        server_name = split_text[1]

        result = get_server_price(
            server_name
        )

        # 지원하지 않는 서버
        if result is None:

            send_message(
                chat_id,
                "지원하지 않는 서버입니다."
            )

            return

        send_message(
            chat_id,
            f"📡 {server_name} 서버 시세 조회 중..."
        )

        send_message(
            chat_id,
            result
        )

    # ===== 일반 채팅 무시 =====
    else:

        return


# ===== 업데이트 =====
def get_updates(offset=None):

    url = f"{BASE_URL}/getUpdates"

    params = {
        "timeout": 30
    }

    if offset:

        params["offset"] = offset

    try:

        response = requests.get(
            url,
            params=params,
            timeout=35
        )

        return response.json()

    except Exception as e:

        print("get_updates 오류:", e)

        return {"result": []}


# ===== 메인 =====
def main():

    offset = None

    # ===== 이전 메시지 제거 =====
    data = get_updates()

    if (
        "result" in data
        and len(data["result"]) > 0
    ):

        offset = (
            data["result"][-1]["update_id"] + 1
        )

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

                            print("메시지 처리 오류:", e)

                    offset = (
                        update["update_id"] + 1
                    )

            time.sleep(1)

        except Exception as e:

            print("메인 루프 오류:", e)

            time.sleep(5)


# ===== 시작 =====
if __name__ == "__main__":

    print("게임 시세 봇 실행 중...")

    keep_alive()

    while True:

        try:

            main()

        except Exception as e:

            print("치명적 오류:", e)

            time.sleep(10)