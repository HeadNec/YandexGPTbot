from config import FOLDER_ID, IAM_TOKEN
import requests
#from creds import get_creds  # модуль для получения токенов
#iam_token, folder_id = get_creds()  # получаем iam_token и folder_id из файлов
def speech_to_text(data):
    # указываем параметры запроса
    params = "&".join([
        "topic=general",
        f"folderId={FOLDER_ID}",
        "lang=ru-RU"
    ])
    url = f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}"
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
    }
    response = requests.post(url=url, headers=headers, data=data)
    decoded_data = response.json()
    if decoded_data.get("error_code") is None:
        return True, decoded_data.get("result")
    else:
        return False, "При запросе в SpeechKit возникла ошибка"

def text_to_speech(text: str):

    # Аутентификация через IAM-токен
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
    }
    data = {
        'text': text,  # текст, который нужно преобразовать в голосовое сообщение
        'lang': 'ru-RU',  # язык текста - русский
        'voice': 'filipp',  # голос Филлипа
        'folderId': FOLDER_ID,
    }
    # Выполняем запрос
    response = requests.post('https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize', headers=headers, data=data)

    if response.status_code == 200:
        return True, response.content  # Возвращаем голосовое сообщение
    else:
        return False, "При запросе в SpeechKit возникла ошибка"


if __name__ == "__main__":
    # Текст, который хочешь преобразовать в голос
    text = "Привет! Я учусь работать с API SpeechKit. Это очень интересно!"

    # Вызываем функцию и получаем результат
    success, response = text_to_speech(text)

    if success:
        # Если все хорошо, сохраняем аудио в файл
        with open("output.ogg", "wb") as audio_file:
            audio_file.write(response)
        print("Аудиофайл успешно сохранен как output.ogg")
    else:
        # Если возникла ошибка, выводим сообщение об ошибке
        print("Ошибка:", response)