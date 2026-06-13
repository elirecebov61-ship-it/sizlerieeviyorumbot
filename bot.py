import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors import PeerFloodError, UserPrivacyRestrictedError, UserAlreadyParticipantError

# API məlumatlarını daxil et
API_ID = 1234567 
API_HASH = 'hash_buraya'
SESSION_NAME = 'my_userbot'

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# 'from_users="me"' hissəsi botun yalnız sənin yazdığın mesajlara reaksiya verməsini təmin edir
@client.on(events.NewMessage(pattern='/add', from_users='me'))
async def handler(event):
    await event.edit("🚀 Köçürmə prosesi başladı...") # Mesajı cavaba dəyişir
    
    source_group = 'kaynaq_qrup_username' 
    target_group = 'hedef_qrup_username'
    
    target_participants = {u.id async for u in client.iter_participants(target_group)}
    count = 0
    
    async for user in client.iter_participants(source_group):
        if user.bot or user.id in target_participants:
            continue
        
        try:
            await client(InviteToChannelRequest(target_group, [user]))
            target_participants.add(user.id)
            count += 1
            await asyncio.sleep(45) 
            
        except UserPrivacyRestrictedError:
            continue
        except UserAlreadyParticipantError:
            continue
        except PeerFloodError:
            await event.edit("⚠️ Flood xətası! 1 saatlıq fasilə.")
            return # Prosesi dayandır
        except Exception as e:
            continue
            
    await event.edit(f"✅ Köçürmə bitdi! Cəmi əlavə edildi: {count}")

client.start()
client.run_until_disconnected()
