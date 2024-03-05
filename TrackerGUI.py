import tkinter as tk
from tkinter import filedialog
from colors import *
from Calc import *
import json
import matplotlib as mpl
from matplotlib import animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import random


mpl.rcParams['toolbar'] = 'None'
mpl.rcParams['text.color'] = text_color
mpl.rcParams['axes.labelcolor'] = text_color
mpl.rcParams['xtick.color'] = text_color
mpl.rcParams['ytick.color'] = text_color
mpl.rcParams['figure.facecolor'] = grey
mpl.rcParams['axes.facecolor'] = grey
mpl.rcParams['axes.edgecolor'] = text_color


class RegrMagic(object):
    def __init__(self, calc):
        self.x = 0
        self.calc = calc

    def __call__(self):
        self.x += 1
        return self.x, self.calc.dpm_by_name


class TrackerGUI():
    """GUI Client Code
    
    This class's functionality is intended to encompass all possible states of the client.
    It does not perform any damage calculations from game.txt, that work is done
    solely in Calc."""
    def __init__(self):
        self.root = tk.Tk()
        self.calc = Calc([], '')
        self.track = False
        self.datacells = {}
        self.namelabels = {}
        self.names = []
        self.log = ""
        self.graph_widget = None
        self.graphvar = tk.BooleanVar()
        try:
            with open('settings.json') as settings:
                self.settings = json.load(settings)
        except FileNotFoundError:
            self.settings = {}
        self.currentPreset = tk.StringVar(self.root, "")
        # Initialize the base GUI:
        self.root.title("MoM Damage Tracker")
        self.root.configure(background=grey)
        self.makeNameBox()
        self.makeLogButton()
        self.makeThreshold()
        self.makeSaveSettings()
        self.makePresetDropdown()
        self.makeDeletePreset()
        self.makeStart()
        self.makeStop()
        self.makeTracking()
        self.makeSave()
        self.makeGraphCheck()
        self.makeLabels()

    """Create Buttons"""
    def makeNameBox(self):
        self.namebox = tk.Entry(self.root, width=14, bg=grey, fg=text_color, insertbackground='cyan')
        self.namebox.grid(column=0, row=0)
        self.namebox.insert(0, "Name")
        self.namebox.bind("<FocusIn>", self.handleNoNameFocus)
        self.namebox.bind("<FocusOut>", self.handleNoNameUnfocus)

    def makeLogButton(self):
        self.logbutton = tk.Button(self.root, text="Set Log Path", activebackground=hoverBG,
                activeforeground=hoverText, bg=button_brown, command=self.getLog,
                fg=text_color)
        self.logbutton.grid(row=0, column=1)

    def makeThreshold(self):
        self.inactivity = tk.Entry(self.root, width=4, bg=grey, fg="cyan", insertbackground='cyan')
        self.inactivity.grid(column=2, row=1, sticky="e")
        self.inactivity.insert(0, 10)
        self.inactivityLabel = tk.Label(self.root, width=8, bg=grey, font=("Arial", 8),
                                        fg=text_color,text="Inactivity\nThreshold")
        self.inactivityLabel.grid(column=2, row=1, sticky="w")

    def makeSaveSettings(self):
        self.save = tk.Button(self.root, text="Save Settings", activebackground=hoverBG,
               activeforeground=hoverText, bg=button_brown, command=self.savePreset,
               fg=text_color)
        self.save.grid(column=4, row=0)

    def makePresetDropdown(self):
        if self.settings:
            self.currentPreset.set(list(self.settings)[0])
        else:
            self.currentPreset.set("Presets")
        self.presets = tk.OptionMenu(self.root,
                        self.currentPreset,
                        *self.settings.keys() if self.settings else ["Presets"],
                        command=self.loadPreset)
        self.presets.config(bg=button_brown, activebackground=button_brown,
                        fg=text_color, activeforeground = text_color,
                        highlightthickness=0, width=20, anchor=tk.W)
        self.presets.grid(column=2, row=0, padx=5, pady=5, columnspan=2)
        if len(self.settings) > 0:
            self.loadPreset()

    def makeDeletePreset(self):
        self.delete = tk.Button(self.root, text="Delete Preset", activebackground=hoverBG,
                  activeforeground=hoverText, bg=button_brown, command=self.deletePreset,
                  fg=text_color)
        self.delete.grid(column=5, row=0)

    def makeStart(self):
        tk.Button(self.root, text='Start', activebackground=hoverBG,
               activeforeground=hoverText, bg=button_brown, command=self.start,
               fg=text_color, width=8).grid(column=0, row=1)

    def makeStop(self):
        tk.Button(self.root, text='Stop', activebackground=hoverBG,
               activeforeground=hoverText, bg=button_brown, command=self.interrupt,
               fg=text_color, width=8).grid(column=1, row=1)
    def makeTracking(self):
        self.tracklabel = tk.Label(self.root, text='Not Tracking',
                                bg=grey, fg="red")
        self.tracklabel.grid(column=5, row=1)

    def makeSave(self):
        tk.Button(self.root, text="Save Data", activebackground=hoverBG,
               activeforeground=hoverText, bg=button_brown, command=self.saveData,
               fg=text_color).grid(column=4, row=1)

    def makeGraphCheck(self):
        tk.Label(self.root, text="Display\nGraph", bg=grey, fg=text_color, font=("Arial",8)).grid(column=3, row=1, sticky='w', padx=(15, 0))
        settings = self.settings.get(self.currentPreset.get())
        try:
            self.graphvar.set(settings[3])
        except (IndexError, TypeError):
            self.graphvar.set(True)

        self.graphbutton = tk.Checkbutton(self.root, bg=grey, activebackground=grey, activeforeground="white", variable=self.graphvar)
        self.graphbutton.grid(column=3, row=1, sticky='e')

    def makeLabels(self):
        # Initialize output labels, but not the cells:
        self.statlabels = ["Name", "Damage", "Max Hit", "Time (s)", "DPS", "DPM"]
        for i, txt in enumerate(self.statlabels):
            tk.Label(self.root, text=txt, bg=grey, fg=text_color, width=12).grid(column=i, row=2)

    """Button Callback Functions"""
    def getLog(self):
        self.log = filedialog.askopenfilename(filetypes=[('text files', '*.txt')])

    def start(self):
        """Begin tracking damage"""
        if self.log == '':
            return
        # Destroy previous cells:
        for name in self.calc.names:
            self.namelabels[name].destroy()
            for lab in self.datacells[name]:
                lab.destroy()
        if self.graph_widget:
            self.graph_widget.destroy()
        # Initialize a new calc:
        self.names = self.namebox.get().split(', ')
        self.calc = Calc(self.names, self.log, int(self.inactivity.get()))
        self.namecolors = {name: "#"+''.join([random.choice('0123456789ABCDEF')
                    for _ in range(6)]) for name in self.names}
        # Initialize/format output:
        self.namelabels = {name: tk.Label(self.root,width=12, bg=grey, fg=self.namecolors[name], anchor=tk.W) for name in self.names}
        self.datacells = {name: [tk.Label(self.root, width=12, bg=grey, fg=text_color,
                                highlightbackground='grey', highlightthickness=1,
                                anchor=tk.E)
                                for _ in self.statlabels[1:]]
                                for name in self.names}

        for r, name in enumerate(self.names):
            self.namelabels[name].grid(column=0, row=3+r)
            self.namelabels[name]['text'] = name
            for c, cell in enumerate(self.datacells[name]):
                cell.grid(column=c+1, row=3+r)
                cell['text'] = 0

        self.track = True
        self.calc.lastLine = self.calc.getLastLine()

        if self.graphvar.get():
            self.regr_magic = RegrMagic(self.calc)
            self.anim = self.make_graphs()
 
        self.tracklabel.config(text="Tracking Dmg", fg="green2")
        self.update()

    def interrupt(self):
        """Stop update() from recursing, called when 'stop' clicked"""
        if not self.track:
            return
        plt.close('all')
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
            self.settings[key] = [key, self.log, str(self.inactivity.get()), self.graphvar.get()]
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
        # graph var:
        try:
            self.graphvar.set(settings[3])
        except IndexError:
            self.graphvar.set(True)

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
                for lab in self.datacells[name]:
                    dmgdata.write(f"{str(lab.cget('text'))} ")
                dmgdata.write("\n")

    """Helper Functions"""
    def update(self):
        """Update the state of the calc and GUI every second"""
        if not self.track:
            return
        # If actual last line of game.txt and the most recently stored
        # line of game.txt differ, update stats.
        lastline = self.calc.getLastLine()
        if lastline != self.calc.lastLine:
            self.calc.readDmgData()
            for name in self.names:
                if self.calc.damagedict[name] > 0:
                    self.displayStats(name)
        self.root.after(1000, self.update)

    def displayStats(self, name):
        """Displays current state of the calc to the GUI for one name"""
        data = self.calc.getCurStats(name)
        for d, lab in zip(data, self.datacells[name]):
            lab['text'] = d

    def make_graphs(self):
        fig = plt.figure(figsize=(5, 2))
        fig.suptitle("DPM Vs Time")
        ax = plt.subplot()
        # fig.tight_layout(pad=1)
        # ax.set_ylabel("DPM")
        # ax.set_xlabel("Time (s)")
        plt.grid(visible=True, which='major')
        # plt.tick_params(
        #     axis='x',          # changes apply to the x-axis
        #     which='both',      # both major and minor ticks are affected
        #     bottom=False,      # ticks along the bottom edge are off
        #     top=False,         # ticks along the top edge are off
        #     labelbottom=False) # labels along the bottom edge are off
        [ax.plot([], [], label=name, color=self.namecolors[name]) for name in self.names]

        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        self.graph_widget = canvas.get_tk_widget()
        self.graph_widget.grid(column=0, row=3+len(self.names), columnspan=6, padx=(50, 0))

        x = []
        y = {name: [] for name in self.names}

        def animate(args):
            x.append(args[0])
            for name in self.names:
                y[name].append(args[1][name])
            return [ax.plot(x, y[name], label=name, color=self.namecolors[name]) for name in self.names]

        return animation.FuncAnimation(fig, animate, frames=self.frames, interval=1000, cache_frame_data=False, blit=False)

    def frames(self):
        while True:
            yield self.regr_magic()

    def handleNoNameFocus(self, *args):
        self.namebox['fg'] = 'cyan'
        if self.namebox.get() in ["", "Name"]:
            self.namebox.delete(0, tk.END)

    def handleNoNameUnfocus(self, *args):
        if self.namebox.get() == "":
            self.namebox['fg'] = text_color
            self.namebox.insert(0, "Name")