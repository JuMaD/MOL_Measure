import visa
import pymeasure
from pymeasure.instruments.keithley import Keithley2600
from time import sleep
import numpy as np


smu = Keithley2600('GPIB0::26::INSTR')
#smu.triad()
#smu.set_screentext('$R PulseIVCycle $N$B Ready to measure')
#sleep(2)
#smu.smu_screen()
#smu.set_buffer_ascii()


smu.write('*CLS')
smu.clear_buffer()
smu.set_buffer_ascii()
smu.auto_sweep(start=0, stop=3, stime=0.010, points=10, keyword='lin')
smu.wait_for_srq()
smu.triad()
print(smu.get_buffer_data())
print('Done')
#smu.adapter.wait_for_srq()


#n_array = smu.get_buffer_data()
#print(n_array)

