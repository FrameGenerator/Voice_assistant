# import Phrase
# import win32api
# import win32gui
# import win32process
# import win32con
import psutil
import time
k = []
for i in psutil.process_iter():
    if i.name() == 'hsscp.exe':
        print(i)

while 'hsscp.exe' not in [i.name() for i in psutil.process_iter()]:
    time.sleep(1)
    print(1)
