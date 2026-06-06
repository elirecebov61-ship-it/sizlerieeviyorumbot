import os
import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import RetryAfter

# Logları aktivləşdiririk ki, Railway-də nə baş verdiyini görə biləsən
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 8034872992 

spam_task = None
stop_event = asyncio.Event()

async def spam_loop(chat_id, context):
    i = 0
    while not stop_event.is_set():
        i += 1
        try:
            await context.bot.send_message(chat_id=chat_id, text=f". {i}")
            await asyncio.sleep(0.5) 
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            logging.error(f"Xəta: {e}")
            break

async def start_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global spam_task
    # Yalnız admin yoxlaması
    if update.effective_user.id != ADMIN_ID:
        return

    # Əgər artıq işləyirsə, əvvəlkinin bitməsini gözlə
    if spam_task and not spam_task.done():
        stop_event.set()
        await spam_task

    stop_event.clear()
    spam_task = asyncio.create_task(spam_loop(update.effective_chat.id, context))
    await update.message.reply_text("Spam başladı!")

async def stop_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    stop_event.set()
    await update.message.reply_text("Spam dayandırıldı.")

if __name__ == '__main__':
    if not TOKEN:
        print("Xəta: BOT_TOKEN tapılmadı!")
        exit()
        
    print("Bot işə salınır...")
    app = ApplicationBuilder().token(TOKEN).drop_pending_updates(True).build()
    
    app.add_handler(CommandHandler("start", start_spam))
    app.add_handler(CommandHandler("stop", stop_spam))
    
    print("Bot uğurla işə düşdü!")
    app.run_polling()
