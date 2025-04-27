import re
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
        self.dpmhistory: list containing DPM upon each update, for use in charts
        self.times: first and last times of data tracking for each player, dict[str: list[int]]
        self.lastLine: index of current last line in game.txt
        """
        # Give longer names priority
        self.names = sorted(names, key=len, reverse=True)
        self.logpath = logpath
        self.inactivity = inactivity
        self.damagedict = {name: 0 for name in self.names}
        # self.damagelists = {name: [] for name in self.names}
        self.maxdamagedict = {name: 0 for name in self.names}
        self.dpm_by_name = {name: 0 for name in self.names}
        self.times = {name: [-1, -1] for name in self.names}
        if os.path.exists(self.logpath):
            with open(self.logpath) as log:
                self.lastLine = max(0, len(log.readlines()) - 1)
        else:
            self.lastLine = 0

    def reset(self):
        # Resets damage and time data
        self.damagedict = {name: 0 for name in self.names}
        self.maxdamagedict = {name: 0 for name in self.names}
        self.times = {name: [-1, -1] for name in self.names}
    
    def updateTime(self, time, name):
        """Updates list, meant to be called for every valid damage line"""
        # If day rollover, add 24 hours
        if time < self.times[name][0]:
            time += 86400
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

    def getCurStats(self, name):
        elapsedTime = self.elapsedTime(name)
        data = [self.damagedict[name],
                self.maxdamagedict[name],
                elapsedTime,
                int(self.damagedict[name]) // (elapsedTime)
                    if elapsedTime > 0 else 0,
                int(self.damagedict[name]) // (elapsedTime) * 60
                    if elapsedTime > 0 else 0]
        self.dpm_by_name[name] = data[-1]
        return data

    def readDmgData(self):
        # Given lines from game.txt, calculate damage stats
        logdata = self.getLines()
        if len(logdata) == 0:
            return
        for line in logdata:
            m = re.search(r"for (\d+) damage!", line)
            try:
                dmg = int(m.group(1))
                for name in self.names:
                    # Dmg lines always look like 'timestamp - name ...'
                    # Split at the ' - ', then the second half should start with name
                    txt = line.split(' - ')[1]
                    if txt.lower().startswith(name.lower()):
                        # Update damage and time data
                        self.updateTime(getTime(line), name)
                        self.damagedict[name] += dmg
                        if dmg > self.maxdamagedict[name]:
                            self.maxdamagedict[name] = dmg
                        break
            except (ValueError, AttributeError, IndexError):
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
