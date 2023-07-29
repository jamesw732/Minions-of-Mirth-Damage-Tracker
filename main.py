from Calc import *
from TrackerGUI import *

#pyinstaller -F -n DamageTracker --noconsole main.py
if __name__ == "__main__":
    try:
        with open("settings.txt", "r") as settings:
            settingdata = []
            for line in settings:
                settingdata.append(line)
            name = settingdata[0].strip() # exclude newline character
            gamelog = settingdata[1].strip() # game.txt path, contains all messages sent to game window
            inactivity = int(settingdata[2])
    except (FileNotFoundError, ValueError, IndexError):
        name = gamelog = ""
        inactivity = 10
    calc = Calc(name, gamelog, inactivity)
    TrackerGUI(calc)