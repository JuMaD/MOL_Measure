# Import necessary packages
from pymeasure.instruments.keithley import Keithley2400
from pymeasure.experiment import Procedure
from pymeasure.experiment import IntegerParameter, FloatParameter
from time import sleep
import sys
import tempfile
import numpy as np

from pymeasure.log import console_log
from pymeasure.display.Qt import QtGui
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Procedure, Results
from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter

class IVProcedure(Procedure):
    instrument_adress = "GPIB::4"

    averages = IntegerParameter('Averages', default=50)
    max_voltage = FloatParameter('Maximum Voltage', units='V', default=1)
    min_voltage = FloatParameter('Minimum Voltage', units='V', default=-1)

    voltage_step = FloatParameter('Voltage Step', units='V', default=0.1)
    data_points = IntegerParameter('Data points',
                                   default=np.ceil((max_voltage.value - min_voltage.value) / voltage_step.value))

    DATA_COLUMNS = ['Voltage (V)', 'Current (A)', 'Current Std (A)']


    def startup(self):
        log.info("Connecting and configuring the instrument")
        self.sourcemeter = Keithley2400(instrument_adress)
        #self.sourcemeter.reset()
        self.sourcemeter.use_front_terminals()
        self.sourcemeter.measure_current()
        self.sourcemeter.config_voltage_source()
        sleep(0.1) # wait here to give the instrument time to react
        self.sourcemeter.set_buffer(averages)

    def execute(self):

        voltages = np.linspace(
            self.min_voltage,
            self.max_voltage,
            num=self.data_points
        )

        # Loop through each current point, measure and record the voltage
        for voltage in voltages:
            log.info("Setting the voltage to %g V" % voltage)
            self.sourcemeter.voltage = voltage
            self.sourcemeter.reset_buffer()
            sleep(0.1)
            self.sourcemeter.start_buffer()
            log.info("Waiting for the buffer to fill with measurements")
            self.sourcemeter.wait_for_buffer()

            self.emit('results', {
                'Current (A)': self.sourcemeter.means,
                'Voltage (V)': voltage,
                'Current Std (A)': self.sourcemeter.standard_devs
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
            procedure_class=IVProcedure,
            inputs=['averages', 'max_voltage', 'min_voltage', 'voltage_step'],
            displays=['averages', 'max_voltage', 'min_voltage', 'voltage_step', 'data_points'],
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


        #construct a new instance of Results
        results = Results(procedure, filename)
        #call new_experiment to construct a new Experiment (=convinient container) from the results, curve and browser_item
        experiment = self.new_experiment(results)
        #if its the first experiment don't start it right away
        if not self.manager.experiments.queue:
            self.manager._start_on_add = False
            self.manager.queue(experiment)
            self.manager._is_continuous = False

        #add experiment to que
        else:
            self.manager.queue(experiment)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())