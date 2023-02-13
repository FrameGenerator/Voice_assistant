import vosk
import sys
import sounddevice as sd
import queue


model = vosk.Model('model_small')
model_EN = vosk.Model('model_small_EN')
samplerate = 16000

q = queue.Queue()
q2 = queue.Queue()


def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))
    q2.put(bytes(indata))


def record():
    with sd.RawInputStream(samplerate=samplerate, blocksize=0, device=1, dtype='int16',
                           channels=1, callback=callback):
        rec = vosk.KaldiRecognizer(model, samplerate)
        rec_EN = vosk.KaldiRecognizer(model_EN, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                text = rec.Result()[14:-3]
                if len(text) > 0:
                    return text
            data = q2.get()
            if rec_EN.AcceptWaveform(data):
                text_EN = rec_EN.Result()[14:-3]
                if len(text_EN) > 0:
                    return text_EN
