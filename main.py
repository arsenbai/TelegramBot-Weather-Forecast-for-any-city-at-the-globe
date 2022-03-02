from config import TOKEN, token_openweathermap
import telebot
from datetime import datetime, timedelta
# import datetime
import requests
# from telegram.ext import Updater, CommandHandler, CallbackContext
# import logging


bot = telebot.TeleBot(TOKEN)
city_name = ''


# updater = Updater(token=TOKEN, use_context=True)
# dispatcher = updater.dispatcher
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# j = updater.job_queue
#
#
# def once(context: CallbackContext):
#     message = "Hello, this message will be sent only once"
#
#     # send message to all users
#     for keys in db_keys:
#         id = r.get(keys).decode("UTF-8")
#         context.bot.send_message(chat_id=id, text=message)
# j.run_once(once, 30)
#
#
# def morning(context: CallbackContext):
#     message = "Good Morning! Have a nice day!"
#
#     # send message to all users
#     for keys in db_keys:
#         id = r.get(keys).decode("UTF-8")
#         context.bot.send_message(chat_id=id, text=message)
# job_daily = j.run_daily(morning, days=(0, 1, 2, 3, 4, 5, 6), time=datetime.time(hour=3, minute=25, second=00))



@bot.message_handler(func=lambda m: True)
def reply_message(message):
    if message.text == '/start':
        bot.send_message(message.from_user.id, 'Select your city')
        bot.register_next_step_handler(message, saving_city)

def saving_city(message):
    try:
        bot.send_message(message.from_user.id, text=f'You have selected {message.text}')
        global city_name
        city_name = message.text

        # START of PARSING DATA
        lat_lon_request = requests.get(
            f'http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={token_openweathermap}'
        )
        lat_lon_json = lat_lon_request.json()
        lat = lat_lon_json[0]['lat']
        lon = lat_lon_json[0]['lon']


        forecast_request = requests.get(
            f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={token_openweathermap}&units=metric&cnt=16'
        )
        forecast_request_json = forecast_request.json()

        tmrw_date_for_calc = datetime.now() + timedelta(1)
        target_date_time = tmrw_date_for_calc.strftime("%Y-%m-%d") + ' 06:00:00'


        for i in range(len(forecast_request_json['list'])):
            if forecast_request_json['list'][i]['dt_txt'] == target_date_time:
                global tommorow_morning_date_time, tommorow_morning_weather_forecast_description, tommorow_morning_weather_forecast_icon
                tommorow_morning_date_time = forecast_request_json['list'][i]['dt_txt']
                tommorow_morning_weather_forecast_description = forecast_request_json['list'][i]['weather'][0]['main']
                tommorow_morning_weather_forecast_icon = forecast_request_json['list'][i]['weather'][0]['icon']
                break
            else:
                continue
        # ENDING of PARSING DATA
        if tommorow_morning_weather_forecast_description == 'Shower rain' or tommorow_morning_weather_forecast_description == 'Rain':
            bot.send_message(message.from_user.id, text=f'''
{tommorow_morning_date_time}
Tommorow morning - 🏙 {forecast_request_json['city']['name']}
    Weather: {tommorow_morning_weather_forecast_description} 🌧
    Temperature: {forecast_request_json['list'][i]['main']['temp']} ℃
    🌟 Advice 🌟
    Please take an umbrella ☔ 
    ''')

        elif tommorow_morning_weather_forecast_description == 'Snow':
            bot.send_message(message.from_user.id, text=f'''
{tommorow_morning_date_time}
Tommorow morning - 🏙 {forecast_request_json['city']['name']}
    Weather: {tommorow_morning_weather_forecast_description} ❄🌨❄
    Temperature: {forecast_request_json['list'][i]['main']['temp']} ℃
    🌟 Advice 🌟
    It will be snowy - be careful on the road.
            ''')

        elif tommorow_morning_weather_forecast_description == 'Clouds':
            bot.send_message(message.from_user.id, text=f'''
{tommorow_morning_date_time}
Tommorow morning - 🏙 {forecast_request_json['city']['name']}
    Weather: {tommorow_morning_weather_forecast_description} ☁
    Temperature: {forecast_request_json['list'][i]['main']['temp']} ℃''')

        elif tommorow_morning_weather_forecast_description == 'Clear':
            bot.send_message(message.from_user.id, text=f'''
    {tommorow_morning_date_time}
Tommorow morning - 🏙 {forecast_request_json['city']['name']}
    Weather: {tommorow_morning_weather_forecast_description} ☀
    Temperature: {forecast_request_json['list'][i]['main']['temp']} ℃''')

        else:
            bot.send_message(message.from_user.id, text=f'''
{tommorow_morning_date_time}
Tommorow morning - 🏙 {forecast_request_json['city']['name']}
    Weather: {tommorow_morning_weather_forecast_description}
    Temperature: {forecast_request_json['list'][i]['main']['temp']} ℃
                ''')
        bot.register_next_step_handler(message, idle)

    except:
        bot.send_message(message.from_user.id, text='⚠ Check city name for errors ⚠')
        bot.register_next_step_handler(message, reply_message)

@bot.message_handler(func=lambda m: True)
def idle(message):
    if message.text == '/change_city':
        bot.send_message(message.from_user.id, 'Select your city')
        bot.register_next_step_handler(message, saving_city)

bot.polling()


