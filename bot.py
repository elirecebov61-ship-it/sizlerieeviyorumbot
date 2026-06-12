import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, UserAlreadyParticipantError

API_ID = int(os.getenv("API_ID", 1234567))
API_HASH = os.getenv("API_HASH", "varsayilan_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "bura_bot_token")
SESSION_1 = os.getenv("SESSION_1", "")

SOURCE_GROUP = os.getenv("SOURCE_GROUP", "cekilecek_grup")
TARGET_GROUP = os.getenv("TARGET_GROUP", "eklenecek_grup")

OWNER_ID = 8034872992

bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
userbot1 = TelegramClient(StringSession(SESSION_1), API_ID, API_HASH)

is_running = False

@bot.on(events.NewMessage(pattern='/start', incoming=True))
async def check_status(event):
    if event.sender_id != OWNER_ID or not event.is_private:
        return
    await event.respond("🟢 Bot aktif!")

@bot.on(events.NewMessage(pattern='/c31k'))
async def start_adding(event):
    global is_running
    if event.sender_id != OWNER_ID:
        return
    if is_running:
        await event.respond("⚠️ Artıq işləyir!")
        return
    is_running = True
    await event.respond("🚀 Başladı!")
    asyncio.create_task(run_all())

async def run_all():
    global is_running
    target_id = int(TARGET_GROUP)

    existing_users = set()
    async for user in userbot1.iter_participants(target_id):
        existing_users.add(user.id)

    all_participants = []
    async for user in userbot1.iter_participants(SOURCE_GROUP):
        if user.bot:
            continue
        if not user.username:
            continue
        if user.id in existing_users:
            continue
        all_participants.append(user)

    print(f"[+] Əlavə ediləcək {len(all_participants)} yeni nəfər tapıldı.")

    if len(all_participants) == 0:
        print("[!] Yeni üzv yoxdur.")
        is_running = False
        return

    added_count = 0
    try:
        target = await userbot1.get_entity(target_id)
    except Exception as e:
        print(f"[-] Target tapılmadı: {e}")
        is_running = False
        return

    for user in all_participants:
        try:
            await userbot1(InviteToChannelRequest(target, [user]))
            added_count += 1
            print(f"[+] {added_count} | {user.username}")
            await asyncio.sleep(20)
        except PeerFloodError:
            print(f"[-] Flood. Toplam: {added_count}")
            break
        except (UserPrivacyRestrictedError, UserAlreadyParticipantError):
            continue
        except Exception as e:
            print(f"[-] Xəta: {e}")
            await asyncio.sleep(5)

    print(f"[✅] Bitdi. Əlavə edilən: {added_count}")
    is_running = False

async def main():
    await userbot1.start()
    await bot.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
