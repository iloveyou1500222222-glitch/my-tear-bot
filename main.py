import json
import os
from config import ADMIN_IDS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, constants
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

def load(f): 
    try:
        with open(f, 'r') as file: return json.load(file)
    except: return {}

def save(f, data):
    with open(f, 'w') as file: json.dump(data, file)

groups, replies, users = load("groups.json"), load("replies.json"), load("users.json")

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    user = u.effective_user
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Channel", url="https://t.me/tear80808")],
        [InlineKeyboardButton("👑 Owner", url="https://t.me/Tear808")],
        [InlineKeyboardButton("➕ Group ထဲသို့ထည့်ရန်", url="https://t.me/myaigroup_ai_bot?startgroup=true")]
    ])
    
    text = f"ဟယ်လို သဲသဲရေ! 👋\n\n👤 နာမည်: {user.first_name}\n🆔 ID: `{user.id}`\n\nသဲ ကို စတင်ရန် အဆင်သင့်ဖြစ်ပါပြီရှင်။ 🥰"
    
    photos = await c.bot.get_user_profile_photos(user.id)
    if photos.total_count > 0:
        await u.message.reply_photo(photo=photos.photos[0][0].file_id, caption=text, reply_markup=kb, parse_mode='Markdown')
    else:
        await u.message.reply_text(text, reply_markup=kb, parse_mode='Markdown')

async def teach(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id not in ADMIN_IDS: return
    args = u.message.text.split(maxsplit=2)
    if len(args) < 3:
        await u.message.reply_text("⚠️ သုံးပုံစံ: /teach [မေးခွန်း] [အဖြေ1/အဖြေ2/...]")
        return
    question, answers = args[1], args[2].split('/')
    replies[question] = {"answers": answers, "index": 0}
    save("replies.json", replies)
    await u.message.reply_text(f"✅ သဲသဲအတွက် အဖြေ {len(answers)} ခုကို မှတ်ထားလိုက်ပါပြီရှင်။")

async def welcome(u: Update, c: ContextTypes.DEFAULT_TYPE):
    for member in u.message.new_chat_members:
        await u.message.reply_text(f"🌸 {member.first_name} လေး ကြိုဆိုပါတယ်ရှင်! သဲ Group လေးမှာ ပျော်ရွှင်ပါစေနော်။ 🥰")

async def message_handler(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message or not u.message.text: return
    if u.message.text in replies:
        await c.bot.send_chat_action(chat_id=u.effective_chat.id, action=constants.ChatAction.TYPING)
        data = replies[u.message.text]
        answers = data["answers"]
        idx = data["index"]
        await u.message.reply_text(answers[idx])
        data["index"] = (idx + 1) % len(answers)
        save("replies.json", replies)

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("teach", teach))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()
  
