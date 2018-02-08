#  Import necessary packages
import logging
import random
from time import sleep

import numpy as np

from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter
from pymeasure.experiment import Procedure
from pymeasure.instruments.keithley import Keithley2600

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


##########
# global #
##########


##########################
# Pre-Defined Procedures #
##########################

# todo: Define Standard Procedures

###########################
# User-Defined Procedures #
###########################
# Todo: Write Sweep Procedure
# Todo: Write Cycle Procedure
# Todo: Write Pulse Procedure (Just factory script)
# Todo: Write Pulse Procedure (write Pulse, read cycle)
# Todo: Write Retention Procedure
# Todo: Write Endurance Procedure

class ProcedureWithInstruments(Procedure):
    """Class that adds a dict of instruments to Procedure. SelectionWindow uses this dict to pass
    user selected, connected devices (names & adresses)"""
    def __init__(self, instruments_dict={}):
        Procedure.__init__(self)
        instrument_adress = ''


class IVCycles(ProcedureWithInstruments):

    #define required instruments
    required_instruments = ['Keithley Instruments Inc., Model 2635B']

    # define measurement paramters here
    averages = IntegerParameter('Averages', default=50)
    measurement_delay = FloatParameter('Measurement Delay', default=0.5)
    max_voltage = FloatParameter('Maximum Voltage', units='V', default=0.5)
    min_voltage = IntegerParameter('Minimum Voltage', units='V', default=-1.0)
    compliance = FloatParameter('Compliance', units='A', default=0.1)
    cycles = IntegerParameter('No. of Cycles', default=1)
    voltage_step = FloatParameter('Voltage Step', units='V', default=0.1)


    # Add Comments as parameters to show up in measurement file
    operator = Parameter('Operator', default='JD')
    location = Parameter('Location', default='Mun')
    setup = Parameter('Setup', default='Probe Station')

    # Calculate the number of data points from range and step
    data_points = IntegerParameter('Data points',
                                   default=np.ceil((max_voltage.value - min_voltage.value) / voltage_step.value))

    # define DATA_COLUMNS that are written to the file
    DATA_COLUMNS = ['Voltage (V)', 'Current (A)']

    def startup(self):
        print('startup')
        for adress,name in self.instruments_dict.items():
            if 'Keithley Instruments Inc., Model 2635B' in name:
                self.instrument_adress = adress
        log.info("Connecting and configuring the instrument")
        log.info("Instrument Adress: " + self.instrument_adress)
        log.info("Instrument Dict: " + str(self.instruments_dict))
        self.sourcemeter = Keithley2600(self.instrument_adress)
        #self.sourcemeter.triad()
        self.sourcemeter.set_screentext('$R PulseIVCycle $N$B Ready to measure')

    def execute(self):
        print('execute')
        # reset instrument and its dedicated buffer
        self.sourcemeter.reset()
        self.sourcemeter.clear_buffer()
        self.sourcemeter.setup_buffer(precision=6)
        log.info(f'start: {self.min_voltage}. stop {self.max_voltage}, stime {self.measurement_delay}. points = {self.data_points}')

        self.sourcemeter.set_output(state='ON')
        self.sourcemeter.auto_sweep(start=0, stop=self.max_voltage, stime=self.measurement_delay, points=np.ceil(self.data_points / 2 +1),
                                   source='V')
        self.sourcemeter.wait_for_srq()
        results = self.sourcemeter.get_buffer_data()
        for i in range(0, len(results['sourced']) - 1):
            self.emit('results',
                      {
                          'Voltage (V)': results['sourced'][i],
                          'Current (A)': results['measured'][i],
                      })

    def shutdown(self):
        self.sourcemeter.shutdown()
        log.info("Finished measuring")
        print('shutdown')

class PulseIVCycle(ProcedureWithInstruments):
    """
    Uses a Keithley 26XX device to perform the following measurement:
    1. Pulse at voltage `pulse_voltage` for `pulse_duration` in ms
    2. Perform `cycles` sweeps from `min_voltage` to `max_voltage` starting with a sweep from 0 to max and ending with a sweep from max to 0
    """

    # define measurement paramters here
    max_voltage = FloatParameter('Maximum Voltage', units='V', default=1)
    min_voltage = FloatParameter('Minimum Voltage', units='V',
                                   default=-1)
    compliance = FloatParameter('Compliance', units='A', default=0.1)
    cycles = IntegerParameter('No. of Cycles', default=1)
    voltage_step = FloatParameter('Voltage Step', units='V', default=0.1)
    stime = FloatParameter('Settling Time', units='s', default=0.5)

    # Add Comments as parameters to show up in measurement file
    operator = Parameter('Operator', default='JD')
    location = Parameter('Location', default='Mun')
    setup = Parameter('Setup', default='Probe Station')

    # define DATA_COLUMNS that are written to the file
    DATA_COLUMNS = ['Voltage (V)', 'Current (A)', 'Current Std (A)', 'Cycle']

    def startup(self):
        # System startup: Build instances of all necessary device objects here
        log.info("Connecting and configuring the instrument")
        log.info("Instrument Adress" + instrument_adress)
        self.sourcemeter = Keithley2600(instrument_adress)
        self.sourcemeter.reset()
        self.sourcemeter.clear_buffer()
        self.sourcemeter.triad()
        self.sourcemeter.set_screentext('$R PulseIVCycle $N$B Ready to measure')

    def execute(self):
        # Make Pulse

        # Make Sweep
        log.info("Starting sweep")
        steps = (self.max_voltage - self.min_voltage) / self.voltage_step
        self.sourcemeter.autosweep(0, self.max_voltage, self.stime, steps, 'lin', 'V')
        for i in cycles:
            if self.should_stop():
                log.info("User aborted the procedure")
                break
            log.info(f"Performing sweep number {i}")
            self.soucemeter.autosweep(self.max_voltage, self.min_voltage, self.stime, steps, 'lin', 'V')
            # TODO:Wait for finished measurement?!
            self.soucemeter.autosweep(self.min_voltage, self.max_voltage, self.stime, steps, 'lin', 'V')
            # TODO:Wait for finished measurement?!
        else:
            self.sourcemeter.autosweep(self.max_voltage, 0, self.stime, steps, 'lin', 'V')
            # TODO:Wait for finished measurement?!

        data_array = self.sourcemeter.get_buffer_data()

        # print to console to check array
        print(data_array)
        # emit data
        for i in range(0, len(data_array) - 1):
            self.emit('results',
                      {
                          'Voltage (V)': data_array[0][i],
                          'Current (A)': data_array[1][i],
                          'Voltage Std (V)': data_array[2][i]
                      })

    def shutdown(self):
        self.sourcemeter.shutdown()

class Retention(ProcedureWithInstruments):
    # retention here
    # paramet


    averages = IntegerParameter('Averages', default=50)
    set_voltage = FloatParameter('SET Voltage', units='V', default=1)
    read_voltage = FloatParameter('READ Voltage', units='V', default=1)
    set_duration = FloatParameter('Duration SET Pulse', units='ms', default=1)
    read_duration = FloatParameter('Duration READ Pulse', units='ms', default=1)
    read_delay = FloatParameter('WRITE-READ Delay', units='s', default=1)
    cycles = IntegerParameter('#Cycles', default=1)
    DATA_COLUMNS = ['Voltage (V)', 'Current (A)', 'Current Std (A)', 'Cycle']

    def execute(self):
        log.info("Retention Procedure Running")

    def shutdown(self):
        self.sourcemeter.shutdown()
        log.info("Finished measuring")

class RandomProcedure(ProcedureWithInstruments):
    iterations = IntegerParameter('Loop Iterations')
    delay = FloatParameter('Delay Time', units='s', default=0.2)
    seed = Parameter('Random Seed', default='12345')
    negNumber = IntegerParameter('Number', default=-1)

    DATA_COLUMNS = ['Iteration', 'Random Number']

    def startup(self):
        log.info("Setting the seed of the random number generator")
        log.info("Connected Instruments:"+str(self.instruments_dict))
        random.seed(self.seed)

    def execute(self):
        log.info("Starting the loop of %d iterations" % self.iterations)
        for i in range(self.iterations):
            data = {
                'Iteration': i,
                'Random Number': random.random()
            }
            self.emit('results', data)
            log.debug("Emitting results: %s" % data)
            sleep(self.delay)
            if self.should_stop():
                log.warning("Caught the stop flag in the procedure")
                break
