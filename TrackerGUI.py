#from tkinter import *
import tkinter as tk
from tkinter import ttk
from colors import *
from Calc import *
import json


class TrackerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        """Initialize the whole GUI, including making all the widgets."""
        # Initialize some instance variables
        self.calc = Calc()
        self.track = False
        try:
            with open('settings.json') as settings:
                self.settings = json.load(settings)
        except FileNotFoundError:
            self.settings = {}
        # Make the GUI
        # initialize overall frame:
        self.title("MoM Damage Calc")
        self['bg'] = grey
        # initialize output portion, which is just the data cells and their labels:
        statlabels = ["Name", "Damage", "# Hits", "Min Hit", "Max Hit", "Avg Hit",
                   "Time (s)", "DPS", "DPM"]
        self.entries = [tk.Label(self, width=12, bg=grey, fg=text_color,
                            highlightbackground="grey", highlightthickness=1,
                            anchor="e") for _ in statlabels[1:]]
        [entry.grid(column=i+1, row=2) for i, entry in enumerate(self.entries)]
        self.namelabel = tk.Label(self, width=12, bg=grey, fg=text_color)
        self.namelabel.grid(column=0, row=2)
        # Create labels anonymously
        [tk.Label(self, text=txt, bg=grey, fg=text_color).grid(column=i, row=1)
            for i, txt in enumerate(statlabels)]
        # initialize input portion:
        # The name entry:
        self.namebox = tk.Entry(self, width=14, bg=grey, fg=text_color)
        self.namebox.grid(column=0, row=0)
        self.namebox.insert(0, "Name")
        #self.namebox.bind("<ButtonPress>", self.handleNoNameFocus)
        self.namebox.bind("<FocusIn>", self.handleNoNameFocus)
        self.namebox.bind("<FocusOut>", self.handleNoNameUnfocus)
        self.namebox.bind("<Return>", self.handleNoNameReturn)
        # Game log entry:
        self.logentry = tk.Entry(self, width=14, bg=grey, fg=text_color,
                              justify="left")
        self.logentry.grid(column=1, row=0)
        self.logentry.insert(0, "game.txt path")
        #self.logentry.bind("<ButtonPress>", self.handleNoLogFocus)
        self.logentry.bind("<FocusIn>", self.handleNoLogFocus)
        self.logentry.bind("<FocusOut>", self.handleNoLogUnfocus)
        self.logentry.bind("<Return>", self.handleNoLogReturn)
        # Inactivity timer entry:
        self.inactivity = tk.Entry(self, width=4, bg=grey, fg="cyan")
        self.inactivity.grid(column=2, row=0, sticky="e")
        self.inactivity.insert(0, 10)
        self.inactivityLabel = tk.Label(self, width=8, bg=grey,
                                        fg=text_color, text="Threshold:")
        self.inactivityLabel.grid(column=2, row=0, sticky="w")
        # Save settings:
        self.save = tk.Button(self, text="Save Settings", activebackground=hoverBG,
               activeforeground=hoverText, bg=button_brown, command=self.savePreset,
               fg=text_color)
        self.save.grid(column=3, row=0)
        # Settings Presets:
        if self.settings:
            self.currentPreset = tk.StringVar(self, list(self.settings.keys())[0])
        else:
            self.currentPreset = tk.StringVar(self, "Presets")
        self.presets = tk.OptionMenu(self,
                        self.currentPreset,
                        *self.settings.keys() if self.settings else ["Presets"],
                        command=self.loadPreset)
        self.presets.config(bg=button_brown, activebackground=button_brown,
                        fg=text_color, activeforeground = text_color,
                        highlightthickness=0)
        self.presets.grid(column=4, row=0, sticky=tk.W, padx=5, pady=5)
        if len(self.settings) > 0:
            self.loadPreset()
        # Delete Preset:
        self.delete = tk.Button(self, text="Delete Preset", activebackground=hoverBG,
                  activeforeground=hoverText, bg=button_brown, command=self.deletePreset,
                  fg=text_color)
        self.delete.grid(column=5, row=0)
        # Start/stop buttons:
        tk.Button(self, text='Start', activebackground=hoverBG,
               activeforeground=hoverText, bg=button_brown, command=self.start,
               fg=text_color).grid(column=6, row=0, sticky=tk.W)
        tk.Button(self, text='Stop', activebackground=hoverBG,
               activeforeground=hoverText, bg=button_brown, command=self.interrupt,
               fg=text_color).grid(column=6, row=0, sticky=tk.E)
        # "Tracking DPS" label:
        self.tracklabel = tk.Label(self, text='Not Tracking',
                                bg=grey, fg="red")
        self.tracklabel.grid(column=7, row=0)
        # Save Buttons:
        tk.Button(self, text="Save Data", activebackground=hoverBG,
               activeforeground=hoverText, bg=button_brown, command=self.saveData,
               fg=text_color).grid(column=8, row=0)

    def start(self):
        """Begin tracking damage"""
        # Make sure calc has right inputs
        self.calc.setName(self.namebox.get())
        self.calc.path = self.logentry.get()
        self.calc.inactivity = int(self.inactivity.get())
        for entry in self.entries:
            entry['text'] = 0
        self.namelabel['text'] = self.calc.pname
        self.track = True
        # Reset the calc:
        self.calc.reset()
        self.calc.setLastLine()
        # Disable entries during data collection
        self.namebox['state'] = 'disabled'
        self.logentry['state'] = 'disabled'
        self.inactivity['state'] = 'disabled'
        self.save['state'] = 'disabled'
        self.delete['state'] = 'disabled'
        self.presets['state'] = 'disabled'
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
        self.entries[4]['text'] = round(self.calc.damage/len(dmgList))
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

    def interrupt(self):
        """Stop update() from recursing, called when 'stop' clicked"""
        self.track = False
        self.tracklabel.config(text="Not Tracking", fg="red")
        self.namebox['state'] = 'normal'
        self.logentry['state'] = 'normal'
        self.inactivity['state'] = 'normal'
        self.save['state'] = 'normal'
        self.delete['state'] = 'normal'
        self.presets['state'] = 'normal'

    def savePreset(self):
        """Save current setup as a preset in settings.json"""
        try:
            # Add the new preset to the json
            key = str(self.namebox.get())
            self.settings[key] = [key, self.logentry.get(), str(self.inactivity.get())]
            with open('settings.json', 'w') as settings:
                json.dump(self.settings, settings, indent=4)
        except KeyError:
            print("That is not a valid preset name")
        # Add the new preset to the option menu
        self.currentPreset.set(key)
        self.presets['menu'].delete(0, tk.END)
        for choice in list(self.settings.keys()):
            self.presets['menu'].add_command(label=choice,
                                command=tk._setit(self.currentPreset, choice, self.loadPreset))

    def loadPreset(self, *args):
        if self.currentPreset.get() not in self.settings:
            return
        # Two parts to this, 1. insert preset into GUI, 2. insert into calc
        settings = self.settings[self.currentPreset.get()]
        # Name:
        self.namebox.delete(0, tk.END)
        self.namebox['fg'] = 'cyan'
        self.namebox.insert(0, settings[0])
        self.calc.setName(settings[0])
        # game.txt path:
        self.logentry.delete(0, tk.END)
        self.logentry['fg'] = 'cyan'
        self.logentry.insert(0, settings[1])
        self.calc.path = settings[1]
        # inactivity threshold:
        self.inactivity.delete(0, tk.END)
        self.inactivity.insert(0, settings[2])
        self.calc.inactivity = settings[2]

    def deletePreset(self):
        """Delete a preset from settings.json."""
        key = self.currentPreset.get()
        if key in self.settings:
            # Update settings.json
            self.settings.pop(key)
            with open('settings.json', 'w') as settings:
                json.dump(self.settings, settings, indent=4)
            # Update the option menu
            if len(self.settings) > 0:
                self.currentPreset.set(list(self.settings.keys())[0])
                self.presets['menu'].delete(0, tk.END)
                for choice in list(self.settings.keys()):
                    self.presets['menu'].add_command(label=choice,
                        command=tk._setit(self.currentPreset, choice, self.loadPreset))
                self.loadPreset()
            else:
                self.currentPreset.set("Presets")
                self.presets['menu'].delete(0, tk.END)
        else:
            print("Invalid Name")

    def saveData(self):
        with open("damagedata.txt", "a") as dmgdata:
            dmgdata.write(f"{self.namelabel.cget('text')} ")
            for entry in self.entries:
                dmgdata.write(f"{str(entry.cget('text'))} ")
            dmgdata.write("\n")

    def handleNoNameFocus(self, *args):
        self.namebox['fg'] = 'cyan'
        if self.namebox.get() in ["", "Name"]:
            self.namebox.delete(0, tk.END)

    def handleNoNameUnfocus(self, *args):
        self.calc.setName(self.namebox.get())
        if self.calc.pname == "":
            self.namebox['fg'] = text_color
            self.namebox.insert(0, "Name")

    def handleNoNameReturn(self, *args):
        self.calc.setName(self.namebox.get())

    def handleNoLogFocus(self, *args):
        self.logentry['fg'] = "cyan"
        if self.logentry.get() in ["", "game.txt path"]:
            self.logentry.delete(0, tk.END)

    def handleNoLogUnfocus(self, *args):
        self.calc.path = self.logentry.get()
        if self.calc.path == "":
            self.logentry['fg'] = text_color
            self.logentry.insert(0, "game.txt path")

    def handleNoLogReturn(self, *args):
        self.calc.path = self.logentry.get()