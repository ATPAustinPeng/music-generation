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
### and appending them to a numpy array with status, note value, and time.

notes_list = np.zeros([1,3])

for message in list_of_messages:
    note_temp = Note(message)
    if note_temp.velocity == 0:  # all note_on with velocity 0 is turned into note_off
        note_temp.status = "note_off"
    if note_temp.status == "note_on":
        note_temp.status = 1
    elif note_temp.status == "note_off":
        note_temp.status = 0
    to_append = [note_temp.status, note_temp.note, note_temp.time]
    notes_list = np.vstack((notes_list, to_append))

# notes_list is now in (status, value, time) format.

# transforming time into start_time by adding up all the times that came before
total_time = 0
for note in notes_list:
    total_time += note[2]
    note[2] = total_time

print(notes_list)

# puts into note blocks [pitch, start time, end time]

note_blocks = np.zeros([1,3])
for index, note in enumerate(notes_list):
    if note[0] == 1:
        pitch = note[1]
        start_time = note[2]
        i = 0
        while True:
            current_status = notes_list[i][0]
            current_pitch = notes_list[i][1]
            if current_status == 0 and current_pitch == pitch:
                end_time = notes_list[i][2]
                to_append1 = [pitch, start_time, end_time]
                note_blocks = np.vstack((note_blocks, to_append1))
                break
            i += 1

print(note_blocks)
