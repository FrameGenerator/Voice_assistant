import sys
import queue
import json
import os
import vosk
import sounddevice as sd

# Инициализируем ОБЕ модели при старте приложения (они загружаются в память один раз)
# Если английской модели нет, скрипт выведет понятную ошибку, но не упадет сразу
print("📦 Загрузка языковых моделей Vosk...")
model_ru = vosk.Model('model_small')

model_en = None
if os.path.exists('model_small_en'):
    model_en = vosk.Model('model_small_en')
else:
    print("⚠️ Внимание: Папка 'model_small_en' не найдена. Английский режим будет недоступен.")

samplerate = 16000
audio_queue = queue.Queue()

# Переменная, которая управляет тем, какой язык сейчас слушает ассистент ('ru' или 'en')
current_language = 'ru'


def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(bytes(indata))


def start_speech_recognition(text_queue):
    """Фоновый поток, который слушает микрофон и динамически переключает языковые модели."""
    global current_language

    # Создаем распознаватели для обоих языков
    rec_ru = vosk.KaldiRecognizer(model_ru, samplerate)
    rec_en = vosk.KaldiRecognizer(model_en, samplerate) if model_en else None

    # Открываем ОДИН общий аудиопоток с микрофона
    with sd.RawInputStream(samplerate=samplerate, blocksize=0, dtype='int16',
                           channels=1, callback=callback):
        print("🎙️ Поток распознавания речи запущен и слушает окружающую среду...")

        while True:
            data = audio_queue.get()

            # Динамически выбираем, какой распознаватель использовать прямо сейчас
            if current_language == 'en' and rec_en:
                active_rec = rec_en
            else:
                active_rec = rec_ru

            if active_rec.AcceptWaveform(data):
                raw_text = active_rec.Result()
                try:
                    res_dict = json.loads(raw_text)
                    text = res_dict.get('text', '').strip()

                    if text:
                        print(f"[Vosk | Language: {current_language.upper()}] Распознано: {text}")
                        text_queue.put(text)
                except Exception as e:
                    print(f"Ошибка парсинга JSON в потоке Vosk: {e}")