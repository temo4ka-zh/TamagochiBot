import telebot
import os

TOKEN = ''  # Вставьте сюда ваш токен бота
bot = telebot.TeleBot(TOKEN)

user_data = {}
max_level = 10

# Создаем папку для изображений при необходимости
if not os.path.exists('images'):
    os.makedirs('images')

def init_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            'pets': {},
            'current_pet': None
        }

# Основное меню с добавлением "Удалить аватар"
def get_main_keyboard():
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row('Выбрать питомца', 'Создать питомца')
    kb.row('Статус', 'Кормить')
    kb.row('Играть', 'Разрядить обстановку')
    kb.row('Загрузить аватар', 'Удалить аватар')
    return kb

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    init_user(user_id)
    bot.send_message(user_id, "Привет! Это виртуальный питомец.\nВыберите 'Создать питомца' или 'Выбрать питомца'.", reply_markup=get_main_keyboard())

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
    bot.send_message(user_id, f"Питомец '{pet_name}' создан и выбран.", reply_markup=get_main_keyboard())

# Выбираем питомца
@bot.message_handler(func=lambda m: m.text == 'Выбрать питомца')
def handle_select_pet(message):
    user_id = message.chat.id
    init_user(user_id)
    if not user_data[user_id]['pets']:
        bot.send_message(user_id, "У вас нет питомцев. Создайте первого:", reply_markup=get_main_keyboard())
        return
    pet_names = list(user_data[user_id]['pets'].keys())
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for p in pet_names:
        kb.row(p)
    bot.send_message(user_id, "Выберите питомца:", reply_markup=kb)

# Обработка команд и выбора питомца
@bot.message_handler(func=lambda m: True)
def handle_pet_commands(message):
    user_id = message.chat.id
    init_user(user_id)
    text = message.text

    # Проверяем, есть ли такой питомец и он активен
    if text in user_data[user_id]['pets']:
        user_data[user_id]['current_pet'] = text
        bot.send_message(user_id, f"Вы выбрали питомца '{text}'. Что хотите сделать?", reply_markup=get_main_keyboard())
        return

    # Обработка системных команд
    if text == 'Статус':
        handle_status(message)
    elif text == 'Кормить':
        handle_feed(message)
    elif text == 'Играть':
        handle_play(message)
    elif text == 'Загрузить аватар':
        handle_upload_avatar(message)
    elif text == 'Удалить аватар':
        handle_delete_avatar(message)
    elif text == 'Создать питомца' or text == 'Выбрать питомца':
        # Эти команды уже обрабатываются выше, можно оставить так, чтобы не дублировать
        pass
    else:
        bot.send_message(user_id, "Команда не распознана или выберите питомца.", reply_markup=get_main_keyboard())

# Получение текущего питомца
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

# Статус питомца
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

# Играть
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

def update_level(pet):
    pet['level'] += 1

# Загрузка аватара
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

# Удаление аватара
def handle_delete_avatar(message):
    user_id = message.chat.id
    init_user(user_id)
    pet_name = user_data[user_id]['current_pet']
    if not pet_name:
        bot.send_message(user_id, "Сначала выберите питомца.")
        return
    pet = user_data[user_id]['pets'][pet_name]
    if 'avatar' in pet:
        try:
            os.remove(pet['avatar'])
        except:
            pass  # файл мог уже быть удален
        del pet['avatar']
        bot.send_message(user_id, "Аватар питомца удален.")
    else:
        bot.send_message(user_id, "У этого питомца нет аватара.")

# Обработка загрузки аватара (отправка фото)
def handle_upload_avatar(message):
    user_id = message.chat.id
    init_user(user_id)
    if not user_data[user_id]['current_pet']:
        bot.send_message(user_id, "Сначала выберите питомца.")
        return
    bot.send_message(user_id, "Пожалуйста, отправьте фотографию питомца.")

# Запуск бота
bot.polling()