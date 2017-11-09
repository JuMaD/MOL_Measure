from PyQt5 import QtWidgets

from MOL_Measure import *
from measurement_procedures import *
from setup import Ui_SetupDialog


class SelectionWindow(Ui_SetupDialog):
    """Provides a class to select one of the Procedure classes stored in measurement_procedures.py
    and the corresponding connected instrument as well as the GUI to be displayed.
    The user can select the type of measurement, the measurement equipment and the gui

    :param dialog:          A QtWidgets.QDialog() object
    :param procedures:      Array of procedure classes for the user to select from
    :param window_class:    The window_class that represents the GUI. window_class(Procedure) and window_class.show() are called to construct and show the GUI-

    """

    # todo: preselect instruments that fit to the selected_procedure
    # todo: add window_class selector to the gui
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

        # Todo: Find a solution to selecting multiple items from listed instruments
        self.listWidget.itemActivated.connect(self.instrument_selected)

        self.ProcedureSelection.addItems(self.procedures_dict.keys())
        self.selected_procedure = self.procedures_dict[self.ProcedureSelection.currentText()]
        print(self.selected_procedure)
        self.ProcedureSelection.currentTextChanged.connect(self.procedure_selected)

        self.refresh_instruments()

    def refresh_instruments(self):
        """Prompts the connected instruments using VISA Resource Manager and prints the result as into QListWidget"""
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
            message = QWidget()
            QMessageBox.information(message, "Refresh", "Instruments refreshed")
            # log.info('Connected instruments refreshed.')

    def instrument_selected(self, item):
        """Returns the VISA adress(es) of the instruments selected by the user from QListWidget."""
        itemtext = item.text()
        n, instr, idn = itemtext.split('-')
        ###############
        # PLACEHOLDER #
        ###############
        # todo: Implement function that overloads adresses to start_MainWindow
        # todo: Make multiple Instruments selectable

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

        self.label_5.setText(label_text[:-2])

        label_text = ""
        for label in procedure.DATA_COLUMNS:
            label_text += label + ", "
        self.label_7.setText(label_text[:-2])

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


# Example Usage
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()
    DialogWindow = SelectionWindow(dialog, [IVCycles, PulseIVCycle, Retention, RandomProcedure], MainWindow)
    dialog.show()

    sys.exit(app.exec_())
