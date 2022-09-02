#==================================================================================================================
#  THIS FILE GOES THROUGH THE PROGRAM FILES AND STORES FILES WITH A .EXE IN A TXT FOLDER
#==================================================================================================================

#==================================================================================================================
#                                               SETUP
#==================================================================================================================

import os
import glob
from os import walk

#==================================================================================================================
#                                               VARIABLES
#==================================================================================================================

files = []

#==================================================================================================================
#                                               FUNCTIONS
#==================================================================================================================

def nested_file_searcher(path):
    f = []
    d = []
    #STORE ALL FOLDERS AND FILES IN ORIGINAL PATH
    for (dirpath, dirnames, filenames) in walk(path):
        d.extend(dirnames)
        files.extend(filenames)
        break
    if(d): #if there are still folders in this directory
        #Turn the list of directories into a list of paths
        for x in range(0, len(d)): 
            d[x] = dirpath + "\\" + d[x] + "\\"
        for x in d:
            nested_file_searcher(x)

#After all the files have been found, go through them and eliminate any that don't contain .exe
def eliminator():
    apps = []
    for f in files:
        if f[-4:]==".exe":
            if f not in apps:
                apps.append(f)
    return apps

def update_apps(apps):
    #Pull all the past apps from storage file
    existing_apps = []
    applist = open(r"C:\Program Files\AudioMixer\Data\Master List.txt", "r")
    #Store them in list
    for line in applist:
        if line != "\n":
            existing_apps.append(line[:-1])
    applist.close()
    applist = open(r"C:\Program Files\AudioMixer\Data\Master List.txt", "w")
    
    #If the current app list does not contain something from the past app list, it will add it
    for i in apps:
        if i not in existing_apps:
            existing_apps.append(i)
    
    existing_apps.sort()

    for i in existing_apps:
        applist.write(i + "\n")
    applist.close()

def main():
    path = "C:\\"
    #Setup list to stores files and folders found
    nested_file_searcher(path)
    apps = eliminator()
    update_apps(apps)

#==================================================================================================================
#                                               MAIN
#==================================================================================================================

if __name__ == "__main__":
    main()