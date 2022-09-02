import os
import ApplicationUpdater

class FileCreator():
    def __init__(self, dir_path):
        self.dir_path = dir_path
    
    def _create_file(self, filename):
        try:
            path = self.dir_path + "\\" + filename
            f = open(path, "x")
            f.close()
        except:
            pass

#create files needed
    
parent = "C:\Program Files"
dir =  "AudioMixer\Data"
path = os.path.join(parent, dir)
try:
    os.mkdir(path)
except OSError as error:
    print(error)

file_creator = FileCreator("C:\Program Files\AudioMixer\Data")
file_creator._create_file("Master List.txt")
file_creator._create_file("Previous Apps.txt")
file_creator._create_file("Selected Apps.txt")
file_creator._create_file("Temp.txt")

ApplicationUpdater.main()
selected_apps = ["chrome.exe", "msedge.exe", "mspaint.exe", "snippingtool.exe"]
selected_apps.sort()
f = open(selected_apps_file, "w'")
for i in selected_apps:
    f.write(i + "\n")
f.close()
prev_apps = selected_apps