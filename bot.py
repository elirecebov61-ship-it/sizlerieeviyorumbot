import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import FloodControlExceeded

# Railway-də Environment Variables hissəsindən BOT_TOKEN-i əlavə et
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = 8034872992 

async def spam_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Yalnız qrup üçün yoxlama
    if update.effective_chat.type == 'private':
        return 

    # Yalnız sənin ID-n üçün yoxlama
    if update.effective_user.id != ADMIN_ID:
        return

    chat_id = update.effective_chat.id
    
    # Dövr (məsələn, 50 dəfə)
    for i in range(50):
        try:
            await context.bot.send_message(chat_id=chat_id, text=f". {i+1}")
            await asyncio.sleep(0.1) # Sürəti tənzimləyir
        except FloodControlExceeded as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            break

if __name__ == '__main__':
    if not TOKEN:
        print("Xəta: BOT_TOKEN tapılmadı!")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()
    
    # CommandHandler-i .start olaraq dəyişdik
    app.add_handler(CommandHandler("start", spam_start))
    
    print("Bot işə düşdü...")
    app.run_polling()

