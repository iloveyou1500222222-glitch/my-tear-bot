import json
import os
from config import ADMIN_IDS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions, constants
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
    users[str(user.id)] = user.first_name
    save("users.json", users)
    
    if u.effective_chat.type in ['group', 'supergroup']:
        groups[str(u.effective_chat.id)] = u.effective_chat.title
        save("groups.json", groups)
        await u.message.reply_text("🌸 သဲ Group ထဲရောက်သွားပါပြီရှင်။")
        return

    kb = InlineKeyboardMarkup([[InlineKeyboardButton("➕ Group ထဲသို့ထည့်ရန်", url="https://t.me/YourBotUsername?startgroup=true")]])
    text = f"ဟယ်လို သဲသဲရေ! 👋\n\nName: {user.first_name}\nID: `{user.id}`\n\nသဲ ကို စတင်ရန် အဆင်သင့်ဖြစ်ပါပြီရှင်။ 🥰"
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

async def message_handler(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if not u.message or not u.message.text: return
    chat = u.effective_chat
    
    if u.message.entities:
        for entity in u.message.entities:
            if entity.type in ['url', 'text_link']:
                await u.message.delete()
                await chat.send_message("🥺 သဲသဲရေ... ဒီ Group ထဲမှာ Link လေးတွေ မချရဘူးရှင်။")
                return
    
    # Auto Reply (Sequential & Typing Action)
    if u.message.text in replies:
        # "Typing..." ပုံစံလေးပေါ်အောင်လုပ်ခြင်း
        await c.bot.send_chat_action(chat_id=chat.id, action=constants.ChatAction.TYPING)
        
        data = replies[u.message.text]
        answers = data["answers"]
        idx = data["index"]
        
        await chat.send_message(answers[idx])
        
        data["index"] = (idx + 1) % len(answers)
        save("replies.json", replies)
        return

    if chat.type == 'private' and not u.message.text.startswith('/'):
        for admin in ADMIN_IDS:
            await c.bot.forward_message(admin, chat.id, u.message.message_id)

async def admin_actions(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id not in ADMIN_IDS or not u.message.reply_to_message: return
    cmd, target = u.message.text.split()[0].lower(), u.message.reply_to_message.from_user
    if "/ban" in cmd: await c.bot.ban_chat_member(u.effective_chat.id, target.id)
    elif "/mute" in cmd: await c.bot.restrict_chat_member(u.effective_chat.id, target.id, permissions=ChatPermissions(can_send_messages=False))
    elif "/unmute" in cmd: await c.bot.restrict_chat_member(u.effective_chat.id, target.id, permissions=ChatPermissions(can_send_messages=True))

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("teach", teach))
    app.add_handler(CommandHandler(["ban", "mute", "unmute"], admin_actions))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handler))
    app.run_polling()
  
