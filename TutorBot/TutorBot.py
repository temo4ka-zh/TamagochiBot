import telebot
import random
TOKEN = ''

bot = telebot.TeleBot(TOKEN)


user_data = {}
max_level = 10

def init_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            'pets': {},
            'current_pet': None
        }

# Клавиатуры
main_kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.row('Выбрать питомца', 'Создать питомца', 'Статус', 'Кормить', 'Играть', 'Разрядить обстановку')

def create_pet_name_keyboard(user_id):
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    pets = list(user_data[user_id]['pets'].keys())
    if pets:
        for p in pets:
            kb.row(p)
    else:
        kb.row('Нет питомцев')
    return kb

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    init_user(user_id)
    bot.send_message(user_id, "Привет! Это виртуальный питомец.\nВыберите 'Создать питомца' или 'Выбрать питомца'.", reply_markup=main_kb)

@bot.message_handler(func=lambda m: m.text == 'Создать питомца')
def handle_create_pet(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Введите имя нового питомца:")
    bot.register_next_step_handler(message, process_pet_name)

def process_pet_name(message):
    user_id = message.chat.id
    pet_name = message.text.strip()
    init_user(user_id)
    if pet_name in user_data[user_id]['pets']:
        bot.send_message(user_id, "Питомец с таким именем уже есть. Введите другое имя:")
        bot.register_next_step_handler(message, process_pet_name)
        return
    # Создаем питомца
    user_data[user_id]['pets'][pet_name] = {'name': pet_name, 'food': 50, 'mood': 50, 'level':1}
    user_data[user_id]['current_pet'] = pet_name
    bot.send_message(user_id, f"Питомец '{pet_name}' создан и выбран.", reply_markup=main_kb)
@bot.message_handler(func=lambda m: m.text == 'Разрядить обстановку')
def little_joke(message):
    lst = ['— Я тут код написал…\n— Работает?\n— Да! Но только если не смотреть на него и ничего не трогать.',
           '— Почему твой код такой длинный?\n-Это не код.\n— А что?\n— Документация к багу.', '— Ты починил тот баг?\n— Да.\n— И что теперь?\n— Теперь их два.', '— Как прошло ревью?\n— Отлично!\n— Тебя похвалили?\n— Нет, но я хотя бы понял, что жить можно и без самооценки.', '— У тебя почему всё работает?\n— Потому что…\n— Потому что ты крутой?\n— Нет, потому что я боюсь трогать.']
    rnd = random
    rnd.randint(1, 5)
    if lst[rnd] == lst[0]:
        return lst[rnd] and open('sticker.webp')
    elif lst[rnd] == lst[1]:
        return lst[rnd] and open('sticker1.webp')
    elif lst[rnd] == lst[2]:
        return lst[rnd] and open('sticker2.webp')
    elif lst[rnd] == lst[3]:
        return lst[rnd] and open('sticker3.webp')
    elif lst[rnd] == lst[4]:
        return lst[rnd] and open('sticker4.webp')
@bot.message_handler(func=lambda m: m.text == 'Выбрать питомца')
def handle_select_pet(message):
    user_id = message.chat.id
    init_user(user_id)
    if not user_data[user_id]['pets']:
        bot.send_message(user_id, "У вас нет питомцев. Создайте первого:", reply_markup=main_kb)
        return
    pet_names = list(user_data[user_id]['pets'].keys())
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for p in pet_names:
        kb.row(p)
    bot.send_message(user_id, "Выберите питомца:", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text in user_data[m.chat.id]['pets'])
def handle_pet_selection_or_commands(message):
    user_id = message.chat.id
    init_user(user_id)
    text = message.text
    # Проверка, является ли сообщение именем питомца
    if text in user_data[user_id]['pets']:
        user_data[user_id]['current_pet'] = text
        bot.send_message(user_id, f"Вы выбрали питомца '{text}'. Что хотите сделать?", reply_markup=main_kb)
        return

    if text == 'Статус':
        handle_status(message)
    elif text == 'Кормить':
        handle_feed(message)
    elif text == 'Играть':
        handle_play(message)
    elif text == 'Создать питомца':
        handle_create_pet(message)
    elif text == 'Выбрать питомца':
        handle_select_pet(message)
    else:
        bot.send_message(user_id, "Неизвестная команда или выберите питомца.")

def get_current_pet(user_id):
    pet_name = user_data[user_id]['current_pet']
    if pet_name and pet_name in user_data[user_id]['pets']:
        return user_data[user_id]['pets'][pet_name]
    return None

def check_pet_dead(pet):
    return pet['food'] <= 0 or pet['mood'] <= 0

def resurrect_pet(user_id, pet_name):
    user_data[user_id]['pets'][pet_name] = {'name': pet_name, 'food': 50, 'mood': 50, 'level':1}
    user_data[user_id]['current_pet'] = pet_name

def handle_status(message):
    user_id = message.chat.id
    pet = get_current_pet(user_id)
    if not pet:
        bot.send_message(user_id, "Нет выбранного питомца.")
        return
    status = f"Питомец: {pet['name']}\nЕда: {pet['food']}\nНастроение: {pet['mood']}"
    bot.send_message(user_id, status)

def handle_feed(message):
    user_id = message.chat.id
    pet = get_current_pet(user_id)
    if not pet:
        bot.send_message(user_id, "Нет выбранного питомца.")
        return
    if check_pet_dead(pet):

        resurrect_pet(user_id, pet['name'])
        bot.send_message(user_id, "Питомец умер и был воскресшен.")
        return

    pet['food'] += 10
    pet['mood'] -= 5
    if pet['food'] > 100:
        pet['food'] = 100
    if pet['food'] >= 80:
        update_level(pet)
    bot.send_message(message.chat.id, f'Еда: {pet['food']}. Настроение: {pet['mood']}. Уровень: {pet['level']}')

def handle_play(message):
    user_id = message.chat.id
    pet = get_current_pet(user_id)
    if not pet:
        bot.send_message(user_id, "Нет выбранного питомца.")
        return
    if check_pet_dead(pet):
        resurrect_pet(user_id, pet['name'])
        bot.send_message(user_id, "Питомец умер и был воскресшен.")
        return
    pet['mood'] += 10
    pet['food'] -= 5
    if pet['mood'] > 100:
        pet['mood'] = 100
    if pet['mood']>=80:
        update_level(pet)
    bot.send_message(message.chat.id, f'Еда: {pet['food']}. Настроение: {pet['mood']}. Уровень: {pet['level']}')

def update_level(pet):
    if pet['level']<max_level:
        pet['level'] += 1

# Обработка получения сообщений
@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    user_id = message.chat.id
    init_user(user_id)
    text = message.text
    if text == 'Создать питомца':
        handle_create_pet(message)
    elif text == 'Выбрать питомца':
        handle_select_pet(message)
    elif text == 'Статус':
        handle_status(message)
    elif text == 'Кормить':
        handle_feed(message)
    elif text == 'Играть':
        handle_play(message)
    elif text in user_data[user_id]['pets']:
        # Переключение текущего питомца
        user_data[user_id]['current_pet'] = text
        bot.send_message(user_id, f"Вы выбрали питомца '{text}'. Что хотите сделать?", reply_markup=main_kb)
    else:
        bot.send_message(user_id, "Команда не распознана. Используйте меню.")

bot.polling(non_stop=True)
