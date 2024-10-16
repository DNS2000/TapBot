import configparser, sqlite3, types, json
from telebot import *

global errors, started, bot_name, admin_list
errors = 0
bot_name = "DNS2000's BOT"

config = configparser.ConfigParser()
config.read("TapBotConfig.ini")
try:
    bot_token = config.get("TapBotConfig", "bot_token")
    admin_list = json.loads(config.get("TapBotConfig", "admin_list"))
except:
    config.add_section("TapBotConfig")
    config.set("TapBotConfig", "bot_token", "bot_token") # Токен бота без кавычек
    config.set("TapBotConfig", "admin_list", "[]") # ID администраторов бота через запятую
    config.write(open("TapBotConfig.ini", "w"))

connection = sqlite3.connect("TapBotDatabase.db", check_same_thread=False)
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY NOT NULL, user_name TEXT NOT NULL, bot_score INTEGER NOT NULL, bot_level INTEGER NOT NULL, theme_current TEXT NOT NULL, theme_dark INTEGER NOT NULL)")
connection.commit()

telebot.logger.setLevel(logging.ERROR)
class ExceptionHandler(telebot.ExceptionHandler):
    def handle(self, exception):
        global errors
        errors += 1
        print(f"\n{str(traceback.format_exc()).replace(str(bot_token), "*bot_token*")}\nВозникла ошибка. ({errors})\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n")
        return True

bot = telebot.TeleBot(token=str(bot_token), exception_handler=ExceptionHandler())

@bot.message_handler(commands=["start"])
def start(message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, user_name, bot_score, bot_level, theme_current, theme_dark) VALUES (?, ?, ?, ?, ?, ?)", (message.from_user.id, message.from_user.first_name, 0, 1, "Light", 0))
    cursor.execute("SELECT bot_score, theme_current FROM users WHERE user_id = ?", (message.from_user.id,))
    fetched = cursor.fetchall()
    if fetched[0][0] < 0:
        cursor.execute("UPDATE users SET bot_score = ? WHERE user_id = ?", (0, message.from_user.id))
        bot_score = 0
    else:
        bot_score = fetched[0][0]
    connection.commit()
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Кнопка", callback_data="button")
    profile = types.InlineKeyboardButton(text=f"{bot_score}", callback_data="profile")
    shop = types.InlineKeyboardButton(text="Магазин", callback_data="shop")
    markup.row(button)
    markup.row(profile, shop)
    bot.send_photo(chat_id=message.chat.id, message_thread_id=message.message_thread_id, photo=open(f"TapBotThemes/{fetched[0][1]}/Start.png", "rb"), caption=f"<b>Привет, {message.from_user.first_name}!</b>\nЭто {bot_name}!\n\nНажимай на кнопку\nи зарабатывай очки.\n\nЗачем всё это?\n<i>Кто знает...</i>", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=["help"])
def help(message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, user_name, bot_score, bot_level, theme_current, theme_dark) VALUES (?, ?, ?, ?, ?, ?)", (message.from_user.id, message.from_user.first_name, 0, 1, "Light", 0))
    cursor.execute("SELECT theme_current FROM users WHERE user_id = ?", (message.from_user.id,))
    fetched = cursor.fetchone()[0]
    connection.commit()
    markup = types.InlineKeyboardMarkup()
    start = types.InlineKeyboardButton(text="Главное меню", callback_data="start")
    markup.add(start)
    bot.send_photo(chat_id=message.chat.id, message_thread_id=message.message_thread_id, photo=open(f"TapBotThemes/{fetched}/Help.png", "rb"), caption="Спасибо, что использовали /help\nСкоро здесь что-то будет, а пока <i>ничего...</i>", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=["privacy"])
def privacy(message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, user_name, bot_score, bot_level, theme_current, theme_dark) VALUES (?, ?, ?, ?, ?, ?)", (message.from_user.id, message.from_user.first_name, 0, 1, "Light", 0))
    cursor.execute("SELECT theme_current FROM users WHERE user_id = ?", (message.from_user.id,))
    fetched = cursor.fetchone()[0]
    connection.commit()
    markup = types.InlineKeyboardMarkup()
    start = types.InlineKeyboardButton(text="Главное меню", callback_data="start")
    markup.add(start)
    bot.send_photo(chat_id=message.chat.id, message_thread_id=message.message_thread_id, photo=open(f"TapBotThemes/{fetched}/Privacy.png", "rb"), caption="Спасибо, что использовали /privacy\nСкоро здесь что-то будет, а пока <i>ничего...</i>", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=["admin"])
def admin(message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, user_name, bot_score, bot_level, theme_current, theme_dark) VALUES (?, ?, ?, ?, ?, ?)", (message.from_user.id, message.from_user.first_name, 0, 1, "Light", 0))
    connection.commit()
    markup = types.InlineKeyboardMarkup()
    start = types.InlineKeyboardButton(text="Главное меню", callback_data="start")
    markup.add(start)
    if message.from_user.id in admin_list:
        bot.send_message(chat_id=message.chat.id, message_thread_id=message.message_thread_id, text="Спасибо, что использовали /admin\nСкоро здесь что-то будет, а пока <i>ничего...</i>", parse_mode="HTML", reply_markup=markup)
    else:
        bot.send_message(chat_id=message.chat.id, message_thread_id=message.message_thread_id, text="У вас отсутствуют\nправа администратора!", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, user_name, bot_score, bot_level, theme_current, theme_dark) VALUES (?, ?, ?, ?, ?, ?)", (call.from_user.id, call.from_user.first_name, 0, 1, "Light", 0))
    cursor.execute("UPDATE users SET user_name = ? WHERE user_id = ?", (call.from_user.first_name, call.from_user.id))
    cursor.execute("SELECT bot_score, bot_level, theme_current, theme_dark FROM users WHERE user_id = ?", (call.from_user.id,))
    fetched = cursor.fetchall()
    if fetched[0][0] < 0:
        cursor.execute("UPDATE users SET bot_score = ? WHERE user_id = ?", (0, call.from_user.id))
        bot_score = 0
    else:
        bot_score = fetched[0][0]
    bot_level = fetched[0][1]
    theme_current = fetched[0][2]
    theme_dark = fetched[0][3]
    cursor.execute("SELECT COUNT(*), SUM(bot_score) FROM users")
    fetched = cursor.fetchall()
    total_users = fetched[0][0]
    total_score = fetched[0][1]
    connection.commit()
    # Кнопки
    # Главное меню
    button = types.InlineKeyboardButton(text="Кнопка", callback_data="button")
    profile = types.InlineKeyboardButton(text=f"{bot_score}", callback_data="profile")
    shop = types.InlineKeyboardButton(text="Магазин", callback_data="shop")
    # Профиль
    profile_bot = types.InlineKeyboardButton(text="Информация о боте", callback_data="profile_bot")
    profile_bot_update = types.InlineKeyboardButton(text="Обновить", callback_data="profile_bot")
    profile_bot_cancel = types.InlineKeyboardButton(text="Назад", callback_data="profile")
    profile_update = types.InlineKeyboardButton(text="Обновить", callback_data="profile")
    profile_cancel = types.InlineKeyboardButton(text="Главное меню", callback_data="start")
    # Магазин
    dice = types.InlineKeyboardButton(text="Кубик", callback_data="dice")
    dice_buy = types.InlineKeyboardButton(text="Купить", callback_data="dice_buy")
    casino = types.InlineKeyboardButton(text="Казино", callback_data="casino")
    casino_buy = types.InlineKeyboardButton(text="Купить", callback_data="casino_buy")
    upgrade = types.InlineKeyboardButton(text="Улучшение", callback_data="upgrade")
    upgrade_buy = types.InlineKeyboardButton(text="Купить", callback_data="upgrade_buy")
    themes = types.InlineKeyboardButton(text="Темы", callback_data="themes")
    shop_cancel = types.InlineKeyboardButton(text="Назад", callback_data="start")
    cancel_to_shop = types.InlineKeyboardButton(text="Назад", callback_data="shop")
    # Темы
    themes_light = types.InlineKeyboardButton(text="Светлая", callback_data="themes_light")
    themes_dark = types.InlineKeyboardButton(text="Тёмная", callback_data="themes_dark")
    if theme_current == "Light" and theme_dark == 0:
        themes_light_buy = types.InlineKeyboardButton(text="Установлена", callback_data="themes_light_buy")
        themes_dark_buy = types.InlineKeyboardButton(text="Купить", callback_data="themes_dark_buy")
    elif theme_current == "Light" and theme_dark == 1:
        themes_light_buy = types.InlineKeyboardButton(text="Установлена", callback_data="themes_light_buy")
        themes_dark_buy = types.InlineKeyboardButton(text="Установить", callback_data="themes_dark_buy")
    elif theme_current == "Dark" and theme_dark == 1:
        themes_light_buy = types.InlineKeyboardButton(text="Установить", callback_data="themes_light_buy")
        themes_dark_buy = types.InlineKeyboardButton(text="Установлена", callback_data="themes_dark_buy")
    cancel_to_themes = types.InlineKeyboardButton(text="Назад", callback_data="themes")
    if call.data == "button":
        cursor.execute("UPDATE users SET bot_score = ? WHERE user_id = ?", (bot_score + 1, call.from_user.id))
        connection.commit()
        markup = types.InlineKeyboardMarkup()
        profile = types.InlineKeyboardButton(text=f"{bot_score + 1}", callback_data="profile")
        markup.row(button)
        markup.row(profile, shop)
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id, media=types.InputMedia(type="photo", media=open(f"TapBotThemes/{theme_current}/Start.png", "rb"), caption=f"<b>Привет, {call.from_user.first_name}!</b>\nЭто {bot_name}!\n\nНажимай на кнопку\nи зарабатывай очки.\n\nЗачем всё это?\n<i>Кто знает...</i>", parse_mode="HTML"), reply_markup=markup)
    elif call.data == "start":
        markup = types.InlineKeyboardMarkup()
        markup.row(button)
        markup.row(profile, shop)
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id, media=types.InputMedia(type="photo", media=open(f"TapBotThemes/{theme_current}/Start.png", "rb"), caption=f"<b>Привет, {call.from_user.first_name}!</b>\nЭто {bot_name}!\n\nНажимай на кнопку\nи зарабатывай очки.\n\nЗачем всё это?\n<i>Кто знает...</i>", parse_mode="HTML"), reply_markup=markup)
    elif call.data == "profile":
        markup = types.InlineKeyboardMarkup()
        markup.row(profile_bot)
        markup.row(profile_update, profile_cancel)
        if call.from_user.username is None:
            username = ""
        else:
            username = f"\nUsername: @{call.from_user.username}"
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id, media=types.InputMedia(type="photo", media=open(f"TapBotThemes/{theme_current}/Profile.png", "rb"), caption=f"<b>Профиль {call.from_user.first_name}:</b>\n\nОчки: {bot_score}\nУровень: {bot_level}\n\nUser ID: <tg-spoiler>{call.from_user.id}</tg-spoiler>{username}", parse_mode="HTML"), reply_markup=markup)
    elif call.data == "profile_bot":
        markup = types.InlineKeyboardMarkup()
        markup.add(profile_bot_update, profile_bot_cancel)
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id, media=types.InputMedia(type="photo", media=open(f"TapBotThemes/{theme_current}/ProfileBot.png", "rb"), caption=f"<b>Информация о {bot_name}:</b>\n\nВсего очков: {total_score}\nВсего игроков: {total_users}\n\nОшибок: {errors}\nЗапущен: {started}\n\nКод бота на GitHub:\nhttps://github.com/DNS2000/TapBot", parse_mode="HTML"), reply_markup=markup)
    elif call.data == "shop":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(dice, casino, upgrade, themes, profile, shop_cancel)
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id, media=types.InputMedia(type="photo", media=open(f"TapBotThemes/{theme_current}/Shop.png", "rb"), caption="Добро пожаловать в магазин!\n\nЗдесь вы можете купить\nполезные штуки и прочие вещи."), reply_markup=markup)
    elif call.data == "dice":
        markup = types.InlineKeyboardMarkup()
        markup.row(dice_buy)
        markup.row(profile, cancel_to_shop)
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id, media=types.InputMedia(type="photo", media=open(f"TapBotThemes/{theme_current}/Dice.png", "rb"), caption=f"Цена броска кубика: {3 * bot_level} очков.\nМожно выбросить число от 1 до 6.\n\nПолученные очки умножатся\nна ваш текущий уровень. ({bot_level})"), reply_markup=markup)
    elif call.data == "dice_buy":
        if bot_score < 3 * bot_level:
            bot.answer_callback_query(callback_query_id=call.id, text="У вас не хватает очков для этого!", show_alert=True)
        else:
            cursor.execute("UPDATE users SET bot_score = ? WHERE user_id = ?", (bot_score - 3 * bot_level, call.from_user.id))
            connection.commit()
            try:
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
            finally:
                dice = bot.send_dice(chat_id=call.message.chat.id, message_thread_id=call.message.message_thread_id)
                message = bot.send_message(chat_id=call.message.chat.id, message_thread_id=call.message.message_thread_id, text=f"Вам выпадает...")
                time.sleep(4)
                cursor.execute("SELECT bot_score FROM users WHERE user_id = ?", (call.from_user.id,))
                fetched = cursor.fetchall()
                bot_score = fetched[0][0]
                cursor.execute("UPDATE users SET bot_score = ? WHERE user_id = ?", (bot_score + dice.dice.value, call.from_user.id))
                connection.commit()
                bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=f"Вам выпадает: {dice.dice.value}!")
                if bot_level > 1:
                    time.sleep(1)
                    bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=f"Вам выпадает: {dice.dice.value}!\n(Вы получаете {dice.dice.value * bot_level})")
                time.sleep(1)
                cursor.execute("SELECT bot_score FROM users WHERE user_id = ?", (call.from_user.id,))
                fetched = cursor.fetchall()
                bot_score = fetched[0][0]
                markup = types.InlineKeyboardMarkup()
                profile = types.InlineKeyboardButton(text=f"{bot_score}", callback_data="profile")
                markup.row(dice_buy)
                markup.row(profile, cancel_to_shop)
                bot.send_photo(chat_id=call.message.chat.id, message_thread_id=call.message.message_thread_id, photo=open(f"TapBotThemes/{theme_current}/Dice.png", "rb"), caption=f"Цена броска кубика: {3 * bot_level} очков.\nМожно выбросить число от 1 до 6.\n\nПолученные очки умножатся\nна ваш текущий уровень. ({bot_level})", reply_markup=markup)
    elif call.data == "casino":
        markup = types.InlineKeyboardMarkup()
        markup.row(casino_buy)
        markup.row(profile, cancel_to_shop)
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id, media=types.InputMedia(type="photo", media=open(f"TapBotThemes/{theme_current}/Casino.png", "rb"), caption=f"Цена прокрута казино: {30 * bot_level} очков.\nМожет выпасть число от 1 до 64.\n\nПолученные очки умножатся\nна ваш текущий уровень. ({bot_level})"), reply_markup=markup)
    elif call.data == "casino_buy":
        if bot_score < 30 * bot_level:
            bot.answer_callback_query(callback_query_id=call.id, text="У вас не хватает очков для этого!", show_alert=True)
        else:
            cursor.execute("UPDATE users SET bot_score = ? WHERE user_id = ?", (bot_score - 30 * bot_level, call.from_user.id))
            connection.commit()
            try:
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
            finally:
                casino = bot.send_dice(chat_id=call.message.chat.id, message_thread_id=call.message.message_thread_id, emoji="🎰")
                message = bot.send_message(chat_id=call.message.chat.id, message_thread_id=call.message.message_thread_id, text=f"Вам выпадает...")
                time.sleep(2)
                cursor.execute("SELECT bot_score FROM users WHERE user_id = ?", (call.from_user.id,))
                fetched = cursor.fetchall()
                bot_score = fetched[0][0]
                cursor.execute("UPDATE users SET bot_score = ? WHERE user_id = ?", (bot_score + casino.dice.value, call.from_user.id))
                connection.commit()
                bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=f"Вам выпадает: {casino.dice.value}!")
                if bot_level > 1:
                    time.sleep(1)
                    bot.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=f"Вам выпадает: {casino.dice.value}!\n(Вы получаете {casino.dice.value * bot_level})")
                time.sleep(1)
                cursor.execute("SELECT bot_score FROM users WHERE user_id = ?", (call.from_user.id,))
                fetched = cursor.fetchall()
                bot_score = fetched[0][0]
                markup = types.InlineKeyboardMarkup()
                profile = types.InlineKeyboardButton(text=f"{bot_score}", callback_data="profile")
                markup.row(casino_buy)
                markup.row(profile, cancel_to_shop)
                bot.send_photo(chat_id=call.message.chat.id, message_thread_id=call.message.message_thread_id, photo=open(f"TapBotThemes/{theme_current}/Casino.png", "rb"), caption=f"Цена прокрута казино: {30 * bot_level} очков.\nМожет выпасть число от 1 до 64.\n\nПолученные очки умножатся\nна ваш текущий уровень. ({bot_level})", reply_markup=markup)
    elif call.data == "upgrade":
        markup = types.InlineKeyboardMarkup()
        markup.row(upgrade_buy)
        markup.row(profile, cancel_to_shop)
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id, media=types.InputMedia(type="photo", media=open(f"TapBotThemes/{theme_current}/Upgrade.png", "rb"), caption=f"Цена улучшения: {500 * 2 ** (bot_level - 1)} очков.\nУвеличивает ваш уровень. ({bot_level})\n\nЦена улучшения увеличивается\nв два раза после каждой покупки."), reply_markup=markup)
    elif call.data == "upgrade_buy":
        if bot_score < 500 * 2 ** (bot_level - 1):
            bot.answer_callback_query(callback_query_id=call.id, text="У вас не хватает очков для этого!", show_alert=True)
        else:
            cursor.execute("UPDATE users SET bot_score = ?, bot_level = ? WHERE user_id = ?", (bot_score - 500 * 2 ** (bot_level - 1), bot_level + 1, call.from_user.id))
            connection.commit()
            try:
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
            finally:
                bot.send_photo(chat_id=call.message.chat.id, message_thread_id=call.message.message_thread_id, photo=open(f"TapBotThemes/{theme_current}/LevelUp.png", "rb"), caption=f"Ваш уровень повышен! ({bot_level + 1})")
                time.sleep(1)
                cursor.execute("SELECT bot_score, bot_level FROM users WHERE user_id = ?", (call.from_user.id,))
                fetched = cursor.fetchall()
                bot_score = fetched[0][0]
                bot_level = fetched[0][1]
                markup = types.InlineKeyboardMarkup()
                profile = types.InlineKeyboardButton(text=f"{bot_score}", callback_data="profile")
                markup.row(upgrade_buy)
                markup.row(profile, cancel_to_shop)
                bot.send_photo(chat_id=call.message.chat.id, photo=open(f"TapBotThemes/{theme_current}/Upgrade.png", "rb"), caption=f"Цена улучшения: {500 * 2 ** (bot_level - 1)} очков.\nУвеличивает ваш уровень. ({bot_level})\n\nЦена улучшения увеличивается\nв два раза после каждой покупки.", reply_markup=markup)
    elif call.data == "themes":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(themes_light, themes_dark, profile, cancel_to_shop)
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id, media=types.InputMedia(type="photo", media=open(f"TapBotThemes/{theme_current}/Themes.png", "rb"), caption=f"В магазине тем можно купить и\nустановить разные темы для бота.\n\nДа будет цвет!"), reply_markup=markup)
    elif call.data == "themes_light":
        markup = types.InlineKeyboardMarkup()
        markup.row(themes_light_buy)
        markup.row(profile, cancel_to_themes)
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id, media=types.InputMedia(type="photo", media=open(f"TapBotThemes/Light/Theme.png", "rb"), caption=f"Светлая тема.\n\nВыдаётся по умолчанию."), reply_markup=markup)
    elif call.data == "themes_light_buy":
        if theme_current == "Light":
            bot.answer_callback_query(callback_query_id=call.id, text="Эта тема уже установлена!", show_alert=True)
        else:
            cursor.execute("UPDATE users SET theme_current = ? WHERE user_id = ?", ("Light", call.from_user.id))
            connection.commit()
            markup = types.InlineKeyboardMarkup()
            themes_light_buy = types.InlineKeyboardButton(text="Установлена", callback_data="themes_light_buy")
            markup.row(themes_light_buy)
            markup.row(profile, cancel_to_themes)
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id, media=types.InputMedia(type="photo", media=open(f"TapBotThemes/Light/Theme.png", "rb"), caption=f"Светлая тема.\n\nВыдаётся по умолчанию."), reply_markup=markup)
            bot.answer_callback_query(callback_query_id=call.id, text="Тема установлена!", show_alert=True)
    elif call.data == "themes_dark":
        markup = types.InlineKeyboardMarkup()
        markup.row(themes_dark_buy)
        markup.row(profile, cancel_to_themes)
        bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id, media=types.InputMedia(type="photo", media=open(f"TapBotThemes/Dark/Theme.png", "rb"), caption=f"Тёмная тема.\n\nЦена: 10000 очков."), reply_markup=markup)
    elif call.data == "themes_dark_buy":
        if theme_current == "Dark":
            bot.answer_callback_query(callback_query_id=call.id, text="Эта тема уже установлена!", show_alert=True)
        elif theme_dark == 1:
            cursor.execute("UPDATE users SET theme_current = ? WHERE user_id = ?", ("Dark", call.from_user.id))
            connection.commit()
            markup = types.InlineKeyboardMarkup()
            themes_dark_buy = types.InlineKeyboardButton(text="Установлена", callback_data="themes_dark_buy")
            markup.row(themes_dark_buy)
            markup.row(profile, cancel_to_themes)
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id, media=types.InputMedia(type="photo", media=open(f"TapBotThemes/Dark/Theme.png", "rb"), caption=f"Тёмная тема.\n\nЦена: 10000 очков."), reply_markup=markup)
            bot.answer_callback_query(callback_query_id=call.id, text="Тема установлена!", show_alert=True)
        else:
            if bot_score < 10000:
                bot.answer_callback_query(callback_query_id=call.id, text="У вас не хватает очков для этого!", show_alert=True)
            else:
                cursor.execute("UPDATE users SET bot_score = ?, theme_current = ?, theme_dark = ? WHERE user_id = ?", (bot_score - 10000, "Dark", 1, call.from_user.id))
                connection.commit()
                markup = types.InlineKeyboardMarkup()
                themes_dark_buy = types.InlineKeyboardButton(text="Установлена", callback_data="themes_dark_buy")
                markup.row(themes_dark_buy)
                markup.row(profile, cancel_to_themes)
                bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.id, media=types.InputMedia(type="photo", media=open(f"TapBotThemes/Dark/Theme.png", "rb"), caption=f"Тёмная тема.\n\nЦена: 10000 очков."), reply_markup=markup)
                bot.answer_callback_query(callback_query_id=call.id, text="Тема приобретена и установлена!", show_alert=True)
    else:
        bot.answer_callback_query(callback_query_id=call.id, text="Кнопка недоступна!", show_alert=True)

started = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"\nБот успешно запущен.\n{started}\n")

while True:
    try:
        bot.polling(none_stop=True, timeout=600)
    except:
        errors += 1
        print(f"\n{str(traceback.format_exc()).replace(str(bot_token), "*bot_token*")}\nВозникла ошибка. ({errors})\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n")