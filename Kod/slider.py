from PyQt5.QtWidgets import QSlider
from PyQt5.QtCore import Qt

class slider(QSlider):

    max_slidera = 1000

    def __init__(self,Mainwinow,min,max,value,*args, **kwargs):
        super(slider, self).__init__(*args, **kwargs)
        self.mainwindow = Mainwinow
        
        self.max,self.min,self.value = max, min,value
        
        self.valueChanged[int].connect(self.changed)
        
        self.setFocusPolicy(Qt.StrongFocus)
        self.setTickPosition(QSlider.TicksBothSides)
        self.setTickInterval(100)
        self.setSingleStep(10)
        self.setMaximum(self.max_slidera)
        self.setMinimum(0)
        
        self.setValue(self.unconwert(25))

    def conwertion(self,value):
        return value/self.max_slidera*(self.max-self.min)+self.min
    
    def unconwert(self,value):
        return ((value-self.min)/(self.max-self.min))*self.max_slidera
    
    def changed(self,value):
        #print(value,self.conwertion(value))
        self.mainwindow.manipulaor.move_x(self.conwertion(value))
    
    def set_min_max(self,min,max):
        self.max,self.min = int(max), int(min)
