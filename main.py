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
    'time': lambda txt: Phrase_to_cmd.times(),
    'tab': lambda txt: Phrase_to_cmd.tab(txt),
    'write': lambda txt: Phrase_to_cmd.write(txt),
    'google': lambda txt: Phrase_to_cmd.open_google(),
    'music': lambda txt: Phrase_to_cmd.music(txt),
    'manage_program': lambda txt: Phrase_to_cmd.manage_program(txt),
    'press': lambda txt: Phrase_to_cmd.button(txt),
    'translate': lambda txt: Phrase_to_cmd.translate(txt, text_queue),
    'sound_level': lambda txt: Phrase_to_cmd.sound_volume(txt),
    'silent_mode': lambda txt: Phrase_to_cmd.manage_silent_mode(txt),
    'coin': lambda txt: Phrase_to_cmd.coin(txt),
    'calculator': lambda txt: Phrase_to_cmd.calculator(txt)
}


def process_command(text_start):
    global last_cmd, is_sleeping

    clean_text = text_start.lower().strip()
    close_code_full = 'полностью' in clean_text
    close_code_wait = Phrase.for_wait_or_end(clean_text) == 'wait'

    if (is_sleeping or close_code_wait) and close_code_full:
        Vosproizvedenie_RU.speak('пока пока')
        return 'SHUTDOWN'

    if is_sleeping:
        if close_code_wait:
            is_sleeping = False
            Vosproizvedenie_RU.speak('да, я тут')
            print("🔊 Ассистент проснулся и готов к работе!")
        return 'CONTINUE'

    cmd = Phrase.cmd_phrase(clean_text)

    if cmd is None and last_cmd in ['music', 'sound_level', 'tab']:
        cmd = last_cmd

    last_cmd = cmd
    if cmd is None:
        if text_start.isascii():
            Vosproizvedenie_EN.speak(text_start)
        else:
            Vosproizvedenie_RU.speak(text_start)
        return 'CONTINUE'

    if cmd == 'wait_or_end':
        is_sleeping = True
        Vosproizvedenie_RU.speak('ухожу в режим ожидания')
        print("💤 Ассистент уснул. Ожидает фразу активации...")
        return 'CONTINUE'

    action = command_dict.get(cmd)
    if action:
        action(text_start)

    return 'CONTINUE'


if __name__ == '__main__':

    vosk_thread = threading.Thread(
        target=Raspoznavanie_RU.start_speech_recognition,
        args=(text_queue,),
        daemon=True
    )
    vosk_thread.start()

    Vosproizvedenie_RU.speak('Привет, готова к работе')

    print("🤖 Главный поток готов к обработке команд...")
    while True:
        try:
            text_start = text_queue.get()
            if process_command(text_start) == 'SHUTDOWN':
                break
        except KeyboardInterrupt:
            print("\nПрограмма остановлена пользователем.")
            break
        except Exception as e:
            print(f"Ошибка в главном цикле: {e}")

    print("👋 До свидания! Все ресурсы успешно освобождены.")