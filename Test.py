
text = 'поставь звук пять'
sound_level = {'один': 0.1, 'два': 0.2, 'три': 0.3, 'четыре': 0.4, 'пять': 0.5,
                'шесть': 0.6, 'семь': 0.7, 'восемь': 0.8, 'девять': 0.9, 'десять': 1}
def level_sound(txt):
    for i in sound_level:
        if i in txt:
            return sound_level[i]

print(level_sound(text))

