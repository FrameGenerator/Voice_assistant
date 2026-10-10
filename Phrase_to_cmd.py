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
import pyperclip

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


def send_win32_hotkey(modifiers, key_code):
    """
    Вспомогательная функция: позволяет корректно отрабатывать
    функциям, использующим клавиатуру(исключает залипание)
    """
    for mod in [win32con.VK_CONTROL, win32con.VK_SHIFT, win32con.VK_MENU]:
        win32api.keybd_event(mod, 0, win32con.KEYEVENTF_KEYUP, 0)

    time.sleep(0.01)
    for mod in modifiers:
        win32api.keybd_event(mod, 0, 0, 0)

    win32api.keybd_event(key_code, 0, 0, 0)
    win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)

    for mod in reversed(modifiers):
        win32api.keybd_event(mod, 0, win32con.KEYEVENTF_KEYUP, 0)


def manage_program(text_for, silent=False):
    """
    Универсальный менеджер программ.
    Сам понимает из фразы, какую программу и что с ней сделать: открыть, свернуть или закрыть.
    """
    text_for = text_for.lower().strip()
    prog_name = Phrase.name_programs(text_for)
    action = Phrase.for_open_close_program(text_for)
    hwnd = get_main_hwnd(prog_name)

    def say(phrase):
        if not silent:
            Vosproizvedenie_RU.speak(phrase)


    if action == 'close':
        # 1. Посылаем сигнал закрытия окна
        if hwnd:
            # Вместо WM_CLOSE шлем системную команду закрытия меню (так надежнее)
            win32gui.PostMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_CLOSE, 0)
            time.sleep(0.2)  # Даем 200 мс на сохранение настроек плеера

        # 2. Жестко зачищаем ВСЕ оставшиеся процессы-зомби этого приложения
        procs_killed = False
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and proc.info['name'].lower() == f"{prog_name}.exe":
                try:
                    proc.kill()
                    procs_killed = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

        if procs_killed or hwnd:
            say(f"закрываю {prog_name}")
        else:
            say(f"{prog_name} и так не была открыта")
        return

    if action == 'minimize':
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            say("свернула")
        else:
            say("программа и так не запущена")
        return

    if not hwnd:
        path = Phrase.program_path(prog_name)
        if path and os.path.exists(path):
            say(f"открываю {prog_name}")
            subprocess.Popen(path)
        else:
            say(f"Я не знаю где лежит {prog_name}.")
        return

    if win32gui.GetForegroundWindow() == hwnd:
        return

    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    else:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
        try:
            win32gui.SetForegroundWindow(hwnd)
        except Exception as e:
            print(f"Критическая ошибка фокуса: {e}")
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)

    say("разворачиваю")


def times():
    now = datetime.now()
    print(str(now.time())[:5])
    hours = num2words(now.hour, lang='ru')
    minutes = num2words(now.minute, lang='ru')
    Vosproizvedenie_RU.speak(f'Сейчас {hours} {minutes}')


def write(text_for):
    """Печатает текст в активное окно пользователя через буфер обмена (поддерживает русский язык)."""
    write_keywords = Phrase.DATA_PHRASE.get('write', set())
    pattern = r'^.*?\b(' + '|'.join(map(re.escape, write_keywords)) + r')\b\s*'
    clean_text = re.sub(pattern, '', text_for, count=1, flags=re.IGNORECASE).strip()

    if not clean_text:
        Vosproizvedenie_RU.speak('А что именно написать?')
        return

    pyperclip.copy(clean_text)
    send_win32_hotkey([win32con.VK_CONTROL], ord('V'))
    Vosproizvedenie_RU.speak('написала')


def tab(text_for):
    """Управление вкладками активного браузера Chrome с умным ожиданием."""
    manage_program("хром", silent=True)
    chrome_focused = False
    start_wait = time.time()

    while time.time() - start_wait < 1.5:
        try:
            active_hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(active_hwnd)
            proc_name = psutil.Process(pid).name().lower()

            if "chrome" in proc_name:
                chrome_focused = True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        time.sleep(0.02)

    if not chrome_focused:
        Vosproizvedenie_RU.speak('Браузер не активен')
        return

    time.sleep(0.05)
    action = Phrase.for_tab(text_for)

    if action == 'close':
        send_win32_hotkey([win32con.VK_CONTROL], ord('W'))
        Vosproizvedenie_RU.speak('закрыла')
    elif action == 'reestablish':
        send_win32_hotkey([win32con.VK_CONTROL, win32con.VK_SHIFT], ord('T'))
        Vosproizvedenie_RU.speak('вернула')
    else:
        number = Phrase.numbers(text_for)
        if number:
            send_win32_hotkey([win32con.VK_CONTROL], ord(str(number)))
            Vosproizvedenie_RU.speak(f'открыла {number}-ю')


def open_google():
    webbrowser.open('https://google.com', new=0)
    Vosproizvedenie_RU.speak('открыла')


def send_media_key(vk_code):
    """Специальная функция для эмуляции физических медиа-кнопок клавиатуры."""
    # Флаг расширенной клавиши (0x0001) сообщает Windows, что это медиа-кнопка
    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP = 0x0002

    # Сначала сбрасываем залипшие модификаторы
    for mod in [win32con.VK_CONTROL, win32con.VK_SHIFT, win32con.VK_MENU]:
        win32api.keybd_event(mod, 0, KEYEVENTF_KEYUP, 0)

    # Имитируем физическое нажатие мультимедийной кнопки
    win32api.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
    time.sleep(0.01)
    win32api.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)


def music(text_for):
    """Управление музыкой через Winamp"""
    action = Phrase.cmd_phrase_music(text_for)

    if not action:
        Vosproizvedenie_RU.speak('не поняла')
        return

    if action == 'on':
        winamp_running = any(
            p.info['name'] and p.info['name'].lower() == 'winamp.exe'
            for p in psutil.process_iter(['name'])
        )

        if not winamp_running:
            manage_program("винамп", silent=True)
            start_wait = time.time()
            hwnd = None
            while time.time() - start_wait < 4.0:
                target_hwnd = get_main_hwnd("winamp")
                if target_hwnd:
                    title = win32gui.GetWindowText(target_hwnd).lower()
                    if "winamp" in title or "build" in title:
                        hwnd = target_hwnd
                        break
                time.sleep(0.1)

            if hwnd:
                time.sleep(0.4)
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            else:
                time.sleep(1.0)

        send_win32_hotkey([win32con.VK_CONTROL, win32con.VK_MENU], win32con.VK_INSERT)
        return

    if action == 'off':
        send_win32_hotkey([win32con.VK_CONTROL, win32con.VK_MENU], win32con.VK_HOME)
        return

    if action == 'another':
        send_win32_hotkey([win32con.VK_CONTROL, win32con.VK_MENU], win32con.VK_NEXT)
        return

    if action == 'back':
        send_win32_hotkey([win32con.VK_CONTROL, win32con.VK_MENU], win32con.VK_PRIOR)
        return


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
