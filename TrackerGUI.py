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
        self.datalabels = {}
        self.namelabels = {}
        self.names = []
        self.log = ""
        self.graph_widget = None
        try:
            with open('settings.json') as settings:
                self.settings = json.load(settings)
        except FileNotFoundError:
            self.settings = {}
        # Make the GUI
        # initialize overall frame:
        self.root.title("MoM Damage Calc")
        self.root.configure(background=grey)
        # Initialize output labels, but not the cells:
        self.statlabels = ["Name", "Damage", "# Hits", "Min Hit", "Max Hit", "Avg Hit",
                   "Time (s)", "DPS", "DPM"]
        [tk.Label(self.root, text=txt, bg=grey, fg=text_color, width=12).grid(column=i, row=1)
            for i, txt in enumerate(self.statlabels)]
        # initialize input portion:
        # The name entry:
        self.namebox = tk.Entry(self.root, width=14, bg=grey, fg=text_color, insertbackground='cyan')
        self.namebox.grid(column=0, row=0)
        self.namebox.insert(0, "Name")
        #self.namebox.bind("<ButtonPress>", self.handleNoNameFocus)
        self.namebox.bind("<FocusIn>", self.handleNoNameFocus)
        self.namebox.bind("<FocusOut>", self.handleNoNameUnfocus)
        # Log file button:
        self.logbutton = tk.Button(self.root, text="Set Log Path", activebackground=hoverBG,
                activeforeground=hoverText, bg=button_brown, command=self.getLog,
                fg=text_color)
        self.logbutton.grid(row=0, column=1)
        # Inactivity timer entry:
        self.inactivity = tk.Entry(self.root, width=4, bg=grey, fg="cyan", insertbackground='cyan')
        self.inactivity.grid(column=2, row=0, sticky="e")
        self.inactivity.insert(0, 10)
        self.inactivityLabel = tk.Label(self.root, width=8, bg=grey,
                                        fg=text_color, text="Threshold:")
        self.inactivityLabel.grid(column=2, row=0, sticky="w")
        # Save settings:
        self.save = tk.Button(self.root, text="Save Settings", activebackground=hoverBG,
               activeforeground=hoverText, bg=button_brown, command=self.savePreset,
               fg=text_color)
        self.save.grid(column=3, row=0)
        # Settings Presets:
        if self.settings:
            self.currentPreset = tk.StringVar(self.root, list(self.settings)[0])
        else:
            self.currentPreset = tk.StringVar(self.root, "Presets")
        self.presets = tk.OptionMenu(self.root,
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
        self.delete = tk.Button(self.root, text="Delete Preset", activebackground=hoverBG,
                  activeforeground=hoverText, bg=button_brown, command=self.deletePreset,
                  fg=text_color)
        self.delete.grid(column=5, row=0)
        # Start/stop buttons:
        tk.Button(self.root, text='Start', activebackground=hoverBG,
               activeforeground=hoverText, bg=button_brown, command=self.start,
               fg=text_color, width=5).grid(column=6, row=0, sticky=tk.W)
        tk.Button(self.root, text='Stop', activebackground=hoverBG,
               activeforeground=hoverText, bg=button_brown, command=self.interrupt,
               fg=text_color, width=4).grid(column=6, row=0, sticky=tk.E)
        # "Tracking Damage" label:
        self.tracklabel = tk.Label(self.root, text='Not Tracking',
                                bg=grey, fg="red")
        self.tracklabel.grid(column=7, row=0)
        # Save Buttons:
        tk.Button(self.root, text="Save Data", activebackground=hoverBG,
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
        if self.graph_widget:
            self.graph_widget.destroy()
        # Initialize a new calc:
        self.names = self.namebox.get().split(', ')
        self.calc = Calc(self.names, self.log, int(self.inactivity.get()))
        # Initialize/format output cells:
        self.datalabels = {name: [tk.Label(self.root, width=12, bg=grey, fg=text_color,
                                highlightbackground='grey', highlightthickness=1,
                                anchor=tk.E)
                                for _ in self.statlabels[1:]]
                                for name in self.names}

        [[label.grid(column=i+1, row=2+j) for i, label in enumerate(self.datalabels[name])] for j, name in enumerate(self.names)]
        # Initialize/format name labels:
        self.colors = {name: "#"+''.join([random.choice('0123456789ABCDEF')
                    for _ in range(6)]) for name in self.names}
        self.namelabels = {name: tk.Label(self.root,width=12, bg=grey, fg=self.colors[name], anchor=tk.W) for name in self.names}
        [self.namelabels[name].grid(column=0, row=2+i) for i, name in enumerate(self.namelabels)]

        # Insert text into labels:
        for name in self.names:
            self.namelabels[name]['text'] = name
            for lab in self.datalabels[name]:
                lab['text'] = 0

        self.track = True
        self.calc.lastLine = self.calc.getLastLine()

        self.regr_magic = RegrMagic(self.calc)
        self.anim = self.make_graphs()
 
        self.tracklabel.config(text="Tracking Dmg", fg="green2")
        self.update()

    def frames(self):
        while True:
            yield self.regr_magic()

    def make_graphs(self):
        fig, ax = plt.subplots()
        fig.set_size_inches(8.5, 2)
        fig.tight_layout(pad=4)
        ax.set_ylabel("DPM")
        ax.set_ylim(0, 500000)
        plt.grid(visible=True, which='major')
        plt.tick_params(
            axis='x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom=False,      # ticks along the bottom edge are off
            top=False,         # ticks along the top edge are off
            labelbottom=False) # labels along the bottom edge are off
        [ax.plot([], [], label=name, color=self.colors[name]) for name in self.names]

        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        self.graph_widget = canvas.get_tk_widget()
        self.graph_widget.grid(column=0, row=3+len(self.names), columnspan=9)

        x = []
        y = {name: [] for name in self.names}

        def animate(args):
            x.append(args[0])
            for name in self.names:
                y[name].append(args[1][name])
            return [ax.plot(x, y[name], label=name, color=self.colors[name]) for name in self.names]

        return animation.FuncAnimation(fig, animate, frames=self.frames, interval=1000, cache_frame_data=False, blit=False)

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
        for d, lab in zip(data, self.datalabels[name]):
            lab['text'] = d

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