import json
import os
from config import ADMIN_IDS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Database Load/Save
def load(f): 
    try: with open(f, 'r') as file: return json.load(file)
    except: return {}

def save(f, data):
    with open(f, 'w') as file: json.dump(data, file)

groups, replies, users = load("groups.json"), load("replies.json"), load("users.json")

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    user = u.effective_user
    users[str(user.id)] = user.first_name
    save("users.json", users)
    
    # ခလုတ်များ တည်ဆောက်ခြင်း
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Channel", url="https://t.me/BOTSPTE")],
        [InlineKeyboardButton("👑 Owner", url="https://t.me/Tear808")],
        [InlineKeyboardButton("➕ Group ထဲသို့ထည့်ရန်", url="https://t.me/myaigroup_ai_bot?startgroup=true")]
    ])
    
    username = f"@{user.username}" if user.username else "မရှိပါ"
    text = (f"ဟယ်လို သဲသဲရေ! 👋\n\n"
            f"👤 နာမည်: {user.first_name}\n"
            f"🆔 ID: `{user.id}`\n"
            f"🔗 Username: {username}\n\n"
            f"သဲ ကို စတင်ရန် အဆင်သင့်ဖြစ်ပါပြီရှင်။ 🥰")
    
    photos = await c.bot.get_user_profile_photos(user.id)
    if photos.total_count > 0:
        await u.message.reply_photo(photo=photos.photos[0][0].file_id, caption=text, reply_markup=kb, parse_mode='Markdown')
    else:
        await u.message.reply_text(text, reply_markup=kb, parse_mode='Markdown')

# ကြေညာချက် (Broadcast) စနစ်
async def broadcast(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id not in ADMIN_IDS: return
    if not c.args:
        await u.message.reply_text("⚠️ သုံးပုံစံ: /bcast [စာသား]")
        return
    
    message = " ".join(c.args)
    for group_id in groups.keys():
        try: await c.bot.send_message(group_id, message)
        except: continue
    await u.message.reply_text("✅ ကြေညာချက် ပို့ပြီးပါပြီရှင်။")

async def message_handler(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message or not u.message.text: return
    chat = u.effective_chat
    
    # Auto Reply (Typing Action)
    if u.message.text in replies:
        await c.bot.send_chat_action(chat_id=chat.id, action=constants.ChatAction.TYPING)
        data = replies[u.message.text]
        answers = data["answers"]
        idx = data["index"]
        await chat.send_message(answers[idx])
        data["index"] = (idx + 1) % len(answers)
        save("replies.json", replies)
        return

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bcast", broadcast)) # ကြေညာချက် Command
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handler))
    app.run_polling()
  
