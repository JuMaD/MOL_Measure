"""Testing GUI setup to make a list of available Instruments and Select one. VISA Manger --> QtListWidget --> ManagedWindow (ListItem)"""
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys

class myListWidget(QListWidget):

    def Clicked(self,item):
        QMessageBox.information(self, "ListWidget", "You clicked: "+item.text())

    def SelectInstrument():

        listWidget = myListWidget()

        #Resize width and height
        listWidget.resize(300,120)

        listWidget.addItem("Item 1")
        listWidget.addItem("Item 2")
        listWidget.addItem("Item 3")
        listWidget.addItem("Item 4")

        listWidget.setWindowTitle('Select Instrument')
        listWidget.itemClicked.connect(listWidget.Clicked)

        listWidget.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ListOfInstruments = myListWidget()
    ListOfInstruments.SelectInstrument()
    sys.exit(app.exec_())