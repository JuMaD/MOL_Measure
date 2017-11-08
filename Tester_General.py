import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from setup import Ui_SetupDialog
import visa
from pymeasure import *
from MOL_Measure import *

from measurement_procedures import *


class SelectionWindow(Ui_SetupDialog):
    """Provides a class to select one of the Procedure classes stored in measurement_procedures.py"""

    def __init__(self, dialog, procedures, window_class=MainWindow):
        self.procedures = procedures
        self.procedures_dict = {}
        self.make_procedures_dict()
        self.selected_procedure = None
        self.window_class = window_class

        Ui_SetupDialog.__init__(self)
        self.setupUi(dialog)

        # Connect Signals
        self.pushButton.clicked.connect(self.refresh_instruments)

        self.pushButton_2.clicked.connect(self.start_MainWindow)

        self.label_5.setWordWrap(True)
        self.label_7.setWordWrap(True)
        self.label_2.setText("Connected Instruments")

        self.listWidget.itemClicked.connect(self.instrument_selected)

        self.ProcedureSelection.addItems(self.procedures_dict.keys())
        self.selected_procedure = self.procedures_dict[self.ProcedureSelection.currentText()]
        print(self.selected_procedure)
        self.ProcedureSelection.currentTextChanged.connect(self.procedure_selected)


        self.refresh_instruments()

    def refresh_instruments(self):
        if self.listWidget.count() == 0:
            startup = True
        else:
            self.listWidget.clear()
            startup = False
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
                    self.listWidget.addItem(str(n) + "-" + str(instr) + "-" + str(idn))
            except visa.VisaIOError as e:
                print(n, ":", instr, ":", "Visa IO Error: check connections")
                print(e)
        rm.close()
        if not startup:
            QMessageBox.information(self, "Refresh", "Instruments refreshed")
            # log.info('Connected instruments refreshed.')

    def instrument_selected(self, item):
        print('Selected Instrument')
        itemtext = item.text()
        print(itemtext)
        n, instr, idn = itemtext.split('-')
        ###############
        # PLACEHOLDER #
        ###############
        # todo: Implement function that overloads adresses to start_MainWindow
        message = QWidget()
        QMessageBox.information(message, "Instrument Selection",
                                "You clicked: \nitem\t\t" + n + "\nadress:\t\t" + instr + "\nidn:\t\t" + idn)  # TODO: Replace this with a function that adds the selected instrument(-adress) to the current procedure

    def procedure_selected(self):
        """Sets the selected procedure"""

        self.selected_procedure = self.procedures_dict[self.ProcedureSelection.currentText()]

        procedure = self.selected_procedure()
        dict = procedure.parameter_objects()
        print(dict)

        label_text = ""
        parameters = procedure.parameter_objects()
        for name in dict.keys():
            label_text += parameters[name].name + ", "
        print(label_text)

        self.label_5.setText(label_text)

        label_text = ""
        for label in procedure.DATA_COLUMNS:
            label_text += label + ", "
        self.label_7.setText(label_text)

        print(self.selected_procedure)

    def make_procedures_dict(self):
        self.procedures_dict.clear()
        self.procedures_dict[''] = None
        for procedure in self.procedures:
            self.procedures_dict[procedure.__name__] = procedure

    def start_MainWindow(self):
        # Todo:Overload Instrument_Adress

        self.window = self.window_class(procedure_class=self.selected_procedure)
        self.window.show()






if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()
    DialogWindow = SelectionWindow(dialog, [IVCycles, PulseIVCycle, Retention], MainWindow)
    dialog.show()

    sys.exit(app.exec_())
