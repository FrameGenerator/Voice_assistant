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
                        'закройся'},
        'write': {'напиши', 'запиши', 'набери', 'опиши', 'пиши',
                  'запишись', 'пишусь', 'запишусь'},
        'tab': {'вкладку', 'кладку', 'вклад', 'вкладка', 'вкладках', 'хватку'},
        'music': {'музыку', 'музыка', 'музычку', 'песню', 'песня', 'песенку',
                  'песни', 'трек', 'песен', 'песенка', 'мужика'},
        'google': {'гугл'},
        'all': {'все'},
        'folder': {'папку', 'коробку', 'пробку', 'папки'},
        'press': {'нажмите', 'нажми', 'жми', 'зажми'},
        'translate': {'переводится', 'переведи', 'перевод', 'означает', 'перевести',
                      'сказать', 'перевода', 'режим'},
        'sound_level': {'звук', 'громкость', 'звуков', 'круг', 'бог', 'громкости',
                        'звука'},
        'for_last_cmd': for_last_cmd,
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
    global for_last_cmd
    for_last_cmd = {j for k in [data_mus[i] for i in data_mus] for j in k}
    return get_cmd(text, data_mus)


def for_open_close_all(text):
    data_open_close = {
        'minimeze': {'сверни', 'вернее', 'ферме', 'севернее'},
        'close': {'крой', 'закрой', 'аковой'},
        'open': {'открой', 'кажи', 'покажи', 'разверни', 'разве'}
    }
    return get_cmd(text, data_open_close)


def for_wait_or_end(text):
    if text in {'ты тут', 'включись', 'продолжим', 'продолжить', 'алло', 'отключись',
                'включи', 'отключи', 'и не', 'и нет', 'дальше', 'слышишь', 'але',
                'включайся', 'химии', 'их', 'и и', 'и', 'имя', 'и ним', 'и ник',
                'и и не', 'имя але'}:
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
        'chrome': {'браузер', 'браузера', 'браузеров', 'браузером', 'браузере', 'градусов', 'браузерах', 'фронт', 'хром'
                   },
        'pycharm': {'чарм', 'чарам', 'чан', 'чар', 'плечами', 'чарли', 'чат',
                    'чарам', 'плечам', 'пальчиком', 'чаем', 'вечером'}

    }
    if text == 'all':
        return {j for k in [data_programs[i] for i in data_programs] for j in k}
    return get_cmd(text, data_programs)


def for_open_close_program(text):
    data_cmd_program = {
        'open': {'открой', 'запусти', 'включи', 'откройте'},
        'close': {'закрой'},
        'forward': {'покажи', 'закажи', 'покажите', 'зверни', 'разверни'},
        'minimize': {'сверни', 'вернее', 'заверни'}
    }
    return get_cmd(text, data_cmd_program)


def program_path(text):
    data_program_path = {
        'winamp': 'C:\Program Files (x86)\Winamp\winamp.exe',
        'Battle.net': 'C:\Program Files (x86)\Battle.net\Battle.net.exe',
        'osu!': r'C:\Users\user\AppData\Local\osu!\osu!.exe',
        'Steam': 'C:\Program Files (x86)\Steam\steam.exe',
        'chrome': 'C:\Program Files\Google\Chrome\Application\chrome.exe',
        'pycharm': 'C:\\Program Files\\JetBrains\\PyCharm Community Edition 2022.3.3\\bin\pycharm64.exe'
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
        'reestablish': {'останови', 'установи', 'восстановить', 'верни', 'вернее', 'верхний'}
    }
    return get_cmd(text, data_tab)


def for_sound_volume(text):
    data_volume = {
        'down': {'уменьши', 'уменьшить', 'меньше', ''},
        'up': {'увеличь', 'увеличить', 'больше'},
        'change': {'установи', 'поставь', 'сделай', 'уровень'}
    }
    global for_last_cmd
    for_last_cmd = {j for k in [data_volume[i] for i in data_volume] for j in k}
    return get_cmd(text, data_volume)


for_last_cmd = set()
