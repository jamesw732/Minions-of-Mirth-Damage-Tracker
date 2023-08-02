from re import split

class Calc:
    def __init__(self):
        """
        self.damage: total damage dealt while tracking, int
        self.damagelist: list of all damage dealt, list[int]
        self.times: first and last times that we're tracking, list[int]
        self.lastLine: index of current last line in game.txt
        """
        self.damage = 0
        self.damagelist = []
        self.times = [-1, -1]
        self.lastLine = 0
    
    def setName(self, name):
        self.pname = name
        self.namelist = name.split()

    def reset(self):
        # Resets damage and time data
        self.damage = 0
        self.damagelist.clear()
        self.times = [-1, -1]
        return
    
    def updateTime(self, time):
        # Voodoo magic that updates the times list
        if self.times[0] == -1: # data is empty
            self.times[0] = time
            self.times[1] = time
        elif time - self.times[1] > self.inactivity: # inactivity triggered
            self.reset()
            self.times[0] = time
            self.times[1] = time
        else: # no inactivity triggered, typical case
            self.times[1] = time


    def resetLastLine(self):
        self.lastLine = 0

    def setLastLine(self):
        # Set new last line
        with open(self.path) as gamelog:
            self.lastLine = len(gamelog.readlines())-1

    def getLines(self):
        # Get all lines since self.lastLine
        lines = []
        with open(self.path) as gamelog:
            allLines = gamelog.readlines()
            if self.lastLine > len(allLines): # hail mary for when game.txt gets replaced by a blank game.txt
                lines = allLines
            else:
                lines = allLines[self.lastLine:len(allLines) - 1]
            self.lastLine = len(allLines) - 1
        return lines

    def elapsedTime(self):
        # Returns time elapsed over this tracking period thus far
        return self.times[-1] - self.times[0]
    
    def updateStats(self):
        # Given lines from game.txt, calculate damage stats
        lines = self.getLines()
        if len(lines) == 0:
            return
        for line in lines:
            damage = ""
            # an array containing mostly junk, then damage, then junk
            lineArr = split(" for | damage!", line)
            # if it wasn't split three ways, then we can toss out this line
            if len(lineArr) != 3:
                continue
            try:
                damage = lineArr[1]
            except IndexError:
                continue
            try:
                damage = int(damage)
                splitline = lineArr[0].split(" ")
                validname = True
                for nameind in range(2, 2 + len(self.namelist)): # check if name is valid
                    if splitline[nameind] != self.namelist[nameind - 2]:
                        validname = False
                # at this point, we were able to extract a damage, and the damage was coming from the player
                if validname:
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

def getLastLine(f):
    # Returns the index of the final line in the given file
    with open(f) as file:
        l = len(file.readlines()) - 1
    file.close()
    return l
