from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import pyfiglet
from colorama import init, Fore, Style
from google.oauth2 import service_account
import google.auth.transport.requests
import sys
import time
import threading
import random
import tkinter as tk
from tkinter import messagebox, Tk, Canvas, Label, PhotoImage
#Прогрессбар в начале (фикция)
def progress_bar(iteration, total, length=40):
    percent = (iteration / total) * 100
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r|{bar}| {percent:.2f}%')
    sys.stdout.flush()

def loading_indicator(duration):
    total = 100
    delay = duration / total  # Основная задержка на каждую итерацию
    for i in range(total + 1):
        progress_bar(i, total)
        time.sleep(delay)
        if random.random() < 0.05:
            random_delay = random.uniform(0.1, 0.2)
            time.sleep(random_delay)
    print()

loading_thread = threading.Thread(target=loading_indicator, args=(0.5,), daemon=True)  # Задаем время работы индикатора
loading_thread.start()

#Коннектер Google cloud
SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
credentials_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..\..\DialogFlow\JSON\Private.json')

credentials = service_account.Credentials.from_service_account_file(
    credentials_path, scopes=SCOPES)
#API DIALOGFLOW
DIALOGFLOW_API_KEY = 'AIzaSyDUYB54lamN52glZC4FqC7Hz3yBGe30hgw'
#GOOGLEAPIS URL
DIALOGFLOW_URL = 'https://dialogflow.googleapis.com/v2/projects/temisupport-vjgf/agent/sessions/123456789:detectIntent'

request = google.auth.transport.requests.Request()
credentials.refresh(request)
access_token = credentials.token
loading_thread.join()

#Сообщение о подключении (фикция)
print(f" DialogFlow connected: sucsess!")
print(f" API Telegram connected: sucsess!")
print(f" Google cloud connected: sucsess!")
print(f" All handlers active!")
#Сообщение при /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Привет, давай пообщаемся?')

#Обработка запросов
async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    message_text = update.message.text
    timestamp = update.message.date
    user = update.effective_user

    # Вывод информации о сообщении в консоль
    print(f"")
    print(f" ____________NEW MESSAGE__________")
    print(f" User ID: {user.id}")
    print(f" Chat ID: {chat_id}")
    print(f" User First Name: {user.first_name}")
    print(f" User Last Name: {user.last_name}")
    print(f" Message: {message_text}")
    print(f" Message ID: {update.message.message_id}")
    print(f" Timestamp: {timestamp}")
    print(f" _________________________________")
    print(f"")

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Формируем запрос
    data = {
        "queryInput": {
            "text": {
                "text": update.message.text,
                "languageCode": "ru"
            }
        }
    }

    # Отправляем запрос
    response = requests.post(DIALOGFLOW_URL, headers=headers, json=data)

    # Обработка ответа
    if response.status_code == 200:
        response_json = response.json()
        response_text = response_json.get('queryResult', {}).get('fulfillmentText', '')
        
        if response_text:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Я Вас не совсем понял!')
    else:
        print(f'Error {response.status_code}: {response.text}')  # Выводим текст ответа для отладки
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Ошибка обращения к Dialogflow.')

# API TELEGRAM
application = ApplicationBuilder().token('8138073009:AAG_MbSK11SQKdA37f66Q-3aCvZqy_ZApzo').build()

# Хендлеры
start_command_handler = CommandHandler('start', start_command)
text_message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, text_message)

# Добавляем хендлеры в приложение
application.add_handler(start_command_handler)
application.add_handler(text_message_handler)

#Уведомление о старте
init()
console_startmessage = pyfiglet.figlet_format("Temisupport", font="slant")
print(Fore.GREEN + console_startmessage + Style.RESET_ALL)

#Polling starter
application.run_polling()