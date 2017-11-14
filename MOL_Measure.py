#  Import necessary packages
# Connect to Log
import logging
import re
import sys
import uuid

import visa
from PyQt5.QtWidgets import *

from measurement_procedures import *
from pymeasure.display.Qt import QtGui
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# TODO: make a dictionnary that stores instrument_adress:instrument_class pairs as attribute of Procedure and define __init__(instruments={}).
# That way, instruments become attributes of procedures and can _genrally_ be changed by other functions calling procedure.instruments[key]=value


##########################
# Measurement Procedures #
##########################





############################
# Graphical User Interface #
############################

class MainWindow(ManagedWindow):
    # overload kwargs to be able to dynamically call MainWindow(kwargs)
    def __init__(self, procedure_class=IVCycles,
                 inputs=['averages', 'max_voltage', 'min_voltage', 'voltage_step', 'compliance', 'cycles', 'operator',
                         'location',
                         'setup'],
                 displays=['averages', 'max_voltage', 'min_voltage', 'voltage_step', 'data_points', 'compliance',
                           'operator',
                           'location', 'setup'],
                 x_axis='Voltage (V)',
                 y_axis='Current (A)'):
        super(MainWindow, self).__init__(
            procedure_class=procedure_class,
            inputs=inputs,
            displays=displays,
            x_axis=x_axis,
            y_axis=y_axis
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
            inputs=['iterations', 'delay', 'seed', 'negNumber'],
            displays=['iterations', 'delay', 'seed', 'negNumber'],
            x_axis='Iteration',
            y_axis='Random Number'
        )
        self.setWindowTitle('GUI Example')


    def queue(self):
        # create filename based on procedure name, position in queue and a unique identifier
        procedure_string = re.search("'(?P<name>[^']+)'",
                                     repr(self.procedure_class)).group("name")
        main_str, basename = procedure_string.split('.')
        queue_position = len(self.manager.experiments.queue) + 1
        uidn = uuid.uuid4().clock_seq_hi_variant
        filename = f'{basename}-{queue_position}_{uidn}.csv'

        #create new experiment
        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)
        #que new experiment
        self.manager.queue(experiment)


##############################
# Utility classes & Functions#
##############################


class Dummy(Procedure):
    instrument_adress = "GPIB::25"

    # define measurement paramters here
    max_voltage = FloatParameter('Maximum Voltage', units='V', default=1)

    # Add Comments as parameters to show up in measurement file
    operator = Parameter('Operator', default='JD')
    location = Parameter('Location', default='Mun')
    setup = Parameter('Setup', default='Probe Station')

    # define DATA_COLUMNS that are written to the file
    DATA_COLUMNS = ['Voltage (V)', 'Current (A)', 'Current Std (A)']

    def startup(self):
        # System startup: Build instances of all necessary device objects here
        log.info("Connecting and configuring the instrument")
        log.info("Instrument Adress" + self.instrument_adress)

        sourcemeter = Keithley2600(self.instrument_adress)

    def execute(self):
        # Execute Script here
        print("Execute")

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
    print("Inside main")

    app = QtGui.QApplication(sys.argv)
    # window = MainWindow()
    window = MainWindow(procedure_class=IVCycles)
    window.show()
    # picker = InstrumentPicker()
    # picker.show()
    sys.exit(app.exec_())