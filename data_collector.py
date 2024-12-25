# scripts/data_collector.py
import requests
import psycopg2
import time
import telebot

API_URL = "https://api.openweathermap.org/data/2.5/weather?q=Moscow&appid=b128a68b5a99a869eae52f9e9a708da6&units=metric"
TELEGRAM_TOKEN = '8187727666:AAHtYT0jXByLCeKPNSOCHaBZ1F2OM-tDW-M'
TEMP_THRESHOLD = 5  # Порог для скачка температуры

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Настройки подключения к PostgreSQL
DB_CONFIG = {
    'dbname': 'weather_db',
    'user': 'user',
    'password': 'pass',
    'host': 'postgres_db',
    'port': 5432
}

def create_weather_table():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather (
            id SERIAL PRIMARY KEY,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT (CURRENT_TIMESTAMP  + INTERVAL '3 hours')
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()
#i = 0
def fetch_weather_data():
    response = requests.get(API_URL)
    data = response.json()
    #global i #потом удалить контейнеры бота и колерктора их имеджи и запустить поочереди
    #i+=1
    temperature = data['main']['temp']
    humidity = data['main']['humidity']
    #if i>=2:
        #temperature += 100.0
    return temperature, humidity

def get_previous_temperature():
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT temperature FROM weather ORDER BY timestamp DESC LIMIT 1")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result[0]
    return None

def store_weather_data(temperature, humidity):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO weather (temperature, humidity) VALUES (%s, %s)", (temperature, humidity))
    conn.commit()
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

def check_for_temperature_spike(current_temp):
    previous_temp = get_previous_temperature()
    if previous_temp is not None:
        temp_diff = abs(current_temp - previous_temp)
        if temp_diff >= TEMP_THRESHOLD:
            notify_all_users(current_temp, previous_temp, temp_diff)

def notify_all_users(current_temp, previous_temp, temp_diff):
    chat_ids = get_all_chat_ids()
    message = f"Внимание! Резкий скачок температуры:\n" \
              f"Предыдущая температура: {previous_temp} °C\n" \
              f"Текущая температура: {current_temp} °C\n" \
              f"Разница: {temp_diff} °C"
    for chat_id in chat_ids:
        bot.send_message(chat_id, message)

def main():
    create_weather_table()
    while True:
        temperature, humidity = fetch_weather_data()
        check_for_temperature_spike(temperature)
        store_weather_data(temperature, humidity)
        time.sleep(60)  

if __name__ == '__main__':
    main()
