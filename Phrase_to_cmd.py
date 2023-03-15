import sys
import Phrase
import Raspoznavanie_RU
import Vosproizvedenie_RU
import Raspoznavanie_EN
import Vosproizvedenie_EN
import Raspoznavanie_both
import keyboard
import win32gui
import psutil
import webbrowser
import win32con
import win32process
import win32api
import os
import time
import pyautogui
from num2t4ru import num2text
from datetime import datetime
from googletrans import Translator
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import comtypes


def get_program_hwnd_path(file_name):
    def wins(hwnd, _):  # вывод [[name(0), hwnd(1), path(2), wind_text(3)], [...], ]
        if win32gui.IsWindowVisible(hwnd):
            x, pid = win32process.GetWindowThreadProcessId(hwnd)
            proc_path = win32process.GetModuleFileNameEx(
                win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION |
                                     win32con.PROCESS_VM_READ, False, pid), 0)
            if proc_path.split('\\')[-1] == file_name + '.exe' or \
                    win32gui.GetWindowText(hwnd).lower() == file_name:
                find_proc.append([proc_path.split('\\')[-1][:-4], hwnd, proc_path,
                                  win32gui.GetWindowText(hwnd)])

    find_proc = []
    win32gui.EnumWindows(wins, None)
    print(find_proc)
    if len(find_proc) > 0:
        if find_proc[0][3] == 'Редактор списка воспроизведения Winamp':
            find_proc.pop(0)
            print('удаление не главных окон винампа из списка')
        return find_proc
    else:
        return [['процесс не запущен', win32gui.GetForegroundWindow(), '']]


def window_forward(file_name):  # вывод окна на передний план
    tmp = get_program_hwnd_path(file_name)
    try:
        win32gui.ShowWindow(tmp[0][1], win32con.SW_NORMAL)  # вывод из трея
        keyboard.press("alt")
        time.sleep(0.5)
        win32gui.SetForegroundWindow(tmp[0][1])  # вывод на передний план
        keyboard.release("alt")
    except:
        keyboard.release("alt")
    print('Forward ' + file_name)


def times():
    print(str(datetime.now().time())[:5])
    Vosproizvedenie_RU.speak('Сейчас' + ' ' + num2text(datetime.now().hour) + ' ' +
                          num2text(datetime.now().minute)
                          )


def my_keyboard(text_for):
    keyboard.write(text_for[7:])
    Vosproizvedenie_RU.speak('написала')


def tab(text_for):
    t = win32gui.GetForegroundWindow()
    window_forward('chrome')
    if 'close' == Phrase.for_tab(text_for):
        keyboard.send('Ctrl+w')
        Vosproizvedenie_RU.speak('закрыла')
    elif 'reestablish' == Phrase.for_tab(text_for):
        keyboard.send('Ctrl + Shift + T')
        Vosproizvedenie_RU.speak('вернула')
    win32gui.SetForegroundWindow(t)


def open_google():
    webbrowser.open('https://google.com', new=0)
    Vosproizvedenie_RU.speak('открыла')


def music(text_for):
    if 'on' == Phrase.cmd_phrase_music(text_for):
        if 'winamp.exe' not in [i.name() for i in psutil.process_iter()]:
            tmp = win32gui.GetForegroundWindow()
            tmp2 = 0
            os.startfile('C:\Program Files (x86)\Winamp\winamp.exe')
            while 'Winamp' not in win32gui.GetWindowText(win32gui.GetForegroundWindow()).split():
                time.sleep(1)
                tmp2 = win32gui.GetForegroundWindow()
            while win32gui.IsWindowVisible(tmp2) == 0:
                time.sleep(1)
            win32gui.ShowWindow(win32gui.GetForegroundWindow(), win32con.SW_MINIMIZE)
            win32gui.ShowWindow(tmp, 1)
        keyboard.send('ctrl+alt+insert')

    elif 'off' == Phrase.cmd_phrase_music(text_for):
        keyboard.send('ctrl+alt+home')

    elif 'another' == Phrase.cmd_phrase_music(text_for):
        keyboard.send('ctrl+alt+pagedown')

    elif 'back' == Phrase.cmd_phrase_music(text_for):
        keyboard.send('ctrl+alt+pageup')

    else:
        Vosproizvedenie_RU.speak('не поняла')


def open_close_all(text_for):
    if 'open_close_all' == Phrase.for_open_close_all(text_for):
        tmp = pyautogui.position()
        pyautogui.click(1918, 1078)
        pyautogui.moveTo(tmp)
        time.sleep(0.5)
    else:
        Vosproizvedenie_RU.speak(text_for)


def wait_or_end(text_for):
    if 'полностью' in text_for:
        Vosproizvedenie_RU.speak('пока пока')
        sys.exit()
    else:
        Vosproizvedenie_RU.speak('ожидаю')
        while Phrase.for_wait_or_end(text_for) != 'wait':
            text_for = Raspoznavanie_RU.record()
            print(text_for)
            if 'полностью' in text_for:
                Vosproizvedenie_RU.speak('пока пока')
                sys.exit()
        Vosproizvedenie_RU.speak('да')


def window_minimized(wind):
    print('Minimized ' + wind)
    win32gui.ShowWindow(get_program_hwnd_path(wind)[0][1], win32con.SW_MINIMIZE)
    Vosproizvedenie_RU.speak('ок')


def open_close_program(prog):
    program = Phrase.name_programs(prog)
    print(program)
    if 'open' == Phrase.for_open_close_program(prog):
        if program + '.exe' in [i.name() for i in psutil.process_iter()]:
            window_forward(program)
            Vosproizvedenie_RU.speak('уже открыт')
        else:
            os.startfile(Phrase.program_path(program))
            Vosproizvedenie_RU.speak('открываю')
            k = 0
            while program + '.exe' not in [i.name() for i in psutil.process_iter()]:
                time.sleep(1)
                k += 1
                if k > 10:
                    Vosproizvedenie_RU.speak('очень долго запускается')
                    break
            if program == 'chrome' and get_program_hwnd_path(program)[0][3] == 'Восстановить страницы?':
                window_forward('chrome')
                button('интер')
    elif 'close' == Phrase.for_open_close_program(prog):
        Vosproizvedenie_RU.speak('закрываю')
        for i in psutil.process_iter():
            if i.name() == program + '.exe':
                i.kill()
    elif 'forward' == Phrase.for_open_close_program(prog):
        window_forward(program)
        Vosproizvedenie_RU.speak('ок')
    elif 'minimize' == Phrase.for_open_close_program(prog):
        window_minimized(program)
    else:
        Vosproizvedenie_RU.speak('не поняла команду')


def open_folder(text_for):
    desktop = os.listdir(path=r'C:\Users\user\Desktop')
    cmd = Phrase.for_open_close_program(text_for)
    if cmd == 'open':
        if 'диск' in text_for.split():
            os.startfile('C:\\')
        else:
            for i in desktop:
                if i[:i.find('.')].lower() in text_for.split():
                    os.startfile(r'C:\Users\user\Desktop' + '\\' + i)
    elif cmd == 'close':
        print(text_for.split()[-1])
        folder = get_program_hwnd_path(text_for.split()[-1])
        print(folder)
        if folder[0][0] != 'процесс не запущен':
            win32gui.PostMessage(folder[0][1], win32con.WM_CLOSE, 0, 0)


def button(button):
    buttton = Phrase.buttons(button)
    if buttton is not None:
        keyboard.send(buttton)
    else:
        Vosproizvedenie_RU.speak('нет такой кнопки')


def translate(text):
    translator = Translator()
    if 'английский' in text.split():
        Vosproizvedenie_RU.speak('режим перевода с русского на английский')
        while text != 'выход':
            text = Raspoznavanie_RU.record()
            print(text)
            try:
                temp = translator.translate(text, dest='en')
                print(temp.text)
                if temp.text[0].encode().isalpha():
                    Vosproizvedenie_EN.speak(temp.text)
                else:
                    Vosproizvedenie_RU.speak(text + ' не переведено')
            except:
                print('ошибка перевода(APi)')
        Vosproizvedenie_EN.speak('normal mode')

    elif 'русский' in text.split():
        Vosproizvedenie_RU.speak('режим перевода с английского на русский')
        while text != 'out':
            text = Raspoznavanie_EN.record()
            print(text)
            try:
                temp = translator.translate(text, dest='ru')
                print(temp.text)
                if not temp.text[0].encode().isalpha():
                    Vosproizvedenie_RU.speak(temp.text)
                else:
                    Vosproizvedenie_EN.speak(text + ' dont translated')
            except:
                print('ошибка перевода(APi)')
        Vosproizvedenie_RU.speak('обычный режим')

    elif 'двойной' in text.split():
        Vosproizvedenie_RU.speak('режим перевода на двойной')
        while Phrase.for_translate(str(text.split(' ')[0])) != 'out':
            text = Raspoznavanie_both.record()
            print(text)
            if str(text[0].encode())[2].isalpha():
                temp = translator.translate(text, dest='ru')
                print(temp.text)
                Vosproizvedenie_RU.speak(temp.text)
            else:
                temp = translator.translate(text, dest='en')
                print(temp.text)
                Vosproizvedenie_EN.speak(temp.text)
        Vosproizvedenie_RU.speak('обычный режим')
    else:
        Vosproizvedenie_RU.speak('какой режим работы?')


def sound_volume(text):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_,
        comtypes.CLSCTX_ALL,
        None
    )
    volume = interface.QueryInterface(IAudioEndpointVolume)
    current_volume = volume.GetMasterVolumeLevelScalar()

    if 'down' == Phrase.for_sound_volume(text) and current_volume >= 0.1:
        volume.SetMasterVolumeLevelScalar(current_volume - 0.1, None)
    elif 'up' == Phrase.for_sound_volume(text) and current_volume <= 0.9:
        volume.SetMasterVolumeLevelScalar(current_volume + 0.1, None)
    elif 'change' == Phrase.for_sound_volume(text):
        sound_level = {'один': 0.1, 'два': 0.2, 'три': 0.3, 'четыре': 0.4, 'пять': 0.5,
                       'шесть': 0.6, 'семь': 0.7, 'восемь': 0.8, 'девять': 0.9, 'десять': 1}
        def level_sound(txt):
            for i in sound_level:
                if i in txt:
                    return sound_level[i]
            return current_volume
        volume.SetMasterVolumeLevelScalar(level_sound(text), None)
    else: Vosproizvedenie_RU.speak('не поняла')


