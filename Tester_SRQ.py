
from pymeasure.instruments.keithley import Keithley2600

smu = Keithley2600('GPIB0::26::INSTR')

smu.write('*CLS')
smu.beep(440,0.2)
smu.beep(440,0.2)
smu.beep(440,0.8)
#smu.setup_buffer(precision=7)
smu.set_integration_time(20)
smu.write('nplc = smua.measure.nplc')
print(smu.write('print(nplc)'))

#smu.auto_sweep(start=1, stop=10, stime=0.0010, points=5, keyword='log')
#smu.wait_for_srq()
#smu.triad()
#print('Measurement Done')

#n_array = smu.get_buffer_data()
#print('Results:')
#print(n_array)

