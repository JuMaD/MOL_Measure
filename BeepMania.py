import time
import winsound

#time of full note in ms
_fullnotetime = 800

# the notes
P = 0   # pause
C = 1
CS = 2  # C sharp
D = 3
DS = 4
E = 5
F = 6
FS = 7
G = 8
GS = 9
A = 10
AS = 11
B = 12
# enharmonics
CF = B
DF = CS
EF = DS
FF = E
GF = FS
AF = GS
BF = AS
#durations
FN = _fullnotetime   #full note
EN = FN/8   #eighth note
QN = FN/4   #quarter note
HN = FN/2   #half note


def play(octave, note, duration):
    """play note (C=1 to B=12), in octave (1-8), and duration (msec)"""
    if note == 0:    # a pause
        time.sleep(duration/1000)
        return
    frequency = 32.7032           # C1
    for k in range(0, octave):    # compute C in given octave
        frequency *= 2
    for k in range(0, note):      # compute frequency of given note
        frequency *= 1.059463094  # 1.059463094 = 12th root of 2
    time.sleep(0.0001*_fullnotetime)             # delay between keys
    winsound.Beep(int(frequency), int(duration))

def bigben():
    play(4,E,HN)
    play(4,C,HN)
    play(4,D,HN)
    play(3,G,HN+QN); play(3,P,QN)
    play(3,G,HN)
    play(4,D,HN)
    play(4,E,HN)
    play(4,C,HN+QN)

bigben()