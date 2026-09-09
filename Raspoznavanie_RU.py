import sys
import queue
import json
import vosk
import sounddevice as sd


model = vosk.Model('model_small')
samplerate = 16000
audio_queue = queue.Queue()


def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(bytes(indata))


def start_speech_recognition(text_queue):
    with sd.RawInputStream(samplerate=samplerate, blocksize=0, dtype='int16',
                           channels=1, callback=callback):
        rec = vosk.KaldiRecognizer(model, samplerate)
        print("🎙️ Поток распознавания речи запущен и слушает...")

        while True:
            data = audio_queue.get()
            if rec.AcceptWaveform(data):
                raw_text = rec.Result()

                try:
                    res_dict = json.loads(raw_text)
                    text = res_dict.get('text', '').strip()

                    if text:
                        print(f"[Vosk] Распознано: {text}")
                        text_queue.put(text)
                except Exception as e:
                    print(f"Ошибка парсинга JSON: {e}")
