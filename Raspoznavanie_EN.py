import vosk
import sys
import sounddevice as sd
import queue


model = vosk.Model('model_small_EN')
samplerate = 16000

q = queue.Queue()


def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def record():
    with sd.RawInputStream(samplerate=samplerate, blocksize=0, device=1, dtype='int16',
                           channels=1, callback=callback):
        rec = vosk.KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                raw_text = rec.Result()
                if len(raw_text[14:-3]) > 0:
                    if raw_text[14:-3] not in ['by', 'but', 'be', 'huh']:
                        return raw_text[14:-3]


