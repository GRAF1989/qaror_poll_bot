import logging
from telegram import Update, Poll
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, PollHandler

# Log sozlamalari
logging.basicConfig(level=logging.INFO)

# Ruxsat etilgan foydalanuvchilar
ALLOWED_USERS = {"@farrux_yoqubjonov", "@saidakromraculev", "@AzamatQobilov"}

# Har bir poll uchun ovozlar
poll_votes = {}

# Trigger bo'lgan xabarni tekshirish
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return

    message = update.message

    if message.photo:
        await send_poll(message, context)

    elif message.text and "app" in message.text.lower():
        await send_poll(message, context)

# Poll yuborish funksiyasi
async def send_poll(message, context):
    poll_message = await message.reply_poll(
        question="Jamoaning ushbu varianti uchun qaror qabul qiling",
        options=["Qabul", "Qabul emas"],
        is_anonymous=False
    )
    poll_votes[poll_message.poll.id] = {
        "message": poll_message,
        "votes": {},
    }

# Har bir foydalanuvchining ovozini qayd etish
async def poll_vote_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll_id = update.poll_answer.poll_id
    user_id = update.poll_answer.user.id
    username = update.poll_answer.user.username

    if poll_id not in poll_votes:
        return

    if f"@{username}" not in ALLOWED_USERS:
        return

    poll_data = poll_votes[poll_id]
    poll_data["votes"][user_id] = update.poll_answer.option_ids[0]

    if len(poll_data["votes"]) == 3:
        options = poll_data["votes"].values()
        qabul_count = sum(1 for o in options if o == 0)
        result_text = "✅ Qabul qilindi" if qabul_count >= 2 else "❌ Qabul qilinmadi"

        await context.bot.send_message(
            chat_id=poll_data["message"].chat_id,
            text=result_text,
            reply_to_message_id=poll_data["message"].message_id
        )
        del poll_votes[poll_id]

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Qaror Bot ishga tushdi!")

if __name__ == '__main__':
    import os
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.add_handler(PollHandler(poll_vote_handler))

    app.run_polling()
