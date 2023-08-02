from re import split

class Calc:
    """Damage Calculator
    
    The "under the hood" portion of this program, reads from game.txt and 
    outputs data whenever called."""
    def __init__(self):
        """
        self.name: name of the player being tracked, str
        self.logpath: global path to game.txt, str
        self.inactivity: inactivity timer threshold, resets if time between two valid damage lines is higher than this.
        self.damage: total damage dealt while tracking, int
        self.damagelist: list of all damage dealt, list[int]
        self.times: first and last times of our data tracking, list[int]
        self.lastLine: index of current last line in game.txt
        """
        self.name = ''
        self.logpath = ''
        self.inactivity = 10
        self.damage = 0
        self.damagelist = []
        self.times = [-1, -1]
        self.lastLine = 0

    def reset(self):
        # Resets damage and time data
        self.damage = 0
        self.damagelist.clear()
        self.times = [-1, -1]
    
    def updateTime(self, time):
        """Updates list, meant to be called for every valid damage line"""
        # Initial no data case, times haven't been set yet
        if self.times[0] == -1:
            self.times[0] = time
            self.times[1] = time
        # We went over inactivity threshold, so we reset and then start again on this time
        elif time - self.times[1] > self.inactivity:
            self.reset()
            self.times[0] = time
            self.times[1] = time
        # Typical case where we just update the most recent time
        else:
            self.times[1] = time

    def getLastLine(self):
        # Returns the latest line in game.txt. Does not store it.
        with open(self.logpath) as gamelog:
            return len(gamelog.readlines())-1

    def getLines(self):
        # Get all lines since self.lastLine and update lastline
        lines = []
        with open(self.logpath) as gamelog:
            allLines = gamelog.readlines()
            if self.lastLine > len(allLines): # hail mary for when game.txt gets replaced by a blank game.txt
                lines = allLines
            else:
                lines = allLines[self.lastLine:len(allLines) - 1]
            self.lastLine = len(allLines) - 1
        return lines

    def elapsedTime(self):
        # Returns time elapsed over this tracking period thus far
        return self.times[1] - self.times[0]
    
    def updateStats(self):
        # Given lines from game.txt, calculate damage stats
        lines = self.getLines()
        if len(lines) == 0:
            return
        for line in lines:
            damage = ""
            lineArr = split(" for | damage!", line)
            # line should be split [junk, dmg, nothing]
            if len(lineArr) != 3:
                continue
            try:
                damage = int(lineArr[1])
                # 'timestamp - name', so name is always index 2
                if line.split(' - ')[1].startswith(self.name):
                    curTime = getTime(line)
                    self.updateTime(curTime)
                    self.damage += damage
                    self.damagelist.append(damage)
            except ValueError:
                continue
        return

    def out(self):
        return (self.damage, self.damagelist, self.elapsedTime())

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
