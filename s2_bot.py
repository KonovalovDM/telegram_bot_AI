import telebot
from openai import OpenAI
from gtts import gTTS
import os
from pydub import AudioSegment
from pydub.utils import which
import logging

# Настройка логирования для отладки
logging.basicConfig(level=logging.INFO)

# Проверка текущей рабочей директории
import os
print(f'текущая рабочая директория', os.getcwd())

# Укажите путь к ffmpeg
ffmpeg_path = r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe"
if not os.path.isfile(ffmpeg_path):
    logging.error(f"ffmpeg не найден по пути {ffmpeg_path}")
else:
    AudioSegment.converter = which(ffmpeg_path)
    logging.info(f"Установлен путь к ffmpeg: {ffmpeg_path}")

# Инициализация клиента OpenAI
api_key = "{PROXY_API_KEY}"
base_url = "https://api.proxyapi.ru/openai/v1"
try:
    client = OpenAI(api_key=api_key, base_url=base_url)
    logging.info("Клиент OpenAI инициализирован успешно")
except Exception as e:
    logging.error(f"Ошибка инициализации клиента OpenAI: {e}")

# Инициализация Telegram-бота
API_TOKEN = 'YOUR_API_TOKEN_HERE'
bot = telebot.TeleBot(API_TOKEN)

# Обработчик сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text
    logging.info(f"Получено сообщение от пользователя: {user_input}")

    try:
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106", 
            messages=[
                {"role": "system", "content": "отвечай в стиле веселого программиста"},
                {"role": "user", "content": user_input}
            ]
        )
        neural_net_response = chat_completion.choices[0].message.content
        logging.info(f"Ответ нейронной сети: {neural_net_response}")
    except Exception as e:
        logging.error(f"Ошибка получения ответа от OpenAI: {e}")
        bot.reply_to(message, "Произошла ошибка при получении ответа от нейронной сети.")
        return

    # Сначала отправляем текстовый ответ
    bot.reply_to(message, neural_net_response)

    try:
        # Преобразование текста в голос
        tts = gTTS(text=neural_net_response, lang='ru')
        tts.save("response.mp3")

        # Используем pydub для изменения темпа речи
        sound = AudioSegment.from_file("response.mp3")
        sound_with_increased_tempo = sound.speedup(playback_speed=1.25)

        # Сохранение измененного файла
        temp_file = "response_fast.mp3"
        sound_with_increased_tempo.export(temp_file, format="mp3")

        # Отправка голосового сообщения
        with open(temp_file, "rb") as voice:
            bot.send_voice(message.chat.id, voice)
    except Exception as e:
        logging.error(f"Ошибка при обработке голосового сообщения: {e}")
        bot.reply_to(message, "Произошла ошибка при обработке голосового сообщения.")
    finally:
        # Удаление временных файлов
        if os.path.isfile("response.mp3"):
            os.remove("response.mp3")
        if os.path.isfile(temp_file):
            os.remove(temp_file)

# Запуск бота
if __name__ == "__main__":
    logging.info("Запуск бота")
    bot.polling(none_stop=True)
