import torch
import sounddevice as sd
import time

# Глобальные флаги состояния
silent_mode = False
is_speaking = False  # Этим флагом мы будем глушить микрофон!

# Конфигурация моделей
MODELS_CONFIG = {
    'ru': {'model_id': 'v3_1_ru', 'speaker': 'baya', 'sample_rate': 48000},
    'en': {'model_id': 'v3_en', 'speaker': 'en_18', 'sample_rate': 48000}
}

# Сюда будут загружаться модели по мере необходимости (Lazy Loading)
loaded_models = {}


def _get_model(lang):
    """При первом вызове загружает модель в память и кэширует её."""
    if lang not in loaded_models:
        print(f"📦 Загрузка модели синтеза речи Silero [{lang.upper()}]...")
        model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                  model='silero_tts',
                                  language=lang,
                                  speaker=MODELS_CONFIG[lang]['model_id'])
        model.to(torch.device('cpu'))
        loaded_models[lang] = model
    return loaded_models[lang]


def for_silent_mode():
    global silent_mode
    speak('тихий режим', lang='ru')
    silent_mode = not silent_mode
    speak('да', lang='ru')


def speak(text, lang='ru'):
    global is_speaking
    if silent_mode or not text:
        return

    # Защита: поднимаем флаг, микрофон в этот момент ослепнет
    is_speaking = True

    try:
        if lang == 'ru':
            # Специфичный хак для числительного "семь"
            text = ' '.join(['ссемь' if word == 'семь' else word for word in text.split()])

        cfg = MODELS_CONFIG[lang]
        model = _get_model(lang)

        print(f"[TTS | {lang.upper()}]: {text}")
        audio = model.apply_tts(text=text + '!',
                                speaker=cfg['speaker'],
                                sample_rate=cfg['sample_rate'],
                                put_accent=True,
                                put_yo=True)

        sd.play(audio, cfg['sample_rate'])
        time.sleep(len(audio) / cfg['sample_rate'])
        sd.stop()
    except Exception as e:
        print(f"Ошибка синтеза речи [{lang}]: {e}")
    finally:
        # Обязательно опускаем флаг, даже если синтез упал с ошибкой
        is_speaking = False