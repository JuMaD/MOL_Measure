import visa
import pymeasure
from pymeasure.instruments.keithley import Keithley2600
from time import sleep
import numpy as np


smu = Keithley2600('GPIB0::25::INSTR')
#smu.triad()
#smu.set_screentext('$R PulseIVCycle $N$B Ready to measure')
#sleep(2)
#smu.smu_screen()
#smu.set_buffer_ascii()


smu.write('*CLS')
print('STB  '+str(smu.ask('*STB?')))

smu.write("*SRE 1")
print('SRE  '+str(smu.ask('*SRE?')))

smu.write('status.measurement.enable = status.measurement.BAV')
print('SME  '+str(smu.ask('print(status.measurement.enable)')))

smu.auto_sweep(start=0, stop=1, stime=0.010, points=2, keyword='lin')
smu.wait_for_buffer()
print('Done')
#smu.adapter.wait_for_srq()


#n_array = smu.get_buffer_data()
#print(n_array)

