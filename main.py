import threading
import queue
import Raspoznavanie_RU
import Vosproizvedenie_EN
import Vosproizvedenie_RU
import Phrase
import Phrase_to_cmd


text_queue = queue.Queue()
last_cmd = ''
command_dict = {
    'time': lambda: Phrase_to_cmd.times(),
    'all': lambda: Phrase_to_cmd.open_close_all(text_start),
    'tab': lambda: Phrase_to_cmd.tab(text_start),
    'write': lambda: Phrase_to_cmd.write(text_start),
    'google': lambda: Phrase_to_cmd.open_google(),
    'music': lambda: Phrase_to_cmd.music(text_start),
    'wait_or_end': lambda: Phrase_to_cmd.wait_or_end(text_start),
    'minimize': lambda: Phrase_to_cmd.window_minimized(text_start),
    'program': lambda: Phrase_to_cmd.open_close_program(text_start),
    'folder': lambda: Phrase_to_cmd.open_folder(text_start, 'folder'),
    'disk': lambda: Phrase_to_cmd.open_folder(text_start, 'disk'),
    'press': lambda: Phrase_to_cmd.button(text_start),
    'translate': lambda: Phrase_to_cmd.translate(text_start),
    'sound_level': lambda: Phrase_to_cmd.sound_volume(text_start),
    'silent_mode': lambda: Vosproizvedenie_RU.for_silent_mode(),
    'coin': lambda: Phrase_to_cmd.coin(text_start),
    'calculator': lambda: Phrase_to_cmd.calculator(text_start)
}


def process_command(text_start):
    global last_cmd
    cmd = Phrase.cmd_phrase(text_start)
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
            action()


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
            process_command(text_start)
        except KeyboardInterrupt:
            print("\nПрограмма остановлена.")
            break
        except Exception as e:
            print(f"Ошибка в главном цикле: {e}")
