import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    CallbackQueryHandler, 
    ConversationHandler, 
    ContextTypes
)

# Mərhələlər
WAIT_MEDIA, WAIT_ARTIST, WAIT_COVER = range(3)

TOKEN = "8739864488:AAGN_GXGEJn-JToWQPRutHwQ7bhYEd7NhK8"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ses veya video dosyası gönderin")
    return WAIT_MEDIA

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("sanatçı ismini girin")
    return WAIT_ARTIST

async def handle_artist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['artist'] = update.message.text
    keyboard = [[InlineKeyboardButton("/skip", callback_data='skip')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("kapak fotoğrafı gönderin veya /skip yazın", reply_markup=reply_markup)
    return WAIT_COVER

async def handle_cover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("işlem tamamlandı. yeni dosya için /start")
    return ConversationHandler.END

async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("İşlem tamamlandı.")
    return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("hata: islem tamamlanamadi. ffmpeg yuklu mu?")
    return WAIT_MEDIA

def main():
    app = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAIT_MEDIA: [MessageHandler(filters.AUDIO | filters.VIDEO | filters.DOCUMENT, handle_media)],
            WAIT_ARTIST: [MessageHandler(filters.TEXT, handle_artist)],
            WAIT_COVER: [MessageHandler(filters.PHOTO, handle_cover), CallbackQueryHandler(skip, pattern='skip')]
        },
        fallbacks=[MessageHandler(filters.ALL, error_handler)]
    )
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == '__main__':
    main()
