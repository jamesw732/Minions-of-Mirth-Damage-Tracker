from tkinter import *
from tkinter import ttk
from colors import *
from calc import *

#pyinstaller -F -n DamageTracker --noconsole main.py

def start(calc):
    for entry in entries:
        entry.delete(0, END)
        entry.insert(0, 0)
    global track
    track = True
    calc.setLastLine()
    calc.setName(namebox.get())
    update(calc)

def update(calc): # update the state of the calc and GUI based on new game log content
    if not track:
        return

    global tracklabel
    tracklabel.config(text="Tracking DPS")

    lastline = getLastLine(calc.path)
    if lastline != calc.lastLine:
        calc.updateStats()
        if calc.damage > 0:
            clearEntries()
            displayStats(calc)
    root.after(1000, lambda: update(calc))

def displayStats(calc): # displays current state of the calc to the GUI
    Label(root, width=10, bg=grey, fg=text).grid(column=4, row=0)
    entries[0].insert(0, calc.damage) # total damage
    dmgList = calc.damagelist
    entries[1].insert(0, len(dmgList)) # number of hits
    entries[2].insert(0, min(dmgList)) # min hit
    entries[3].insert(0, max(dmgList)) # max hit
    entries[4].insert(0, round(int(entries[0].get())/int(entries[1].get())))  # avg hit
    elapsedTime = calc.elapsedTime()
    entries[5].insert(0, elapsedTime) # elapsed time
    if elapsedTime > 0:
        entries[6].insert(0, round(int(calc.damage) // (elapsedTime))) # DPS
        entries[7].insert(0, int(entries[6].get()) * 60) # DPM
    else:
        entries[6].insert(0, "N/A")
        entries[7].insert(0, "N/A")


def interrupt(): # stop tracking damage
    global track
    global tracklabel
    track = False
    tracklabel.config(text="")

def clearEntries(): # clear the stat entries, used when you first click "start"
    for entry in entries:
        entry.delete(0, END)

def createInputFrame(container, calc):
    frame = ttk.Frame(container)
    Label(container, text='Name:', bg=grey, fg=text).grid(column=0, row=0)
    global namebox
    namebox = Entry(container, width=12, bg=grey, fg="cyan")
    namebox.insert(0, calc.pname)
    namebox.focus()
    namebox.grid(column=1, row=0)
    Button(container, text='Start', activebackground=hoverBG, activeforeground=hoverText, bg=brown, command= lambda: start(calc)).grid(column=2, row=0)
    Button(container, text='Stop', activebackground=hoverBG, activeforeground=hoverText, bg=brown, command=interrupt).grid(column=3, row=0)
    return frame

def createOutputFrame(container):
    frame = ttk.Frame(container)
    cols = ["Damage", "# Hits", "Min Hit", "Max Hit", "Avg Hit", "Time (s)", "DPS", "DPM"]
    for i in range(8):
        Label(container, text=cols[i], bg=grey, fg=text).grid(column=i,row=1)
    for j in range(8):
        entries[j].grid(column=j,row=2)
    
    return frame

def createMainWindow(calc):
    createOutputFrame(root)
    createInputFrame(root, calc)
    root.mainloop()
    return

if __name__ == "__main__":
    root = Tk()
    root.title("DPS Calc")
    root.configure(bg="#282828")

    track = False
    entries = [Entry(root, width=12, bg=grey, fg=text) for _ in range(8)]
    namebox = None

    tracklabel = Label(root, text='', bg=grey, fg=text)
    tracklabel.grid(column=4, row=0)

    settings = open("settings.txt", "r")
    data = []
    for line in settings:
        data.append(line)
    name = data[0].strip() # exclude newline character
    gamelog = data[1].strip() # game.txt path, contains all messages sent to game window
    try:
        inactivity = int(data[2])
    except ValueError:
        inactivity = 10
    except IndexError:
        inactivity = 10
    calc = Calc(name, inactivity)
    calc.path = gamelog

    createMainWindow(calc)