import telebot
from telebot.types import Message
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

ALLOWED_USERS = ['@farrux_yoqubjonov', '@saidakromraculev', '@AzamatQobilov']
poll_votes = {}
poll_meta = {}

@bot.message_handler(func=lambda message: message.text and 'app' in message.text.lower())
def on_app_text(message: Message):
    send_poll(message)

@bot.message_handler(content_types=['photo'])
def on_photo(message: Message):
    send_poll(message)

def send_poll(message: Message):
    poll_msg = bot.send_poll(
        chat_id=message.chat.id,
        question="Jamoaning ushbu varianti uchun qaror qabul qiling",
        options=["Qabul", "Qabul emas"],
        is_anonymous=False,
        reply_to_message_id=message.message_id
    )
    poll_votes[poll_msg.poll.id] = {}
    poll_meta[poll_msg.poll.id] = {
        'chat_id': message.chat.id,
        'reply_to_message_id': message.message_id
    }

@bot.poll_answer_handler()
def handle_poll_answer(poll_answer):
    poll_id = poll_answer.poll_id
    user_id = poll_answer.user.id
    username = '@' + poll_answer.user.username if poll_answer.user.username else None
    option_id = poll_answer.option_ids[0]

    if poll_id not in poll_votes:
        poll_votes[poll_id] = {}

    if username not in ALLOWED_USERS:
        bot.send_message(user_id, "⛔ Siz ruxsatsiz foydalanuvchisiz. So‘rovnoma bekor qilindi.")
        poll_votes.pop(poll_id, None)
        poll_meta.pop(poll_id, None)
        return

    poll_votes[poll_id][username] = option_id

    if len(poll_votes[poll_id]) == 3:
        qabul_soni = sum(1 for vote in poll_votes[poll_id].values() if vote == 0)
        result = "✅ Qabul qilindi" if qabul_soni >= 2 else "❌ Qabul qilinmadi"

        meta = poll_meta.get(poll_id)
        if meta:
            bot.send_message(
                chat_id=meta['chat_id'],
                text=result,
                reply_to_message_id=meta['reply_to_message_id']
            )

        poll_votes.pop(poll_id, None)
        poll_meta.pop(poll_id, None)

bot.infinity_polling()
