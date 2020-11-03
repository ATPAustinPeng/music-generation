# imports
from music21 import *
import os
import numpy as np
from collections import Counter
import random

from sklearn.model_selection import train_test_split

from keras.layers import *
from keras.models import *
from keras.callbacks import *
import keras.backend as K

# from keras.models import load_model

# library for visualiation
import matplotlib.pyplot as plt


# SOURCE : https://www.analyticsvidhya.com/blog/2020/01/how-to-perform-automatic-music-generation/
# GET CLASSICAL MUSIC: http://www.piano-midi.de/chopin.htm

def main():
    # path = os.getcwd() + "/resources/chopin/prelude"
    path = os.getcwd() + "/resources/chopin/etude-op25"

    # read all the filenames
    files = [i for i in os.listdir(path) if i.endswith(".mid")]

    # reading each midi file
    notes_array = np.array([read_midi(path + "/" + i) for i in files])

    notes = list()

    # converting 2D array into 1D array
    for note in notes_array:
        for element in note:
            notes.append(element)
    # notes_ = [element for note_ in notes_array for element in note_]

    # No. of unique notes
    unique_notes = list(set(notes))
    print(len(unique_notes))

    # computing frequency of each note
    freq = dict(Counter(notes))

    # consider only the frequencies
    no = [count for _, count in freq.items()]

    # set the figure size
    plt.figure(figsize=(5, 5))

    # plot
    plt.hist(no)
    # plt.show()

    # find the more frequent notes (excluding the very common ones)
    frequent_notes = notes
    # frequent_notes = [note for note, count in freq.items() if count >= 50]
    print(len(frequent_notes))

    # preparing music file with only the top frequent notes
    new_music = []

    for notes in notes_array:
        temp = []
        for note_ in notes:
            if note_ in frequent_notes:
                temp.append(note_)
        new_music.append(temp)

    new_music = np.array(new_music)


    # preparing the input and output sequences as mentioned in the article
    no_of_timesteps = 32
    x = []
    y = []

    for note_ in new_music:
        for i in range(0, len(note_) - no_of_timesteps, 1):
            # preparing input and output sequences
            input_ = note_[i:i + no_of_timesteps]
            output = note_[i + no_of_timesteps]

            x.append(input_)
            y.append(output)

    x = np.array(x)
    y = np.array(y)


    # assigning a unique integer to each note
    unique_x = list(set(x.ravel()))
    x_note_to_int = dict((note, number) for number, note in enumerate(unique_x))


    # prepare integer sequences for input data
    # preparing input sequences
    x_seq = []
    for i in x:
        temp = []
        for j in i:
            # assigning unique integer to every note
            temp.append(x_note_to_int[j])
        x_seq.append(temp)

    x_seq = np.array(x_seq)


    # preparing integer sequences for output data
    unique_y = list(set(y))
    y_note_to_int = dict((note_, number) for number, note_ in enumerate(unique_y))
    y_seq = np.array([y_note_to_int[i] for i in y])


    # use 80% of data for training
    x_tr, x_val, y_tr, y_val = train_test_split(x_seq, y_seq, test_size=0.2, random_state=0)


    # using keras
    K.clear_session()
    model = Sequential()

    # embedding layer
    model.add(Embedding(len(unique_x), 100, input_length=32, trainable=True))

    model.add(Conv1D(64, 3, padding='causal', activation='relu'))
    model.add(Dropout(0.2))
    model.add(MaxPool1D(2))

    model.add(Conv1D(128, 3, activation='relu', dilation_rate=2, padding='causal'))
    model.add(Dropout(0.2))
    model.add(MaxPool1D(2))

    model.add(Conv1D(256, 3, activation='relu', dilation_rate=4, padding='causal'))
    model.add(Dropout(0.2))
    model.add(MaxPool1D(2))

    # model.add(Conv1D(256,5,activation='relu'))
    model.add(GlobalMaxPool1D())

    model.add(Dense(256, activation='relu'))
    model.add(Dense(len(unique_y), activation='softmax'))

    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam')

    model.summary()



    # define the callback to save the best model during training:
    mc = ModelCheckpoint('best_model.h5', monitor='val_loss', mode='min', save_best_only=True, verbose=1)


    # define the callback to save the best model during training:
    history = model.fit(np.array(x_tr), np.array(y_tr), batch_size=128, epochs=50,
                        validation_data=(np.array(x_val), np.array(y_val)), verbose=1, callbacks=[mc])

    # loading best model
    model = load_model('best_model.h5')





    # composing music
    ind = np.random.randint(0, len(x_val) - 1)

    random_music = x_val[ind]

    predictions = []
    for i in range(10):
        random_music = random_music.reshape(1, no_of_timesteps)

        prob = model.predict(random_music)[0]
        y_pred = np.argmax(prob, axis=0)
        predictions.append(y_pred)

        random_music = np.insert(random_music[0], len(random_music[0]), y_pred)
        random_music = random_music[1:]

    print(predictions)



    # converting integers to notes
    x_int_to_note = dict((number, note_) for number, note_ in enumerate(unique_x))
    predicted_notes = [x_int_to_note[i] for i in predictions]



    # converting notes to midi
    convert_to_midi(predicted_notes)

def read_midi(file_path):
    print("parsing: " + file_path)

    notes = list()

    # parse midi file
    midi = converter.parse(file_path)
    instruments = instrument.partitionByInstrument(midi)

    for part in instruments:
        # if part is piano, read the notes
        if 'Piano' in str(part):
            notes_to_parse = part.recurse()

            # finding whether a particular element is note or a chord
            for i in notes_to_parse:

                # note
                if isinstance(i, note.Note):
                    notes.append(str(i.pitch))

                # chord
                elif isinstance(i, chord.Chord):
                    notes.append('.'.join(str(n) for n in i.normalOrder))

    # print(np.array(notes))
    return np.array(notes)

# build lstm model
def lstm():
  model = Sequential()
  model.add(LSTM(128,return_sequences=True))
  model.add(LSTM(128))
  model.add(Dense(256))
  model.add(Activation('relu'))
  model.add(Dense(n_vocab))
  model.add(Activation('softmax'))
  model.compile(loss='sparse_categorical_crossentropy', optimizer='adam')
  return model

# converting notes to midi
def convert_to_midi(prediction_output):

    offset = 0
    output_notes = []

    # create note and chord objects based on the values generated by the model
    for pattern in prediction_output:

        # pattern is a chord
        if ('.' in pattern) or pattern.isdigit():
            notes_in_chord = pattern.split('.')
            notes = []
            for current_note in notes_in_chord:
                cn = int(current_note)
                new_note = note.Note(cn)
                new_note.storedInstrument = instrument.Piano()
                notes.append(new_note)

            new_chord = chord.Chord(notes)
            new_chord.offset = offset
            output_notes.append(new_chord)

        # pattern is a note
        else:

            new_note = note.Note(pattern)
            new_note.offset = offset
            new_note.storedInstrument = instrument.Piano()
            output_notes.append(new_note)

        # increase offset each iteration so that notes do not stack
        offset += 1
    midi_stream = stream.Stream(output_notes)
    midi_stream.write('midi', fp='music.mid')

if __name__ == '__main__':
    main()
