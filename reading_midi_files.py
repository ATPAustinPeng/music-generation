from mido import MidiFile
import numpy as np

# reads midi file
mid = MidiFile('freddie_transcription_no_chords.mid', clip=True)
print(mid)  # prints info about the midi file

# prints all tracks of midi file
'''
for track in mid.tracks:
    print(track)
'''
# meta messages = specific info about track


### converting each message to string
def convertMessagesToListOfStrings(tracks, track_index):
    list_of_strings = []
    for msg in tracks[track_index]:
        list_of_strings.append(str(msg))
    return list_of_strings

list_of_all_messages = convertMessagesToListOfStrings(mid.tracks,0)
print(list_of_all_messages)

### removing <meta message>, control_change, and program_change
def removeUselessStuff(messy_list):
    clean_list = []
    for item in messy_list:
        if not "meta message" in item and not "control_change" in item and not "program_change" in item:
            clean_list.append(item)
    return clean_list

list_of_messages = removeUselessStuff(list_of_all_messages)
print(list_of_messages)

### creating the "note" class
class Note:
    def __init__(self, string):
        info_in_list = string.split()
        self.status = info_in_list[0]  # important
        self.channel = info_in_list[1]
        self.note = int(info_in_list[2].replace("note=",""))  # important
        self.velocity = int(info_in_list[3].replace("velocity=",""))
        self.time = int(info_in_list[4].replace("time=",""))  # important


### Converting all messages into the note class
### and appending them to a list with status, note value, and time.
notes_list = []

for message in list_of_messages:
    note_temp = Note(message)
    if note_temp.velocity == 0:  # all note_on with velocity 0 is turned into note_off
        note_temp.status = "note_off"
    notes_list.append((note_temp.status, note_temp.note, note_temp.time))

print(notes_list)  # (status, value, time)


# transforming into note blocks
current_note = 0
for note in notes_list:
    current_note = note[1]




# converting into numpy arrays



