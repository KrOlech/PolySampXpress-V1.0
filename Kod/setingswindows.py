from PyQt5.QtWidgets import QWidget, QLabel, QTextEdit, QGridLayout,QLineEdit,QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt,QRegExp
from PyQt5.QtGui import QRegExpValidator,QDoubleValidator, QIcon, QIntValidator

class axissetingwindow(QWidget):


    def __init__(self,mainwindow,*args, **kwargs):
        super(axissetingwindow, self).__init__(*args, **kwargs)
        
        self.mainwindow = mainwindow
        
        self.setWindowIcon(QIcon('icon.png'))
        
        self.setWindowTitle("Ustawienia osi")
        
        self.options = ()
        
        self.leyout = QGridLayout()
        
        self.create_option("Minimum slidera osi X",0,20)
        
        self.create_option("maximum slidera osi X",1,30)
        
        self.create_option("Krok dla y i z w 0.1 mm",2,10)
        
        self.booton = QPushButton("Zapisz i zastosuj ustawienia")
        self.booton.clicked.connect(self.printimputs)
        self.bootonleyout = QVBoxLayout()
        
        self.bootonleyout.addLayout(self.leyout)
        self.bootonleyout.addWidget(self.booton)
        
        self.setLayout(self.bootonleyout)
        
    
    def printimputs(self):
        self.mainwindow.slide.set_min_max(int(self.options[0].text()),int(self.options[1].text()))
        self.mainwindow.setkrok(int(self.options[2].text()))
        self.hide()
    
    def create_option(self,text,posytion,value):    
    
        self.leyout.addWidget(QLabel(text),posytion,0)
        
        self.options += (self.createlinedition(),)
        self.options[-1].setText(str(value))
        self.leyout.addWidget(self.options[-1],posytion,1)
    
        
    def createlinedition(self):
        lineEdit = QLineEdit()
        validator = QIntValidator()
        lineEdit.setValidator(validator)
        
        return lineEdit
