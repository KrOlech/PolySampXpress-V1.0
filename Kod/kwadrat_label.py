from PyQt5.QtGui import *
from PyQt5.QtWidgets import *  # QFileDialog ,QMainWindow,QToolBar ,QAction
from PyQt5.QtCore import *

class simple_obraz(QLabel):

    kalibracja = [6.36, 6.72, 6.33, 6.53]

    def __init__(self, img, Rectagle, *args, **kwargs):
        super(QWidget, self).__init__(*args, **kwargs)

       #wgraj obiekt
        self.wgraj(img, Rectagle)

    def wgraj(self, img, Rect):
    
        #kalibrate reded cords
        Rect = [r/a for r, a in zip(Rect, self.kalibracja)]
    
        #wgranie obrazu
        self._img = img

        #odczyt wymiarw zaczytanego obrazu
        h0 = img.size().height()
        w0 = img.size().width()
        
        self.rectangle = QRect(QPoint(Rect[0],Rect[1]),QPoint(Rect[2],Rect[3]))
        
        #wgranie obrazu
        self.setPixmap(self._img)

    #metod alowing calibration of podglond
    def update_rectagle(self, kalibracja):

        Rect = [r/a for r,a in zip(self.Rectagle, kalibracja)]

        self.rectangle = QRect(QPoint(Rect[0], Rect[1]), QPoint(Rect[2], Rect[3]))

    #overload metody paint event z Pyqt5
    def paintEvent(self, QPaintEvent):
        # inicializacja pintera
        qp = QPainter(self)

        # rysowanie obrazu
        qp.drawPixmap(self.rect(), self._img)

        # kolro i tlo
        #br = QBrush(QColor(200, 20, 20, 255),Qt.CrossPattern)
        br = QBrush(QColor(200, 10, 10, 200))

        # wgranie stylu
        qp.setBrush(br)

        qp.drawRect(self.rectangle)


class podglond_roi(QWidget):

    def __init__(self, text, img, obiekt_oznaczony, *args, **kwargs):

        super(QWidget, self).__init__(*args, **kwargs)
        
        self.img = img

        # wskaznik do obiekt clasy obszar oznaczony
        self.obiekt_oznaczony = obiekt_oznaczony
        
        x,x1,y,y1 = self.obiekt_oznaczony.get_niezalezne_pixele()
        ######################################################################################
        ##################################Przyciski i labele##################################
        ######################################################################################

        #custom label for viusalkizastion porpos
        self.podglond = simple_obraz(self.img,obiekt_oznaczony.get_wzgledny_rectagle())
        
        self.name_lable = QLineEdit(text)
        self.name_lable.textChanged.connect(self.newname)
        
        self.x_label = QLabel("x")
        
        self.x0_label = QLabel(str(x))
        self.x1_label = QLabel(str(x1))
        
        self.y_label = QLabel("y")
        
        self.y0_label = QLabel(str(y))
        self.y1_label = QLabel(str(y1))
        
        self.z_label = QLabel("z:")
        
        self.z0_label = QLabel("25")
        
        
        
        p_pixele = self.pole(x,x1,y,y1)
        
        self.pole_label = QLabel("Pole obszaru:")
        self.poleL = QLabel(str(p_pixele))
        ######################################################################################
        ##################################Leyout##############################################
        ###################################################################################### 
        
        self.buton_layout = QHBoxLayout()
        
        self.label_layout = QHBoxLayout()

        self.label_layout.addWidget(self.x_label)
        self.label_layout.addWidget(self.x0_label)
        self.label_layout.addWidget(self.x1_label)
        
        self.label_layout.addWidget(self.y_label)
        self.label_layout.addWidget(self.y0_label)
        self.label_layout.addWidget(self.y1_label)

        
        self.pole_layout = QHBoxLayout()
        self.pole_layout.addWidget(self.pole_label)
        self.pole_layout.addWidget(self.poleL)
        
        self.secondary_layout = QVBoxLayout()
        self.secondary_layout.addWidget(self.name_lable)
        self.secondary_layout.addLayout(self.label_layout)
        self.secondary_layout.addLayout(self.pole_layout)
        self.secondary_layout.addLayout(self.buton_layout)
        
        

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.podglond)
        self.main_layout.addLayout(self.secondary_layout)

        self.kierunkowe_layout = QGridLayout()
        self.main_layout.addLayout(self.kierunkowe_layout)

        self.setLayout(self.main_layout)
        
        self.main_butons()
        
        self.set_size()
    
    def __del__(self):
        self.obiekt_oznaczony = 0

    #blokada rozmiaru
    def set_size(self, x=180, y=225):
        self.setMaximumSize(x, y)
        self.setMinimumSize(x, y)

    #metocda tworzoca przycisk o zadanych parametrach
    @staticmethod
    def buton(fun, text, clicable = False):
        buton = QPushButton()
        buton.setMaximumWidth(50)
        buton.setText(text)
        buton.setCheckable(clicable)
        buton.clicked.connect(fun)
        return buton

######################################################################################
##################################boton config########################################
######################################################################################

    #metoda tworzoca glówne przyciski
    def main_butons(self):

        self.butons = [QPushButton() for _ in range(3)]

        [self.buton_layout.addWidget(Value) for Value in self.butons]

        nazwy = ["edit", "fine edit", "del"]

        [swich.setText(name) for name, swich in zip(nazwy, self.butons)]

        fun = [self.edit, self.fine_edit, self.dellite]

        [b.clicked.connect(f) for b, f in zip(self.butons, fun)]
        
        self.butons[0].setCheckable(True)

    #metod removing clasic bootons an aplaying calibration bootons
    def calibration_butons(self):

        self.butons = [QPushButton() for _ in range(8)]

        [self.buton_layout.addWidget(Value) for Value in self.butons]

        nazwykalibracionmode = ['xp', "yp", "zp", 'sp', "xm", "ym", "zm", "sm"]

        [swich.setText(name) for name, swich in zip(nazwy, self.butons)]

        self.x, self.y, self.z, self.s = 6.36, 6.72, 6.33, 6.53

        funkalibracionmode = [self.xp, self.yp, self.zp, self.sp, self.xm, self.ym, self.zm, self.sm]
        [b.clicked.connect(f) for b, f in zip(self.butons, fun)]

    def _Direction_buttons(self):

            self.kierunkowe = [QPushButton() for _ in range(4)]

            [button.setMaximumWidth(50) for button in self.kierunkowe]

            # nadanie nazw przyciska
            nazwy = ['/\\', "<", ">", '\/']
            [swich.setText(name) for name, swich in zip(nazwy, self.kierunkowe)]

            # przypiecie fukcji do przycisków
            fun = [self.top_booton,  self.lef_booton, self.rig_bootom, self.dwn_booton]

            [swich.clicked.connect(f) for f, swich in zip(fun, self.kierunkowe)]

            # dodanie do leyatów przyciskó kierunkowych
            it = [3, 2, 4, 3]
            jt = [2, 3, 3, 4]
            [self.kierunkowe_layout.addWidget(value, j, i) for j, i, value in zip(jt, it, self.kierunkowe)]

            #Return to main bootons
            self.t = self.buton(self.retyurn_to_normalbutons, "return")
            self.kierunkowe_layout.addWidget(self.t, 2, 2)
            self.kierunkowe.append(self.t)

            #przelaczanie pomiedzy ruszaniem obszarem a jego rozszerzaniem
            self.move = self.buton(self.TogleMove, "move", True)
            self.kierunkowe_layout.addWidget(self.move, 2, 4)
            self.kierunkowe.append(self.move)
            
            #przelaczanie pomiedzy ruszaniem obszarem a jego rozszerzaniem
            self.incrise = self.buton(self.Togleincrise, "+", True)
            self.kierunkowe_layout.addWidget(self.incrise, 4, 4)
            self.kierunkowe.append(self.incrise)

    def remove_kierunkowe(self):
        #removing main bootons
        [self.kierunkowe_layout.removeWidget(b) for b in self.kierunkowe]
        self.kierunkowe = 0
        self.move = 0
        self.t = 0
        self.incrise = 0

    def remove_main_bootons(self):
        #cliring standard bootons
        [self.buton_layout.removeWidget(b) for b in self.butons]
        self.butons = 0

######################################################################################
##################################Obiekt oznaczony komunication#######################
######################################################################################

    #live update nazwy obiektu
    def newname(self):
        self.obiekt_oznaczony.setName(self.name_lable.text())

    #metoda updatujaca na bierzoco kordynaty wyswietlane na obiekcie
    def update_cords(self):
    
        self.podglond.wgraj(self.img,self.obiekt_oznaczony.get_wzgledny_rectagle())
        
        x, x1, y, y1 = self.obiekt_oznaczony.get_niezalezne_pixele()
        
        
        self.x0_label.setText(str(x))
        self.x1_label.setText(str(x1))
        

        
        self.y0_label.setText(str(y))
        self.y1_label.setText(str(y1))
        
        self.poleL.setText(str(self.pole(x, x1, y, y1)))

    #fukcja liczaca pole obszaru oznaczonego
    def pole(self, x, x1, y, y1):
    
        xm = min(x, x1)
        xM = max(x, x1)
        
        ym = min(y, y1)
        yM = max(y, y1)
        
        return abs(xM-xm)*abs(yM-ym)
        
######################################################################################
##################################Boton function######################################
######################################################################################

    #rising edit flag
    def edit(self):
    
        if self.butons[0].isChecked():
            self.obiekt_oznaczony.edit()

        else:
            self.obiekt_oznaczony.end_edit()

    def new_image(self, img):
        if type(img) == QPixmap:
            self.podglond.wgraj(img,self.obiekt_oznaczony.get_wzgledny_rectagle())
            self.img = img
        else:
            self.podglond.wgraj(self.img,self.obiekt_oznaczony.get_wzgledny_rectagle())
        #swiching to fine edit bootns
    def fine_edit(self):
        self.remove_main_bootons()

        #creating direction botons
        self._Direction_buttons()

        #poprawienie ksztaltu okna
        self.set_size(180, 270+15)

    #deleting object
    def dellite(self):
        self.obiekt_oznaczony.kill()
        self.obiekt_oznaczony = 0

    #metod removing fine bootons and seting main ones
    def retyurn_to_normalbutons(self):

        self.remove_kierunkowe()

        self.main_butons()
        self.set_size()

######################################################################################
##################################Fine moving#########################################
######################################################################################

##########################dwutrybowe przyciski _kierunkowe############################
    def top_booton(self):
        if self.move.isChecked():
            self.obiekt_oznaczony.move_top_line(self.incrise.isChecked())
        else:
            self.obiekt_oznaczony.move_top()
            
        self.update_cords()

    def dwn_booton(self):
        if self.move.isChecked():
            self.obiekt_oznaczony.move_dwn_line(self.incrise.isChecked())
        else:
            self.obiekt_oznaczony.move_dwn()
            
        self.update_cords()
            
    def lef_booton(self):
        if self.move.isChecked():
            self.obiekt_oznaczony.move_lft_line(self.incrise.isChecked())
        else:
            self.obiekt_oznaczony.move_lft()

        self.update_cords()
                
    def rig_bootom(self):
        if self.move.isChecked():
            self.obiekt_oznaczony.move_rig_line(self.incrise.isChecked())
        else:
            self.obiekt_oznaczony.move_rig()
            
        self.update_cords()

######################################################################################
    def TogleMove(self):

        if self.move.isChecked():
             self.move.setText("shape")

        else:
             self.move.setText("move")
             
                        
    def Togleincrise(self):
     
        if self.incrise.isChecked():
            self.incrise.setText("-")

        else:
            self.incrise.setText("+")

######################################################################################
##################################Kalibration#########################################
######################################################################################

    def xp(self):
        self.x += 0.001
        self.chang()

    def yp(self):
        self.y += 0.001
        self.chang()
        
    def zp(self):
        self.z += 0.001
        self.chang()
        
    def sp(self):
        self.s += 0.001
        self.chang()

    def xm(self):
        self.x -= 0.001
        self.chang()
        
    def ym(self):
        self.y -= 0.001
        self.chang()
        
    def zm(self):
        self.z -= 0.001
        self.chang()
        
    def sm(self):
        self.s -= 0.001
        self.chang()

    def chang(self):
        self.podglond.update_rectagle((self.x, self.y, self.z, self.s))
        print(self.x, self.y, self.z, self.s)
        self.update()
