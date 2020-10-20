from mido import MidiFile
import pandas as pd

mid = MidiFile('Naruto.mid', clip=True)

def convertMessageToStr(tracks, track_index): 
    list_of_strings = []
    for msg in tracks[track_index]: 
        list_of_strings.append(str(msg)) 
    return list_of_strings

StartList = (convertMessageToStr(mid.tracks, 1))

def removeUselessInfo(messy_list):
    clean_list = []
    for item in messy_list:
        if not "meta message" in item and not "control_change" in item and not "program_change" in item:
            clean_list.append(item)
    return clean_list

StandardList = removeUselessInfo(StartList)


def makeCleanList(messy_list):
    newList = []
    for note in messy_list:
        info_in_list = note.split()
        status = info_in_list[0] 
        note = int(info_in_list[2].replace("note=",""))
        velocity = int(info_in_list[3].replace("velocity=",""))
        time = int(info_in_list[4].replace("time=",""))
        newList.append((note, velocity, time))
    return newList

def makeDataFrame(cleanList):
     note = []
     velocity = []
     time = []
     for i in cleanList:
        note.append(i[0])
        velocity.append(i[1])
        time.append(i[2])
    
     newList = {'Note': note,'Velocity': velocity,'Time': time}
     df = pd.DataFrame(newList, columns = ['Note', 'Velocity', 'Time'])
     return df
    
cleanList = makeCleanList(StandardList)

dataf = makeDataFrame(cleanList)
        
print(dataf)



