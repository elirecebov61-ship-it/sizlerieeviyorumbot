import logging
import os
import asyncio
from telegram import Update, ChatPermissions
from telegram.ext import (
    Application, MessageHandler,
    ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN      = os.environ["BOT_TOKEN"]
FOUNDER_ID = 8034872992

# Yetkili istifadəçilər (RAM-da saxlanır)
authorized: set[int] = set()

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return
    if update.effective_chat.type == "private":
        return

    msg  = update.message
    uid  = update.effective_user.id
    text = msg.text or ""

    # ── /c31k — yetki ver ─────────────────────────────────────────────────
    if text.startswith("/c31k"):
        if uid != FOUNDER_ID:
            return
        if not msg.reply_to_message:
            await msg.reply_text("❗ Birine yanıt verip /c31k yaz.")
            return
        target = msg.reply_to_message.from_user
        authorized.add(target.id)
        await msg.reply_text(f"✅ {target.first_name} yetki aldı.")
        return

    # ── /yarrak — herkesi banla ───────────────────────────────────────────
    if text.startswith("/yarrak"):
        if uid != FOUNDER_ID and uid not in authorized:
            return

        cid      = update.effective_chat.id
        bildirim = await msg.reply_text("🔨 Banlanıyor...")

        banned  = 0
        skipped = 0

        try:
            async for member in ctx.bot.get_chat_members(cid):
                user = member.user
                # Botu, kurucuyu və yetkilileri atla
                if user.is_bot:
                    skipped += 1
                    continue
                if user.id == FOUNDER_ID:
                    skipped += 1
                    continue
                if user.id in authorized:
                    skipped += 1
                    continue
                try:
                    await ctx.bot.ban_chat_member(cid, user.id)
                    banned += 1
                    # 30 ban/saniyə limitini aşmamaq üçün
                    if banned % 30 == 0:
                        await asyncio.sleep(1)
                except Exception as e:
                    logger.warning(f"Ban xətası {user.id}: {e}")
                    skipped += 1
        except Exception as e:
            await bildirim.edit_text(f"❌ Hata: {e}")
            return

        await bildirim.edit_text(
            f"✅ Tamamlandı!\n"
            f"🔨 Banlanan: {banned}\n"
            f"⏭ Atlanan: {skipped}"
        )

async def post_init(app: Application):
    # Komut siyahısında göstərmə
    await app.bot.set_my_commands([])

def main():
    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, handle_message))

    print("Ban botu başladı...")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
