import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import UserStatusOnline, UserStatusRecently, UserStatusLastWeek
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

@bot.on(events.NewMessage(pattern='/start', incoming=True))
async def check_status(event):
    if event.sender_id != OWNER_ID or not event.is_private:
        return
    await event.respond("🟢 Bot aktif, 1 hesab hazırdır!")

@bot.on(events.NewMessage(pattern='/c31k'))
async def start_adding(event):
    if event.sender_id != OWNER_ID:
        return
    await event.respond("🚀 Əlavə etmə başladı!")
    asyncio.create_task(run_all())

async def add_users(userbot, participants, index):
    added_count = 0
    try:
        target = await userbot.get_entity(int(TARGET_GROUP))
    except Exception as e:
        print(f"[-] Target tapılmadı: {e}")
        return

    for user in participants:
        try:
            await userbot(InviteToChannelRequest(target, [user]))
            added_count += 1
            print(f"[Hesab {index}][{added_count}] Əlavə edildi: {user.username}")
            await asyncio.sleep(20)
        except PeerFloodError:
            print(f"[-] Flood limitə düşdü. Toplam: {added_count}")
            break
        except UserPrivacyRestrictedError:
            continue
        except UserAlreadyParticipantError:
            continue
        except Exception as e:
            print(f"[-] Xəta: {e}")
            await asyncio.sleep(5)

    print(f"[✅] Bitdi. Əlavə edilən: {added_count}")

async def run_all():
    target_id = int(TARGET_GROUP)

    existing_users = set()
    async for user in userbot1.iter_participants(target_id):
        existing_users.add(user.id)
    print(f"[+] Qrupda artıq {len(existing_users)} nəfər var.")

    all_participants = []
    async for user in userbot1.iter_participants(SOURCE_GROUP):
        if not user.bot and user.username:
            if user.id in existing_users:
                continue
            if isinstance(user.status, (UserStatusOnline, UserStatusRecently, UserStatusLastWeek)):
                all_participants.append(user)

    print(f"[+] Əlavə ediləcək {len(all_participants)} nəfər tapıldı.")
    await add_users(userbot1, all_participants, 1)
    print("[🏁] Bitdi!")

async def main():
    await userbot1.start()
    await bot.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
