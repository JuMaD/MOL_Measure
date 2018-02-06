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

    # ToDo: change label names into comprehensive names instead of "label_n"
    # todo: preselect instruments that fit to the selected_procedure
    # todo: add window_class selector to the gui to select a certain gui

    def __init__(self, dialog, procedures, window_class=MainWindow):
        # setting up variables
        self.procedures = procedures
        self.procedures_dict = {}
        self.make_procedures_dict()
        self.selected_procedure = None
        self.window_class = window_class

        self.instruments_dict = {}

        # init the GUI defined in Ui_SetupDialog
        Ui_SetupDialog.__init__(self)
        self.setupUi(dialog)

        # Connect Signals
        self.pushButton.clicked.connect(self.refresh_instruments)
        self.pushButton_2.clicked.connect(self.start_MeasureGUI)
        self.label_5.setWordWrap(True)
        self.label_7.setWordWrap(True)
        self.label_2.setText("Connected Instruments")


        self.listWidget.itemClicked.connect(self.update_instruments_dict)
        self.listWidget.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)

        self.ProcedureSelection.addItems(self.procedures_dict.keys())
        self.selected_procedure = self.procedures_dict[self.ProcedureSelection.currentText()]
        self.ProcedureSelection.currentTextChanged.connect(self.procedure_selected)

        self.refresh_instruments()

    def refresh_instruments(self):
        """Prompts the connected instruments using VISA Resource Manager and prints the result as selectable items into QListWidget"""
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

    def update_instruments_dict(self):
        """Updates instruments_dict to the instruments selected by the user in QListWidget and passes it to the selected ProcedureWithInstruments"""
        self.instruments_dict.clear()
        for item in self.listWidget.selectedItems():
            n, instr, idn = item.text().split('-')
            self.instruments_dict[instr] = idn
        try:
            self.selected_procedure.instruments_dict = self.instruments_dict
        except:
            print('Passing instruments failed.')
            pass
        print(self.instruments_dict)

    def procedure_selected(self):
        """Sets the selected procedure and prints its Parameters and DATA_COLUMNS to the corresponding labels in the GUI.
        """

        self.selected_procedure = self.procedures_dict[self.ProcedureSelection.currentText()]

        procedure = self.selected_procedure()

        # Show parameters of selected Procedure to the according qtLabel
        dict = procedure.parameter_objects()
        label_text = ""
        parameters = procedure.parameter_objects()
        for name in dict.keys():
            label_text += parameters[name].name + ", "
        print(label_text)

        self.label_5.setText(label_text[:-2])

        #Print DATA_COLUMNS of selected Procedure to the according qtLabel
        label_text = ""
        for label in procedure.DATA_COLUMNS:
            label_text += label + ", "
        self.label_7.setText(label_text[:-2])

        #console output for debugging
        print(self.selected_procedure)

    def make_procedures_dict(self):
        """Makes a dictionary NAME_OF_PROCEDURE:PROCEDURE_OBJECT from the string list procedures
        to easily adress Procedure Objects.
        """

        self.procedures_dict.clear()
        self.procedures_dict[''] = None
        for procedure in self.procedures:
            self.procedures_dict[procedure.__name__] = procedure

    def start_MeasureGUI(self):
        """Starts the specified GUI with the user selected Procedure and Instrument(s)"""
        # Todo:Overload Instrument(s) to the GUI?
        # Todo: Introduce required_instruments and connected_instruments to Procedure class

        self.window = self.window_class(procedure_class=self.selected_procedure)
        self.window.show()

# Example Usage
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dialog = QtWidgets.QDialog()
    DialogWindow = SelectionWindow(dialog, [IVCycles, PulseIVCycle, Retention, RandomProcedure], MainWindow)
    dialog.show()

    sys.exit(app.exec_())
