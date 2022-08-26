#==================================================================================================================
#                                               SETUP
#==================================================================================================================

from email.mime import application
from fnmatch import translate
from operator import contains
import threading
import tkinter
from pycaw.pycaw import AudioUtilities
import serial
from tkinter import*
import ApplicationUpdater
import FileMaker
from PIL import Image, ImageTk
import sys
import psutil

#==================================================================================================================
#                                               CLASSES
#==================================================================================================================

class AudioController:
    def __init__(self, process_name):
        self.process_name = process_name
        self.volume = self.process_volume()

    def mute(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                interface.SetMute(1, None)

    def unmute(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                interface.SetMute(0, None)

    def process_volume(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                return interface.GetMasterVolume()

    def set_volume(self, decibels):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                # only set volume in the range 0.0 to 1.0
                self.volume = min(1.0, max(0.0, decibels))
                interface.SetMasterVolume(self.volume, None)

    def decrease_volume(self, decibels):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                # 0.0 is the min value, reduce by decibels
                self.volume = max(0.0, self.volume - decibels)
                interface.SetMasterVolume(self.volume, None)

    def increase_volume(self, decibels):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                # 1.0 is the max value, raise by decibels
                self.volume = min(1.0, self.volume + decibels)
                interface.SetMasterVolume(self.volume, None)

class DropDown():
    def __init__(self, parent, options, index, x_pos, y_pos):
        self.parent = parent
        self.options = options
        self.all_options = options

        self.om_variable = tkinter.StringVar(self.parent)
        self.om_variable.set(current_apps[index])
        self.om_variable.trace('w', update_lists)

        self.om = tkinter.OptionMenu(self.parent, self.om_variable, *self.options)
        self.om.place(x=x_pos, y=y_pos)

    def update_option_menu(self):
        menu = self.om["menu"]
        menu.delete(0, "end")
        for string in self.options:
            menu.add_command(label=string, command=lambda value=string: self.om_variable.set(value))

    def add_option(self, option):
         self.options.append(option)

    def clear_options(self):
        self.options = []

    def update_all_options(self, new_options):
        self.all_options = new_options
        update_lists()

    def update_list(self, *args):
        current = update_current_apps()
        update_applications()
        self.clear_options()
        for i in self.all_options:
            if i not in current:
                self.add_option(i)
        self.update_option_menu()    

#==================================================================================================================
#                                               VARIABLES
#==================================================================================================================

version = "v1.1.0"
git_url = "https://github.com/tlabrie15/AudioMixer.git"

window = Tk()
title = "Audio Mixer " + version
window.title(title)           
window.geometry("1000x600")
window.configure(bg="white")


applist_file = r"C:\Program Files\AudioMixer\Data\Master List.txt"
selected_apps_file = r"C:\Program Files\AudioMixer\Data\Selected Apps.txt"
prev_apps_file = r"C:\Program Files\AudioMixer\Data\Previous Apps.txt"
temp_apps_file = r"C:\Program Files\AudioMixer\Data\Temp.txt"
mute_icon_path = r"C:\Program Files\AudioMixer\Data\mute.png"
exit_icon_path = r"C:\Program Files\AudioMixer\Data\exit.png"

prev_apps = [0, 0, 0, 0] #the previous apps selected from last startup
app_list = [] #master app list
selected_apps = [] #The pool of apps to choose from that have been selected by the user
unused_apps = [] #list of unused apps
current_apps = prev_apps
ser = serial.Serial()
data = [0,0,0,0,0,0,0,0] #HOLDS CURRENT MUTE AND VOLUME VALUES
keep_settings = [0]
running_apps_showing = False

#==================================================================================================================
#                                               INITIALIZE
#==================================================================================================================
try:
    prev_apps_txt = open(prev_apps_file, "r")
    selected_apps_txt = open(selected_apps_file, "r")
    applist_txt = open(applist_file, "r")

except:
    FileMaker.main()
    prev_apps_txt = open(prev_apps_file, "r")
    selected_apps_txt = open(selected_apps_file, "r")
    applist_txt = open(applist_file, "r")
    
i = 0
for line in prev_apps_txt:
    prev_apps[i] = (line[:-1])
    i+=1
for line in selected_apps_txt:
    selected_apps.append(line[:-1])
for line in applist_txt:
    app_list.append(line[:-1])

prev_apps_txt.close()
selected_apps_txt.close()
applist_txt.close()
applications = [AudioController(prev_apps[0]), AudioController(prev_apps[1]), AudioController(prev_apps[2]), AudioController(prev_apps[3])]


#==================================================================================================================
#                                               FUNCTIONS
#==================================================================================================================

#Update master app list using ApplicationUpdated file
def update_apps():
    ApplicationUpdater.main()

def connect():
    ser.port=commport.get()
    ser.baudrate=9800
    ser.timeout=1
     
    try:
        if ser.isOpen():
            ser.close()
            connect_button.configure(bg="red")
            connect_button.configure(fg="white")
        else:
            ser.open()
            connect_button.configure(bg="green")
            connect_button.configure(fg="black")
            mixer.start()

    except:
        error_message("Cannot connect to port")

def error_message(message):
    popup = Toplevel(window)
    popup.geometry("250x50")
    popup.title("Error")
    Label(popup, text=message).place(x=10,y=15)

#Function to ask to keep audio settings on close
def keep_audio_settings():

    def yes():
        keep_settings[0] = 1
        keep.destroy()
    def no():
        keep_settings[0] = 0
        keep.destroy()

    def cancel():
        keep_settings[0] = -1
        keep.destroy()

    keep = Toplevel(window)
    keep.title("")
    keep.geometry("240x100")
    keep.configure(bg="white")
    keep.protocol("WM_DELETE_WINDOW", cancel)

    prompt = Label(keep, text="Keep Audio Settings?", bg="white")
    warning = Label(keep, text="Selecting 'Yes' means you will have to either manually adjust volumes or re-run application", bg="white", wraplength=200)
    yes_button = Button(keep, text="Yes", command=yes, relief="groove", width=10)
    no_button = Button(keep, text="No", command=no, relief="groove", width=10)
    cancel_button = Button(keep, text="Cancel", command=cancel, relief="groove", width=10)

    prompt.grid(column=0,row=0, columnspan=5)
    yes_button.grid(column=1,row=2)
    no_button.grid(column=2,row=2)
    cancel_button.grid(column=3,row=2)
    warning.grid(column=0,row=1,columnspan=5)
    keep.wait_window()

#Add to the available apps to choose from for drop down menus
def add_to_selected_apps():
    #=====================================
    # INNER FUNCTIONS
    #=====================================
    def update_entries():
        app1_entry.update_all_options(selected_apps)
        app2_entry.update_all_options(selected_apps)
        app3_entry.update_all_options(selected_apps)
        app4_entry.update_all_options(selected_apps)
        return 0

    
    def populate_selected_apps(file):
        out = ""
        txt = open(file, "r")
        for line in txt:
            out = out + line
        return out

    def add_to_selected(app_name):
        app_name = app_name[:-1]
        if (app_name in app_list) and (app_name not in selected_apps):
            selected_apps.append(app_name)
            update_selected_apps()
            selected_apps_box.configure(state="normal")
            selected_apps_box.delete(1.0, END)
            selected_apps_box.insert(1.0, populate_selected_apps(selected_apps_file))
            selected_apps_box.configure(state="disabled")
            update_entries()
    
    def remove_from_selected(app_name):
        app_name = app_name[:-1]
        if app_name in selected_apps:
            selected_apps.remove(app_name)
            update_selected_apps()
            selected_apps_box.configure(state="normal")
            selected_apps_box.delete(1.0, END)
            selected_apps_box.insert(1.0, populate_selected_apps(selected_apps_file))
            selected_apps_box.configure(state="disabled")
            update_entries()
    
    def key_pressed(event):
        search = search_box.get(1.0, "end-1c")
        search_available(search)

    def search_available(search):
        search = search
        if  running_apps_showing:
            search = search
            txt = open(temp_apps_file, "r")
            temp_array=[]
            print_val = ""
            #create array with components containing search keyword
            for line in txt:
                if line.find(search) > -1:
                    temp_array.append(line[:-1])
            for i in temp_array:
                print_val = print_val + i + "\n"
            
            available_apps_box.configure(state="normal")
            available_apps_box.delete(1.0, END)
            available_apps_box.insert(1.0, print_val)
            available_apps_box.configure(state="disabled")
        else:
            txt = open(applist_file, "r")
            temp_array=[]
            print_val = ""
            #create array with components containing search keyword
            for line in txt:
                if line.find(search) > -1:
                    temp_array.append(line[:-1])
            for i in temp_array:
                print_val = print_val + i + "\n"
            
            available_apps_box.configure(state="normal")
            available_apps_box.delete(1.0, END)
            available_apps_box.insert(1.0, print_val)
            available_apps_box.configure(state="disabled")

    def list_running_apps():
        txt = ""
        for proc in psutil.process_iter():
            try:
                # Get process name & pid from process object.
                name = proc.name()
                if name[-4:] == ".exe":
                    if name not in txt:
                        txt += name
                        txt += "\n"
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        tmp = open(temp_apps_file, "w")
        tmp.write(txt)
        tmp.close()
        return txt

    #Switch between showing the available apps and the running apps
    def show_running_availabe():
        global running_apps_showing
        if running_apps_showing:
            show_running_button.configure(text="Running Apps")
            #Show all Available apps
            available_apps_box.configure(state="normal")
            available_apps_box.delete(1.0, END)
            available_apps_box.insert(1.0, populate_selected_apps(applist_file))
            available_apps_box.configure(state="disabled")
        else:
            show_running_button.configure(text="All Avialable")
            available_apps_box.configure(state="normal")
            available_apps_box.delete(1.0, END)
            available_apps_box.insert(1.0, list_running_apps())
            available_apps_box.configure(state="disabled")

        #Switch the case
        running_apps_showing = not running_apps_showing

    def update_all_available_apps():
        ApplicationUpdater.main()
        available_apps_box.configure(state="normal")
        available_apps_box.delete(1.0, END)
        available_apps_box.insert(1.0, populate_selected_apps(applist_file))
        available_apps_box.configure(state="disabled")

    selectApp = Toplevel(window)
    selectApp.title("Select Applications")
    selectApp.geometry("1100x600")
    selectApp.configure(bg="white")

    #Elements
    sel_label = Label(selectApp, text="Selected Apps", bg="white")
    search = Label(selectApp, text="Search:", bg="white")
    search_box = Text(selectApp, width=20, height=1, fg="black", bg="white")
    add_label = Label(selectApp, text="Add App:", bg="white")
    add_box = Text(selectApp, width=20, height=1, fg="black", bg="white")
    add_button = Button(selectApp, text="Add", command= lambda: add_to_selected(add_box.get(1.0, END)), relief="groove")
    remove_button = Button(selectApp, text="Remove", command= lambda: remove_from_selected(add_box.get(1.0, END)), relief="groove")
    show_running_button = Button(selectApp, text="Running Apps", relief="groove", command=show_running_availabe, width=12)
    selected_apps_box = Text(selectApp, width=20, height = 30, fg="black", bg="white", state="disabled")
    available_apps_box = Text(selectApp, width=87, height = 30, fg="black", bg="white", state="disabled")
    update_available_apps_button = Button(selectApp, text="Update App List", command=update_all_available_apps, relief="groove")
    scroll_available = Scrollbar(selectApp, command=available_apps_box.yview)

    #Placement
    search.place(x=862,y=20)
    search_box.place(x=912,y=20)
    search_box.bind('<KeyRelease>', key_pressed)
    add_label.place(x = 375, y=20)
    add_box.place(x=435,y=20)
    add_button.place(x=605,y=16)
    remove_button.place(x=650,y=16)
    show_running_button.place(x=725, y= 16)
    selected_apps_box.place(x=20, y=50)
    available_apps_box.place(x=375,y=50)
    sel_label.place(x=20,y=20)
    update_available_apps_button.place(x=980,y=535)
    scroll_available.place(x=1058, y=52)
    available_apps_box['yscrollcommand'] = scroll_available.set

    #initialize
    selected_apps_box.configure(state="normal")
    selected_apps_box.insert("end", populate_selected_apps(selected_apps_file))
    selected_apps_box.configure(state="disabled")
    available_apps_box.configure(state="normal")
    available_apps_box.insert("end", populate_selected_apps(applist_file))
    available_apps_box.configure(state="disabled")

def update_selected_apps():
    selected_apps.sort()
    f = open(selected_apps_file, "w")
    for i in selected_apps:
        f.write(i + "\n")
    f.close()

def update_lists(*args):
    app1_entry.update_list()
    app2_entry.update_list()
    app3_entry.update_list()
    app4_entry.update_list()

def update_current_apps():
    current_apps[0] = app1_entry.om_variable.get()
    current_apps[1] = app2_entry.om_variable.get()
    current_apps[2] = app3_entry.om_variable.get()
    current_apps[3] = app4_entry.om_variable.get()
    temp = current_apps
    return temp

def update_applications():
    applications[0] = AudioController(app1_entry.om_variable.get())
    applications[1] = AudioController(app2_entry.om_variable.get())
    applications[2] = AudioController(app3_entry.om_variable.get())
    applications[3] = AudioController(app4_entry.om_variable.get())

def from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb

def update_widget(volumes, mute):
    canvas.coords(vol_1_box, [80, 255, 160, volumes[0]])
    canvas.coords(vol_2_box, [230, 255, 310, volumes[1]])
    canvas.coords(vol_3_box, [380, 255, 460, volumes[2]])
    canvas.coords(vol_4_box, [530, 255, 610, volumes[3]])
    vol_1_per.config(text=get_percent(volumes[0]))
    vol_2_per.config(text=get_percent(volumes[1]))
    vol_3_per.config(text=get_percent(volumes[2]))
    vol_4_per.config(text=get_percent(volumes[3]))
    canvas.itemconfig(vol_1_box, fill=from_rgb((255-volumes[0], volumes[0], 0)))
    canvas.itemconfig(vol_2_box, fill=from_rgb((255-volumes[1], volumes[1], 0)))
    canvas.itemconfig(vol_3_box, fill=from_rgb((255-volumes[2], volumes[2], 0)))
    canvas.itemconfig(vol_4_box, fill=from_rgb((255-volumes[3], volumes[3], 0)))
    
    if mute[0] == 0:
        mute_label_1.place_configure(y=900)
    else:
        mute_label_1.place_configure(y=400)
    if mute[1] == 0:
        mute_label_2.place_configure(y=900)
    else:
        mute_label_2.place_configure(y=400)
    if mute[2] == 0:
        mute_label_3.place_configure(y=900)
    else:
        mute_label_3.place_configure(y=400)
    if mute[3] == 0:
        mute_label_4.place_configure(y=900)
    else:
        mute_label_4.place_configure(y=400)

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def get_percent(val):
    string = "" + str(int(translate(val, 255, 0, 0, 100))) + "%"
    return string

#TODO EDIT TO REFLECT NEW MESSAGE FORMAT
def convert_to_matrix(message):
    data[0] = int(message[0:1])
    data[1] = int(message[1:2])
    data[2] = int(message[2:3])
    data[3] = int(message[3:4])

    data[4] = int(message[4:7])
    data[5] = int(message[7:10])
    data[6] = int(message[10:13])
    data[7] = int(message[13:])

def audio_mixer():
    while True:
        mess = ser.readline()
        if(len(mess) >= 16): #TODO EDIT TO REFLECT NEW MESSAGE FORMAT
            convert_to_matrix(mess)
            mute = data[:4]
            volumes = data[4:]

            #update volume levels in widget
            update_widget(volumes, mute)
            
            i = 0
            for x in applications:
                #Set value to appropriate level
                x.set_volume(round(translate(volumes[i], 255, 0, 0.0, 1.0), 2))

                #Toggle mute
                if mute[i] == 1:
                    x.mute()
                else:
                    x.unmute()

                i+=1

def exit_mixer():
    #Write the current 4 applications to the prev_apps_file
    prev_apps_txt = open(prev_apps_file, "w")
    prev_apps_txt.write(app1_entry.om_variable.get() + "\n")
    prev_apps_txt.write(app2_entry.om_variable.get() + "\n")
    prev_apps_txt.write(app3_entry.om_variable.get() + "\n")
    prev_apps_txt.write(app4_entry.om_variable.get() + "\n")
    prev_apps_txt.close()

    #Run the keep settings window
    keep_audio_settings()
    #Keep settings?
    if keep_settings[0] == -1: #Cancel
        #Exit method and go back to app
        return 0
    elif keep_settings[0] == 0: #No
        #Reset volumes and mutes to 100% and unmuted and exit app
        for i in selected_apps:
            AudioController(i).set_volume(1.0)
            AudioController(i).unmute()
        window.destroy()
    elif keep_settings[0] == 1: #Yes
        #Leave settings as is and exit app
        window.destroy()


#==================================================================================================================
#                                               GUI
#==================================================================================================================

#variables
mixer = threading.Thread(target=audio_mixer)
mixer.daemon = True
commports = ["COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8","COM9","COM10"]
commport = StringVar()
commport.set("COM4")

mute1path = Image.open(mute_icon_path).resize((20,20), Image.Resampling.LANCZOS)
mute_1_pic = ImageTk.PhotoImage(mute1path)
mute_2_pic = ImageTk.PhotoImage(mute1path)
mute_3_pic = ImageTk.PhotoImage(mute1path)
mute_4_pic = ImageTk.PhotoImage(mute1path)
mute_label_1 = Label(window, image=mute_1_pic)
mute_label_2 = Label(window, image=mute_2_pic)
mute_label_3 = Label(window, image=mute_3_pic)
mute_label_4 = Label(window, image=mute_4_pic)
mute_label_1.place(x=327,y=400)
mute_label_2.place(x=482,y=400)
mute_label_3.place(x=630,y=400)
mute_label_4.place(x=780,y=400)

#Main Window Elements
commsettings = Label(window, text="Comm Port Settings", bg="white")
commport_label = Label(window, text="Comm Port:", bg="white")
commport_entry = OptionMenu(window, commport, *commports)
applications_label = Label(window, text="Applications:", bg = "white")
app1_entry = DropDown(window, selected_apps, 0, 300, 35)
app2_entry = DropDown(window, selected_apps, 1, 450, 35)
app3_entry = DropDown(window, selected_apps, 2, 600, 35)
app4_entry = DropDown(window, selected_apps, 3, 750, 35)
vol_1_per = Label(window, text="0%", fg="black", bg="white")
vol_2_per = Label(window, text="0%", fg="black", bg="white")
vol_3_per = Label(window, text="0%", fg="black", bg="white")
vol_4_per = Label(window, text="0%", fg="black", bg="white")
update_lists()
selectAppButton = Button(window, text="Add/Remove Applications", command=add_to_selected_apps, relief="groove")
connect_button = Button(window, text="Connect", command=connect, relief="groove", fg="white", bg="red")

#Canvas for volume visual
canvas = tkinter.Canvas(width=680, height=256, bg="white")
coord = 0, 256, 680, 256
baseline = canvas.create_line(coord)
vol_1_box = canvas.create_rectangle(80, 255, 160, 200, fill='green')
vol_2_box = canvas.create_rectangle(230, 255, 310, 200, fill='green')
vol_3_box = canvas.create_rectangle(380, 255, 460, 200, fill='green')
vol_4_box = canvas.create_rectangle(530, 255, 610, 200, fill='green')

#Main Element PLacement
commsettings.place(x=40,y=10)
commport_label.place(x=10,y=40)
commport_entry.place(x=98,y=35)
applications_label.place(x=220,y=40)
selectAppButton.place(x=800, y=550)
connect_button.place(x=20,y=75)
canvas.place(x=220,y=100)
vol_1_per.place(x=325, y=365)
vol_2_per.place(x=480, y=365)
vol_3_per.place(x=630, y=365)
vol_4_per.place(x=780, y=365)

#==================================================================================================================
#                                               MAIN
#==================================================================================================================

def main():
    window.protocol("WM_DELETE_WINDOW", exit_mixer)
    mainloop()

if __name__ == "__main__":
    main()
