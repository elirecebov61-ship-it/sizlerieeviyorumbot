import os
import asyncio
import logging
from telegram.ext import ApplicationBuilder, CommandHandler

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 8034872992 

spam_task = None
stop_event = asyncio.Event()

# ... (start_spam və stop_spam funksiyaları eyni qalır) ...
async def start_spam(update, context):
    global spam_task
    if update.effective_user.id != ADMIN_ID: return
    if spam_task and not spam_task.done():
        stop_event.set()
        await spam_task
    stop_event.clear()
    spam_task = asyncio.create_task(spam_loop(update.effective_chat.id, context))
    await update.message.reply_text("Spam başladı!")

async def stop_spam(update, context):
    if update.effective_user.id != ADMIN_ID: return
    stop_event.set()
    await update.message.reply_text("Spam dayandırıldı.")

async def spam_loop(chat_id, context):
    i = 0
    while not stop_event.is_set():
        i += 1
        try:
            await context.bot.send_message(chat_id=chat_id, text=f". {i}")
            await asyncio.sleep(0.5)
        except Exception: break

if __name__ == '__main__':
    # 1. Builder-i qur
    builder = ApplicationBuilder().token(TOKEN)
    app = builder.build()
    
    # 2. Handler-ləri əlavə et
    app.add_handler(CommandHandler("start", start_spam))
    app.add_handler(CommandHandler("stop", stop_spam))
    
    print("Bot işə salınır...")
    # 3. İndi polling-i başlat, amma drop_pending_updates-i burada yox, 
    # botun başlanğıcında Telegram serverinə məcburi bildiririk
    app.run_polling(drop_pending_updates=True) 
