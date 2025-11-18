import telebot
from config import TELEGRAM_BOT_TOKEN

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, f"Вы написали: {message.text}")

if __name__ == "__main__":
    bot.infinity_polling()

