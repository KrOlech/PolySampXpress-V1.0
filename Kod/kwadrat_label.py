from PyQt5.QtGui import *
from PyQt5.QtWidgets import *  # QFileDialog ,QMainWindow,QToolBar ,QAction
from PyQt5.QtCore import *

class simple_obraz(QLabel):

    def __init__(self, img, Rectagle, *args, **kwargs):
        super(QWidget, self).__init__(*args, **kwargs)
        
        self.Rectagle = Rectagle
        
        Rectagl = []
        Rectagl.append(Rectagle[0]/6.36)
        Rectagl.append(Rectagle[1]/6.72)
        Rectagl.append(Rectagle[2]/6.33)
        Rectagl.append(Rectagle[3]/6.53)
       
        self.wgraj(img, Rectagl)

    def wgraj(self, img, Rect):
    
        #wgranie obrazu
        self._img = img[0]

        #odczyt wymiarw zaczytanego obrazu
        h0 = img[0].size().height()
        w0 = img[0].size().width()
        
        self.rectangle = QRect(QPoint(Rect[0],Rect[1]),QPoint(Rect[2],Rect[3]))
        
        #wgranie obrazu
        self.setPixmap(self._img)

    def update_rectagle(self,x,y,z,s):
        Rect = []
        Rect.append(self.Rectagle[0]/x)
        Rect.append(self.Rectagle[1]/y)
        Rect.append(self.Rectagle[2]/z)
        Rect.append(self.Rectagle[3]/s)
        self.rectangle = QRect(QPoint(Rect[0],Rect[1]),QPoint(Rect[2],Rect[3]))

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

    def __init__(self, text, img, obiekt_oznaczony, *args, **kwargs):

        super(QWidget, self).__init__(*args, **kwargs)
        
        
        self.obiekt_oznaczony = obiekt_oznaczony

        ######################################################################################
        ##################################Przyciski i labele##################################
        ######################################################################################

        
        self.podglond = simple_obraz(img,obiekt_oznaczony.get_wzgledny_rectagle())
        
        self.name_lable = QLabel()    
        self.name_lable.setText(text)            

        ######################################################################################
        ##################################Leyout##############################################
        ###################################################################################### 
        
        self.buton_layout =  QHBoxLayout()
        
        self.secenduary_layout = QVBoxLayout()
        self.secenduary_layout.addWidget(self.name_lable)
        self.secenduary_layout.addLayout(self.buton_layout)
        

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.podglond)
        self.main_layout.addLayout(self.secenduary_layout)

        self.kierunkowelayout = QGridLayout()
        self.main_layout.addLayout(self.kierunkowelayout)
        
        
        self.setLayout(self.main_layout)
        
        self.main_butons()
        
        self.set_size()
       

        ######################################################################################
        ##################################conected############################################
        ######################################################################################

        
    
    def __del__(self):
        self.obiekt_oznaczony = 0

    def edit(self):
        pass

    def main_butons(self):
        
        self.butons = [QPushButton() for _ in range(3)]
        
        [self.buton_layout.addWidget(Value) for Value in self.butons]
        
        nazwy = ["edit", "fine edit", "del"]
        
        [swich.setText(name) for name, swich in zip(nazwy, self.butons)]
         
        fun = [self.edit,self.fine_edit,self.dellite]
        
        [b.clicked.connect(f) for b,f in zip(self.butons,fun)]
        
    def calibration_butons(self):
    
        self.butons = [QPushButton() for _ in range(8)]
        
        [self.buton_layout.addWidget(Value) for Value in self.butons]
        
        nazwykalibracionmode = ['xp', "yp", "zp", 'sp',"xm","ym","zm","sm"]
        
        [swich.setText(name) for name, swich in zip(nazwy, self.butons)]
        
        self.x, self.y, self.z, self.s = 6.36,6.72,6.33,6.53
        
        funkalibracionmode = [self.xp,self.yp,self.zp,self.sp,self.xm,self.ym,self.zm,self.sm]
        [b.clicked.connect(f) for b,f in zip(self.butons,fun)]

    def fine_edit(self):#
        [self.buton_layout.removeWidget(b) for b in self.butons]
        self.butons = 0
        
        self._Direction_buttons()
        self.set_size(180,240)

    def _Direction_buttons(self):
        self.kierunkowe = [QPushButton() for _ in range(4)]

        [button.setMaximumWidth(50) for button in self.kierunkowe]

        #nadanie nazw przyciska
        nazwy = ['/\\', "<", ">", '\/']
        [swich.setText(name) for name, swich in zip(nazwy, self.kierunkowe)]

        #przypiecie fukcji do przycisków
        fun = [lambda : None ,lambda : None,lambda : None,lambda : None]

        [swich.clicked.connect(f) for f, swich in zip(fun, self.kierunkowe)]
        
        #dodanie do leyatów przyciskó kierunkowych
        it = [3, 2, 4, 3]
        jt = [2, 3, 3, 4]
        [self.kierunkowelayout.addWidget(value, j, i) for j, i, value in zip(jt, it, self.kierunkowe)]
    
        
        self.t = QPushButton()
        self.t.setMaximumWidth(50)
        self.t.setText("return")
        self.t.clicked.connect(self.normalbutons)
        self.kierunkowelayout.addWidget(self.t,2,2)
        
    def normalbutons(self):
        [self.kierunkowelayout.removeWidget(b) for b in self.kierunkowe]
        self.kierunkowe = 0
        
        self.kierunkowelayout.removeWidget(self.t)
        
        self.t = 0

        self.main_butons()
        self.set_size()
        
    def dellite(self):
        self.obiekt_oznaczony.kill()
        self.obiekt_oznaczony = 0

    def set_size(self,x = 180,y = 180):
        self.setMaximumSize(x,y)
        self.setMinimumSize(x,y)
        
    def xp(self):
        self.x += 0.001
        self.podglond.update_rectagle(self.x, self.y, self.z, self.s)
        print(self.x, self.y, self.z, self.s)
        self.update()
        
    def yp(self):
        self.y += 0.001
        self.podglond.update_rectagle(self.x, self.y, self.z, self.s)
        print(self.x, self.y, self.z, self.s)
        self.update()
        
    def zp(self):
        self.z += 0.001
        self.podglond.update_rectagle(self.x, self.y, self.z, self.s)
        print(self.x, self.y, self.z, self.s)
        self.update()
        
    def sp(self):
        self.s += 0.001
        self.podglond.update_rectagle(self.x, self.y, self.z, self.s)
        print(self.x, self.y, self.z, self.s)
        self.update()

    def xm(self):
        self.x -= 0.001
        self.podglond.update_rectagle(self.x, self.y, self.z, self.s)
        print(self.x, self.y, self.z, self.s)
        self.update()
        
    def ym(self):
        self.y -= 0.001
        self.podglond.update_rectagle(self.x, self.y, self.z, self.s)
        print(self.x, self.y, self.z, self.s)
        self.update()
        
    def zm(self):
        self.z -= 0.001
        self.podglond.update_rectagle(self.x, self.y, self.z, self.s)
        print(self.x, self.y, self.z, self.s)
        self.update()
        
    def sm(self):
        self.s -= 0.001
        self.podglond.update_rectagle(self.x, self.y, self.z, self.s)
        print(self.x, self.y, self.z, self.s)
        self.update()

#
