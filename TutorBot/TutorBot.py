import os
import random
import telebot

TOKEN = '8533332080:AAE7qeUDO0X3aD6RdYZC31-HVRvn84hPWCE'
bot = telebot.TeleBot(TOKEN)

user_data = {}
max_level = 10

if not os.path.exists('images'):
    os.makedirs('images')

def init_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            'pets': {},
            'current_pet': None
        }

# Основное меню
main_kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.row('Выбрать питомца', 'Создать питомца', 'Статус', 'Кормить', 'Играть', 'Разрядить обстановку', 'Загрузить аватар')

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    init_user(user_id)
    bot.send_message(user_id, "Привет! Это виртуальный питомец.\nВыберите 'Создать питомца' или 'Выбрать питомца'.", reply_markup=main_kb)

# Создаем питомца
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
    user_data[user_id]['pets'][pet_name] = {'name': pet_name, 'food': 50, 'mood': 50, 'level':1}
    user_data[user_id]['current_pet'] = pet_name
    bot.send_message(user_id, f"Питомец '{pet_name}' создан и выбран.", reply_markup=main_kb)

# Выбираем питомца
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

# Обработка выбора питомца или команд
@bot.message_handler(func=lambda m: m.text in user_data.get(m.chat.id, {}).get('pets', {}) or m.text in ['Статус', 'Кормить', 'Играть', 'Загрузить аватар'])
def handle_pet_commands(message):
    user_id = message.chat.id
    init_user(user_id)
    text = message.text
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
    elif text == 'Загрузить аватар':
        handle_upload_avatar(message)
    else:
        bot.send_message(user_id, "Неизвестная команда или выберите питомца.")

# Получение текущего питомца
def get_current_pet(user_id):
    pet_name = user_data[user_id]['current_pet']
    if pet_name and pet_name in user_data[user_id]['pets']:
        return user_data[user_id]['pets'][pet_name]
    return None

# Проверка на смерть питомца
def check_pet_dead(pet):
    return pet['food'] <= 0 or pet['mood'] <= 0

# Воскрешение питомца
def resurrect_pet(user_id, pet_name):
    user_data[user_id]['pets'][pet_name] = {'name': pet_name, 'food': 50, 'mood': 50, 'level':1}
    user_data[user_id]['current_pet'] = pet_name

# Статус питомца (с аватаркой, если есть)
def handle_status(message):
    user_id = message.chat.id
    pet = get_current_pet(user_id)
    if not pet:
        bot.send_message(user_id, "Нет выбранного питомца.")
        return
    status = f"Питомец: {pet['name']}\nЕда: {pet['food']}\nНастроение: {pet['mood']}\nУровень: {pet['level']}"
    if 'avatar' in pet:
        try:
            with open(pet['avatar'], 'rb') as photo:
                bot.send_photo(user_id, photo, caption=status)
        except:
            bot.send_message(user_id, status)
    else:
        bot.send_message(user_id, status)

# Кормим питомца
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
    bot.send_message(user_id, f'Еда: {pet["food"]}. Настроение: {pet["mood"]}. Уровень: {pet["level"]}')

# Играть с питомцем
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
    if pet['food'] < 0:
        pet['food'] = 0
    bot.send_message(user_id, f'Еда: {pet["food"]}. Настроение: {pet["mood"]}.')

# Обновление уровня
def update_level(pet):
    if 'level' in pet:
        pet['level'] += 1
    else:
        pet['level'] = 1

# Обработка фото для аватара
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.chat.id
    init_user(user_id)
    if not user_data[user_id]['current_pet']:
        bot.send_message(user_id, "Сначала выберите питомца.")
        return
    pet_name = user_data[user_id]['current_pet']
    pet = user_data[user_id]['pets'][pet_name]
    try:
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        file_path = file_info.file_path
        file_content = bot.download_file(file_path)
        filename = f'images/{user_id}_{pet_name}.jpg'
        with open(filename, 'wb') as f:
            f.write(file_content)
        pet['avatar'] = filename
        bot.send_message(user_id, f"Аватар питомца '{pet_name}' успешно установлен.")
    except Exception as e:
        bot.send_message(user_id, "Ошибка при сохранении аватара: " + str(e))

# Обработка команды для загрузки аватара (вызывается кнопкой)
def handle_upload_avatar(message):
    user_id = message.chat.id
    init_user(user_id)
    if not user_data[user_id]['current_pet']:
        bot.send_message(user_id, "Сначала выберите питомца.")
        return
    bot.send_message(user_id, "Пожалуйста, отправьте фотографию питомца.")
bot.polling(non_stop=True)