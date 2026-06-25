import asyncio
import os
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from flask import Flask
from threading import Thread

# --- မင်းရဲ့ DATA များ ---
API_ID = 1234567  # ပြင်ရန်
API_HASH = "your_api_hash" # ပြင်ရန်
BOT_TOKEN = "your_bot_token" # ပြင်ရန်

OWNER_ID = 7771663458
OWNER_USERNAME = "Tear808"
BOT_USERNAME = "myaigroup_ai_bot"
CHANNEL_URL = "https://t.me/BOTUAPTE"
GROUP_URL = "https://t.me/+XukiNeB77qw2M2I9"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
groups_db = set()

# --- WEB SERVER FOR RENDER ---
web_server = Flask(__name__)
@web_server.route('/')
def home(): return "Bot is Alive!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    web_server.run(host="0.0.0.0", port=port)

# --- START COMMAND ---
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Message):
    user = message.from_user
    photo_id = None
    try:
        async for photo in client.get_chat_photos(user.id, limit=1):
            photo_id = photo.file_id
    except: pass

    text = (f"👋 မင်္ဂလာပါ {user.mention} ရေ...\n\n"
            f"🆔 ID: `{user.id}`\n"
            f"👤 User: @{user.username if user.username else 'N/A'}\n\n"
            f"ကျွန်တော့်ကို မင်းရဲ့ Group ထဲထည့်ချင်ရင် အောက်က ခလုပ်ကို နှိပ်လိုက်နော်!")
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👨‍💻 Owner", url=f"https://t.me/{OWNER_USERNAME}"), InlineKeyboardButton("📢 Channel", url=CHANNEL_URL)],
        [InlineKeyboardButton("👥 Group", url=GROUP_URL)],
        [InlineKeyboardButton("➕ Add Bot to Your Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")]
    ])
    
    if photo_id: await message.reply_photo(photo_id, caption=text, reply_markup=buttons)
    else: await message.reply_text(text, reply_markup=buttons)

# --- WELCOME SYSTEM (လူဝင်ရင်) ---
@app.on_message(filters.new_chat_members)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        groups_db.add(message.chat.id)
        photo_id = None
        try:
            async for photo in client.get_chat_photos(member.id, limit=1):
                photo_id = photo.file_id
        except: pass
            
        welcome_text = (f"✨ ကြိုဆိုပါတယ် {member.mention} ရေ... ✨\n\n"
                        f"🆔 ID: `{member.id}`\n"
                        f"👤 User: @{member.username if member.username else 'N/A'}\n"
                        f"🏘 Group: {message.chat.title}\n\n"
                        f"ပျော်ရွှင်စွာနဲ့ စာတွေ အတူတူပြောကြရအောင်နော်! 🌸")
        
        buttons = InlineKeyboardMarkup([[InlineKeyboardButton("➕ Add Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")]])
        if photo_id: await message.reply_photo(photo_id, caption=welcome_text, reply_markup=buttons)
        else: await message.reply_text(welcome_text, reply_markup=buttons)

# --- LEFT SYSTEM (လူထွက်ရင်) ---
@app.on_message(filters.left_chat_member)
async def member_left(client, message: Message):
    member = message.left_chat_member
    photo_id = None
    try:
        async for photo in client.get_chat_photos(member.id, limit=1):
            photo_id = photo.file_id
    except: pass

    left_text = (f"👤 {member.mention} (@{member.username if member.username else 'N/A'})\n"
                 f"🆔 ID: `{member.id}`\n\n"
                 f"ငါလေလွှမ်းမြဲ..လွှမ်းစဲ့ပါ\n"
                 f"မင်းဆီက...စာပို့မဲ့💌\n"
                 f"အချိန်ကို  မျော်နေမိတယ်❤️\n"
                 f"အချိန်တိုင်း....🥹\n"
                 f"ချစ်ရသူရယ်...နင်မြင်ပါစေ🌷🌷\n"
                 f"ငါအချစ်တွေ🥀🥀🥀\n\n"
                 f"                    Tear(စာတို)")

    if photo_id: await message.reply_photo(photo_id, caption=left_text)
    else: await message.reply_text(left_text)

# --- REACTION, AUTO-REPLY, FORWARD ---
@app.on_message(filters.all & ~filters.service)
async def main_handler(client, message: Message):
    # Auto Reaction
    try: await message.react(enums.ReactionTypeEmoji(emoji="👍"))
    except: pass

    # Member to Owner Forward
    if message.chat.type == enums.ChatType.PRIVATE and message.from_user.id != OWNER_ID:
        await message.forward(OWNER_ID)

    # Group Auto Reply
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        groups_db.add(message.chat.id)
        if message.text and not message.from_user.is_bot:
            await message.reply_text(f"'{message.text}' တဲ့လား... ချစ်စရာလေးနော် 😍")

# --- BROADCAST & STATS ---
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(client, message: Message):
    if not message.reply_to_message: return await message.reply_text("စာကို Reply ထောက်ပြီး /broadcast ရိုက်ပါ။")
    sent = 0
    for chat_id in list(groups_db):
        try:
            await message.reply_to_message.copy(chat_id)
            sent += 1
            await asyncio.sleep(0.3)
        except: continue
    await message.reply_text(f"✅ Group {sent} ခုကို ပို့ပြီးပါပြီ။")

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats(client, message: Message):
    await message.reply_text(f"📊 လက်ရှိ Bot သုံးနေတဲ့ Group ပေါင်း: {len(groups_db)}")

if __name__ == "__main__":
    Thread(target=run_server).start()
    print("Bot is Started!")
    app.run()
