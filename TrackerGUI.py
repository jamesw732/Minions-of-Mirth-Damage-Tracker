from tkinter import *
from colors import *
from Calc import *


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
        # The name entry:
        self.namebox = Entry(self.root, width=14, bg=grey, fg="cyan")
        self.namebox.grid(column=0, row=0)
        if calc.pname == "":
            self.namebox.config(fg=text_color)
            self.namebox.insert(0, "Name")
        else:
            self.namebox.insert(0, calc.pname)
        self.namebox.bind("<ButtonPress>", self.handleNoNameFocus)
        self.namebox.bind("<FocusOut>", self.handleNoNameUnfocus)
        self.namebox.bind("<Return>", self.handleNoNameReturn)
        # Game log entry:
        self.logentry = Entry(self.root, width=14, bg=grey, fg="cyan",
                              justify="left")
        self.logentry.grid(column=1, row=0)
        if self.calc.path == "":
            self.logentry.config(fg=text_color)
            self.logentry.insert(0, "game.txt path")
        else:
            self.logentry.insert(0, self.calc.path)
        self.logentry.bind("<ButtonPress>", self.handleNoLogFocus)
        self.logentry.bind("<FocusOut>", self.handleNoLogUnfocus)
        self.logentry.bind("<Return>", self.handleNoLogReturn)
        # Inactivity timer entry:
        self.inactivity = Entry(self.root, width=4, bg=grey, fg="cyan")
        self.inactivity.grid(column=2, row=0, sticky="e")
        self.inactivity.insert(0, self.calc.inactivity)
        self.inactivityLabel = Label(self.root, width=8, bg=grey, fg=text_color)
        self.inactivityLabel.config(text="Threshold:")
        self.inactivityLabel.grid(column=2, row=0, sticky="w")
        # Start/stop buttons:
        Button(self.root, text='Start', activebackground=hoverBG,
               activeforeground=hoverText, bg=brown, command=self.start,
               fg=text_color).grid(column=3, row=0)
        Button(self.root, text='Stop', activebackground=hoverBG,
               activeforeground=hoverText, bg=brown, command=self.interrupt,
               fg=text_color).grid(column=4, row=0)
        # "Tracking DPS" label:
        self.tracklabel = Label(self.root, text='Not Tracking',
                                bg=grey, fg="red")
        self.tracklabel.grid(column=5, row=0)
        # Save Buttons:
        Button(self.root, text="Save Data", activebackground=hoverBG,
               activeforeground=hoverText, bg=brown, command=self.saveData,
               fg=text_color).grid(column=6, row=0)
        Button(self.root, text="Save Settings", activebackground=hoverBG,
               activeforeground=hoverText, bg=brown, command=self.saveSettings,
               fg=text_color).grid(column=7, row=0)
        self.root.mainloop()

    def start(self):
        """Begin tracking damage"""
        for entry in self.entries:
            entry.config(text="0")
        self.track = True
        # Reset the calc:
        self.calc.reset()
        self.calc.setLastLine()
        # Make sure calc has right inputs
        self.calc.setName(self.namebox.get())
        self.calc.path = self.logentry.get()
        self.calc.inactivity = int(self.inactivity.get())
        # Disable entries during data collection
        self.namebox.config(state="disabled")
        self.logentry.config(state="disabled")
        self.inactivity.config(state="disabled")
        self.tracklabel.config(text="Tracking DPS", fg="green2")
        self.update()

    def update(self):
        """Update the state of the calc and GUI every second"""
        if not self.track:
            return

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

    def saveSettings(self):
        with open("settings.txt", "w") as settings:
            settings.write(f"{self.calc.pname}\n")
            settings.write(f"{self.calc.path}\n")
            settings.write(str(self.calc.inactivity))

    def saveData(self):
        with open("damagedata.txt", "w") as dmgdata:
            dmgdata.write(f"{self.calc.pname} ")
            for entry in self.entries:
                dmgdata.write(f"{str(entry.cget('text'))} ")

    def interrupt(self):
        """Stop update() from recursing, called when 'stop' clicked"""
        self.track = False
        self.tracklabel.config(text="Not Tracking", fg="red")
        self.namebox.config(state="normal")
        self.logentry.config(state="normal")
        self.inactivity.config(state="normal")

    def handleNoNameFocus(self, _):
        self.namebox.config(fg="cyan", )
        if self.namebox.get() in ["", "Name"]:
            self.namebox.delete(0, END)

    def handleNoNameUnfocus(self, _):
        self.calc.setName(self.namebox.get())
        if self.calc.pname == "":
            self.namebox.config(fg=text_color)
            self.namebox.insert(0, "Name")

    def handleNoNameReturn(self, _):
        self.calc.setName(self.namebox.get())

    def handleNoLogFocus(self, _):
        self.logentry.config(fg="cyan", )
        if self.logentry.get() in ["", "game.txt path"]:
            self.logentry.delete(0, END)

    def handleNoLogUnfocus(self, _):
        self.calc.path = self.logentry.get()
        if self.calc.path == "":
            self.logentry.config(fg=text_color)
            self.logentry.insert(0, "game.txt path")

    def handleNoLogReturn(self, _):
        self.calc.path = self.logentry.get()