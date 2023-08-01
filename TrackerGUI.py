#from tkinter import *
import tkinter as tk
from tkinter import ttk
from colors import *
from Calc import *
import json


class TrackerGUI(tk.Tk):
    def __init__(self, calc):
        super().__init__()
        """Initialize the whole GUI, including making all the widgets."""
        # Initialize some instance variables
        self.calc = calc
        self.track = False
        with open('settings.json') as settings:
            self.settings = json.load(settings)
        # Make the GUI
        # initialize overall frame:
        self.title("MoM Damage Calc")
        self['bg'] = '#282828'
        # initialize output portion, which is just the data cells and their labels:
        entrytext = ["Name", "Damage", "# Hits", "Min Hit", "Max Hit", "Avg Hit",
                   "Time (s)", "DPS", "DPM"]
        self.entries = [tk.Label(self, width=12, bg=grey, fg=text_color,
                            highlightbackground="grey", highlightthickness=1,
                            anchor="e") for _ in entrytext]
        [entry.grid(column=i+1, row=2) for i, entry in enumerate(self.entries)]
        [tk.Label(self, text=txt, bg=grey, fg=text_color).grid(column=i, row=1)
            for i, txt in enumerate(entrytext)]
        # initialize input portion:
        # The name entry:
        self.namebox = tk.Entry(self, width=14, bg=grey, fg="cyan")
        self.namebox.grid(column=0, row=0)
        if calc.pname == "":
            self.namebox['fg'] = text_color
            self.namebox.insert(0, "Name")
        else:
            self.namebox.insert(0, calc.pname)
        self.namebox.bind("<ButtonPress>", self.handleNoNameFocus)
        self.namebox.bind("<FocusOut>", self.handleNoNameUnfocus)
        self.namebox.bind("<Return>", self.handleNoNameReturn)
        # Game log entry:
        self.logentry = tk.Entry(self, width=14, bg=grey, fg="cyan",
                              justify="left")
        self.logentry.grid(column=1, row=0)
        if self.calc.path == "":
            self.logentry['fg'] = text_color
            self.logentry.insert(0, "game.txt path")
        else:
            self.logentry.insert(0, self.calc.path)
        self.logentry.bind("<ButtonPress>", self.handleNoLogFocus)
        self.logentry.bind("<FocusOut>", self.handleNoLogUnfocus)
        self.logentry.bind("<Return>", self.handleNoLogReturn)
        # Inactivity timer entry:
        self.inactivity = tk.Entry(self, width=4, bg=grey, fg="cyan")
        self.inactivity.grid(column=2, row=0, sticky="e")
        self.inactivity.insert(0, self.calc.inactivity)
        self.inactivityLabel = tk.Label(self, width=8, bg=grey, fg=text_color, text="Threshold:")
        self.inactivityLabel.grid(column=2, row=0, sticky="w")
        # Start/stop buttons:
        tk.Button(self, text='Start', activebackground=hoverBG,
               activeforeground=hoverText, bg=brown, command=self.start,
               fg=text_color).grid(column=3, row=0)
        tk.Button(self, text='Stop', activebackground=hoverBG,
               activeforeground=hoverText, bg=brown, command=self.interrupt,
               fg=text_color).grid(column=4, row=0)
        # "Tracking DPS" label:
        self.tracklabel = tk.Label(self, text='Not Tracking',
                                bg=grey, fg="red")
        self.tracklabel.grid(column=5, row=0)
        # Save Buttons:
        tk.Button(self, text="Save Data", activebackground=hoverBG,
               activeforeground=hoverText, bg=brown, command=self.saveData,
               fg=text_color).grid(column=6, row=0)
        tk.Button(self, text="Save Settings", activebackground=hoverBG,
               activeforeground=hoverText, bg=brown, command=self.saveSettings,
               fg=text_color).grid(column=7, row=0)
        # Settings Presets:
        presets = tk.OptionMenu(self,
                                tk.StringVar(self, "Presets"),
                                *self.settings.keys(),
                                command=self.loadPreset)
        presets.grid(column=8, row=0, sticky=tk.W, padx=5, pady=5)

        self.mainloop()

    def start(self):
        """Begin tracking damage"""
        for entry in self.entries:
            entry['text'] = 0
        self.track = True
        # Reset the calc:
        self.calc.reset()
        self.calc.setLastLine()
        # Make sure calc has right inputs
        self.calc.setName(self.namebox.get())
        self.calc.path = self.logentry.get()
        self.calc.inactivity = int(self.inactivity.get())
        # Disable entries during data collection
        self.namebox['state'] = 'disabled'
        self.logentry['state'] = 'disabled'
        self.inactivity['state'] = 'disabled'
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
                    entry['text'] = ''
                self.displayStats()
        self.after(1000, self.update)

    def displayStats(self):
        """Displays current state of the calc to the GUI"""
        dmgList = self.calc.damagelist
        elapsedTime = self.calc.elapsedTime()
        # total damage
        self.entries[0]['text'] = self.calc.damage
        # number of hits
        self.entries[1]['text'] = len(dmgList)
        # min hit
        self.entries[2]['text'] = min(dmgList)
        # max hit
        self.entries[3]['text'] = max(dmgList)
        # avg hit
        self.entries[4]['text'] = round(int(self.entries[0].cget("text"))
                                / int(self.entries[1].cget("text")))
        # elapsed time
        self.entries[5]['text'] = elapsedTime
        if elapsedTime > 0:
            # DPS
            self.entries[6]['text'] = round(int(self.calc.damage) // (elapsedTime))
            # DPM
            self.entries[7]['text'] = int(self.entries[6].cget("text")) * 60
        else:
            self.entries[6]['text'] = "N/A"
            self.entries[7]['text'] = "N/A"

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
        self.namebox['state'] = 'normal'
        self.logentry['state'] = 'normal'
        self.inactivity['state'] = 'normal'

    def handleNoNameFocus(self, _):
        self.namebox['fg'] = 'cyan'
        if self.namebox.get() in ["", "Name"]:
            self.namebox.delete(0, tk.END)

    def handleNoNameUnfocus(self, _):
        self.calc.setName(self.namebox.get())
        if self.calc.pname == "":
            self.namebox['fg'] = text_color
            self.namebox.insert(0, "Name")

    def handleNoNameReturn(self, _):
        self.calc.setName(self.namebox.get())

    def handleNoLogFocus(self, _):
        self.logentry['fg'] = "cyan"
        if self.logentry.get() in ["", "game.txt path"]:
            self.logentry.delete(0, tk.END)

    def handleNoLogUnfocus(self, _):
        self.calc.path = self.logentry.get()
        if self.calc.path == "":
            self.logentry['fg'] = text_color
            self.logentry.insert(0, "game.txt path")

    def handleNoLogReturn(self, _):
        self.calc.path = self.logentry.get()
    
    def loadPreset(self):
        pass