from tkinter import *
from tkinter import ttk
from colors import *
from calc import *

#pyinstaller -F -n DamageTracker --noconsole main.py

class TrackerGUI:
    def __init__(self, calc):
        # Initialize some instance variables
        self.calc = calc
        self.track = False
        # Make the GUI
        # initialize overall frame:
        self.root = Tk()
        self.root.title("DPS Calc")
        self.root.configure(bg="#282828")
        # initialize output portion:
        entrytext = ["Damage", "# Hits", "Min Hit", "Max Hit", "Avg Hit",
                   "Time (s)", "DPS", "DPM"]
        self.entries = [Label(self.root, width=12, bg=grey, fg=text_color,
                            highlightbackground="grey", highlightthickness=1,
                            anchor="e") for _ in entrytext]
        [entry.grid(column=i, row=2) for i, entry in enumerate(self.entries)]
        [Label(self.root, text=txt, bg=grey, fg=text_color).grid(column=i, row=1)
            for i, txt in enumerate(entrytext)]
        # initialize input portion:
        # The name box (wow that's surprisingly a lot):
        self.namebox = Entry(self.root, width=12, bg=grey, fg="cyan")
        self.namebox.grid(column=0, row=0)
        if calc.pname == "":
            self.namebox.config(fg="grey")
            self.namebox.insert(0, "Name")
        self.namebox.insert(0, calc.pname)
        self.namebox.bind("<ButtonPress>", self.handleNoNameFocus)
        self.namebox.bind("<FocusOut>", self.handleNoNameDefocus)
        self.namebox.bind("<Return>", self.handleNoNameReturn)
        # Start/stop buttons
        Button(self.root, text='Start', activebackground=hoverBG,
               activeforeground=hoverText, bg=brown, command=self.start) \
                  .grid(column=1, row=0)
        Button(self.root, text='Stop', activebackground=hoverBG,
               activeforeground=hoverText, bg=brown, command=self.interrupt) \
                .grid(column=2, row=0)
        # "Tracking DPS" Label
        self.tracklabel = Label(self.root, text='', bg=grey, fg=text_color)
        self.tracklabel.grid(column=3, row=0)

        self.root.mainloop()

    def start(self):
        """Begin tracking damage"""
        for entry in self.entries:
            entry.config(text="0")
        self.track = True
        self.calc.reset()
        self.calc.setLastLine()
        self.calc.setName(self.namebox.get())
        self.update()

    def update(self):
        """Update the state of the calc and GUI every second"""
        if not self.track:
            return

        self.tracklabel.config(text="Tracking DPS")
        lastline = getLastLine(self.calc.path)
        if lastline != self.calc.lastLine:
            self.calc.updateStats()
            if self.calc.damage > 0:
                # Delete old contents and replace with new
                for entry in self.entries:
                    entry.config(text="")
                self.displayStats()
        self.root.after(1000, self.update)

    def displayStats(self):
        """Displays current state of the calc to the GUI"""
        dmgList = self.calc.damagelist
        elapsedTime = self.calc.elapsedTime()
        self.entries[0].config(text=self.calc.damage) # total damage
        self.entries[1].config(text=len(dmgList)) # number of hits
        self.entries[2].config(text=min(dmgList)) # min hit
        self.entries[3].config(text=max(dmgList)) # max hit
        self.entries[4].config(text=
            round(int(self.entries[0].cget("text"))
                  /int(self.entries[1].cget("text"))))  # avg hit
        self.entries[5].config(text=elapsedTime) # elapsed time
        if elapsedTime > 0:
            self.entries[6].config(text=round(int(self.calc.damage) // (elapsedTime))) # DPS
            self.entries[7].config(text=int(self.entries[6].cget("text")) * 60) # DPM
        else:
            self.entries[6].config(text="N/A")
            self.entries[7].config(text="N/A")

    def interrupt(self):
        """Stop update() from recursing, called when 'stop' clicked"""
        self.track = False
        self.tracklabel.config(text="")

    def handleNoNameFocus(self, _):
        self.namebox.config(fg="cyan", )
        if self.namebox.get() in ["", "Name"]:
            self.namebox.delete(0, END)

    def handleNoNameDefocus(self, _):
        self.calc.pname = self.namebox.get()
        if self.calc.pname == "":
            self.namebox.config(fg="grey")
            self.namebox.insert(0, "Name")

    def handleNoNameReturn(self, _):
        self.calc.pname = self.namebox.get()
        if self.calc.pname == "":
            self.namebox.config(fg="grey")
            self.namebox.insert(0, "Name")


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