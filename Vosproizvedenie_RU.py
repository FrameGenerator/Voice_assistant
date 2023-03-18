import torch
import sounddevice as sd
import time

language = 'ru'
model_id = 'ru_v3'
sample_rate = 48000
speaker = 'baya'  # aidar, baya, kseniya, xenia, random
silent_mode = False

model, i = torch.hub.load(repo_or_dir='snakers4/silero-models',
                          model='silero_tts',
                          language=language,
                          speaker=model_id)

model.to(torch.device('cpu'))


def for_silent_mode():
    global silent_mode
    speak('тихий режим')
    silent_mode = not silent_mode
    speak('да')


def speak(text):
    if silent_mode:
        return
    text = ' '.join(['ссемь' if i == 'семь' else i for i in text.split()])
    audio = model.apply_tts(text=text + '!',
                            speaker=speaker,
                            sample_rate=sample_rate,
                            put_accent=True,
                            put_yo=True)

    sd.play(audio, sample_rate)
    time.sleep(len(audio) / sample_rate)
    sd.stop()

