import Raspoznavanie_RU
import Vosproizvedenie_RU
import Phrase
import Phrase_to_cmd


Vosproizvedenie_RU.speak('Привет, готова к работе')
last_cmd = ''
text_start = ''
command_dict = {
    'time': lambda: Phrase_to_cmd.times(),
    'all': lambda: Phrase_to_cmd.open_close_all(text_start),
    'tab': lambda: Phrase_to_cmd.tab(text_start),
    'write': lambda: Phrase_to_cmd.my_keyboard(text_start),
    'google': lambda: Phrase_to_cmd.open_google(),
    'music': lambda: Phrase_to_cmd.music(text_start),
    'wait_or_end': lambda: Phrase_to_cmd.wait_or_end(text_start),
    'minimize': lambda: Phrase_to_cmd.window_minimized(text_start),
    'program': lambda: Phrase_to_cmd.open_close_program(text_start),  # winamp, BattleNet, Steam, osu, chrome
    'folder': lambda: Phrase_to_cmd.open_folder(text_start),  # Only Desktop
    'for_last_cmd': lambda: Vosproizvedenie_RU.speak(text_start),  # music
    'press': lambda: Phrase_to_cmd.button(text_start),  # Enter
    'translate': lambda: Phrase_to_cmd.translate(text_start)
}


def data():
    global last_cmd, text_start
    text_start = Raspoznavanie_RU.record()
    cmd = Phrase.cmd_phrase(text_start)
    print(cmd)
    print(text_start)
    print(text_start)
    if cmd == 'for_last_cmd':
        cmd = Phrase.cmd_phrase(' '.join(reversed(text_start.split())))
        if last_cmd == 'music':
            cmd = 'music'
    last_cmd = cmd
    if cmd is None:
        if not str(text_start[0].encode())[2].isalpha():
            Vosproizvedenie_RU.speak(text_start)
    else:
        command_dict.get(cmd)()


while True:
    data()
