# Minions of Mirth Reborn DPS Calc
This program records real-time data on the damage dealt by a given player and uses solely the state of the game log file (client\logs\game.txt file). This file is updated once a certain number of lines have been sent to the game window, I believe it's around 10 lines, and upon each game log update, more damage data is collected. This approach is probably the only one that a third-party program will be able to achieve, however there are some limitations and nuances to it that will be important to understand in order to use this program properly.
# How To Use
## Downloading and Running
There are a few ways of getting this program onto your local machine. One is to simply download files from the repo - either DamageTracker.exe alone or every .py file would suffice, but Github also lets you download the whole repo as a .zip, which you can extract anywhere. However, I instead recommend cloning the whole repo (`git clone https://github.com/jamesw732/Minions-of-Mirth-Damage-Tracker.git`), as this will let you call `git pull` on the commandline in the repo instead of having to redownload the files every time I push a change. You do not need to put the files in any specific location (such as your client's directory), this program should work from anywhere. However, the python files must stay together in the same directory, as well as any files created by the program (just damagedata.txt and settings.json I think).  
In either case, you may run the program either by running main.py, which requires Python, or by running DamageTracker.exe, which doesn't require Python but has a slight startup time. If you trust the code but not the exe (technically you have no reason to trust the exe), you can build it with the command `pyinstaller -F -n DamageTracker --noconsole main.py`. You'll want to move it out of the dist folder, though.
## Configuring and Saving Settings
Whichever method you choose to download and run this program, once you're in the GUI, you'll have to put some information in the three left-most columns:
1. The name(s) of the character or mob which you wish to track the damage of. If multiple names are entered, then they must be separated by a comma and space. Example: `Flake, Soulgazer`.
2. The path to the relevant `game.txt` file, select this with the file dialog that pops up. The location of this file will be inside your client's folder (something like `client/logs/game.txt`).
3. The third entry labeled "Threshold" establishes a time threshold (in seconds) such that if the time between two hits by the tracked player is greater than that threshold, then the damage tracking resets. This is desirable because long waits between fights typically make data over that time period uninteresting. If we reset, then there's at least a chance that we get interesting data. By default, this is 10 seconds, and if you wish to disable it, simply input a large number.
Once you have configured your desired settings, click "Save Settings" to save them. You can save multiple presets and change which one you're using whenever you like using the "Presets" dropdown. You can also delete the current preset using the "Delete Preset" button.
## Tracking Damage
It should be pretty intuitive once you have the settings configured. "Start" begins a new damage tracking period, and "Stop" stops it. It will be pretty obvious that you started tracking because a "Tracking DPS" indicator will replace the "Not Tracking" one and data cells will start to populate with numbers. Clicking "Save Data" will write the current contents of those data cells, including the name, to a local file called `damagedata.txt`. Minimal formatting is done here, just the name and the values of each of the data fields separated by a space. I figured something like this would be useful if you were trying to compare damage of weapons.
### Notes on Use
- The elapsed time is based on the difference in time between your first tracked hit and your last tracked hit, NOT using real time elapsed since pressing the start button. The factor that made me decide to do this was that since game log entry always comes in a little late, your time-dependent data would *never* be correct at any point in time if we were using real time, but with this version of elapsed time, the output at least correctly describes data at one point in time.
- The accuracy of the program is pretty dependent on the rate of lines entering the game window. The more lines per second, the more accurate the game log is to the actual state of the game, and thus the input to the program is more accurate at real time.
- On the other hand, the combat channel can get turned off magically, and I'm not certain how. This makes it difficult to accurately track multiple players over a long boss fight.
- A common problem is that you kill a mob but there are a few lines of damage that didn't go through. If you care enough to get the complete damage data, pop a couple /who's or something before you stop tracking and this should force a game.txt update, and your damage/time data will be preserved perfectly, as if captured in real time. An alternative may be to keep tracking until the next log update, but I think it's okay as is.
- Log files are unique to the client you're using, independent of the world. This means that if you want to track damage data in single player, just use the same log file that you were using. It also means that if you log into the same account on two different clients, you will have to manually replace your chosen log file.
- The min hit and avg hit stats are a little bit useless since kicks and archery will skew these values. But still, I figure there's no point in excluding them. It's probably better and more visually appealing than unused space, anyways.
- If you are tracking for more than one character/mob, the inactivity timer is independent for each one.
- In previous versions, editing your inputs while you were tracking your damage would break the program (which led me to disable inputs while tracking), but this no longer the case. You should be able to edit freely during tracking and then stop/start tracking to load your new settings. In other words, updating inputs won't change the behavior of your current damage tracking.
### (Potential) Limitations/Bugs
- After some high amount of lines (18,000 or something), game.txt turns into game.txt.1, and any existing game.txt.1 turns into game.txt.2, etc, and game.txt resets to a blank test file. This will only be an issue for damage tracking very rarely, however I did add handling that *I believe* works. I did not test it by capturing a game.txt rollover in the wild, instead I fabricated the rollover behavior, however it's possible that I'm wrong and did not do this perfectly, but I'm fairly confident that any issue witht this would be small and go unnoticed.
- There are some player names that can break this program. I think the only names that will cause it to break completely are those that have "for" in them as a separate word, ie "\_ for \_". It works normally if "for" is in your name but not as a separate word.
- An unavoidable problem is that mobs with the same name all count towards the same damage source in the tracker. A less avoidable, but still existing problem is that mobs whose names are contained exactly in the name of another mob get double counted - once for their self, once for the other mob. For example, if your name is "Skeleton Bro" and you're fighting a "Skeleton", the skeleton's damage will count towards both itself and you. Cases like these seemed sufficiently rare that I didn't feel the need to spend time handling it in the code (and making the code messier than it already is), however this can change if there's any player using this who is at risk of being affected by this bug.
- In any case, if you notice any bugs or have suggested improvements, whether mentioned here or not, let me know! I'm unlikely to make any more changes outside of requests, as this program is currently in pretty much the best state I can envision it being in.