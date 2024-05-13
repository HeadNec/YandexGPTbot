TOKEN = "6453845523:AAFhvRmJwoXwJpOgCZ3V8DDEPUwpkvDTCa4"  # token телеграм-бота
FOLDER_ID = 'b1g58fejld1m9q0bt6l6'
IAM_TOKEN = 't1.9euelZrPjJWanMzPk8iek8-NlI6Rze3rnpWamMybkI-SjZnHi42cmZPMjZfl9PdQYXdN-e9nfTP03fT3EBB1TfnvZ30z9M3n9euelZqMnpDKys-Ti8yZz4mdnM6RlO_8xeuelZqMnpDKys-Ti8yZz4mdnM6RlL3rnpWay53OnZOamo7Py86PzJGTzsq13oac0ZyQko-Ki5rRi5nSnJCSj4qLmtKSmouem56LntKMng.0yXe1s49wMLFZW4hQ5XpgYFmNrAN7uN4ouPx_BZoWytknV0CJJEDJO29T_xRTSoWeM8uPFHN8wCni5qhhPifAA'
MAX_USERS = 3  # максимальное кол-во пользователей)
MAX_GPT_TOKENS = 120  # максимальное кол-во токенов в ответе GPT
COUNT_LAST_MSG = 4  # кол-во последних сообщений из диалога

# лимиты для пользователя
MAX_USER_STT_BLOCKS = 1_000  # 10 аудиоблоков
MAX_USER_TTS_SYMBOLS = 2_000_000 # 5 000 символов
MAX_USER_GPT_TOKENS = 2_000_000  # 2 000 токенов

LOGS = 'logs.txt'  # файл для логов
DB_FILE = 'messages.db'  # файл для базы данных
SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты веселый собеседник. Общайся с пользователем на "ты" и используй юмор. '
                                            'Поддерживай диалог. Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Изображай человека'}]  # список с системным промтом