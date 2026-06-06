import os
import asyncio
import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram.error import RetryAfter

# Logları aktivləşdiririk ki, bir problem olsa görə biləsən
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 8034872992 

spam_task = None
stop_event = asyncio.Event()

async def spam_loop(chat_id, context):
    i = 0
    # Stop əmri gələnə kimi dayanmadan davam edir
    while not stop_event.is_set():
        i += 1
        try:
            # 1 saniyəlik fasilə ilə göndərir
            await context.bot.send_message(chat_id=chat_id, text=f". {i}")
            await asyncio.sleep(1.0) 
        except RetryAfter as e:
            # Əgər Telegram limitə çatdıq deyirsə, tam lazım olan qədər gözləyir
            logging.warning(f"Limit aşıldı, {e.retry_after} saniyə gözlənilir...")
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            logging.error(f"Xəta baş verdi: {e}")
            break

async def start_spam(update, context):
    global spam_task
    # Yalnız admin yoxlaması
    if update.effective_user.id != ADMIN_ID: return
    
    # Əgər əvvəlki proses hələ də aktivdirsə, onu dayandır
    if spam_task and not spam_task.done():
        stop_event.set()
        await spam_task

    stop_event.clear()
    spam_task = asyncio.create_task(spam_loop(update.effective_chat.id, context))
    await update.message.reply_text("Spam başladı! (Dayandırmaq üçün /stop yaz)")

async def stop_spam(update, context):
    stop_event.set()
    await update.message.reply_text("Spam dayandırıldı.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_spam))
    app.add_handler(CommandHandler("stop", stop_spam))
    print("Bot işə salındı və hazırdır.")
    app.run_polling(drop_pending_updates=True)
