# coding: utf8

# Создание Telegram бота

import telebot

#main variables
TOKEN = ''
bot = telebot.TeleBot(TOKEN)

# Старт
@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    user_name = message.from_user.first_name
    hello_msg = '' \
                'Привет, {}!\nКогда я вырасту, я буду сохранять для тебя места ' \
                'для будущего посещения!'.format(user_name)
    bot.send_message(message.chat.id, hello_msg)

# Добавить
@bot.message_handler(commands=['add', 'a'])
def add_handler(message):
    bot.send_message(message.chat.id, 'Добавить место.')

# Список мест
@bot.message_handler(commands=['list', 'l'])
def list_handler(message):
    bot.send_message(message.chat.id, 'Список мест.')

# Очистить список
@bot.message_handler(commands=['reset', 'r'])
def reset_handler(message):
    bot.send_message(message.chat.id, 'Очистить список')

# Помощь
@bot.message_handler(commands=['help', 'h'])
def help_handler(message):
    msg = 'Помощь по коммандам:\n' \
          '/add, /a - добавление нового места\n' \
          '/list, /l - отображение добавленных мест\n' \
          '/reset, /r - позволяет пользователю удалить все его добавленные локации\n' \
          '/help, /h - помощь по коммандам'
    bot.send_message(message.chat.id, msg)

# Реакция на любой текст
@bot.message_handler(content_types=['text'])
def text_handler(message):
    msg = 'Помощь по коммандам:\n' \
          '/add, /a - добавление нового места\n' \
          '/list, /l - отображение добавленных мест\n' \
          '/reset, /r - позволяет пользователю удалить все его добавленные локации\n' \
          '/help, /h - помощь по коммандам'
    bot.send_message(message.chat.id, msg)

bot.polling(none_stop=True)

