import telebot
from telebot import types
import random
from functools import wraps
from telebot.types import Message
from dotenv import load_dotenv
import os

load_dotenv()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
OWNER_ID = os.getenv('OWNER_ID')


def admin_permission(func):
    """
    Проверка прав администратора для доступа к функции.
    """

    @wraps(func)
    def wrapped(message: Message) -> None:
        try:
            user_id = message.from_user.id
            if str(user_id) != OWNER_ID:
                bot.send_message(user_id, '⛔ У вас нет администраторского доступа')
                return
            return func(message)
        except Exception as e:
            print(f"Ошибка в admin_permission: {e}")

    return wrapped


@admin_permission
@bot.message_handler(commands=['admin'])
def admin_main_menu(message):
    try:
        markup = types.InlineKeyboardMarkup()
        btn_update_files = types.InlineKeyboardButton("Обновить файлы", callback_data="update_files")
        btn_get_files = types.InlineKeyboardButton("Получить файлы", callback_data="get_files")
        markup.add(btn_update_files, btn_get_files)

        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    except Exception as e:
        print(f"Ошибка в admin_main_menu: {e}")


@admin_permission
@bot.callback_query_handler(func=lambda call: call.data == "get_files")
def get_files_menu(call):
    try:
        markup = types.InlineKeyboardMarkup()
        btn_get_easy = types.InlineKeyboardButton("Получить изи файл", callback_data="get_easy")
        btn_get_medium = types.InlineKeyboardButton("Получить средний файл", callback_data="get_medium")
        btn_get_hard = types.InlineKeyboardButton("Получить хард файл", callback_data="get_hard")
        markup.add(btn_get_easy, btn_get_medium, btn_get_hard)

        bot.send_message(call.message.chat.id, "Выберите файл для получения:", reply_markup=markup)
    except Exception as e:
        print(f"Ошибка в get_files_menu: {e}")


@admin_permission
@bot.callback_query_handler(func=lambda call: call.data == "update_files")
def update_files_menu(call):
    try:
        markup = types.InlineKeyboardMarkup()
        btn_update_easy = types.InlineKeyboardButton("Обновить легкий файл", callback_data="update_easy")
        btn_update_medium = types.InlineKeyboardButton("Обновить средний файл", callback_data="update_medium")
        btn_update_hard = types.InlineKeyboardButton("Обновить хард файл", callback_data="update_hard")
        markup.add(btn_update_easy).add(btn_update_medium).add(btn_update_hard)

        bot.send_message(call.message.chat.id, "Выберите файл для обновления:", reply_markup=markup)
    except Exception as e:
        print(f"Ошибка в update_files_menu: {e}")


@admin_permission
@bot.callback_query_handler(func=lambda call: call.data.startswith("get_"))
def send_file(call):
    try:
        file_name = call.data[4:] + '.txt'  # Получаем имя файла, убирая "get_"
        file_path = os.path.join('Files', file_name)

        if os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                bot.send_document(call.message.chat.id, file)
        else:
            bot.send_message(call.message.chat.id, "Файл не найден.")
    except Exception as e:
        print(f"Ошибка в send_file: {e}")


@admin_permission
@bot.callback_query_handler(func=lambda call: call.data.startswith("update_"))
def update_file(call):
    try:
        file_name = call.data[7:] + '.txt'  # Получаем имя файла, убирая "update_"
        bot.send_message(call.message.chat.id, "Пожалуйста, отправьте новый файл для обновления.")

        @bot.message_handler(content_types=['document'])
        def handle_document(message):
            try:
                if message.document.mime_type == 'text/plain':
                    file_id = message.document.file_id
                    new_file = bot.get_file(file_id)
                    downloaded_file = bot.download_file(new_file.file_path)

                    file_path = os.path.join('Files', file_name)
                    with open(file_path, 'wb') as new_file:
                        new_file.write(downloaded_file)

                    bot.send_message(message.chat.id, f"Файл {file_name} успешно обновлен.")
                else:
                    bot.send_message(message.chat.id, "Пожалуйста, отправьте файл в формате .txt.")
            except Exception as e:
                print(f"Ошибка в handle_document: {e}")

        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"Ошибка в update_file: {e}")


def read_tasks(filename):
    try:
        file_path = os.path.join('Files', filename)
        print(f"Пытаемся прочитать файл: {file_path}")  # добавьте для отладки
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            print(f"Прочитано строк: {len(lines)}")  # добавьте для отладки
            return lines
    except Exception as e:
        print(f"Ошибка в read_tasks: {e}")
        return []  # возвращаем пустой список вместо None

@bot.message_handler(commands=['start'])
def start(message):
    try:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Легкий", callback_data="tusk_easy")
        btn2 = types.InlineKeyboardButton("Средний", callback_data="tusk_medium")
        btn3 = types.InlineKeyboardButton("Сложный", callback_data="tusk_hard")
        markup.add(btn1).add(btn2).add(btn3)
        bot.send_message(message.chat.id, "Выберите уровень сложности:", reply_markup=markup)
    except Exception as e:
        print(f"Ошибка в start: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("tusk_"))
def callback_query(call):
    try:
        print(f"Получен callback с данными: {call.data}")  # добавьте для отладки
        if call.data == "tusk_easy":
            task = random.choice(read_tasks('easy.txt')).strip()
            bot.send_message(call.message.chat.id, f"Легкая задача:\n{task}")
        elif call.data == "tusk_medium":
            task = random.choice(read_tasks('medium.txt')).strip()
            bot.send_message(call.message.chat.id, f"Задача средней сложности:\n{task}")
        elif call.data == "tusk_hard":
            task = random.choice(read_tasks('hard.txt')).strip()
            bot.send_message(call.message.chat.id, f"Сложная задача:\n{task}")

        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"Ошибка в callback_query: {e}")

# Удаляем вебхук, если он установлен
try:
    bot.remove_webhook()
except Exception as e:
    print(f"Ошибка при удалении вебхука: {e}")

bot.polling(none_stop=True)
