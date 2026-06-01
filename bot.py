import os
import glob
import asyncio
import subprocess
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, APIC
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, 
    CallbackQueryHandler, ConversationHandler, ContextTypes
)

WAIT_MEDIA, WAIT_ARTIST, WAIT_COVER = range(3)
TOKEN = "8739864488:AAGMynOtY1c6ZpOvNI9KPyonu9mpoEOAP7s"

def find_ffmpeg():
    possible_paths = [
        '/usr/bin/ffmpeg',
        '/usr/local/bin/ffmpeg',
        '/nix/var/nix/profiles/default/bin/ffmpeg',
        'ffmpeg'
    ]
    for path in possible_paths:
        try:
            result = subprocess.run([path, '-version'], capture_output=True, timeout=5)
            if result.returncode == 0:
                return path
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    found = glob.glob('/nix/**/ffmpeg', recursive=True)
    if found:
        return found[0]
    return None

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
    msg = update.message if update.message else update.callback_query.message

    try:
        ffmpeg_path = find_ffmpeg()
        if not ffmpeg_path:
            await msg.reply_text("xəta baş verdi: ffmpeg tapılmadı")
            return

        cmd = [ffmpeg_path, '-y', '-i', 'input_media.tmp',
               '-vn', '-ar', '44100', '-ac', '2', '-b:a', '192k', 'output.mp3']
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            await msg.reply_text(f"xəta baş verdi: {result.stderr[-300:]}")
            return

        audio = MP3("output.mp3", ID3=ID3)
        if audio.tags is None:
            audio.add_tags()
        audio.tags.add(TPE1(encoding=3, text=context.user_data['artist']))

        if cover_path and os.path.exists(cover_path):
            with open(cover_path, 'rb') as f:
                audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=f.read()))
        audio.save()

        with open("output.mp3", "rb") as audio_file:
            await msg.reply_audio(audio=audio_file, caption="işlem tamamlandı. yeni dosya için /start")

    except Exception as e:
        await msg.reply_text(f"xəta baş verdi: {str(e)}")

    finally:
        for f in ["input_media.tmp", "output.mp3", "cover.jpg"]:
            if os.path.exists(f):
                os.remove(f)

def main():
    app = Application.builder().token(TOKEN).build()

    async def clear_webhook():
        await app.bot.delete_webhook(drop_pending_updates=True)
    asyncio.get_event_loop().run_until_complete(clear_webhook())

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAIT_MEDIA: [MessageHandler(filters.AUDIO | filters.VIDEO | filters.Document.ALL, handle_media)],
            WAIT_ARTIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_artist)],
            WAIT_COVER: [MessageHandler(filters.PHOTO, handle_cover), CallbackQueryHandler(skip, pattern='skip')]
        },
        fallbacks=[CommandHandler("start", start)],
        per_message=False,
        per_chat=True,
    )
    app.add_handler(conv_handler)
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
