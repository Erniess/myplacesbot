# coding: utf8

# Создание Telegram бота

import os
import telebot
import psycopg2
import math

#main variables
TOKEN = os.environ['TELEGRAM_TOKEN']
DATABASE_URL = os.environ['DATABASE_URL']

bot = telebot.TeleBot(TOKEN)

# база данных
def connect():
    con = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = con.cursor()
    return con, cur

def disconnect(con):
    con.close ()

# Расчет расстояния
def get_distance_between_2_points(point1, point2):
    radius = 6373.0
    lat1 = math.radians(point1[0])
    lon1 = math.radians(point1[1])
    lat2 = math.radians(point2[0])
    lon2 = math.radians(point2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = radius * c
    return distance

# Создание Таблицы
def create_table():
    con, cur = connect()
    cur.execute('CREATE TABLE IF NOT EXISTS users '
                '(id SERIAL PRIMARY KEY, '
                'login VARCHAR(64), '
                'tel_id INTEGER UNIQUE)')
    con.commit()
    cur.execute('CREATE TABLE IF NOT EXISTS locations '
                '(id SERIAL PRIMARY KEY, '
                'tel_id INTEGER, '
                'name VARCHAR(64), '
                'latitude decimal, '
                'longitude decimal, '
                'photo VARCHAR(255), '
                'comment VARCHAR(64))')
    con.commit()
    disconnect(con)

# Старт
@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    user_name = message.from_user.first_name
    hello_msg = '' \
                'Привет, {}!\nЯ сохраняю места ' \
                'для будущего посещения!'.format(user_name)
    create_table()
    con, cur = connect()
    cur.execute('INSERT INTO users (login, tel_id) '
                'VALUES (%s, %s) ON CONFLICT (tel_id) DO NOTHING',
                (message.from_user.first_name, message.from_user.id))
    con.commit()
    disconnect(con)
    bot.send_message(message.chat.id, hello_msg)
    help_handler(message)

# Добавить
@bot.message_handler(commands=['add', 'a'])
def add_handler(message):
    chat_id = message.chat.id
    tel_id = message.from_user.id
    if message.text.startswith('/add ') and len(message.text) > 5 or message.text.startswith('/a ') and len(message.text) > 3:
        name = message.text.split(maxsplit=1)[1]
        bot.send_message(chat_id, 'Добавлено место:\n{}'.format(name))
        con, cur = connect()
        cur.execute('INSERT INTO locations (name, tel_id) VALUES (%s, %s)',
                    (name, tel_id))
        con.commit()
        disconnect(con)
    else:
        msg = bot.send_message(chat_id, 'Введите название места\n(отправьте "нет" для отмены):')
        db = {'tel_id': tel_id}
        bot.register_next_step_handler(msg, add_name, db=db)

def add_name(message, **kwargs):
    db = kwargs['db']
    chat_id = message.chat.id
    text = message.text
    if text is None:
        msg = bot.send_message(chat_id, 'Введите название места\n(отправьте "нет" для отмены):')
        bot.register_next_step_handler(msg, add_name, db=db)
        return
    if text.lower() in ['нет', 'н', 'no', 'n']:
        bot.send_message(chat_id, 'Действие отменено.\n')
        help_handler(message)
        return
    db['name'] = text
    msg = bot.send_message(chat_id, 'Отправьте геолокацию места\n(отправьте "нет" для отмены):')
    bot.register_next_step_handler(msg, add_location, db=db)
    return

def add_location(message, **kwargs):
    db = kwargs['db']
    chat_id = message.chat.id
    location = message.location
    if location is None:
        if message.text and message.text.lower() in ['нет', 'н', 'no', 'n']:
            bot.send_message(chat_id, 'Действие отменено.\n')
            help_handler(message)
            return
        msg = bot.send_message(chat_id, 'Геолокация места обязательна!\nОтправьте геолокацию места\n(отправьте "нет" для отмены):')
        bot.register_next_step_handler(msg, add_location, db=db)
        return
    else:
        db['latitude'] = location.latitude
        db['longitude'] = location.longitude
    msg = bot.send_message(chat_id, 'Пришлите фото места\n(отправьте "нет" чтобы пропустить этот шаг):')
    bot.register_next_step_handler(msg, add_photo, db=db)
    return

def add_photo(message, **kwargs):
    db = kwargs['db']
    chat_id = message.chat.id
    photo = message.photo
    text = message.text
    if photo is None:
        if text.lower() in ['нет', 'н', 'no', 'n']:
            db['photo'] = None
        else:
            msg = bot.send_message(chat_id, 'Пришлите фото места\n(отправьте "нет" чтобы пропустить этот шаг):')
            bot.register_next_step_handler(msg, add_photo, db=db)
            return
    else:
        db['photo'] = photo[-1].file_id
    msg = bot.send_message(chat_id, 'Оставить комментарий\n(отправьте "нет" чтобы пропустить этот шаг):')
    bot.register_next_step_handler(msg, add_comment, db=db)
    return

def add_comment(message, **kwargs):
    db = kwargs['db']
    chat_id = message.chat.id
    text = message.text
    if text is None:
        msg = bot.send_message(chat_id, 'Оставить комментарий\n(отправьте "нет" чтобы пропустить этот шаг):')
        bot.register_next_step_handler(msg, add_comment, db=db)
        return
    if text.lower() in ['нет', 'н', 'no', 'n']:
        db['comment'] = None
    else:
        db['comment'] = text
    bot.send_message(chat_id, 'Добавлено место:\n{}'.format(db['name']))
    add_handler_ends(message, db=db)

def add_handler_ends(message, **kwargs):
    db = kwargs['db']
    chat_id = message.chat.id
    req = 'INSERT INTO locations ({}) VALUES ({})'
    param = []
    for key, val in db.items():
        req = req.format('{}{}'.format(key, ', {}'), '{}{}'.format('%s', ', {}'))
        param.append(val)
    con, cur = connect()
    cur.execute(req.replace(', {}', ''), tuple(param))
    con.commit()
    disconnect(con)

# Список мест
@bot.message_handler(commands=['list', 'l'])
def list_handler(message):
    tel_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text
    con, cur = connect()
    cur.execute("SELECT name, latitude, longitude, photo, comment FROM locations WHERE tel_id = {} ORDER BY id DESC LIMIT 10".format(tel_id))
    results = cur.fetchall()
    disconnect(con)
    if results != []:
        bot.send_message(chat_id, 'Список последних 10 мест:\n')
        i = 0
        for place in results[::-1]:
            i += 1
            name, latitude, longitude, photo, comment = place
            bot.send_message(chat_id, '{}. {}'.format(i, name))
            if longitude is not None and latitude is not None:
                bot.send_location(chat_id, latitude, longitude)
            if photo is not None:
                bot.send_photo(chat_id, photo)
            if comment is not None:
                bot.send_message(chat_id, 'Комментарий: {}'.format(comment))
    else:
        bot.send_message(chat_id, 'Список мест пуст.\nДобавь их коммандой /add или /a\nПомощь по коммандам - /h')


# Очистить список
@bot.message_handler(commands=['reset', 'r'])
def reset_handler(message):
    tel_id = message.from_user.id
    chat_id = message.chat.id
    con, cur = connect()
    cur.execute('DELETE FROM locations WHERE tel_id = {}'.format(tel_id))
    con.commit()
    disconnect(con)
    bot.send_message(chat_id, 'Список мест пуст.\nДобавь их коммандой /add или /a\nПомощь по коммандам - /h')


# Локации по близости
@bot.message_handler(content_types=['location'])
def location_handler(message):
    tel_id = message.from_user.id
    chat_id = message.chat.id
    location = message.location

    con, cur = connect()
    cur.execute("SELECT name, latitude, longitude, photo, comment FROM locations WHERE tel_id = {}".format(tel_id))
    results = cur.fetchall()
    disconnect(con)

    i = 0
    for place in results:
        name, latitude, longitude, photo, comment = place
        if longitude is not None and latitude is not None:
            if get_distance_between_2_points([location.latitude, location.longitude], [latitude, longitude]) <= 0.5:
                i += 1
                if i == 1:
                    bot.send_message(chat_id, 'Список мест в радиусе 500м от присланной локации:')
                bot.send_message(chat_id, '{}. {}'.format(i, name))
                if longitude is not None and latitude is not None:
                    bot.send_location(chat_id, latitude, longitude)
                if photo is not None:
                    bot.send_photo(chat_id, photo)
                if comment is not None:
                    bot.send_message(chat_id, 'Комментарий: {}'.format(comment))
    if i == 0:
        bot.send_message(chat_id, 'Список мест пуст.\nДобавь их коммандой /add или /a\nПомощь по коммандам - /h')

# Помощь
@bot.message_handler(commands=['help', 'h'])
def help_handler(message):
    create_table()
    msg = 'Помощь по коммандам:\n' \
          '/add, /a - подробное, пошаговое добавление нового места,\n' \
          '/add <name>, /a <name> - name необязательный параметр, быстрая запись места,\n' \
          '/list, /l - выводит список 10 последних мест,\n' \
          '/reset, /r - удалить все добавленные места,\n' \
          '/help, /h - помощь по коммандам\n\n' \
          'Отправьте геопозицию для получения мест из вашего списка, находящихся в радиусе 500 метров.'
    bot.send_message(message.chat.id, msg)

# Реакция на любой текст
@bot.message_handler(content_types=['text'])
def text_handler(message):
    help_handler(message)

bot.polling(none_stop=True)
