import requests
import os
from tkinter import*
import time


#Take the current version and read the contents of the main page to see if the current version is still there,
#Or iterate once in each of the three spots to find out if there is a new one
def check_for_updates(repo_url, current_ver):
    current = convert_ver_to_matrix(current_ver)
    new_ver = get_latest_ver(repo_url)
    latest = convert_ver_to_matrix(new_ver)
    #Evaluate
    if current[0] != latest[0]:
        return 1
    elif current[1] != latest[1]:
        return 1
    elif current[2] != latest[2]:
        return 1
    else:
        return 0

def get_latest_ver(repo_url):
    txt = requests.get(repo_url).text
    txt = txt[txt.index("Data"):] #Needs to be worked with
    x = txt.index("AudioMixer_v") + 12
    back = txt[x:]
    i = back.index(".py")
    return txt[x:x+i]

def convert_ver_to_matrix(ver):
    i_1 = ver.index(".")
    dig_1 = int(ver[0:i_1]) #Grab the first part of the current version
    ver = ver[i_1+1:]
    i_2 = ver.index(".")
    dig_2 = int(ver[0:i_2])
    ver = ver[i_2+1:]
    dig_3 = int(ver)
    return [dig_1, dig_2, dig_3]

def make_source_url(repo_url):
    url = "https://raw.github.com/tlabrie15/AudioMixer/main/AudioMixer_v"
    latest = get_latest_ver(repo_url)
    url += latest + ".py"
    return url

def file_finder(path, filename):
    for root, dirs, files in os.walk(path):
        for name in files:
            # As we need to get the provided python file,
            # comparing here like this
            if name == filename: 
                return os.path.abspath(os.path.join(root, name))

#downloads the new source file, compiles it into an .exe and then moves that new .exe into the cwd, along with the old one
def update(url, ver, pid, old_ver):
    #Set the path for the new updated source code
    filename = "AudioMixer_v" + ver + ".py"
    #For removing the old python versions for when ready for release
    old_py = "AudioMixer_v" + old_ver + ".py"
    old_spec = "AudioMixer_v" + old_ver + ".spec"
    dir = os.getcwd()
    path = os.path.join(dir, filename)
    #Pull the new files contents from github
    updated_file = requests.get(url)
    #Create new file with new source code
    open(path, 'wb').write(updated_file.content)
    #Stores executable in /dist directory, so move it
    old_dir = os.path.join(dir, "dist")
    exename = "AudioMixer_v" + ver + ".exe"
    old_path = os.path.join(old_dir, exename)
    new_path = os.path.join(dir, exename)
    pyinstaller_path = file_finder("C:\\Users\\", "pyinstaller.exe")
    scripts_path = pyinstaller_path[0:-15]
    python_folder = pyinstaller_path[0:-23]
    python_path = os.path.join(python_folder, "python.exe")
    install = os.path.join(path, "install.bat " + scripts_path + " " + python_path + " " + pyinstaller_path + " " + filename)
    os.system(install)
    #Give ample time to reinstall
    time.sleep(90)
    #UNCOMMENT REST OF LINE ON RELEASE
    restart = "restart.bat " + old_path + " " + dir + " " + new_path + " " + str(pid)# + " " + old_py + " " + old_spec
    os.system(restart)
