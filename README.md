# Minions of Mirth Reborn DPS Calc
This program provides real-time statistics on the damage dealt by a given player and uses solely the state of the game log file (client\logs\game.txt file). This file is updated once a certain number of lines have been sent to the game window, I believe it's around 10 lines, and upon each game log update, damage statistics are updated. This approach is probably the only one that a third-party program will be able to achieve, however there are some limitations to it that will be important to understand in order to use this program.
## How To Use
To use this program, clone this whole repo, configure settings.txt, and run main.py. If you don't know how to use git clone or don't have Python installed, then you can probably just download DamageTracker.exe and make a valid settings.txt file in the same directory and it should run on Windows, but may be a struggle on other operating systems.  
Either way, you will need to configure settings.txt yourself, but this is pretty easy:  
1. On the first line, enter the name of the character whose damage you'd wish to track. Technically this is not necessary since you can just type your character's name into the corresponding entry field, this is mostly just for convenience so you don't have to replace a character's name several times.  
2. On the second line, enter the global path of game.txt, for example C:\Windows\Program Files\MomReborn\client\logs\game.txt.  
3. The third line is an optional logistic choice to handle long wait periods between samples of damage. For example, if you have the damage tracker running, and you kill a lava maggot, then go afk for 5 minutes, and come back to kill more, that 5 minutes will skew damage data. Thus, in the third line the user may specify a time threshold such that intervals of time between tracked damage lines cause the tracker to reset all damage data. By default, this is 10 seconds.  
Once it's set up, I think the GUI is pretty intuitive to use. Click "Start" to start tracking damage, and click "Stop" to stop.

## Some Notes on Use
- The time is based off of the difference in time between your first tracked hit and your last tracked hit (using log timestamps). It was a tough choice between this and just using real time, but with the inactivity timer, I think this is better due to the unreliability of log updates.
- The accuracy of the program is pretty dependent on the rate of lines entering the game window. The more lines, the more accurate the game log is to the actual state of the game, and thus the input to the program is more accurate. 
- One potential flaw is that you kill a mob but there are a few lines of damage that didn't go through. In this case, pop a couple /who's and this should force a game.txt update, and your damage data (even the time) should be completely fine.
- There are some player names that can break this program. There are two semi-realistic ones that I can think of: if your name has "for" in it as a separate word, ie "\_ for \_", this program is just not going to work - it works normally if "for" is in your name but not as a separate word; additionally, if your name is a word-for-word subname of your opponent's name, ie you're fighting Himmorlian Chask on a toon named Himmorlian, both of your damages will be counted towards the same cause.
- I believe the single player log file is the same as the multiplayer log file, but I'm not certain.
- The min hit and avg hit stats are a little bit useless since kicks and archery are a thing. But still, I figure there's no point in excluding them.
- Haven't tested on any non-Windows OS, please let me know if you try and it fails.

## Updates from Previous Versions
- Most obviously, this now features (mostly) real time damage updates, rather than over a single interval. Pretty huge change and was impressed that I was able to do it. Damage data attempts to update every second, but is restricted by game log updates.
- Odor sprayed smelly old code and completely refactored calc.py to be object-oriented, much cleaner now but main.py is still a little messy.
- Changed the way the time is tracked and I like it a lot better now.
- Slightly more user-friendly since it allows the user to input a file path without touching the code.
- Fixed the issue where if your character's name was multiple words, you needed to use the first word of it.

## Potential Future Changes
- Transfer settings stuff to the main GUI. I didn't really want to touch this since I don't remember how Tkinter works very well and didn't want to spend too much time figuring it out, but I will probably get to this eventually.
- Bug fixes: I've tested this program quite extensively, however there are just too many edge cases for a single person to consider. Please let me know if you find any bugs.
- Users can currently make their own input to the data boxes. This should definitely be changed but it doesn't impede on any function, it just allows people to fabricate funny screenshots.