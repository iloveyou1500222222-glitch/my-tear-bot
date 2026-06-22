import json
from config import BOT_TOKEN, ADMIN_IDS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Database Load
def load(f): 
    try: with open(f, 'r') as file: return json.load(file)
    except: return {}

groups, replies, users = load("groups.json"), load("replies.json"), load("users.json")

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    user = u.effective_user
    users[str(user.id)] = user.first_name
    
    if u.effective_chat.type in ['group', 'supergroup']:
        groups[str(u.effective_chat.id)] = u.effective_chat.title
        await u.message.reply_text("🌸 Cherrhin Group ထဲရောက်သွားပါပြီရှင်။")
        return

    kb = InlineKeyboardMarkup([[InlineKeyboardButton("➕ Group ထဲသို့ထည့်ရန်", url="https://t.me/YourBotUsername?startgroup=true")]])
    text = f"ဟယ်လို ကိုကိုရေ! 👋\n\nName: {user.first_name}\nID: `{user.id}`\n\nCherrhin ကို စတင်ရန် အဆင်သင့်ဖြစ်ပါပြီရှင်။ 🥰"
    await u.message.reply_text(text, reply_markup=kb, parse_mode='Markdown')

async def message_handler(u: Update, c: ContextTypes.DEFAULT_TYPE):
    # Link Filter
    if u.message.entities:
        for entity in u.message.entities:
            if entity.type in ['url', 'text_link']:
                await u.message.delete()
                await u.message.reply_text("🥺 ကိုကိုရေ... ဒီ Group ထဲမှာ Link လေးတွေ မချရဘူးရှင်။")
                return
    
    # Private Forward
    if u.effective_chat.type == 'private' and not u.message.text.startswith('/'):
        for admin in ADMIN_IDS:
            await c.bot.forward_message(admin, u.effective_chat.id, u.message.message_id)

async def admin_actions(u: Update, c: ContextTypes.DEFAULT_TYPE):
    if u.effective_user.id not in ADMIN_IDS or not u.message.reply_to_message: return
    cmd, target = u.message.text.split()[0].lower(), u.message.reply_to_message.from_user
    
    if "/ban" in cmd: await c.bot.ban_chat_member(u.effective_chat.id, target.id)
    elif "/mute" in cmd: await c.bot.restrict_chat_member(u.effective_chat.id, target.id, permissions=ChatPermissions(can_send_messages=False))
    elif "/unmute" in cmd: await c.bot.restrict_chat_member(u.effective_chat.id, target.id, permissions=ChatPermissions(can_send_messages=True))

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler(["ban", "mute", "unmute"], admin_actions))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handler))
    app.run_polling()
              
