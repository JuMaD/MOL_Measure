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
from pymeasure.instruments.keithley import Keithley2400




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
    # TODO: Change constructor to be able to call MainWindow(Procedure, inputs, displays, x_axis, y_axis)
    def __init__(self):
        super(MainWindow, self).__init__(
            procedure_class=IVCycles,
            inputs=['averages', 'max_voltage', 'min_voltage', 'voltage_step', 'compliance', 'cycles'],
            displays=['averages', 'max_voltage', 'min_voltage', 'voltage_step', 'data_points', 'compliance'],
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
        queue_position = len(self.manager.experiments.queue) + 1
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
                    self.addItem(str(n) + "-" + str(instr) + "-" + str(idn))
            except visa.VisaIOError as e:
                print(n, ":", instr, ":", "Visa IO Error: check connections")
                print(e)

        rm.close()
        # Resize width and height
        self.resize(300, 120)
        self.setWindowTitle('Select Instrument')
        # connect click handle
        self.itemClicked.connect(self.Clicked)

    def Clicked(self, item):
        # pick instrument here!
        # split item.text() string into n,instr,idn again
        itemtext = item.text()
        n, instr, idn = itemtext.split('-')
        QMessageBox.information(self, "Instrument Selection",
                                "You clicked: \nitem\t\t" + n + "\nadress:\t\t" + instr + "\nidn:\t\t" + idn)


################
# Main Program #
################


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    # window = MainWindow()
    window = MainWindowRandom()
    window.show()
    # picker = InstrumentPicker()
    # picker.show()
    sys.exit(app.exec_())