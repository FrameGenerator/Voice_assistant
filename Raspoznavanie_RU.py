import sys
import queue
import json
import os
import vosk
import sounddevice as sd

if os.path.exists('model_small_en') and os.path.exists('model_small'):
    model_ru = vosk.Model('model_small')
    model_en = vosk.Model('model_small_en')
else:
    print('Нет необходимых моделей распознавания')

samplerate = 16000
audio_queue = queue.Queue()
current_language = 'ru'


def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)

    audio_queue.put(bytes(indata))


def start_speech_recognition(text_queue):
    """Фоновый поток, который слушает микрофон и динамически переключает языковые модели."""
    global current_language

    rec_ru = vosk.KaldiRecognizer(model_ru, samplerate)
    rec_en = vosk.KaldiRecognizer(model_en, samplerate)

    with sd.RawInputStream(samplerate=samplerate, blocksize=0, dtype='int16',
                           channels=1, callback=callback):
        print("🎙️ Поток распознавания речи запущен")

        while True:
            data = audio_queue.get()

            if current_language == 'both':
                ru_ready = rec_ru.AcceptWaveform(data)
                en_ready = rec_en.AcceptWaveform(data)

                if ru_ready or en_ready:
                    text_ru = json.loads(rec_ru.Result()).get('text', '').strip()
                    text_en = json.loads(rec_en.Result()).get('text', '').strip()

                    if len(text_ru) >= len(text_en):
                        print(f"[Vosk | AUTO-RU] {text_ru}")
                        text_queue.put(text_ru)
                    elif text_en:
                        print(f"[Vosk | AUTO-EN] {text_en}")
                        text_queue.put(text_en)
                    continue

            if rec_ru.AcceptWaveform(data):
                text = json.loads(rec_ru.Result()).get('text', '').strip()
                if text:
                    print(f"[Vosk | RU] Распознано: {text}")
                    text_queue.put(text)