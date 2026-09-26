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
from num2words import num2words
from datetime import datetime
from googletrans import Translator
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import comtypes
import random
import operator
import re
import subprocess

translator = Translator()


def get_main_hwnd(file_name):
    """Вспомогательная функция: находит главное видимое окно программы по имени её exe-файла"""
    target_file = f"{file_name.lower()}.exe"
    target_pids = {p.info['pid'] for p in psutil.process_iter(['pid', 'name'])
                   if p.info['name'] and p.info['name'].lower() == target_file}

    if not target_pids:
        return None

    found_hwnds = []

    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            _, win_pid = win32process.GetWindowThreadProcessId(hwnd)
            if win_pid in target_pids:
                title = win32gui.GetWindowText(hwnd)
                # Игнорируем служебные фоновые окна и плееры
                if title and "Редактор" not in title and title != "Program Manager":
                    found_hwnds.append(hwnd)

    win32gui.EnumWindows(callback, None)
    return found_hwnds[0] if found_hwnds else None


def manage_program(text_for):
    """
    Универсальный менеджер программ.
    Сам понимает из фразы, какую программу и что с ней сделать: открыть, свернуть или закрыть.
    """
    text_for = text_for.lower().strip()
    prog_name = Phrase.name_programs(text_for)

    action = Phrase.for_open_close_program(text_for)
    hwnd = get_main_hwnd(prog_name)
    print(prog_name, action, hwnd)

    if action == 'close':
        if hwnd:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            Vosproizvedenie_RU.speak(f"закрываю {prog_name}")
        else:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and proc.info['name'].lower() == f"{prog_name}.exe":
                    proc.kill()
            Vosproizvedenie_RU.speak(f"{prog_name} не была открыта, но процессы очищены")
        return

    if action == 'minimize':
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            Vosproizvedenie_RU.speak("свернула")
        else:
            Vosproizvedenie_RU.speak("программа и так не запущена")
        return

    if hwnd:
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        win32gui.SetForegroundWindow(hwnd)
        Vosproizvedenie_RU.speak("разворачиваю")
    else:
        path = Phrase.program_path(prog_name)
        if path and os.path.exists(path):
            Vosproizvedenie_RU.speak(f"открываю {prog_name}")
            subprocess.Popen(path)
        else:
            Vosproizvedenie_RU.speak(f"Я не знаю где лежит {prog_name}. Проверьте пути в настройках.")


def times():
    now = datetime.now()
    print(str(now.time())[:5])
    hours = num2words(now.hour, lang='ru')
    minutes = num2words(now.minute, lang='ru')
    Vosproizvedenie_RU.speak(f'Сейчас {hours} {minutes}')


def write(text_for):
    if len(text_for.split()[0]) < 3:
        keyboard.write(' '.join(text_for.split()[2:]))
    else:
        keyboard.write(' '.join(text_for.split()[1:]))
    Vosproizvedenie_RU.speak('написала')


# def tab(text_for):
#     window_forward('chrome')
#     time.sleep(0.1)
#     if 'close' == Phrase.for_tab(text_for):
#         keyboard.send('Ctrl+w')
#         Vosproizvedenie_RU.speak('закрыла')
#     elif 'reestablish' == Phrase.for_tab(text_for):
#         keyboard.send('Ctrl + Shift + T')
#         Vosproizvedenie_RU.speak('вернула')
#     elif Phrase.numbers(text_for):
#         number = Phrase.numbers(text_for)
#         keyboard.send(f'Ctrl + {number}')


def open_google():
    webbrowser.open('https://google.com', new=0)
    Vosproizvedenie_RU.speak('открыла')


def music(text_for):
    if 'on' == Phrase.cmd_phrase_music(text_for):
        if 'winamp.exe' not in [i.name() for i in psutil.process_iter()]:
            tmp = win32gui.GetForegroundWindow()
            tmp2 = 0
            os.startfile(Phrase.program_path('winamp'))
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





def button(button):
    buttton = Phrase.buttons(button)
    if buttton is not None:
        keyboard.send(buttton)
    else:
        Vosproizvedenie_RU.speak('нет такой кнопки')


def translate(text):
    # translator = Translator()
    if 'английский' in text.split():
        Vosproizvedenie_RU.speak('режим перевода с русского на английский')
        while len(text.split()) == len(set(text.split()) - {'нормальный', 'выход'}):
            text = Raspoznavanie_RU.record()
            print(text)
            try:
                temp = translator.translate(text, src='ru', dest='en')
                time.sleep(0.1)
                print(temp.text)
                Vosproizvedenie_EN.speak(temp.text)
            except:
                print('ошибка перевода(APi)')
        Vosproizvedenie_EN.speak('normal mode')

    elif 'русский' in text.split():
        Vosproizvedenie_RU.speak('режим перевода с английского на русский')
        while len(text.split()) == len(set(text.split()) - {'out', 'normal', 'mode'}):
            text = Raspoznavanie_EN.record()
            print(text)
            try:
                temp = translator.translate(text, src='en', dest='ru')
                print(temp.text)
                Vosproizvedenie_RU.speak(temp.text)
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
        Vosproizvedenie_RU.speak('какой режим?')


def sound_volume(text):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_,
        comtypes.CLSCTX_ALL,
        None
    )
    volume = interface.QueryInterface(IAudioEndpointVolume)
    current_volume = volume.GetMasterVolumeLevelScalar()
    sound_level = {'один': 0.1, 'два': 0.2, 'три': 0.3, 'четыре': 0.4, 'пять': 0.5,
                   'шесть': 0.6, 'семь': 0.7, 'восемь': 0.8, 'девять': 0.9, 'десять': 1}

    if 'down' == Phrase.for_sound_volume(text) and current_volume >= 0.1:
        volume.SetMasterVolumeLevelScalar(current_volume - 0.1, None)
    elif 'up' == Phrase.for_sound_volume(text) and current_volume <= 0.9:
        volume.SetMasterVolumeLevelScalar(current_volume + 0.1, None)
    elif 'change' == Phrase.for_sound_volume(text) or text in sound_level:
        def level_sound(txt):
            for i in sound_level:
                if i in txt:
                    return sound_level[i]
            return current_volume

        volume.SetMasterVolumeLevelScalar(level_sound(text), None)
    else:
        Vosproizvedenie_RU.speak('не поняла')


def coin(text):
    rezult = random.randint(1, 2)
    if rezult == 1:
        Vosproizvedenie_RU.speak('решка')
    elif rezult == 2:
        Vosproizvedenie_RU.speak('орел')


last_symb = 'multi'


def parse_ru_numbers(text):
    """Конвертер русских слов в числа от 0 до 999 (целые и дробные)"""
    words_dict = {
        'ноль': 0, 'один': 1, 'два': 2, 'три': 3, 'четыре': 4, 'пять': 5, 'шесть': 6, 'семь': 7, 'восемь': 8,
        'девять': 9,
        'десять': 10, 'одиннадцать': 11, 'двенадцать': 12, 'тринадцать': 13, 'четырнадцать': 14, 'пятнадцать': 15,
        'шестнадцать': 16, 'семнадцать': 17, 'восемнадцать': 18, 'девятнадцать': 19, 'двадцать': 20, 'тридцать': 30,
        'сорок': 40, 'пятьдесят': 50, 'шестьдесят': 60, 'семьдесят': 70, 'восемьдесят': 80, 'девяносто': 90,
        'сто': 100, 'двести': 200, 'триста': 300, 'четыреста': 400, 'пятьсот': 500, 'шестьсот': 600, 'семьсот': 700,
        'восемьсот': 800, 'девятьсот': 900
    }

    if ' и ' in text:
        left, right = text.split(' и ', 1)
        return float(f"{parse_ru_numbers(left)}.{parse_ru_numbers(right)}")

    return sum(words_dict[word] for word in text.split() if word in words_dict)


def calculator(text):
    symb, word = Phrase.for_calculator(text)
    delimiters = {'на', 'плюс', 'минус', 'к'} | word
    operation = {
        'plus': operator.add,
        'minus': operator.sub,
        'multi': operator.mul,
        'divide': operator.truediv
    }

    try:
        eng_rus_fixer = str.maketrans("caoxepmy", "саохерму")
        cleaned_text = text.translate(eng_rus_fixer)

        pattern = r'\b(?:' + '|'.join(delimiters) + r')\b'
        text_parts = re.split(pattern, cleaned_text)

        if len(text_parts) < 2:
            raise ValueError("Не удалось разделить фразу на два числа")

        res1 = parse_ru_numbers(text_parts[0])
        res2 = parse_ru_numbers(text_parts[1])
        print(res1)
        print(res2)

        res = operation[symb](res1, res2)

        if isinstance(res, float):
            res = round(res, 2)

        print(f"📊 Расчет: {res1} {symb} {res2} = {res}")

        speech_text = num2words(res, lang='ru')
        Vosproizvedenie_RU.speak(speech_text)

    except Exception as e:
        print(f"Ошибка в калькуляторе: {e}")
        Vosproizvedenie_RU.speak(text)
