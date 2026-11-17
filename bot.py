import threading, asyncio, os, re, requests
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Ye 2 line sabse important hai - isse wo loop wala error nahi aayega
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

flask_app = Flask(__name__)

@flask_app.route('/')
def home(): return "Bot Alive"

threading.Thread(target=lambda: flask_app.run(host='0.0.0.0', port=10000), daemon=True).start()

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
AROLINKS_API_KEY = os.environ.get("AROLINKS_API_KEY", "")

DATABASE_CHANNEL = -1003449225454
MAIN_CHANNEL_1 = -1004304048469
MAIN_CHANNEL_2 = -1004304048469

DEFAULT_PREMIUM = "https://t.me/+xpELQlA1L01mMTU1"
DEFAULT_BACKUP = "https://t.me/+Nx-iXXU-cE0yYjk1"

pending = {}

def short_with_arolinks(long_url):
    try:
        r = requests.get(f"https://arolinks.com/api?api={AROLINKS_API_KEY}&url={long_url}", timeout=15).json()
        return r.get("shortenedUrl", long_url)
    except:
        return long_url

app = Client("auto_uploadee_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.chat(DATABASE_CHANNEL))
async def handle(client, message):
    global pending
    text = message.text or message.caption or ""
    file_id = None
    file_type = None
    if message.photo:
        file_id = message.photo.file_id; file_type = 'photo'
    elif message.video:
        file_id = message.video.file_id; file_type = 'video'
    elif message.animation:
        file_id = message.animation.file_id; file_type = 'animation'

    if file_id:
        pending = {'file_id': file_id, 'type': file_type, 'caption': text}
        return

    if pending and "http" in text:
        clean_text = text.replace("\n", "").replace(" ", "")
        urls = re.findall(r'https?://[^\s]+', clean_text)
        if urls:
            short_url = short_with_arolinks(urls[0])
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("WATCH & DOWNLOAD", url=short_url)],
                [InlineKeyboardButton("Premium Plans", url=DEFAULT_PREMIUM),
                 InlineKeyboardButton("Join Backup", url=DEFAULT_BACKUP)]
            ])
            for ch in [MAIN_CHANNEL_1, MAIN_CHANNEL_2]:
                if pending['type'] == 'photo':
                    await app.send_photo(ch, pending['file_id'], caption=pending['caption'], reply_markup=buttons)
                elif pending['type'] == 'video':
                    await app.send_video(ch, pending['file_id'], caption=pending['caption'], reply_markup=buttons)
                else:
                    await app.send_animation(ch, pending['file_id'], caption=pending['caption'], reply_markup=buttons)
            pending = {}

app.run()