import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import PeerFloodError, UserPrivacyRestrictedError, UserAlreadyParticipantError

# API məlumatların
API_ID = 1234567 
API_HASH = 'hash_buraya'
SESSION_NAME = 'my_userbot' # .session faylının adı

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def main():
    await client.start()
    
    # Qrup ID-ləri və ya username-ləri
    source_group = 'kaynaq_qrup_username' 
    target_group = 'hedef_qrup_username'
    
    # Hədəf qrupdakıları əvvəlcədən siyahıya al (təkrar əlavə etməmək üçün)
    target_participants = {u.id async for u in client.iter_participants(target_group)}
    
    print("Köçürmə başlayır...")
    
    async for user in client.iter_participants(source_group):
        # Botları və artıq qrupda olanları keç
        if user.bot or user.id in target_participants:
            continue
        
        try:
            print(f"Əlavə edilir: {user.username or user.id}")
            await client(InviteToChannelRequest(target_group, [user]))
            target_participants.add(user.id)
            print("✅ Uğurla əlavə edildi.")
            await asyncio.sleep(45) # 45 saniyəlik təhlükəsizlik fasiləsi
            
        except UserPrivacyRestrictedError:
            print("❌ Məxfilik parametri bağlıdır (keçildi).")
            continue
        except UserAlreadyParticipantError:
            print("ℹ️ Artıq qrupdadır (keçildi).")
            continue
        except PeerFloodError:
            print("⚠️ Flood xətası! 1 saatlıq fasilə verilir.")
            await asyncio.sleep(3600)
        except Exception as e:
            print(f"❌ Xəta: {e}")
            continue

with client:
    client.loop.run_until_complete(main())

