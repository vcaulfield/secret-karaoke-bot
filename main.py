import os, random, urllib3
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.getenv("BOT_TOKEN")
participants = {}
pairing_done = False

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    if user.id not in participants:
        participants[user.id] = {'username': user.username, 'target': None, 'songs_sent': False}
        update.message.reply_text("Ты участвуешь в Тайном Караоке 🎤")
    else:
        update.message.reply_text("Ты уже в игре.")

def shuffle(update: Update, context: CallbackContext):
    global pairing_done
    if pairing_done:
        update.message.reply_text("Распределение уже было сделано.")
        return
    if len(participants) < 2:
        update.message.reply_text("Слишком мало участников.")
        return

    ids = list(participants.keys())
    random.shuffle(ids)
    for i in range(len(ids)):
        giver = ids[i]
        receiver = ids[(i + 1) % len(ids)]
        participants[giver]['target'] = receiver

    for giver_id, data in participants.items():
        target_id = data['target']
        target_username = participants[target_id]['username']
        context.bot.send_message(chat_id=giver_id,
            text=f"Ты загадываешь песни для @{target_username}. Напиши 1–3 песни в ответ."
        )

    pairing_done = True
    update.message.reply_text("Все участники получили задания!")

def handle_songs(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in participants and participants[user_id]['target'] and not participants[user_id]['songs_sent']:
        songs = update.message.text
        target_id = participants[user_id]['target']
        context.bot.send_message(chat_id=target_id,
            text=f"🎶 Тебе предстоит исполнить одну из этих песен: {songs}"
        )
        participants[user_id]['songs_sent'] = True
        update.message.reply_text("Задание отправлено!")
    else:
        update.message.reply_text("Либо задание уже отправлено, либо ещё не время.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("shuffle", shuffle))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_songs))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
