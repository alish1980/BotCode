import requests
import pandas as pd
import time

# توکن ربات بله (جایگزین کنید)
TOKEN = "79470467:YcCahVfKnQueuYDgi5UptrwvLJvZXRsFYVbRMSKp"
API_URL = f"https://tapi.bale.ai/bot{TOKEN}"

# خواندن داده‌های بارش از فایل CSV
df = pd.read_csv("rainfall_data.csv")

def send_message(chat_id, text, reply_markup=None):
    """ ارسال پیام به کاربر در بله با دکمه‌های انتخابی """
    url = f"{API_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    
    if reply_markup:
        data["reply_markup"] = reply_markup
    
    requests.post(url, json=data)

def get_main_menu():
    """ ایجاد کیبورد شیشه‌ای برای انتخاب ایستگاه یا حوضه آبریز """
    keyboard = {
        "inline_keyboard": [
            [{"text": "📍 ایستگاه خاص", "callback_data": "choose_station"}],
            [{"text": "💧 حوضه آبریز", "callback_data": "choose_watershed"}]
        ]
    }
    return keyboard

def get_station_buttons():
    """ ایجاد دکمه‌های ایستگاه‌ها براساس CSV """
    stations = df["station_name"].unique()
    keyboard = {
        "inline_keyboard": [[{"text": station, "callback_data": f"station_{station}"}] for station in stations]
    }
    return keyboard

def get_watershed_buttons():
    """ ایجاد دکمه‌های حوضه آبریز براساس CSV """
    watersheds = df["watershed"].unique()
    keyboard = {
        "inline_keyboard": [[{"text": ws, "callback_data": f"watershed_{ws}"}] for ws in watersheds]
    }
    return keyboard

def process_message(update):
    """ پردازش پیام‌های دریافتی از کاربر """
    chat_id = update["message"]["chat"]["id"]
    text = update["message"]["text"].strip()

    if text.lower() == "/start":
        send_message(chat_id, "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:", get_main_menu())

def process_callback(update):
    """ پردازش دکمه‌های فشرده شده توسط کاربر """
    callback_query = update["callback_query"]
    chat_id = callback_query["message"]["chat"]["id"]
    data = callback_query["data"]

    if data == "choose_station":
        send_message(chat_id, "یک ایستگاه را انتخاب کنید:", get_station_buttons())
    elif data == "choose_watershed":
        send_message(chat_id, "یک حوضه آبریز را انتخاب کنید:", get_watershed_buttons())
    elif data.startswith("station_"):
        station_name = data.replace("station_", "")
        result = df[df["station_name"] == station_name]
        if not result.empty:
            rainfall = result.iloc[0]["rainfall"]
            send_message(chat_id, f"📍 ایستگاه {station_name}\n🌧 میزان بارش: {rainfall} میلی‌متر")
    elif data.startswith("watershed_"):
        watershed = data.replace("watershed_", "")
        result = df[df["watershed"] == watershed]
        if not result.empty:
            response = f"💧 حوضه آبریز {watershed}:\n"
            for _, row in result.iterrows():
                response += f"📍 ایستگاه {row['station_name']}: {row['rainfall']} میلی‌متر\n"
            send_message(chat_id, response)

def get_updates(offset=None):
    """ دریافت پیام‌های جدید از بله """
    url = f"{API_URL}/getUpdates"
    params = {"offset": offset} if offset else {}
    response = requests.get(url, params=params).json()
    return response.get("result", [])

def main():
    """ اجرای حلقه اصلی ربات برای پردازش پیام‌ها """
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        for update in updates:
            last_update_id = update["update_id"] + 1
            if "message" in update:
                process_message(update)
            elif "callback_query" in update:
                process_callback(update)
        time.sleep(1)

if __name__ == "__main__":
    main()
