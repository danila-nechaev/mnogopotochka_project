import psycopg2
import telebot
from datetime import datetime, timedelta

API_TOKEN = '8187727666:AAHtYT0jXByLCeKPNSOCHaBZ1F2OM-tDW-M'
bot = telebot.TeleBot(API_TOKEN)

# Настройки подключения к PostgreSQL
DB_CONFIG = {
    'dbname': 'weather_db',
    'user': 'user',
    'password': 'pass',
    'host': 'postgres_db',
    'port': 5432
}

def create_chat_table():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id SERIAL PRIMARY KEY,
            chat_id BIGINT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

def save_chat_id(chat_id):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO chats (chat_id) VALUES (%s) ON CONFLICT (chat_id) DO NOTHING", (chat_id,))
        conn.commit()
    except Exception as e:
        print(f"Ошибка сохранения chat_id: {e}")
    finally:
        cursor.close()
        conn.close()


def get_all_chat_ids():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM chats")
    chat_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return chat_ids

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    save_chat_id(chat_id)
    bot.reply_to(message, "Привет! Ты будешь получать уведомления о погоде. Используй команду /weather, чтобы узнать последние данные.")


@bot.message_handler(commands=['weather'])
def send_weather(message):
    chat_id = message.chat.id
    save_chat_id(chat_id)  # Сохраняем chat_id, если его ещё нет в базе

    # Подключение к базе данных
    
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Получаем последние данные о погоде
    cursor.execute("SELECT temperature, humidity FROM weather ORDER BY timestamp DESC LIMIT 1")
    weather_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if weather_data:
        temperature, humidity = weather_data

        # Текущее время с добавлением 3 часов
        updated_time = datetime.now() + timedelta(hours=3)
        formatted_time = updated_time.strftime('%Y-%m-%d %H:%M')

        # Ответ
        response = (
            f"Последние данные о погоде:\n"
            f"Температура: {temperature} °C\n"
            f"Влажность: {humidity}%\n"
            f"Текущее время : {formatted_time}"
        )
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "Нет доступных данных о погоде.")


if __name__ == '__main__':
    create_chat_table()
    bot.polling()

