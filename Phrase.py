def get_cmd(text_start, data_words):
    for word in text_start.split():
        for key in data_words:
            for cmd_word in data_words[key]:
                if word == cmd_word:
                    return key


def cmd_phrase(text):
    data_phrase = {
        'time': {'время', 'времени', 'часов', 'час'},
        'wait_or_end': {'выключись', 'выключиться', 'выключи', 'отключись', 'отключи',
                        },
        'write': {'напиши', 'запиши', 'набери', 'опиши', 'пиши',
                  'запишись', 'пишусь', 'запишусь', 'пишет'},
        'tab': {'вкладку', 'кладку', 'вклад', 'вкладка', 'вкладках', 'хватку',
                'схватку', ''},
        'music': {'музыку', 'музыка', 'музычку', 'песню', 'песня', 'песенку',
                  'песни', 'трек', 'песен', 'песенка', 'мужика'},
        'google': {'гугл'},
        'all': {'все', 'всем'},
        'folder': {'папку', 'папка', 'коробку', 'пробку', 'папки', 'папке', 'ди', 'папа',
                   'пап', 'бабки'},
        'disk': {'диск', 'диска', 'иск', 'иска', 'киска'},
        'press': {'нажмите', 'нажми', 'жми', 'зажми'},
        'silent_mode': {'тихий', 'тихо', 'молчи', 'ничего', 'тихого', 'тихие',
                        'але'},
        'translate': {'переводится', 'переведи', 'перевод', 'означает', 'перевести',
                      'сказать', 'перевода'},
        'sound_level': {'звук', 'громкость', 'звуков', 'круг', 'бог', 'громкости',
                        'звука'},
        'coin': {'монетку', 'монеты', 'монет'},
        'calculator': for_calculator('all'),
        'program': name_programs('all')
    }
    if text == 'for_open_close_all':
        return data_phrase['folder']
    return get_cmd(text, data_phrase)


def cmd_phrase_music(text):
    data_mus = {
        'off': {'останови', 'стоп', 'паузу', 'убери', 'пауза', 'установи',
                'остановите'},
        'another': {'переключи', 'следующую', 'не нравится', 'дальше', 'следующая',
                    'другую', 'нет', 'другой', 'следующий', 'следующие', 'вперёд',
                    'следующее', 'знаешь', 'перед', 'далее', 'даришь'},
        'back': {'назад', 'предыдущую', 'играла'},
        'on': {'включи', 'продолжи', 'продолжить', 'запусти'}
    }
    return get_cmd(text, data_mus)


def for_open_close_all(text):
    data_open_close = {
        'minimize': {'сверни', 'вернее', 'ферме', 'севернее', 'сверлили', 'сферы',
                     'сбер', 'сфер'},
        'close': {'крой', 'закрой', 'аковой'},
        'open': {'открой', 'кажи', 'покажи', 'разверни', 'разве'}
    }
    return get_cmd(text, data_open_close)


def for_wait_or_end(text):
    if text in {'ты тут', 'включись', 'продолжим', 'продолжить', 'алло', 'отключись',
                'включи', 'отключи', 'и не', 'и нет', 'дальше', 'слышишь', 'але',
                'включайся', 'химии', 'их', 'и и', 'и', 'имя', 'и ним', 'и ник',
                'и и не', 'имя але', 'подруга'}:
        return 'wait'


def name_programs(text):
    data_programs = {
        'winamp': {'винамп', 'вина', 'динамо', 'нам', 'вином', 'вино'},
        'Battle.net': {'батл'},
        'osu!': {'су', 'косу', 'полосу', 'ложку', 'воску', 'мозгу', 'ласку', 'оскар', 'ласку', 'осы',
                 'вашу', 'голосу', 'кошку', 'брошу', 'осло', 'кошек', 'глаза', 'осени', 'ос', 'коз',
                 'косы', 'прошлом', 'доску', 'полоску'},
        'Steam': {'ним', 'сидим', 'чтим', 'тим', 'систем', 'стин', 'стиль', 'остин', 'стимул', 'стивен',
                  'вести'},
        'chrome': {'браузер', 'браузера', 'браузеров', 'браузером', 'браузере',
                   'градусов', 'браузерах', 'фронт', 'хром', 'брокер'
                   },
        'pycharm64': {'чарм', 'чарам', 'чан', 'чар', 'плечами', 'чарли', 'чат',
                      'чарам', 'плечам', 'пальчиком', 'чаем', 'вечером', 'плеча',
                      'паралича'},
        'vpn': {'вып', 'его', 'нивы', 'вы', 'пэн'}

    }
    if text == 'all':
        return {j for k in [data_programs[i] for i in data_programs] for j in k}
    if text == 'all_programs':
        return list(data_programs.keys())
    return get_cmd(text, data_programs)


def for_open_close_program(text):
    data_cmd_program = {
        'open': {'открой', 'запусти', 'включи', 'откройте'},
        'close': {'закрой', 'закрыл', 'закрыть'},
        'forward': {'покажи', 'закажи', 'покажите', 'зверни', 'разверни'},
        'minimize': {'сверни', 'вернее', 'заверни', 'севернее', 'фирме', 'сергей'}
    }
    return get_cmd(text, data_cmd_program)


def program_path(text):
    data_program_path = {
        'winamp': 'A:\Winamp\Winamp\winamp.exe',
        'Battle.net': 'A:\BattleNet\Battle.net\Battle.net Launcher.exe',
        'osu!': r'G:\Users\user\AppData\Local\osu!\osu!.exe',
        # 'Steam': 'C:\Program Files (x86)\Steam\steam.exe',
        'chrome': 'C:\Program Files\Google\Chrome\Application\chrome.exe',
        'pycharm': 'A:\Pycharm\PyCharm Community Edition 2023.1.2\bin\pycharm64.exe',
        # 'vpn': 'C:\\Program Files (x86)\\Hotspot Shield\\12.1.0\\bin\\hsscp.exe'
    }
    return data_program_path[text]


def buttons(text):
    data_buttons = {
        'Enter': {'интер', 'принтер'}
    }
    return get_cmd(text, data_buttons)


def for_translate(text):
    data_translate = {
        'out': {'выйти', 'выйди', 'стоп', 'понятно', 'ясно',
                'exit', 'out', 'okay', 'выход'}
    }
    return get_cmd(text, data_translate)


def for_tab(text):
    data_tab = {
        'close': {'закрой', 'закроешь'},
        'reestablish': {'останови', 'установи', 'восстановить', 'верни', 'вернее',
                        'верхний'},
        'tab selection': {'открой', 'покажи'}
    }
    return get_cmd(text, data_tab)


def for_sound_volume(text):
    data_volume = {
        'down': {'уменьши', 'уменьшить', 'меньше', ''},
        'up': {'увеличь', 'увеличить', 'больше'},
        'change': {'установи', 'поставь', 'сделай', 'уровень'}
    }
    return get_cmd(text, data_volume)


def for_folders(text):
    data_disks = {
        'C': {'це', 'тебя', 'цель'},
        'D': {'да', 'дэ', 'для'},
        'E': {'еп', 'не', 'я', 'еде', 'джейка', 'джей'}
    }
    return get_cmd(text, data_disks)


def numders(text):
    data_numbers = {
        '1': {'первым', 'первую', 'первого', 'один', 'первая'},
        '2': {'вторую', 'два', 'вторая'},
        '3': {'третьем', 'третью', 'третье', 'три'},
        '4': {'четвёртую', 'четвёртая', 'четыре'},
        '5': {'пятую', 'пятая', 'пять'},
        '6': {'шестую', 'шестой', 'шестую', 'шесть'},
        '7': {'седьмой', 'седьмое', 'седьмую', 'семь'},
        '8': {'шестую', 'шестой', 'шесть'},
        '9': {'последняя', 'последнюю', 'последнее', 'последние', 'последний',
              'лав', 'пласт', 'балласт', 'ласк', 'девятый', 'девятую', 'ласт',
              'девять', 'крайнюю', 'вправо', 'права', 'справа'}
    }
    return get_cmd(text, data_numbers)


def for_calculator(text):
    data_symbols = {
        'plus': {'плюс'},
        'minus': {'минус', 'минут'},
        'multi': {'умножить', 'умножь', 'множественные', 'наш'},
        'divide': {'разделить', 'поделить', 'пропили', 'пойти', 'одели', 'отели',
                   'подери', 'пробили', 'провели', 'отделить', 'отдели', 'подери'}
    }
    delimiter = {'на', 'плюс', 'минус', 'к'}
    if text == 'all': return {i for j in data_symbols.values() for i in j}
    print(get_cmd(text, data_symbols), delimiter & set(text.split()), '****')
    return get_cmd(text, data_symbols), delimiter & set(text.split())

