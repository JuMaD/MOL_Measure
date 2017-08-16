"""Testing GUI setup to make a list of available Instruments and Select one. VISA Manger --> QtListWidget --> ManagedWindow (ListItem)"""
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import visa
import sys

class InstrumentPicker(QListWidget):
    #initialize List and populate with visa instruments
    def __init__(self):
        super().__init__()

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






if __name__ == '__main__':
    app = QApplication(sys.argv)
    Picker = InstrumentPicker()
    Picker.show()
    sys.exit(app.exec_())