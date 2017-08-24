import time
import winsound
import re
#time of full note in ms
class Beeper(object):
    """
    Defines a class to provide a convienient way to play notes on a beeperfunction.
    Beeper gets constructed with myBeeper = Beep(tempo), where 'tempo' is an integer with the tempo in beats per minute.
    Songs with the format song = [[(int)octave, (str)note, (str)duration], [(int)octave, (str)note, (str)duration], ...] can be played using Beeper.play_song(song)
    Comes with 3 versions of tetris ('short', 'medium','long') and bigben as predefined songs.
    """

    def __init__(self, tempo):
        self._fullnotetime = 60000/tempo
        self.notes_dict = {"C":1, "CS":2, "DF":2, "D":3, "DS":4, "EF":4, "E":5, "FF":5, "F":6, "FS":7, "GF":7, "G":8, "GS":9, "AF":9, "A":10, "AS":11, "BF":11, "B":12,"BS":1, "CF":12, "P":0}
        self.durations_dict = {"F":self._fullnotetime, "H":self._fullnotetime/2, "Q":self._fullnotetime/4, "E":self._fullnotetime/8, "S":self._fullnotetime/16}



    def beepfcn(self, frequency, duration):
        """
        Defines the function generating the beep. Can be overwritten by child to feature a different beep source.
        :param frequency: Defines the Beep Frequency
        :param duration: Defines the Beep Duration
        """
        winsound.Beep(frequency, duration)
    def play(self, octave, note, duration):
        """
        Play a note with calculated frequency for a certain duration using the defined beepfcn.
        :param octave: The octave of the note. (Int) value is directly used.
        :param note: The name of the note. (str) value is used as key to look up the associated (int)
        :param duration: The duration of the note. (str) value used to determine the duration of the note, taking into account _fullnotetime
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


    ####################
    # predefined songs #
    ####################
    def play_tetris(self, length):
        self.play(3,"E","Q")
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
        self.play(2, "B", "Q"+"E")
        self.play(3, "C", "E")
        self.play(3, "D", "Q")
        self.play(3, "E", "Q")
        self.play(3, "C", "Q")
        self.play(2, "A", "Q")
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



myBeep = Beeper(60)
#myBeep.play_bigben(1)
song = [(4, 'E', 'H'), (4, 'E', 'H'), (4, 'E', 'H')]
song2 = "4EH4EH4EH4EH4EH"
notes = "1PQ2EQ1PQ1BE1PE2CE1PE2DQ"
myBeep.play_song(song2)