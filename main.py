import os
import json
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["BOT_TOKEN"]
OWNER_ID  = 8034872992
DATA_FILE = "videos.json"

app = Client("videobot", bot_token=BOT_TOKEN)

def load_videos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_videos(videos):
    with open(DATA_FILE, "w") as f:
        json.dump(videos, f)

@app.on_message(filters.command("start") & filters.user(OWNER_ID))
async def cmd_start(client, message: Message):
    await message.reply(
        "👋 Merhaba!\n\n"
        "📹 Video gönder → bot kaydetsin\n"
        "/send → videoları gruba gönder\n"
        "/liste → kaç video kaydedildi\n"
        "/sil → tüm videoları sil"
    )

@app.on_message(filters.video & filters.private & filters.user(OWNER_ID))
async def receive_video(client, message: Message):
    file_id = message.video.file_id
    videos = load_videos()
    videos.append(file_id)
    save_videos(videos)
    await message.reply(f"✅ Video kaydedildi! Toplam: {len(videos)} video")

@app.on_message(filters.command("liste") & filters.user(OWNER_ID))
async def cmd_liste(client, message: Message):
    videos = load_videos()
    if not videos:
        await message.reply("📭 Hiç video kaydedilmedi.")
    else:
        await message.reply(f"📹 Kayıtlı video sayısı: {len(videos)}")

@app.on_message(filters.command("sil") & filters.user(OWNER_ID))
async def cmd_sil(client, message: Message):
    save_videos([])
    await message.reply("🗑️ Tüm videolar silindi.")

@app.on_message(filters.command("send") & filters.user(OWNER_ID))
async def cmd_send(client, message: Message):
    videos = load_videos()
    if not videos:
        await message.reply("📭 Gönderilecek video yok. Önce bota video gönder.")
        return

    chat_id = message.chat.id
    await message.reply(f"🚀 {len(videos)} video gönderiliyor...")

    sent = 0
    for file_id in videos:
        try:
            await client.send_video(chat_id=chat_id, video=file_id)
            sent += 1
        except Exception as e:
            logging.error(f"Hata: {e}")

    await client.send_message(chat_id=chat_id, text=f"✅ {sent} video gönderildi!")

print("Bot başlatıldı...")
app.run()
