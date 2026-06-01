import os
import ffmpeg
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, APIC
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, 
    CallbackQueryHandler, ConversationHandler, ContextTypes
)

WAIT_MEDIA, WAIT_ARTIST, WAIT_COVER = range(3)
TOKEN = "8739864488:AAGGc_TvRs2IkYnQJgz7QaoCxp31Yilt8fM"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ses veya video dosyası gönderin")
    return WAIT_MEDIA

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.effective_attachment.get_file()
    await file.download_to_drive("input_media.tmp")
    await update.message.reply_text("sanatçı ismini girin")
    return WAIT_ARTIST

async def handle_artist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['artist'] = update.message.text
    keyboard = [[InlineKeyboardButton("/skip", callback_data='skip')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("kapak fotoğrafı gönderin veya /skip yazın", reply_markup=reply_markup)
    return WAIT_COVER

async def handle_cover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("cover.jpg")
    await send_final_audio(update, context, "cover.jpg")
    return ConversationHandler.END

async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await send_final_audio(update, context, None)
    return ConversationHandler.END

async def send_final_audio(update, context, cover_path):
    try:
        # ffmpeg'i sistemdeki konumundan çalıştır
        ffmpeg.input("input_media.tmp").output("output.mp3").run(overwrite_output=True, cmd='ffmpeg')
        
        audio = MP3("output.mp3", ID3=ID3)
        audio.tags.add(TPE1(encoding=3, text=context.user_data['artist']))
        if cover_path:
            with open(cover_path, 'rb') as f:
                audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=f.read()))
        audio.save()
        
        msg = update.message if update.message else update.callback_query.message
        await msg.reply_audio(
            audio=open("output.mp3", "rb"), 
            caption="işlem tamamlandı. yeni dosya için /start"
        )
    except Exception as e:
        msg = update.message if update.message else update.callback_query.message
        await msg.reply_text(f"xəta baş verdi: {str(e)}")

def main():
    app = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAIT_MEDIA: [MessageHandler(filters.AUDIO | filters.VIDEO | filters.Document.ALL, handle_media)],
            WAIT_ARTIST: [MessageHandler(filters.TEXT, handle_artist)],
            WAIT_COVER: [MessageHandler(filters.PHOTO, handle_cover), CallbackQueryHandler(skip, pattern='skip')]
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False
    )
    app.add_handler(conv_handler)
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
