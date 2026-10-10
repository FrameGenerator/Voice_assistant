import threading
import queue
import Raspoznavanie_RU
import Vosproizvedenie_EN
import Vosproizvedenie_RU
import Phrase
import Phrase_to_cmd

text_queue = queue.Queue()
last_cmd = ''

is_sleeping = False

command_dict = {
    'time': lambda: Phrase_to_cmd.times(),
    'tab': lambda: Phrase_to_cmd.tab(text_start),
    'write': lambda: Phrase_to_cmd.write(text_start),
    'google': lambda: Phrase_to_cmd.open_google(),
    'music': lambda: Phrase_to_cmd.music(text_start),
    'wait_or_end': lambda: process_sleep_or_exit(text_start),
    'manage_program': lambda: Phrase_to_cmd.manage_program(text_start),
    'press': lambda: Phrase_to_cmd.button(text_start),
    'translate': lambda: Phrase_to_cmd.translate(text_start),
    'sound_level': lambda: Phrase_to_cmd.sound_volume(text_start),
    'silent_mode': lambda: Vosproizvedenie_RU.for_silent_mode(),
    'coin': lambda: Phrase_to_cmd.coin(text_start),
    'calculator': lambda: Phrase_to_cmd.calculator(text_start)
}


def process_sleep_or_exit(text):
    global is_sleeping

    if 'полностью' in text.lower():
        Vosproizvedenie_RU.speak('пока пока')
        return 'EXIT_SIGNAL'

    is_sleeping = True
    Vosproizvedenie_RU.speak('ухожу в режим ожидания')
    print("💤 Ассистент уснул. Ждет фразу активации...")
    return 'SLEEP_SIGNAL'


def process_command(text_start):
    global last_cmd, is_sleeping

    if is_sleeping:
        if Phrase.for_wait_or_end(text_start) == 'wait':
            is_sleeping = False
            Vosproizvedenie_RU.speak('да, я тут')
            print("🔊 Ассистент проснулся и готов к работе!")
        return

    cmd = Phrase.cmd_phrase(text_start)
    print(cmd, 'cmd')

    if cmd is None and last_cmd in ['music', 'sound_level', 'tab']:
        cmd = last_cmd

    last_cmd = cmd
    if cmd is None:
        if text_start.isascii():
            Vosproizvedenie_EN.speak(text_start)
        else:
            Vosproizvedenie_RU.speak(text_start)
    else:
        action = command_dict.get(cmd)
        if action:
            result = action()
            if result == 'EXIT_SIGNAL':
                return 'SHUTDOWN'
    return 'CONTINUE'


if __name__ == '__main__':
    Vosproizvedenie_RU.speak('Привет, готова к работе')

    vosk_thread = threading.Thread(
        target=Raspoznavanie_RU.start_speech_recognition,
        args=(text_queue,),
        daemon=True
    )
    vosk_thread.start()

    print("🤖 Главный поток готов к обработке команд...")
    while True:
        try:
            text_start = text_queue.get()
            status = process_command(text_start)

            if status == 'SHUTDOWN':
                break

        except KeyboardInterrupt:
            print("\nПрограмма остановлена пользователем.")
            break
        except Exception as e:
            print(f"Ошибка в главном цикле: {e}")

    print("👋 До свидания! Все потоки успешно завершены.")