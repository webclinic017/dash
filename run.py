import sys
import subprocess
from datetime import datetime



subprocess.Popen([sys.executable, "datafeed2.py"])

while True:
    dt = datetime.now()
    if dt.second == 1:
        subprocess.Popen([sys.executable, "man.py"])
        break
