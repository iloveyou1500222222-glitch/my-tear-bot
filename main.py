import asyncio
import os
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from flask import Flask
from threading import Thread

# --- API Keys (Render Settings မှ ခေါ်ယူရန်) ---
API_ID = int(os.environ.get("API_ID", 1234567))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

# --- Configurations ---
OWNER_ID = 7771663458
OWNER_USERNAME = "Tear808"
BOT_USERNAME = "myaigroup_ai_bot"
CHANNEL_URL = "https://t.me/BOTUAPTE"
GROUP_URL = "https://t.me/+XukiNeB77qw2M2I9"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
groups_db = set()

# --- WEB SERVER (Render အတွက်) ---
web_server = Flask(__name__)
@web_server.route('/')
def home(): return "Bot is Alive!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    web_server.run(host="0.0.0.0", port=port)

# --- COMMANDS & HANDLERS ---
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Message):
    user = message.from_user
    text = (f"👋 မင်္ဂလာပါ {user.mention} ရေ...\n\n"
            f"ကျွန်တော့်ကို Group ထဲထည့်ချင်ရင် အောက်က ခလုတ်ကို နှိပ်ပါ!")
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("👨‍💻 Owner", url=f"https://t.me/{OWNER_USERNAME}"), InlineKeyboardButton("📢 Channel", url=CHANNEL_URL)],
        [InlineKeyboardButton("👥 Group", url=GROUP_URL)],
        [InlineKeyboardButton("➕ Add Bot", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")]
    ])
    await message.reply_text(text, reply_markup=buttons)

@app.on_message(filters.new_chat_members)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        groups_db.add(message.chat.id)
        await message.reply_text(f"✨ ကြိုဆိုပါတယ် {member.mention} ရေ!")

@app.on_message(filters.left_chat_member)
async def member_left(client, message: Message):
    await message.reply_text("နောက်မှ ပြန်လာခဲ့နော်! 🥀")

@app.on_message(filters.all & ~filters.service)
async def main_handler(client, message: Message):
    try: await message.react(enums.ReactionTypeEmoji(emoji="👍"))
    except: pass
    
    if message.chat.type == enums.ChatType.PRIVATE and message.from_user.id != OWNER_ID:
        await message.forward(OWNER_ID)

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(client, message: Message):
    if not message.reply_to_message: return await message.reply_text("စာကို Reply ထောက်ပြီး /broadcast ရိုက်ပါ။")
    sent = 0
    for chat_id in list(groups_db):
        try:
            await message.reply_to_message.copy(chat_id)
            sent += 1
        except: continue
    await message.reply_text(f"✅ Group {sent} ခုကို ပို့ပြီးပါပြီ။")

@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats(client, message: Message):
    await message.reply_text(f"📊 လက်ရှိ Bot သုံးနေတဲ့ Group ပေါင်း: {len(groups_db)}")

if __name__ == "__main__":
    Thread(target=run_server, daemon=True).start()
    app.run()
  
