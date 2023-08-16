from re import split
import os

class Calc:
    """Damage Calculator
    
    The "under the hood" portion of this program, reads from game.txt and 
    outputs data whenever called."""
    def __init__(self, names, logpath, inactivity=10):
        """
        self.name: names of the mobs being tracked, list[str]
        self.logpath: global path to game.txt, str
        self.inactivity: inactivity timer threshold, resets if time between two valid damage lines is higher than this.
        self.damage: total damage dealt while tracking, dict[str: int]
        self.damagelist: list of all damage dealt, list[int]
        self.times: first and last times of data tracking for each player, dict[str: list[int]]
        self.lastLine: index of current last line in game.txt
        """
        self.names = names
        self.logpath = logpath
        self.inactivity = inactivity
        self.damagedict = {name: 0 for name in self.names}
        self.damagelists = {name: [] for name in self.names}
        self.times = {name: [-1, -1] for name in self.names}
        if os.path.exists(self.logpath):
            with open(self.logpath) as log:
                self.lastLine = max(0, len(log.readlines()) - 1)
        else:
            self.lastLine = 0

    def reset(self):
        # Resets damage and time data
        self.damagedict = {name: 0 for name in self.names}
        self.damagelists = {name: [] for name in self.names}
        self.times = {name: [-1, -1] for name in self.names}
    
    def updateTime(self, time, name):
        """Updates list, meant to be called for every valid damage line"""
        # Initial no data case, times haven't been set yet
        if self.times[name][0] == -1:
            self.times[name][0] = time
            self.times[name][1] = time
        # We went over inactivity threshold, so we reset and then start again on this time
        elif time - self.times[name][1] > self.inactivity:
            self.reset()
            self.times[name][0] = time
            self.times[name][1] = time
        # Typical case where we just update the most recent time
        else:
            self.times[name][1] = time

    def getLastLine(self):
        # Returns the latest line in game.txt. Does not store it.
        with open(self.logpath) as gamelog:
            return len(gamelog.readlines())-1

    def getLines(self):
        # Get all lines since self.lastLine and update lastline
        lines = []
        with open(self.logpath) as gamelog:
            allLines = gamelog.readlines()
            # game.txt overflowed, use game.txt.1 to recover lost data
            if self.lastLine > len(allLines):
                game1path =  self.logpath.replace('game.txt', 'game.txt.1')
                with open(game1path) as gamelog2:
                    log2lines = gamelog2.readlines()
                    lines = log2lines[self.lastLine:]
                lines += allLines
            # typical case where we just take everything since lastline
            else:
                lines = allLines[self.lastLine:]
            self.lastLine = len(allLines) - 1
        return lines

    def elapsedTime(self, name):
        # Returns time elapsed over this tracking period thus far
        return self.times[name][1] - self.times[name][0]
    
    def updateStats(self):
        # Given lines from game.txt, calculate damage stats
        logdata = self.getLines()
        if len(logdata) == 0:
            return
        for line in logdata:
            damage = ""
            lineArr = split(" for | damage!", line)
            # line should be split [junk, dmg, nothing]
            if len(lineArr) != 3 or "is damaged" in line:
                continue
            try:
                damage = int(lineArr[1])
                # 'timestamp - name', so name is always index 2
                for name in self.names:
                    if line.split(' - ')[1].startswith(name):
                        self.updateTime(getTime(line), name) # handle inactivity if applicable
                        self.damagedict[name] += damage
                        self.damagelists[name].append(damage)
            except ValueError:
                continue
        return

# Helper methods
def getTime(line):
    # Get the time, in seconds, of the given line from its timestamp
    if len(line) < 8:
        return -1
    hours = line[0] + line[1]
    mins = line[3] + line[4]
    secs = line[6] + line[7]
    try:
        hours = int(hours)
        mins = int(mins)
        secs = int(secs)
        return int(hours) * 3600 + int(mins) * 60 + int(secs)
    except ValueError:
        return -1
