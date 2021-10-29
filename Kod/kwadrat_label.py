from PyQt5.QtGui import *
from PyQt5.QtWidgets import *  # QFileDialog ,QMainWindow,QToolBar ,QAction
from PyQt5.QtCore import *

class simple_obraz(QLabel):

    def __init__(self,img,*args, **kwargs):
        super(QWidget, self).__init__(*args, **kwargs)
        
        self.wgraj(img)

    def wgraj(self,img):
    
        #wgranie obrazu
        self._img = img[0]

        #odczyt wymiarw zaczytanego obrazu
        h0 = img[0].size().height()
        w0 = img[0].size().width()

        #miniaturyzacja wspurzednych pod
        xHigh = h0#int(w0/h0*100)
        yHigh = w0#int(h0/w0*100)

        #scalpowanei grnego zaznaczonego pkt
        x1 = int(img[2]*xHigh/h0)
        y1 = int(img[1]*yHigh/w0)
        xy1 = QPoint(10,10)

        h0 = self.size().height()
        w0 = self.size().width()
        
        #scalowanie dolnego pkt
        x2 = int((img[2]+img[4])*xHigh/h0)
        y2 = int((img[1]+img[3])*yHigh/w0)
        xy2 = QPoint(300,150)

        self.rectangle = QRect(xy1,xy2)

        
        yHigh = 310#int(w0/h0*100)*2
        xHigh = 160#int(h0/w0*100)*2

        #wgranie obrazu
        self.setPixmap(self._img)

        #zafixowanie rozmiaru poglondu
        self.setMinimumSize(yHigh,xHigh)
        self.setMaximumSize(yHigh,xHigh)

    def paintEvent(self, QPaintEvent):
        # inicializacja pintera
        qp = QPainter(self)

        # rysowanie obrazu
        qp.drawPixmap(self.rect(), self._img)

        # kolro i tlo
        br = QBrush(QColor(200, 10, 10, 200))

        # wgranie stylu
        qp.setBrush(br)

        qp.drawRect(self.rectangle)

class podglond_roi(QWidget):

    def __init__(self,text,img,obiekt_oznaczony,*args, **kwargs):

        super(QWidget, self).__init__(*args, **kwargs)

        ######################################################################################
        ##################################Przyciski i labele##################################
        ######################################################################################

        #przyciski w ramach podglondu
        self.butons = [QPushButton() for _ in range(4)]
        
        self.podglond = simple_obraz(img)
        
        self.name_lable = QLabel()    
        self.name_lable.setText(text)            

        ######################################################################################
        ##################################Leyout##############################################
        ###################################################################################### 

        
        self.buton_layout =  QHBoxLayout()
        [self.buton_layout.addWidget(Value) for Value in self.butons]


        self.secenduary_layout = QVBoxLayout()
        self.secenduary_layout.addWidget(self.name_lable)
        self.secenduary_layout.addLayout(self.buton_layout)
        

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.podglond)
        self.main_layout.addLayout(self.secenduary_layout)

        self.setLayout(self.main_layout)
         
        self.setMaximumSize(640,180)
        self.setMinimumSize(640,180)


        ######################################################################################
        ##################################conected############################################
        ######################################################################################
        
        
        nazwy = ['',"","",'dell']
        [swich.setText(name) for name,swich in zip(nazwy,self.butons)]
         
        self.butons[3].clicked.connect(obiekt_oznaczony.kill)