#  Import necessary packages
import random
from time import sleep

import numpy as np

from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter
from pymeasure.experiment import Procedure
from pymeasure.instruments.keithley import Keithley2600


##########################
# Pre-Defined Procedures #
##########################

# todo: Define Standard Procedures

###########################
# User-Defined Procedures #
###########################

class PulseIVCycle(Procedure):
    """
    Uses a Keithley 26XX device to perform the following measurement:
    1. Pulse at voltage `pulse_voltage` for `pulse_duration` in ms
    2. Perform `cycles` sweeps from `min_voltage` to `max_voltage` starting with a sweep from 0 to max and ending with a sweep from max to 0
    """
    instrument_adress = "GPIB::25"
    # define measurement paramters here
    max_voltage = FloatParameter('Maximum Voltage', units='V', default=1)
    min_voltage = IntegerParameter('Minimum Voltage', units='V',
                                   default=-1)  # todo: change to FloatParameter once FloatParameter accepts negative values
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
        log.info("Instrument Adress" + self.instrument_adress)
        self.sourcemeter = Keithley2600(self.instrument_adress)
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


# Execute Script here

class IVCycles(Procedure):
    instrument_adress = "GPIB::25"
    # define measurement paramters here
    averages = IntegerParameter('Averages', default=50)
    measurement_delay = FloatParameter('Measurement Delay', default=0.5)
    max_voltage = FloatParameter('Maximum Voltage', units='V', default=1)
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
    DATA_COLUMNS = ['Voltage (V)', 'Current (A)', 'Current Std (A)', 'Cycle']

    def startup(self):
        # todo: Adjust this segment to Keithlex 2635B


        # Keithley 2600 version
        log.info("Connecting and configuring the instrument")
        log.info("Instrument Adress" + self.instrument_adress)

        sourcemeter = Keithley2600(self.instrument_adress)

    def execute(self):
        # reset instrument and its dedicated buffer
        self.sourcemeter.reset()
        self.sourcemeter.clear_buffer()

        # set to source V via smua and set buffer precision to 6
        self.sourcemeter.set_output_fcn('suma', 'V')
        self.sourcemeter.set_buffer_ascii(6)

        # execute TSP script with "setup" functions and enable direct execution for cycles
        self.sourcemeter.execute_script()
        self.sourcemeter.start_on_call = True
        # todo: make cycles from sweeps and use input parameters
        for i in range(1, cycles):
            self.sourcemeter.sweep(start=0, stop=max_voltage, stime=measurement_delay, points=np.ceil(data_points / 2),
                                   source='V')
            # wait for buffer?!?!?!
            self.sourcemeter.sweep(start=max_voltage, stop=min_voltage, stime=measurement_delay, points=data_points,
                                   source='V')
            # wait for buffer?!?!?!
            self.sourcemeter.sweep(start=min_voltage, stop=max_voltage, stime=measurement_delay, points=data_points,
                                   source='V')
            # wait for buffer?!
            results = self.sourcemeter.read_buffer()

            # emit results after each full cycle:loop through voltages and use self.emit together with self.sourcemeter.means *.standard_devs and cycle number

        voltages = np.linspace(
            self.min_voltage.value,
            self.max_voltage.value,
            num=self.data_points.value
        )
        # Loop through cycles
        for cycle in xrange(cycles.value):
            # Loop through each voltage point, measure and record the current
            for voltage in voltages:
                log.info("Setting the voltage to %g V" % voltage)
                self.sourcemeter.source_voltage = voltage

                self.sourcemeter.reset_buffer()
                sleep(0.1)
                self.sourcemeter.start_buffer()
                log.info("Waiting for the buffer to fill with measurements")
                self.sourcemeter.wait_for_buffer()
                self.emit('results', {
                    'Current (A)': self.sourcemeter.means,
                    'Voltage (V)': voltage,
                    'Current Std (A)': self.sourcemeter.standard_devs,
                    'Cycle': i
                })
                sleep(0.01)
                if self.should_stop():
                    log.info("User aborted the procedure")
                    break

    def shutdown(self):
        self.sourcemeter.shutdown()
        log.info("Finished measuring")


class Retention(Procedure):
    # retention here
    # paramet

    instrument_adress = "GPIB::4"
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


class Endurance(Procedure):
    print('Endurance Placeholder')
    # define endurance measurements here


class SwitchingEnergy(Procedure):
    print('Switching Energy Placeholder')
    # define switching energy measurements here


class RandomProcedure(Procedure):
    iterations = IntegerParameter('Loop Iterations')
    delay = FloatParameter('Delay Time', units='s', default=0.2)
    seed = Parameter('Random Seed', default='12345')
    negNumber = IntegerParameter('Number', default=-1)

    DATA_COLUMNS = ['Iteration', 'Random Number']

    def startup(self):
        log.info("Setting the seed of the random number generator")
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
