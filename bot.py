import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import RetryAfter

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 8034872992 

# Spam prosesini idarə etmək üçün qlobal dəyişən
spam_task = None
stop_event = asyncio.Event()

async def spam_loop(chat_id, context):
    """Mesaj göndərmə dövrü"""
    i = 0
    while not stop_event.is_set():
        i += 1
        try:
            await context.bot.send_message(chat_id=chat_id, text=f". {i}")
            await asyncio.sleep(0.5) # Sürəti buradan tənzimləyə bilərsən
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            break

async def start_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global spam_task
    if update.effective_chat.type == 'private' or update.effective_user.id != ADMIN_ID:
        return

    # Əgər artıq işləyən spam varsa, dayandır
    if spam_task and not spam_task.done():
        stop_event.set()
        await spam_task

    stop_event.clear()
    spam_task = asyncio.create_task(spam_loop(update.effective_chat.id, context))
    await update.message.reply_text("Spam başladı!")

async def stop_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global spam_task
    if update.effective_user.id != ADMIN_ID:
        return

    stop_event.set()
    await update.message.reply_text("Spam dayandırıldı.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_spam))
    app.add_handler(CommandHandler("stop", stop_spam))
    
    app.run_polling()
