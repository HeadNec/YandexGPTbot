import telebot
from validators import *  # модуль для валидации
from yandex_gpt import ask_gpt  # модуль для работы с GPT
# подтягиваем константы из config файла
from config import TOKEN, LOGS, COUNT_LAST_MSG
# подтягиваем функции из database файла
from database import create_database, add_message, select_n_last_messages
from speechkit import speech_to_text, text_to_speech
from creds import get_bot_token  # модуль для получения bot_token
bot = telebot.TeleBot(get_bot_token())


# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")
bot = telebot.TeleBot(TOKEN)  # создаём объект бота



# обрабатываем команду /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, "Привет! Отправь мне голосовое сообщение или текст, и я тебе отвечу!")
    create_database()



# обрабатываем команду /help
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id, "Чтобы приступить к общению, отправь мне голосовое сообщение или текст\f"
                                           "\f/tts - проверка перевода текста в голосове сообщение"
                                           "\f/stt - проверка перевода голосового сообщения в текст")



# обрабатываем команду /debug - отправляем файл с логами
@bot.message_handler(commands=['debug'])
def debug(message):
    with open("logs.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(commands=['stt'])
def stt_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Отправь голосовое сообщение, чтобы я его распознал!')
    bot.register_next_step_handler(message, stt)

# Переводим голосовое сообщение в текст после команды stt
def stt(message):
    user_id = message.from_user.id

    # Проверка, что сообщение действительно голосовое
    if not message.voice:
        return

    # Считаем аудиоблоки и проверяем сумму потраченных аудиоблоков
    stt_blocks = is_stt_block_limit(user_id, message.voice.duration)
    if not stt_blocks:
        return

    file_id = message.voice.file_id  # получаем id голосового сообщения
    file_info = bot.get_file(file_id)  # получаем информацию о голосовом сообщении
    file = bot.download_file(file_info.file_path)  # скачиваем голосовое сообщение

    # Получаем статус и содержимое ответа от SpeechKit
    status, text = speech_to_text(file)# преобразовываем голосовое сообщение в текст
    duration = message.voice.duration
    audio_blocks = math.ceil(duration / 15)  # округляем в большую сторону
    if not text:
        bot.send_message(user_id, "Голосовое сообщение пустое, либо не имеет понятных слов, пожалуйста отправьте новое")
        return
    if text == "":
        bot.send_message(user_id, "Голосовое сообщение пустое, либо не имеет понятных слов, пожалуйста отправьте новое")
        return
    add_message(user_id, [text, 'user', 0, 0, audio_blocks])
    # Если статус True - отправляем текст сообщения и сохраняем в БД, иначе - сообщение об ошибке
    if status:
        # Записываем сообщение и кол-во аудиоблоков в БД
        bot.send_message(user_id, text, reply_to_message_id=message.id)
    else:
        bot.send_message(user_id, text)



@bot.message_handler(commands=['tts'])
def tts_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Отправь следующим сообщеним текст, чтобы я его озвучил!')
    bot.register_next_step_handler(message, tts)

def tts(message):
    user_id = message.from_user.id
    text = message.text

    # Проверка, что сообщение действительно текстовое
    if message.content_type != 'text':
        bot.send_message(user_id, 'Отправь текстовое сообщение')
        return

        # Считаем символы в тексте и проверяем сумму потраченных символов
    text_symbol, symbol_content = is_tts_symbol_limit(user_id, text)
    if text_symbol is None:
        bot.send_message(user_id, symbol_content)
        return

    # Записываем сообщение и кол-во символов в БД
    add_message(user_id, [text, 'user', 0, text_symbol, 0])
    # Получаем статус и содержимое ответа от SpeechKit
    status, content = text_to_speech(text)

    # Если статус True - отправляем голосовое сообщение, иначе - сообщение об ошибке
    if status:
        bot.send_voice(user_id, content)
    else:
        bot.send_message(user_id, content)



@bot.message_handler(content_types=['voice'])
def handle_voice(message: telebot.types.Message):
        try:
            user_id = message.from_user.id

            # Проверка на максимальное количество пользователей
            status_check_users, error_message = check_number_of_users(user_id)
            if not status_check_users:
                bot.send_message(user_id, error_message)
                return

        # Проверка на доступность аудиоблоков
            stt_blocks, error_message = is_stt_block_limit(user_id, message.voice.duration)
            if error_message:
                bot.send_message(user_id, error_message)
                return

        # Обработка голосового сообщения
            file_id = message.voice.file_id
            file_info = bot.get_file(file_id)
            file = bot.download_file(file_info.file_path)
            status_stt, stt_text = speech_to_text(file)
            if not status_stt:
                bot.send_message(user_id, stt_text)
                return
            if not stt_text:
                bot.send_message(user_id, "Голосовое сообщение пустое, либо не имеет понятных слов, пожалуйста отправьте новое")
                return
            if stt_text == "":
                bot.send_message(user_id, "Голосовое сообщение пустое, либо не имеет понятных слов, пожалуйста отправьте новое")
                return

        # Запись в БД
            add_message(user_id=user_id, full_message=[stt_text, 'user', 0, 0, stt_blocks])
        # Проверка на доступность GPT-токенов
            last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
            total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
            if error_message:
                bot.send_message(user_id, error_message)
                return

        # Запрос к GPT и обработка ответа
            status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
            if not status_gpt:
                bot.send_message(user_id, answer_gpt)
                return
            total_gpt_tokens += tokens_in_answer

        # Проверка на лимит символов для SpeechKit
            tts_symbols, error_message = is_tts_symbol_limit(user_id, answer_gpt)

        # Запись ответа GPT в БД
            add_message(user_id=user_id, full_message=[answer_gpt, 'assistant', total_gpt_tokens, tts_symbols, 0])

            if error_message:
                bot.send_message(user_id, error_message)
                return

        # Преобразование ответа в аудио и отправка
            status_tts, voice_response = text_to_speech(answer_gpt)
            if status_tts:
                bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)
            else:
                bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)

        except Exception as e:
            logging.error(e)
            bot.send_message(user_id, "Не получилось ответить. Попробуй записать другое сообщение")





@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        user_id = message.from_user.id

        # ВАЛИДАЦИЯ: проверяем, есть ли место для ещё одного пользователя (если пользователь новый)
        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)  # мест нет =(
            return

        # БД: добавляем сообщение пользователя и его роль в базу данных
        full_user_message = [message.text, 'user', 0, 0, 0]
        add_message(user_id=user_id, full_message=full_user_message)

        # ВАЛИДАЦИЯ: считаем количество доступных пользователю GPT-токенов
        # получаем последние 4 (COUNT_LAST_MSG) сообщения и количество уже потраченных токенов
        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        # получаем сумму уже потраченных токенов + токенов в новом сообщении и оставшиеся лимиты пользователя
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            # если что-то пошло не так — уведомляем пользователя и прекращаем выполнение функции
            bot.send_message(user_id, error_message)
            return

        # GPT: отправляем запрос к GPT
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        # GPT: обрабатываем ответ от GPT
        if not status_gpt:
            # если что-то пошло не так — уведомляем пользователя и прекращаем выполнение функции
            bot.send_message(user_id, answer_gpt)
            return
        # сумма всех потраченных токенов + токены в ответе GPT
        total_gpt_tokens += tokens_in_answer

        # БД: добавляем ответ GPT и потраченные токены в базу данных
        full_gpt_message = [answer_gpt, 'assistant', total_gpt_tokens, 0, 0]
        add_message(user_id=user_id, full_message=full_gpt_message)

        bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)  # отвечаем пользователю текстом
    except Exception as e:
        logging.error(e)  # если ошибка — записываем её в логи
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй написать другое сообщение")




# обрабатываем все остальные типы сообщений
@bot.message_handler(func=lambda: True)
def handler(message):
    bot.send_message(message.from_user.id, "Отправь мне голосовое или текстовое сообщение, и я тебе отвечу")



bot.infinity_polling() # запускаем бота