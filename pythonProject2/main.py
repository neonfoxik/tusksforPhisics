import telebot
from telebot import types
import random
import os
from dotenv import load_dotenv

load_dotenv()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

def read_tasks(filename):
    with open(os.path.join('Files', filename), 'r', encoding='utf-8') as file:
        return file.readlines()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Легкий", callback_data="easy")
    btn2 = types.InlineKeyboardButton("Средний", callback_data="medium")
    btn3 = types.InlineKeyboardButton("Сложный", callback_data="hard")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "Выберите уровень сложности:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "easy":
        task = random.choice(read_tasks('easy.txt')).strip()
        bot.send_message(call.message.chat.id, f"Легкая задача:\n{task}")
    elif call.data == "medium":
        task = random.choice(read_tasks('medium.txt')).strip()
        bot.send_message(call.message.chat.id, f"Задача средней сложности:\n{task}")
    elif call.data == "hard":
        task = random.choice(read_tasks('hard.txt')).strip()
        bot.send_message(call.message.chat.id, f"Сложная задача:\n{task}")
    
    bot.answer_callback_query(call.id)

# Удаляем вебхук, если он установлен
bot.remove_webhook()

bot.polling(none_stop=True)
