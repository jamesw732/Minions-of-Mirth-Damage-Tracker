import tkinter as tk
from tkinter import filedialog
from colors import *
from Calc import *
import json


class TrackerGUI(tk.Tk):
    """GUI Client Code
    
    This class's functionality is intended to span all possible states of the client.
    It does not perform any damage calculations from game.txt, that work is done
    solely in Calc."""
    def __init__(self):
        super().__init__()
        """Initialize the whole GUI, including making all the widgets."""
        # Need to initialize some blank variables to reference later
        self.calc = Calc([], '')
        self.track = False
        self.datalabels = {}
        self.namelabels = {}
        self.names = []
        self.log = ""
        try:
            with open('settings.json') as settings:
                self.settings = json.load(settings)
        except FileNotFoundError:
            self.settings = {}
        # Make the GUI
        # initialize overall frame:
        self.title("MoM Damage Calc")
        self['bg'] = grey
        # Initialize output labels, but not the cells:
        self.statlabels = ["Name", "Damage", "# Hits", "Min Hit", "Max Hit", "Avg Hit",
                   "Time (s)", "DPS", "DPM"]
        [tk.Label(self, text=txt, bg=grey, fg=text_color, width=12).grid(column=i, row=1)
            for i, txt in enumerate(self.statlabels)]
        # initialize input portion:
        # The name entry:
        self.namebox = tk.Entry(self, width=14, bg=grey, fg=text_color, insertbackground='cyan')
        self.namebox.grid(column=0, row=0)
        self.namebox.insert(0, "Name")
        #self.namebox.bind("<ButtonPress>", self.handleNoNameFocus)
        self.namebox.bind("<FocusIn>", self.handleNoNameFocus)
        self.namebox.bind("<FocusOut>", self.handleNoNameUnfocus)
        # Log file button:
        self.logbutton = tk.Button(self, text="Set Log Path", activebackground=hoverBG,
                activeforeground=hoverText, bg=button_brown, command=self.getLog,
                fg=text_color)
        self.logbutton.grid(row=0, column=1)
        # Inactivity timer entry:
        self.inactivity = tk.Entry(self, width=4, bg=grey, fg="cyan", insertbackground='cyan')
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
            self.currentPreset = tk.StringVar(self, list(self.settings)[0])
        else:
            self.currentPreset = tk.StringVar(self, "Presets")
        self.presets = tk.OptionMenu(self,
                        self.currentPreset,
                        *self.settings.keys() if self.settings else ["Presets"],
                        command=self.loadPreset)
        self.presets.config(bg=button_brown, activebackground=button_brown,
                        fg=text_color, activeforeground = text_color,
                        highlightthickness=0, width=6, anchor=tk.W)
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
               fg=text_color, width=5).grid(column=6, row=0, sticky=tk.W)
        tk.Button(self, text='Stop', activebackground=hoverBG,
               activeforeground=hoverText, bg=button_brown, command=self.interrupt,
               fg=text_color, width=4).grid(column=6, row=0, sticky=tk.E)
        # "Tracking Damage" label:
        self.tracklabel = tk.Label(self, text='Not Tracking',
                                bg=grey, fg="red")
        self.tracklabel.grid(column=7, row=0)
        # Save Buttons:
        tk.Button(self, text="Save Data", activebackground=hoverBG,
               activeforeground=hoverText, bg=button_brown, command=self.saveData,
               fg=text_color).grid(column=8, row=0)

    def getLog(self):
        self.log = filedialog.askopenfilename(filetypes=[('text files', '*.txt')])

    def start(self):
        """Begin tracking damage"""
        if self.log == '':
            return
        # Destroy previous cells:
        for name in self.calc.names:
            self.namelabels[name].destroy()
            for lab in self.datalabels[name]:
                lab.destroy()
        # Initialize a new calc:
        self.names = self.namebox.get().split(', ')
        self.calc = Calc(self.names, self.log, int(self.inactivity.get()))
        # Initialize/format output cells:
        self.datalabels = {name: [tk.Label(self, width=12, bg=grey, fg=text_color,
                                highlightbackground='grey', highlightthickness=1,
                                anchor=tk.E)
                                for _ in self.statlabels[1:]]
                                for name in self.names}

        [[label.grid(column=i+1, row=2+j) for i, label in enumerate(self.datalabels[name])] for j, name in enumerate(self.names)]
        # Initialize/format name labels:
        self.namelabels = {name: tk.Label(self, width=12, bg=grey, fg=text_color, anchor=tk.W) for name in self.names}
        [self.namelabels[name].grid(column=0, row=2+i) for i, name in enumerate(self.namelabels)]

        # Insert text into labels:
        for name in self.names:
            self.namelabels[name]['text'] = name
            for lab in self.datalabels[name]:
                lab['text'] = 0

        self.track = True
        self.calc.lastLine = self.calc.getLastLine()
 
        self.tracklabel.config(text="Tracking Dmg", fg="green2")
        self.update()

    def update(self):
        """Update the state of the calc and GUI every second"""
        if not self.track:
            return
        # If actual last line of game.txt and the most recently stored 
        # line of game.txt differ, update stats.
        lastline = self.calc.getLastLine()
        if lastline != self.calc.lastLine:
            self.calc.updateStats()
            for name in self.names:
                if self.calc.damagedict[name] > 0:
                    self.displayStats(name)
        self.after(1000, self.update)

    def displayStats(self, name):
        """Displays current state of the calc to the GUI"""
        dmglist = self.calc.damagelists[name]
        elapsedTime = self.calc.elapsedTime(name)
        data = [self.calc.damagedict[name],
                len(dmglist),
                min(dmglist),
                max(dmglist),
                self.calc.damagedict[name]//len(dmglist),
                elapsedTime,
                int(self.calc.damagedict[name]) // (elapsedTime)
                    if elapsedTime > 0 else 'N/A',
                int(self.calc.damagedict[name]) // (elapsedTime) * 60
                    if elapsedTime > 0 else 'N/A']

        for d, lab in zip(data, self.datalabels[name]):
            lab['text'] = d

    def interrupt(self):
        """Stop update() from recursing, called when 'stop' clicked"""
        self.track = False
        self.tracklabel.config(text="Not Tracking", fg="red")

    def savePreset(self):
        """Save current setup as a preset in settings.json"""
        try:
            # If default value in namebox
            if self.namebox['fg'] != 'cyan':
                raise KeyError
            # Otherwise, add the new preset to the json
            key = str(self.namebox.get())
            self.settings[key] = [key, self.log, str(self.inactivity.get())]
            with open('settings.json', 'w') as settings:
                json.dump(self.settings, settings, indent=4)
        except KeyError:
            return
        # Add the new preset to the option menu
        self.currentPreset.set(key)
        self.presets['menu'].delete(0, tk.END)
        for choice in list(self.settings):
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
        # game.txt path:
        self.log = settings[1]
        # inactivity threshold:
        self.inactivity.delete(0, tk.END)
        self.inactivity.insert(0, settings[2])

    def deletePreset(self):
        """Delete current preset from settings.json."""
        key = self.currentPreset.get()
        # Update settings.json
        self.settings.pop(key)
        with open('settings.json', 'w') as settings:
            json.dump(self.settings, settings, indent=4)
        # Update the option menu
        if len(self.settings) > 0:
            self.currentPreset.set(list(self.settings)[0])
            self.presets['menu'].delete(0, tk.END)
            for choice in list(self.settings):
                self.presets['menu'].add_command(label=choice,
                    command=tk._setit(self.currentPreset, choice, self.loadPreset))
        else:
            self.currentPreset.set("Presets")
            self.presets['menu'].delete(0, tk.END)

    def saveData(self):
        with open("damagedata.txt", "a") as dmgdata:
            for name in self.names:
                dmgdata.write(f"{self.namelabels[name].cget('text')} ")
                for lab in self.datalabels[name]:
                    dmgdata.write(f"{str(lab.cget('text'))} ")
                dmgdata.write("\n")

    def handleNoNameFocus(self, *args):
        self.namebox['fg'] = 'cyan'
        if self.namebox.get() in ["", "Name"]:
            self.namebox.delete(0, tk.END)

    def handleNoNameUnfocus(self, *args):
        if self.namebox.get() == "":
            self.namebox['fg'] = text_color
            self.namebox.insert(0, "Name")