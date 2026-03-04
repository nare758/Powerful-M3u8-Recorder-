# verify_bot.py
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import datetime

OWNER_ID = 5856009289
BOT_TOKEN = "8191916199:AAE-ezyhTkdta-0p8I-lVSsDn8l7UdjhhY0"
verified_users = {}

@CommandHandler("verify")
async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    verified_users[user_id] = datetime.datetime.now() + datetime.timedelta(hours=6)
    await update.message.reply_text("✅ Verified! You can now access recordings for 6 hours.")

# Run
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("verify", verify))
app.run_polling()
