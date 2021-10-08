import sys
import subprocess
from datetime import datetime

import os


try:
    subprocess.Popen([sys.executable, "oopdatafeed.py"])
    subprocess.Popen([sys.executable, "api.py"])
except:
    print('ERROR')


os.chdir('my-app4')
os.system('ng serve --open')


'''
while True:
    dt = datetime.now()
    if dt.second == 1:
        subprocess.Popen([sys.executable, "oopdatafeed.py"])
        break
'''