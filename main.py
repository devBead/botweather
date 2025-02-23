import requests
import telebot
from telebot import types
from settings.config import token, weather_api_key  
bot = telebot.TeleBot(token=token)

@bot.message_handler(commands=['start'])
def start(message):
    kb = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton("Москва", callback_data="city Moscow")
    button2 = types.InlineKeyboardButton("Питер", callback_data="city Piter")
    button3 = types.InlineKeyboardButton("Волгоград", callback_data="city Волгоград")
    kb.add(button1, button2, button3)

    uid = message.from_user.id
    bot.send_message(uid, """
Привет, я бот прогнозник. И здесь ты можешь просмотреть погоду, выбрав город на клавиатуре. Если твоего города нет, просто отправь его название в наш чат.
""", reply_markup=kb)

class WeatherAPI:
    def __init__(self, city: str):
        self.city = city
        self.api_key = weather_api_key
        self.url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}&lang=ru&units=metric"

    def get_weather(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            data = response.json()
            temperature = data['main']['temp']
            title = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind = data['wind']['speed']
            time = "Текущая погода"
            
            return {
                "temp": temperature,
                "title": title,
                "hum": humidity,
                "time": time,
                "wind": wind
            }
        else:
            return None

@bot.message_handler(content_types=['text'])
def texts(message):
    weather = WeatherAPI(message.text)
    weather_data = weather.get_weather()
    
    if weather_data is None:
        bot.send_message(message.chat.id, f'Информация о городе "{message.text}" не найдена!')
        return
    
    msg = f"""Погода в --> {weather.city}

Дата: {weather_data['time']}
Ветер: {weather_data['wind']} м/с
Температура: {weather_data['temp']}°C
Влажность: {weather_data['hum']}% ({weather_data['title']})"""
    
    bot.send_message(message.chat.id, msg)

@bot.callback_query_handler(func=lambda call: call.data.startswith('city'))
def citys(call):
    city_map = {
        "city Moscow": "Москва",
        "city Piter": "Санкт-Петербург",
        "city Волгоград": "Волгоград"
    }
    
    city = city_map.get(call.data)
    if city:
        weather = WeatherAPI(city)
        weather_data = weather.get_weather()

        if weather_data is None:
            bot.send_message(call.message.chat.id, f'Информация о городе "{city}" не найдена!')
            return
        
        msg = f"""Погода в --> {weather.city}

Дата: {weather_data['time']}
Ветер: {weather_data['wind']} м/с
Температура: {weather_data['temp']}°C
Влажность: {weather_data['hum']}% ({weather_data['title']})"""

        bot.send_message(call.message.chat.id, msg)


if __name__ == '__main__':
    bot.infinity_polling()
