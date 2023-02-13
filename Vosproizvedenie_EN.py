import torch
import sounddevice as sd
import time

language = 'en'
model_id = 'v3_en'
sample_rate = 48000
speaker = 'en_18'  # en_18, en_24, en_94, en_30(M)

model, i = torch.hub.load(repo_or_dir='snakers4/silero-models',
                          model='silero_tts',
                          language=language,
                          speaker=model_id)

model.to(torch.device('cpu'))


def speak(text):
    audio = model.apply_tts(text=text + '!',
                            speaker=speaker,
                            sample_rate=sample_rate,
                            put_accent=True,
                            put_yo=True)

    sd.play(audio, sample_rate)
    time.sleep(len(audio) / sample_rate)
    sd.stop()


