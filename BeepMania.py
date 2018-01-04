import time
import winsound
import re
from random import randint
import visa

import pymeasure
#keithley beep:

#self.write(f'beeper.beep({duration}, {frequency})')


#time of full note in ms
class Beeper(object):
    """
    Defines a class to provide a convienient way to play notes on a beeperfunction.
    Beeper gets constructed with myBeeper = Beep(tempo), where 'tempo' is an integer with the tempo in beats per minute.
    Songs with the format song = [[(int)octave, (str)note, (str)duration], [(int)octave, (str)note, (str)duration], ...] or song = (str)OctaveNoteDurationOctave... can be played using Beeper.play_song(song)
    Comes with 3 versions of tetris ('short', 'medium','long') and bigben as predefined songs.
    """

    def __init__(self, tempo, adress):
        self.adress = 'GPIB0::25::INSTR'
        self.tempo = tempo
        self._fullnotetime = int(60000/tempo)
        self.notes_dict = {"C":1, "CS":2, "DF":2, "D":3, "DS":4, "EF":4, "E":5, "FF":5, "F":6, "FS":7, "GF":7, "G":8, "GS":9, "AF":9, "A":10, "AS":11, "BF":11, "B":12,"BS":1, "CF":12, "P":0}
        self.durations_dict = {"F":self._fullnotetime, "H":self._fullnotetime/2, "Q":self._fullnotetime/4, "E":self._fullnotetime/8, "S":self._fullnotetime/16}

    def beepfcn(self, frequency, duration):
        """
        Defines the function generating the beep. Can be overwritten by child to feature a different beep source.
        :param frequency: Defines the Beep Frequency
        :param duration: Defines the Beep Duration
        """
        #winsound.Beep(frequency, duration)
        duration_sec = duration / 1000
        rm = visa.ResourceManager()
        smu = rm.open_resource(self.adress)
        smu.write('errorqueue.clear()')
        smu.write(f'beeper.beep({duration_sec}, {frequency})')

    def set_tempo(self, tempo):
        self.__init__(tempo)

    def change_tempo(self, change):
        new_tempo = self.tempo + int(change)
        self.set_tempo(new_tempo)

    def play(self, octave, note, duration):
        """
        Play a note with calculated frequency for a certain duration using the defined beepfcn.
        :param octave: The octave of the note. (Int) value is directly used.
        :param note: The name of the note. (str) value is used as key to look up the associated (int)
        :param duration: The duration of the note. (str) value used to determine the duration of the note, taking into account self._fullnotetime
        """
        if self.notes_dict[note] == 0:    # a pause
            time.sleep(self.get_duration(duration)/1000)
            return
        frequency = 32.7032           # C1
        for k in range(0, octave):    # compute C in given octave
            frequency *= 2
        for k in range(0, self.notes_dict[note]):      # compute frequency of given note
            frequency *= 1.059463094  # 1.059463094 = 12th root of 2
        time.sleep(0.0001*self._fullnotetime)             # delay between keys
        self.beepfcn(int(frequency), int(self.get_duration(duration)))

    def play_song(self, song):
        """
        Takes a nested list of triples (octave, note, duration) as input and plays the defined song.
        :param song: nested list with (int octave, str note, str duration)
        :return:
        """
        if type(song) is str:
            song = self.make_song(song)

        octaves, notes, durations = zip(*song)

        for i in range(0, len(octaves)):
            self.play(octaves[i], notes[i], durations[i])

    def get_duration(self, duration):
            value = 0
            if duration in self.durations_dict:
                value = self.durations_dict[duration]
            else:
                for character in duration:
                    if character not in self.durations_dict:
                        value = 0
                    else:
                        value += self.durations_dict[character]
                self.durations_dict[duration] = value
            return value

    def make_song(self, song_str):
        """
        Makes a valid 'song' nested list out of a simple string in the format "(octave)(note)(duration)(octave)..."
        :param song_str:
        :return:
        """

        duration_list = []
        note_list = []

        octave_list = re.findall('\d',song_str)
        octave_list = [int(i) for i in octave_list]
        characters = re.split('\d',song_str)
        characters.pop(0)

        for entry in characters:
            note_list.append(entry[:1])
            duration_list.append(entry[1:])

        return zip(octave_list, note_list, duration_list)

    def transpose_octave(self, song, change):
        if type(song) is str:
            song = self.make_song(song)
        octave_list, note_list, duration_list = zip(*song)
        octave_list = list(octave_list)
        for i, octave in enumerate(octave_list):
            octave_list[i] = octave + change
        return zip(octave_list, note_list, duration_list)

    def transpose_halftones(self, song, change):
        change = int(change)

        if type(song) is str:
            song = self.make_song(song)
        octave_list, note_list, duration_list = zip(*song)
        note_list = list(note_list)
        octave_list = list(octave_list)

        for i, note in enumerate(note_list):
            if note is not "P":
                current_note = self.notes_dict[note]
                new_note = current_note+change
                while new_note>12:
                        new_note = new_note-12
                        octave_list[i] = octave_list[i]+1
                while new_note <1:
                        new_note = new_note+12
                        octave_list[i] = octave_list[i]-1
                note_dict_key = next(note_dict_key for note_dict_key, value in self.notes_dict.items() if value == new_note)
                note_list[i] = note_dict_key

        return zip(octave_list, note_list, duration_list)

    ####################
    # predefined songs #
    ####################

    def play_tetris(self, length):

        song = "3EQ2BE3CE3DQ3CE2BE2AQ2AE3CE3EQ3DE3CE2BQE3CE3DQ3EQ3CQ2AQ"
        self.play_song(song)
        if length == "short":
            self.play(2, "A", "F")
        else:

            self.play(2, "A", "E")
            self.play(2, "A", "E")
            self.play(3, "C", "E")
            self.play(3, "D", "Q" + "E")
            self.play(3, "F", "E")
            self.play(3, "A", "Q")
            self.play(3, "G", "E")
            self.play(3, "F", "E")
            self.play(3, "E", "Q" + "E")
            self.play(3, "C", "E")
            self.play(3, "E", "Q")
            self.play(3, "D", "E")
            self.play(3, "C", "E")
            self.play(2, "B", "Q")
            self.play(2, "B", "E")
            self.play(3, "C", "E")
            self.play(3, "D", "Q")
            self.play(3, "E", "Q")
            self.play(3, "C", "Q")
            self.play(2, "A", "Q")
            self.play(2, "A", "Q")
            self.play(2, "P", "Q")
            if length == "long":
                self.play(3, "E", "H")
                self.play(3, "C", "H")
                self.play(3, "D", "H")
                self.play(2, "B", "H")
                self.play(3, "C", "H")
                self.play(2, "A", "H")
                self.play(2, "GS", "H")
                self.play(2, "B", "Q")
                self.play(2, "P", "Q")
                self.play(3, "E", "H")
                self.play(3, "C", "H")
                self.play(3, "D", "H")
                self.play(2, "B", "H")
                self.play(3, "C", "Q")
                self.play(3, "E", "Q")
                self.play(3, "A", "H")
                self.play(3, "GS", "H")
                self.play(3, "P", "H")

                self.play(3, "E", "Q")
                self.play(2, "B", "E")
                self.play(3, "C", "E")
                self.play(3, "D", "Q")
                self.play(3, "C", "E")
                self.play(2, "B", "E")
                self.play(2, "A", "Q")
                self.play(2, "A", "E")
                self.play(3, "C", "E")
                self.play(3, "E", "Q")
                self.play(3, "D", "E")
                self.play(3, "C", "E")
                self.play(2, "B", "Q" + "E")
                self.play(3, "C", "E")
                self.play(3, "D", "Q")
                self.play(3, "E", "Q")
                self.play(3, "C", "Q")
                self.play(2, "A", "Q")
                self.play(2, "A", "E")
                self.play(2, "A", "E")
                self.play(2, "A", "E")
                self.play(3, "C", "E")
                self.play(3, "D", "Q" + "E")
                self.play(3, "F", "E")
                self.play(3, "A", "Q")
                self.play(3, "G", "E")
                self.play(3, "F", "E")
                self.play(3, "E", "Q" + "E")
                self.play(3, "C", "E")
                self.play(3, "E", "Q")
                self.play(3, "D", "E")
                self.play(3, "C", "E")
                self.play(2, "B", "Q")
                self.play(2, "B", "E")
                self.play(3, "C", "E")
                self.play(3, "D", "Q")
                self.play(3, "E", "Q")
                self.play(3, "C", "Q")
                self.play(2, "A", "Q")
                self.play(2, "A", "F")

    def play_bigben(self):
        song = "4EH4CH4DH3GHQ3PQ3GH4DH4EH4CHQ4PF"
        self.play_song(song)

    def compose_random(self, length, quarters=True, pauses=False, rand_note=[], octave_start=2, octave_end=5):
        octaves =[]
        notes = []
        durations = []
        rand_note_dict = {}
        if len(rand_note) == 0:
            rand_note_dict = self.notes_dict
        # build rand note dictionnary
        else:
            for note_dict_key in rand_note:
                rand_note_dict[note_dict_key] = self.notes_dict[note_dict_key]

        for i in range(0,length):
            octave = randint(octave_start, octave_end)
            octaves.append(octave)


            note = randint(1, len(rand_note_dict))

            note_dict_key = next(note_dict_key for note_dict_key, value in self.notes_dict.items() if value == note)
            notes.append(note_dict_key)
            if quarters:
                durations.append("Q")
            else:
                duration = randint(1, 5)
                if duration == 1:
                    durations.append("F")
                elif duration == 2:
                    durations.append("H")
                elif duration == 3:
                    durations.append("Q")
                elif duration == 4:
                    durations.append("E")
                elif duration == 5:
                    durations.append("S")
        print(octaves)
        print(notes)
        print(durations)

        return(zip(octaves, notes, durations))


if __name__ == "__main__":

    myBeep = Beeper(40)

    myBeep.play_bigben()
    #song = "3EQ2BE3CE3DQ3CE2BE2AQ2AE3CE3EQ3DE3CE2BQE3CE3DQ3EQ3CQ2AQ2AQ"
    #myBeep.play_song(myBeep.transpose_octave(song,1))
    #myBeep.play_bigben()
    #for i in range(0,10):
     #   myBeep.change_tempo(20)
      #  song_transposed = myBeep.transpose_halftones(song2,-2*i)
       # myBeep.play_song(song_transposed)


