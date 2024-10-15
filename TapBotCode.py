import configparser, traceback, logging, sqlite3, time, json
from datetime import *
from telebot import *

config = configparser.ConfigParser()
config.read("TapBotConfig.ini")
try:
    config.get("TapBotConfig", "bot_token")
except:
    config.add_section("TapBotConfig")
    config.set("TapBotConfig", "bot_token", "bot_token") # Токен бота без кавычек
    config.set("TapBotConfig", "admin_list", "[]") # ID администраторов бота через запятую
    config.write(open("TapBotConfig.ini", "w"))

connection = sqlite3.connect("TapBotDatabase.db", check_same_thread=False)
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY NOT NULL, user_name TEXT NOT NULL, bot_score INTEGER NOT NULL, bot_level INTEGER NOT NULL)")
connection.commit()

global errors, started, bot_name, admin_list
errors = 0
bot_name = "DNS2000's BOT"
admin_list = json.loads(config.get("TapBotConfig", "admin_list"))

telebot.telebot.logger.setLevel(logging.ERROR)
class ExceptionHandler(telebot.ExceptionHandler):
    def handle(self, exception):
        global errors
        errors += 1
        print(f"\n{str(traceback.format_exc()).replace(str(config.get("TapBotConfig", "bot_token")), "*bot_token*")}\nВозникла ошибка. ({errors})\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n")
        return True

bot = telebot.TeleBot(token=str(config.get("TapBotConfig", "bot_token")), exception_handler=ExceptionHandler())

started = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"\nБот успешно запущен.\n{started}\n")

@bot.message_handler(commands=["start"])
def start(message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, user_name, bot_score, bot_level) VALUES (?, ?, ?, ?)", (message.from_user.id, message.from_user.first_name, 0, 1))
    cursor.execute("UPDATE users SET user_name = ? WHERE user_id = ?", (message.from_user.first_name, message.from_user.id))
    connection.commit()
    cursor.execute("SELECT bot_score FROM users WHERE user_id = ?", (message.from_user.id,))
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Кнопка", callback_data="button")
    profile = types.InlineKeyboardButton(text=f"{cursor.fetchone()[0]}", callback_data="profile")
    shop = types.InlineKeyboardButton(text="Магазин", callback_data="shop")
    markup.row(button)
    markup.row(profile, shop)
    bot.reply_to(message=message, text=f"<b>Привет, {message.from_user.first_name}!</b>\nЭто {bot_name}!\n\nНажимай на кнопку\nи зарабатывай очки.\n\nЗачем всё это?\n<i>Кто знает...</i>", parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=["help"])
def help(message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, user_name, bot_score, bot_level) VALUES (?, ?, ?, ?)", (message.from_user.id, message.from_user.first_name, 0, 1))
    cursor.execute("UPDATE users SET user_name = ? WHERE user_id = ?", (message.from_user.first_name, message.from_user.id))
    connection.commit()
    bot.reply_to(message=message, text="Спасибо, что использовали /help\nСкоро здесь что-то будет,\nа пока... <i>ничего</i>", parse_mode="HTML")

@bot.message_handler(commands=["privacy"])
def help(message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, user_name, bot_score, bot_level) VALUES (?, ?, ?, ?)", (message.from_user.id, message.from_user.first_name, 0, 1))
    cursor.execute("UPDATE users SET user_name = ? WHERE user_id = ?", (message.from_user.first_name, message.from_user.id))
    connection.commit()
    bot.reply_to(message=message, text="Спасибо, что использовали /privacy\nСкоро здесь что-то будет,\nа пока... <i>ничего</i>", parse_mode="HTML")

@bot.message_handler(commands=["admin"])
def admin(message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, user_name, bot_score, bot_level) VALUES (?, ?, ?, ?)", (message.from_user.id, message.from_user.first_name, 0, 1))
    cursor.execute("UPDATE users SET user_name = ? WHERE user_id = ?", (message.from_user.first_name, message.from_user.id))
    connection.commit()
    if message.from_user.id in admin_list:
        bot.reply_to(message=message, text="Спасибо, что использовали /admin\nСкоро здесь что-то будет,\nа пока... <i>ничего</i>", parse_mode="HTML")
    else:
        bot.reply_to(message=message, text="У вас отсутствуют\nправа администратора!")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    cursor.execute("INSERT OR IGNORE INTO users (user_id, user_name, bot_score, bot_level) VALUES (?, ?, ?, ?)", (call.from_user.id, call.from_user.first_name, 0, 1))
    cursor.execute("UPDATE users SET user_name = ? WHERE user_id = ?", (call.from_user.first_name, call.from_user.id))
    connection.commit()
    cursor.execute("SELECT bot_score, bot_level FROM users WHERE user_id = ?", (call.from_user.id,))
    fetched = cursor.fetchall()
    bot_score = fetched[0][0]
    bot_level = fetched[0][1]
    # Кнопки
    # Главное меню
    button = types.InlineKeyboardButton(text="Кнопка", callback_data="button")
    profile = types.InlineKeyboardButton(text=f"{bot_score}", callback_data="profile")
    shop = types.InlineKeyboardButton(text="Магазин", callback_data="shop")
    # Магазин
    shop_dice = types.InlineKeyboardButton(text="Кубик", callback_data="shop_dice")
    shop_casino = types.InlineKeyboardButton(text="Казино", callback_data="shop_casino")
    shop_upgrade = types.InlineKeyboardButton(text="Улучшение", callback_data="shop_upgrade")
    shop_themes = types.InlineKeyboardButton(text="Темы", callback_data="shop_themes")
    shop_score = types.InlineKeyboardButton(text=f"{bot_score}", callback_data="profile")
    shop_cancel = types.InlineKeyboardButton(text="Назад", callback_data="start")
    # Профиль
    profile_bot = types.InlineKeyboardButton(text="Статистика бота", callback_data="profile_bot")
    profile_bot_update = types.InlineKeyboardButton(text="Обновить", callback_data="profile_bot")
    profile_bot_cancel = types.InlineKeyboardButton(text="Назад", callback_data="profile")
    profile_update = types.InlineKeyboardButton(text="Обновить", callback_data="profile")
    profile_cancel = types.InlineKeyboardButton(text="Главное меню", callback_data="start")
    if call.data == "button":
        cursor.execute("UPDATE users SET bot_score = ? WHERE user_id = ?", (bot_score + 1, call.from_user.id))
        connection.commit()
        markup = types.InlineKeyboardMarkup()
        profile = types.InlineKeyboardButton(text=f"{bot_score + 1}", callback_data="profile")
        markup.row(button)
        markup.row(profile, shop)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f"<b>Привет, {call.from_user.first_name}!</b>\nЭто {bot_name}!\n\nНажимай на кнопку\nи зарабатывай очки.\n\nЗачем всё это?\n<i>Кто знает...</i>", parse_mode="HTML", reply_markup=markup)
    elif call.data == "start":
        markup = types.InlineKeyboardMarkup()
        markup.row(button)
        markup.row(profile, shop)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f"<b>Привет, {call.from_user.first_name}!</b>\nЭто {bot_name}!\n\nНажимай на кнопку\nи зарабатывай очки.\n\nЗачем всё это?\n<i>Кто знает...</i>", parse_mode="HTML", reply_markup=markup)
    elif call.data == "profile":
        markup = types.InlineKeyboardMarkup()
        markup.row(profile_bot)
        markup.row(profile_update, profile_cancel)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f"Профиль @{call.from_user.username}:\n\nОчки: {bot_score}\nУровень: {bot_level}\n\nИмя: {call.from_user.first_name}\nUser ID: <tg-spoiler>{call.from_user.id}</tg-spoiler>", parse_mode="HTML", reply_markup=markup)
    elif call.data == "profile_bot":
        cursor.execute("SELECT * FROM users")
        total_users = len(cursor.fetchall())
        cursor.execute("SELECT SUM(bot_score) FROM users")
        total_score = cursor.fetchone()[0]
        markup = types.InlineKeyboardMarkup()
        markup.row(profile_bot_update, profile_bot_cancel)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f"Статистика {bot_name}:\n\nВсего очков: {total_score}\nВсего игроков: {total_users}\n\nОшибок: {errors}\nЗапущен: {started}", reply_markup=markup)
    elif call.data == "shop":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(shop_dice, shop_casino, shop_upgrade, shop_themes, shop_score, shop_cancel)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Добро пожаловать в магазин!\n\nЗдесь вы можете купить\nполезные штуки и прочие вещи.", reply_markup=markup)
    else:
        bot.answer_callback_query(callback_query_id=call.id, text="Кнопка недоступна!", show_alert=True)

while True:
    try:
        bot.polling(none_stop=True, timeout=600)
    except:
        errors += 1
        print(f"\n{str(traceback.format_exc()).replace(str(config.get("TapBotConfig", "bot_token")), "*bot_token*")}\nВозникла ошибка. ({errors})\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n")