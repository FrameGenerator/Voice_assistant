import sys
import queue
import json
import os
import vosk
import sounddevice as sd
import time

if os.path.exists('model_small_en') and os.path.exists('model_small'):
    model_ru = vosk.Model('model_small')
    model_en = vosk.Model('model_small_en')
else:
    print('Нет необходимых моделей распознавания')

samplerate = 16000
audio_queue = queue.Queue()
current_language = 'ru'

pending_ru = {"text": "", "conf": 0.0, "timestamp": 0.0}
pending_en = {"text": "", "conf": 0.0, "timestamp": 0.0}


def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)

    audio_queue.put(bytes(indata))


def start_speech_recognition(text_queue):
    """Фоновый поток, который слушает микрофон и динамически переключает языковые модели."""
    global current_language, pending_ru, pending_en

    rec_ru = vosk.KaldiRecognizer(model_ru, samplerate)
    rec_en = vosk.KaldiRecognizer(model_en, samplerate)

    with sd.RawInputStream(samplerate=samplerate, blocksize=0, dtype='int16',
                           channels=1, callback=callback):
        print("🎙️ Поток распознавания речи запущен")

        rec_ru.SetWords(True)
        rec_en.SetWords(True)

        while True:
            data = audio_queue.get()

            if current_language == 'both':
                ru_ready = rec_ru.AcceptWaveform(data)
                en_ready = rec_en.AcceptWaveform(data)

                current_time = time.time()

                # 1. Сохраняем русский результат, если он готов
                if ru_ready:
                    res_ru = json.loads(rec_ru.Result())
                    text_ru = res_ru.get('text', '').strip()
                    words = res_ru.get('result', [])
                    conf_ru = sum([w.get('conf', 0.0) for w in words]) / len(words) if words else 0.0

                    if len(text_ru) > 3 and conf_ru > 0.6:
                        pending_ru = {"text": text_ru, "conf": conf_ru, "timestamp": current_time}

                # 2. Сохраняем английский результат, if готов
                if en_ready:
                    res_en = json.loads(rec_en.Result())
                    text_en = res_en.get('text', '').strip()
                    words = res_en.get('result', [])
                    conf_en = sum([w.get('conf', 0.0) for w in words]) / len(words) if words else 0.0

                    if len(text_en) > 3 and conf_en > 0.6:
                        pending_en = {"text": text_en, "conf": conf_en, "timestamp": current_time}

                # 3. Принятие решения по временному окну (0.3 секунды)
                # Если в одном из буферов есть фраза, проверяем, не пора ли сделать выбор
                if pending_ru["text"] or pending_en["text"]:

                    # Случай А: Обе модели выдали текст в пределах окна 0.3 сек
                    if pending_ru["text"] and pending_en["text"]:
                        if pending_ru["conf"] >= pending_en["conf"]:
                            print(f"[Vosk | AUTO-RU] {pending_ru['text']} (conf: {pending_ru['conf']:.2f})")
                            text_queue.put(pending_ru["text"])
                        else:
                            print(f"[Vosk | AUTO-EN] {pending_en['text']} (conf: {pending_en['conf']:.2f})")
                            text_queue.put(pending_en["text"])
                        # Очищаем оба буфера
                        pending_ru = {"text": "", "conf": 0.0, "timestamp": 0.0}
                        pending_en = {"text": "", "conf": 0.0, "timestamp": 0.0}

                    # Случай Б: Есть только РУ фразa, и окно ожидания ЕН фразa (0.3 сек) вышло
                    elif pending_ru["text"] and (current_time - pending_ru["timestamp"] > 0.3):
                        print(f"[Vosk | AUTO-RU] {pending_ru['text']} (conf: {pending_ru['conf']:.2f})")
                        text_queue.put(pending_ru["text"])
                        pending_ru = {"text": "", "conf": 0.0, "timestamp": 0.0}

                    # Случай В: Есть только ЕН фразa, и окно ожидания РУ фразa вышло
                    elif pending_en["text"] and (current_time - pending_en["timestamp"] > 0.3):
                        print(f"[Vosk | AUTO-EN] {pending_en['text']} (conf: {pending_en['conf']:.2f})")
                        text_queue.put(pending_en["text"])
                        pending_en = {"text": "", "conf": 0.0, "timestamp": 0.0}

                continue

            if rec_ru.AcceptWaveform(data):
                text = json.loads(rec_ru.Result()).get('text', '').strip()
                if text:
                    print(f"[Vosk | RU] Распознано: {text}")
                    text_queue.put(text)