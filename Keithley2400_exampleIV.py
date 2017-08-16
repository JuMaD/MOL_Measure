# Import necessary packages
from pymeasure.instruments.keithley import Keithley2400
from pymeasure.experiment import Procedure
from pymeasure.experiment import IntegerParameter, FloatParameter
from time import sleep
import sys
import tempfile
import numpy as np

import visa

from pymeasure.log import console_log
from pymeasure.display.Qt import QtGui
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Procedure, Results
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter

from PyQt5.QtWidgets import *
import visa
import sys



import multiprocessing




class IVCycles(Procedure):
    instrument_adress = "GPIB::4"
    averages = IntegerParameter('Averages', default=50)
    max_voltage = FloatParameter('Maximum Voltage', units='V', default=1)
    min_voltage = FloatParameter('Minimum Voltage', units='V', default=-1)
    compliance = FloatParameter('Compliance', units='A', default=0.1)

    cycles = IntegerParameter('#Cycles', default=1)

    voltage_step = FloatParameter('Voltage Step', units='V', default=0.1)
    #Calculate the number of data points from range and step
    data_points = IntegerParameter('Data points',
                                   default=np.ceil((max_voltage.value - min_voltage.value) / voltage_step.value))

    DATA_COLUMNS = ['Voltage (V)', 'Current (A)', 'Current Std (A)']


    def startup(self):
        log.info("Connecting and configuring the instrument")
        log.info("Instrument Adress" + self.instrument_adress)
        self.sourcemeter = Keithley2400(self.instrument_adress)
        self.sourcemeter.reset()
        #setting source mode to voltage, defining range and compliance
        self.sourcemeter.apply_voltage([-20,20],self.compliance)
        self.sourcemeter.use_front_terminals()
        self.sourcemeter.measure_current()
        sleep(0.1) # wait here to give the instrument time to react
        self.sourcemeter.buffer_points = averages

    def execute(self):

        voltages = np.linspace(
            self.min_voltage.value,
            self.max_voltage.value,
            num=self.data_points.value
        )
        #Loop through cycles
        for cycle in xrange(cycles.value):
            # Loop through each voltage point, measure and record the current
            for voltage in voltages:
                log.info("Setting the voltage to %g V" % voltage)
                sourcemeter.source_voltage = voltage

                sourcemeter.reset_buffer()
                sleep(0.1)
                sourcemeter.start_buffer()
                log.info("Waiting for the buffer to fill with measurements")
                sourcemeter.wait_for_buffer()
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

class MainWindow(ManagedWindow):

    def __init__(self):
        super(MainWindow, self).__init__(
            procedure_class=IVCycles,
            inputs=['averages', 'max_voltage', 'min_voltage', 'voltage_step', 'compliance', 'cycles'],
            displays=['averages', 'max_voltage', 'min_voltage', 'voltage_step', 'data_points', 'compliance'],
            x_axis='Voltage (V)',
            y_axis='Current (A)'
        )
        self.setWindowTitle('Mol_measure 0.0.1')
    #override queue fuction of managed window that gets executed upon clicking on 'Queue'
    def queue(self):
        #make a temporary file
        filename = tempfile.mktemp()
        #call make_procedure from ManagedWindow to construct a new instance of procedure_class
        procedure = self.make_procedure()

        #calculate number of datapoints
        procedure.data_points = np.ceil((procedure.max_voltage - procedure.min_voltage) / procedure.voltage_step)

        procedure.instrument_adress = "GPIB::1"


        #construct a new instance of Results
        results = Results(procedure, filename)
        #call new_experiment to construct a new Experiment (=convinient container for reult + procedure)
        experiment = self.new_experiment(results)
        #if its the first experiment don't start it right away
        if not self.manager.experiments.queue:
            self.manager._start_on_add = False
            self.manager._is_continuous = False
            self.manager.queue(experiment)

            #set the gui accordingly
            self.abort_button.setEnabled(False)
            self.abort_button.setText("Start")
            self.abort_button.clicked.disconnect()
            self.abort_button.clicked.connect(self.resume)
            self.abort_button.setEnabled(True)

        #add experiment to que
        else:

            self.manager.queue(experiment)


class InstrumentPicker(QListWidget):
    #initialize List and populate with visa instruments

    def __init__(self):
        super().__init__()
        #bring window to front
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
        #Resize width and height
        self.resize(300,120)
        self.setWindowTitle('Select Instrument')
        #connect click handle
        self.itemClicked.connect(self.Clicked)


    def Clicked(self,item):
        #pick instrument here!
        #split item.text() string into n,instr,idn again
        itemtext = item.text()
        n, instr, idn = itemtext.split('-')
        QMessageBox.information(self, "Instrument Selection", "You clicked: \nitem\t\t"+n+"\nadress:\t\t"+instr+"\nidn:\t\t"+idn)




if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    #picker = InstrumentPicker()
    #picker.show()
    sys.exit(app.exec_())