from googletrans import Translator

translator = Translator()
text = 'ав'
if not text[0].encode().isalpha():
    print(text[0].encode())
temp = translator.translate(text, dest='en')
print(text)