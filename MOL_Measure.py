#  Import necessary packages
import re
import sys
import tempfile
import uuid
from time import sleep

import numpy as np
import visa
from PyQt5.QtWidgets import *

from pymeasure.display.Qt import QtGui
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter
from pymeasure.experiment import Procedure, Results
from pymeasure.instruments.keithley import Keithley2600AB


# TODO: make a dictionnary that stores instrument_adress:instrument_class pairs as attribute of Procedure and define __init__(instruments={}).
# That way, instruments become attributes of procedures and can _genrally_ be changed by other functions calling procedure.instruments[key]=value


##########################
# Measurement Procedures #
##########################
class IVCycles(Procedure):
    instrument_adress = "GPIB::25"

    # define measurement paramters here
    averages = IntegerParameter('Averages', default=50)
    measurement_delay = FloatParameter('Measurement Delay', default = 0.5)
    max_voltage = FloatParameter('Maximum Voltage', units='V', default=1)
    min_voltage = FloatParameter('Minimum Voltage', units='V', default=-1)
    compliance = FloatParameter('Compliance', units='A', default=0.1)
    cycles = IntegerParameter('No. of Cycles', default=1)
    voltage_step = FloatParameter('Voltage Step', units='V', default=0.1)

    #Add Comments as parameters to show up in measurement file
    operator = Parameter('Operator', default='JD')
    location = Parameter('Location', default='Mun')
    setup = Parameter('Setup',default='Probe Station')
    # Calculate the number of data points from range and step
    data_points = IntegerParameter('Data points',
                                   default=np.ceil((max_voltage.value - min_voltage.value) / voltage_step.value))

    # define DATA_COLUMNS that are written to the file
    DATA_COLUMNS = ['Voltage (V)', 'Current (A)', 'Current Std (A)', 'Cycle']



    def startup(self):
        #todo: Adjust this segment to Keithlex 2635B


        #Keithley 2600 version
        log.info("Connecting and configuring the instrument")
        log.info("Instrument Adress" + self.instrument_adress)

        self.sourcemeter = Keithley2600AB(self.instrument_adress)




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
        for i=1 to cycles:
            self.sourcemeter.sweep(start=0, stop=max_voltage, stime=measurement_delay, points=np.ceil(data_points/2), source='V')
            #wait for buffer?!?!?!
            self.sourcemeter.sweep(start=max_voltage, stop=min_voltage, stime=measurement_delay, points=data_points,
                                   source='V')
            # wait for buffer?!?!?!
            self.sourcemeter.sweep(start=min_voltage, stop=max_voltage, stime=measurement_delay, points=data_points,
                                   source='V')
            #wait for buffer?!
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
    read_delay = FloatParameter('WRITE-READ Delay', units='s', default = 1)
    cycles = IntegerParameter('#Cycles', default=1)
    DATA_COLUMNS = ['Voltage (V)', 'Current (A)', 'Current Std (A)', 'Cycle']

    def execute(self):

    def shutdown(self):
        self.sourcemeter.shutdown()
        log.info("Finished measuring")

class Endurance(Procedure):
    print('Placeholder')
    # define endurance measurements here


class SwitchingEnergy(Procedure):
    print('Placeholder')
    # define switching energy measurements here


class RandomProcedure(Procedure):
    iterations = IntegerParameter('Loop Iterations')
    delay = FloatParameter('Delay Time', units='s', default=0.2)
    seed = Parameter('Random Seed', default='12345')

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


############################
# Graphical User Interface #
############################

class MainWindow(ManagedWindow):
    # TODO: Change constructor to be able to call MainWindow(Procedure, inputs, displays, x_axis, y_axis), i.e. select the procedure on starup
    def __init__(self):
        super(MainWindow, self).__init__(
            procedure_class=IVCycles,
            inputs=['averages', 'max_voltage', 'min_voltage', 'voltage_step', 'compliance', 'cycles', 'operator', 'location', 'setup'],
            displays=['averages', 'max_voltage', 'min_voltage', 'voltage_step', 'data_points', 'compliance','operator','location', 'setup'],
            x_axis='Voltage (V)',
            y_axis='Current (A)'
        )
        self.setWindowTitle('Mol_measure 0.0.1')

    # override queue fuction of managed window that gets executed upon clicking on 'Queue'
    def queue(self):

        # create filename based on procedure name, position in queue and a unique identifier
        procedure_string = re.search("'(?P<name>[^']+)'",
                                     repr(self.procedure_class)).group("name")
        main_str, basename = procedure_string.split('.')
        queue_position = len(self.manager.experiments.queue)+1
        uidn = uuid.uuid4().clock_seq_hi_variant
        filename = f'{basename}-{queue_position}_{uidn}.csv'

        # construct a new instance of procedure and define datapoints
        procedure = self.make_procedure()
        procedure.data_points = np.ceil((procedure.max_voltage - procedure.min_voltage) / procedure.voltage_step)

        # construct a new instance of Results
        results = Results(procedure, filename)

        # construct new experiment (that contains the previously constructed procedure and results objects)
        experiment = self.new_experiment(results)

        # if its the first experiment don't start it right away
        if not self.manager.experiments.queue:
            self.manager._start_on_add = False
            self.manager._is_continuous = False
            self.manager.queue(experiment)

            # set the gui accordingly
            self.abort_button.setEnabled(False)
            self.abort_button.setText("Start")
            self.abort_button.clicked.disconnect()
            self.abort_button.clicked.connect(self.resume)
            self.abort_button.setEnabled(True)

        # add experiment to que
        else:
            self.manager.queue(experiment)


class MainWindowRandom(ManagedWindow):
    def __init__(self):
        super(MainWindowRandom, self).__init__(
            procedure_class=RandomProcedure,
            inputs=['iterations', 'delay', 'seed'],
            displays=['iterations', 'delay', 'seed'],
            x_axis='Iteration',
            y_axis='Random Number'
        )
        self.setWindowTitle('GUI Example')

    def queue(self):
        filename = tempfile.mktemp()

        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)


class InstrumentPicker(QListWidget):
    # initialize List and populate with visa instruments

    def __init__(self):
        super().__init__()
        # bring window to front
        self.raise_()

        rm = visa.ResourceManager()
        instrs = rm.list_resources()
        for n, instr in enumerate(instrs):
           # trying to catch errors in comunication
            try:
                res = rm.open_resource(instr)
                # try to avoid errors from *idn?
                try:
                    # noinspection PyUnresolvedReferences
                    idn = res.ask('*idn?')[:-1]
                except visa.Error:
                    idn = "Not known"
                finally:
                    res.close()
                    self.addItem(str(n)+"-"+str(instr)+"-"+str(idn))
            except visa.VisaIOError as e:
                print(n, ":", instr, ":", "Visa IO Error: check connections")
                print(e)

        rm.close()
        # Resize width and height
        self.resize(300,120)
        self.setWindowTitle('Select Instrument')
        # connect click handle
        self.itemClicked.connect(self.Clicked)


    def Clicked(self,item):
        # pick instrument here!
        # split item.text() string into n,instr,idn again
        itemtext = item.text()
        n, instr, idn = itemtext.split('-')
        QMessageBox.information(self, "Instrument Selection", "You clicked: \nitem\t\t"+n+"\nadress:\t\t"+instr+"\nidn:\t\t"+idn)


################
# Main Program #
################


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # picker = InstrumentPicker()
    # picker.show()
    sys.exit(app.exec_())