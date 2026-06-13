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

async def get_entity_flexible(client, group):
    """Həm group username, həm də kanal ID-si üçün entity al"""
    try:
        # Əgər rəqəmdirsə integer-ə çevir
        group_id = int(group)
        return await client.get_entity(group_id)
    except ValueError:
        # Username və ya link
        return await client.get_entity(group)

async def run_all():
    global is_running

    # Source və target entity-lərini al (group və ya channel olsun, fərqi yox)
    try:
        source_entity = await get_entity_flexible(userbot1, SOURCE_GROUP)
        target_entity = await get_entity_flexible(userbot1, TARGET_GROUP)
    except Exception as e:
        print(f"[-] Qrup/kanal tapılmadı: {e}")
        is_running = False
        return

    # Target-dəki mövcud üzvlər
    existing_users = set()
    try:
        async for user in userbot1.iter_participants(target_entity):
            existing_users.add(user.id)
    except Exception as e:
        print(f"[-] Target üzvlər alınmadı: {e}")
        is_running = False
        return

    # Source-dan üzvləri yığ (bot olmayanlar, artıq target-də olmayanlar)
    all_participants = []
    try:
        async for user in userbot1.iter_participants(source_entity):
            if user.bot:
                continue
            if user.id in existing_users:
                continue
            all_participants.append(user)
    except Exception as e:
        print(f"[-] Source üzvlər alınmadı: {e}")
        is_running = False
        return

    print(f"[+] Əlavə ediləcək {len(all_participants)} yeni nəfər tapıldı.")

    if len(all_participants) == 0:
        print("[!] Yeni üzv yoxdur.")
        is_running = False
        return

    added_count = 0
    skipped_count = 0

    for user in all_participants:
        try:
            await userbot1(InviteToChannelRequest(target_entity, [user]))
            added_count += 1
            label = user.username if user.username else f"id:{user.id}"
            print(f"[+] {added_count} | {label}")
            await asyncio.sleep(20)
        except PeerFloodError:
            print(f"[-] Flood xətası. Dayandırıldı. Toplam: {added_count}")
            break
        except UserAlreadyParticipantError:
            skipped_count += 1
            continue
        except UserPrivacyRestrictedError:
            # Username-siz istifadəçilər bəzən privacy xətası verir — keç
            skipped_count += 1
            continue
        except Exception as e:
            print(f"[-] Xəta ({user.id}): {e}")
            await asyncio.sleep(5)

    print(f"[✅] Bitdi. Əlavə edilən: {added_count} | Keçilən: {skipped_count}")
    is_running = False

async def main():
    await userbot1.start()
    await bot.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
