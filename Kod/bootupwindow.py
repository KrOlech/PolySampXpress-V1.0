from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtCore import Qt

class Loading_window(QWidget):



    def __init__(self,*args, **kwargs):
        super(Loading_window, self).__init__(*args, **kwargs)

        self.setWindowTitle("Mapowanie prubek")  # nazwa
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.leyaout = QHBoxLayout()

        label = QLabel("inicialising Camera")

        label2 = QLabel("inicialising Manipulator")



