# Minions of Mirth Reborn DPS Calc
This program provides real-time statistics on the damage dealt by a given player and uses solely the state of the game log file (client\logs\game.txt file). This file is updated once a certain number of lines have been sent to the game window, I believe it's around 10 lines, and upon each game log update, damage statistics are updated. This approach is probably the only one that a third-party program will be able to achieve, however there are some limitations to it that will be important to understand in order to use this program.
## How To Use
To run this program, you just need to download DamageTracker.exe and have it in the same directory as a valid settings.txt file. You don't need to download any of the Python files, but feel free to use these instead if you don't feel comfortable running the exe. In this case, download all of the Python files, configure settings.txt as below, and run main.py.
You will need to configure settings.txt yourself, but this is pretty easy. For the first line, enter the name of the character whose damage you'd wish to track (technically not even necessary since you can replace the text of the entry field to the character's name; in this case, just leave the line blank). For the second line, enter the global path of game.txt, for example C:\Windows\Program Files\MomReborn\client\logs\game.txt. The third line is an optional logistic choice: because game.txt is updated every few lines, rather than at a set interval of time, it is common for game window lines to be queued for a long time, and sometimes this interferes with damage calculations. Thus, the third line takes a time in seconds such that if the difference in time between any two hits from the character is at least that time, the damage data resets and restarts upon that line. The recommended is 10 seconds, but if you'd wish to completely ignore this mechanic, simply input a large number.
Once it's set up, I think the GUI is pretty intuitive to use.

## Some Notes on Use
- The time is based off of the difference in time between your first tracked hit and your last tracked hit (using log timestamps). It was a tough choice between this and just using real time, but with the inactivity timer, I think this is better due to the unreliability of log updates.
- The accuracy of the program is pretty dependent on the rate of lines entering the game window. The more lines, the more accurate the game log is to the actual state of the game, and thus the input to the program is more accurate. 
- One potential flaw is that you kill a mob but there are a few lines of damage that didn't go through. In this case, pop a couple /who's and this should force a game.txt update, and your damage data (even the time) should be completely fine.
- There are some player names that can break this program. There are two semi-realistic ones that I can think of: if your name has "for" in it as a separate word, ie "\_ for \_", this program is just not going to work - it works normally if "for" is in your name but not as a separate word; additionally, if your name is a word-for-word subname of your opponent's name, ie you're fighting Himmorlian Chask on a toon named Himmorlian, both of your damages will be counted towards the same cause.
- This program should also work on a single player world as long as the correct game.txt path is given. I believe this is the same as the multiplayer log file.
- The min hit and avg hit stats are a little bit useless since kicks and archery are a thing. But still, I figure there's no point in excluding them.

## Updates from Previous Version
- Most obviously, this now features (mostly) real time damage updates, rather than over a single interval. Pretty huge change and was impressed that I was able to do it. Damage data attempts to update every second, but is restricted by game log updates.
- Odor sprayed smelly old code and completely refactored calc.py to be object-oriented, much cleaner now but main.py is still a little messy.
- Changed the way the time is tracked and I like it a lot better now.
- Slightly more user-friendly since it allows the user to input a file path without touching the code.
- Fixed the issue where if your character's name was multiple words, you needed to use the first word of it.

## Potential Future Changes
- Transfer settings stuff to the main GUI. I didn't really want to touch this since I don't remember how Tkinter works very well and didn't want to spend too much time figuring it out, but I will probably get to this eventually.
- Bug fixes: I've tested this program quite extensively, however there are just too many edge cases for a single person to consider. Please let me know if you find any bugs.
- For some reason, I allow the user to make their own inputs to the output boxes. This should definitely be changed but it doesn't impede on any function, it just allows people to fabricate funny screenshots.