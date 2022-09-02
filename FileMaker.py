import os
import ApplicationUpdater

class FileCreator():
    def __init__(self, dir_path):
        self.dir_path = dir_path
    
    def _create_file(self, filename):
        path = self.dir_path + "\\" + filename
        f = open(path, "x")
        f.close()


def main():
    try:
        newpath = r'C:\Program Files\AudioMixer\Data' 
        if not os.path.exists(newpath):
            os.makedirs(newpath)
    except:
        print("exists")
        pass

    file_creator = FileCreator("C:\Program Files\AudioMixer\Data")
    file_creator._create_file("Master List.txt")
    file_creator._create_file("Previous Apps.txt")
    file_creator._create_file("Selected Apps.txt")
    file_creator._create_file("Temp.txt")

    ApplicationUpdater.main()
    selected_apps = ["chrome.exe", "msedge.exe", "mspaint.exe", "snippingtool.exe"]
    selected_apps.sort()
    f = open("C:\Program Files\AudioMixer\Data\Selected Apps.txt", "w")
    p = open("C:\Program Files\AudioMixer\Data\Previous Apps.txt", "w")
    for i in selected_apps:
        f.write(i + "\n")
        p.write(i + "\n")
    f.close()
    p.close()

if __name__ == "__main__":
    main()