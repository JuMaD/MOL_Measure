import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class SetupDialog(QDialog):
    """Prompts procedure (from dropdownlist) and instruments (from connected instruments) from the user before showing MainWindow"""

    def __init__(self, procedures=[]):
        super().__init__(parent=None)
        self.procedures = procedures
        self.picked_procedure = None

        self._setup_ui()
        self._layout()

    # Set Up Gui
    def _setup_ui(self):
        # instrument picker
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.instrument_clicked)
        self.refresh_button = QtGui.QPushButton('Refresh', self)
        self.refresh_button.setEnabled(True)
        self.refresh_button.clicked.connect(self.refresh_instruments)

        self.start_button = QtGui.QPushButton('Start', self)
        self.start_button.setEnabled(True)
        self.start_button.clicked.connect(self.start_mainWindow)

        self.refresh_instruments()

    def _layout(self):
        # ToDo: ReWrite this / use QtManager to get a nice gui
        grid = QGridLayout()

        grid.addWidget(QLabel('Measurement Procedure'), 1, 1)
        grid.addWidget(QLabel('Inputs'), 2, 1)
        grid.addWidget(QLabel('Data'), 3, 1)
        grid.addWidget(QLabel('Instrument(s)'), 4, 1)
        grid.addWidget(refresh_button, 4, 2)

        grid.addWidget(list_widget, 5, 2)
        grid.addWidget(start_button, 6, 2)

        # Instrument Picker
        inputs_vbox.addWidget(self.inputs)
        inputs_vbox.addLayout(hbox)
        inputs_vbox.addWidget(self.list_widget)
        inputs_vbox.addWidget(self.refresh_button)
        inputs_vbox.addStretch()
        inputs_dock.setLayout(inputs_vbox)

    def show_dialog(self):
        app = QApplication(sys.argv)
        win = QWidget()
        win.setLayout(grid)
        win.setGeometry(100, 100, 200, 100)
        win.setWindowTitle("Setup Experiment")
        win.show()
        sys.exit(app.exec_())

    def start_MainWindow(self):
        window = MainWindow(procedure_class=self.picked_procedure)
        window.show()

    # Instrument Picker

    def refresh_instruments(self):
        if self.list_widget.count() == 0:
            startup = True
        else:
            self.list_widget.clear()
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
                    self.list_widget.addItem(str(n) + "-" + str(instr) + "-" + str(idn))
            except visa.VisaIOError as e:
                print(n, ":", instr, ":", "Visa IO Error: check connections")
                print(e)
        rm.close()
        if not startup:
            QMessageBox.information(self, "Refresh", "Instruments refreshed")
        log.info('Connected instruments refreshed.')

    def instrument_clicked(self, item):
        itemtext = item.text()
        n, instr, idn = itemtext.split('-')
        QMessageBox.information(self, "Instrument Selection",
                                "You clicked: \nitem\t\t" + n + "\nadress:\t\t" + instr + "\nidn:\t\t" + idn)  # TODO: Replace this with a function that adds the selected instrument(-adress) to the current procedure
        return idn

    # Procedure Picker
    def PickProcedures(self):
        # todo: list of procedures --> dropdown
        return procedures


def window():
    app = QApplication(sys.argv)
    w = QWidget()
    b = QPushButton(w)
    b.setText("Hello World!")
    b.move(50, 50)
    b.clicked.connect(showdialog)
    w.setWindowTitle("PyQt Dialog demo")
    w.show()
    sys.exit(app.exec_())


def showdialog():
    d = QDialog()
    b1 = QPushButton("ok", d)
    b1.move(50, 50)
    d.setWindowTitle("Dialog")
    d.setWindowModality(Qt.ApplicationModal)
    d.exec_()


if __name__ == '__main__':
    dialog = SetupDialog()
    # dialog.show_dialog()
