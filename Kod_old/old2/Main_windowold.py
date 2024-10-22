from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
import Viue_label as obs
import Map as M
from engineclass import manipulator
from time import sleep
from slider import slider
from setingswindows import axissetingwindow


class MainWindow(QMainWindow):

    ROI = []
    
    #prostokonty zaznaczone
    rectangles = []
    
    krok = 10
    
    last_name = 0
    
    map = None

    def __init__(self, *args, **kwargs):
        
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowIcon(QtGui.QIcon('icon.png'))
                
        self.setWindowTitle("Mapowanie prubek") #nazwa
        self.setGeometry(5, 30, 1280, 1024)
        
        self.setMouseTracking(False)

        #stworzenie podglondu prubki i umiescenie go w leyaucie
        self.obraz = obs.Obraz_z_kamery(self)

        # linking to manipulator for movment
        self.manipulaor = manipulator(self)
                
        #creating leyaut conteeiners for Gui formation
        self._createleyouts()

        #stworzenie przycisków do przemiesczania podglondu
        self._Direction_buttons()
        
        #X axis slieder
        self.slider_create()

        #stworzenie i dodanie przycisków do wszelkich zastosowan
        self._Multipurpos_butons()

        #stworzenie i dodanie obszaru skrolowania
        self._Scroll_arrea()

        #połoczenie leyoutów
        self._layout_marging()

        self._set_central_widget()
        
        self.toolbars()
        
        self.upadet_position_read()

    def closeEvent(self, event):
    
        if self.map != None:
            del self.map
        
        reply = QMessageBox.question(self,"mesage","Czy napewno chcesz zamknac program?",
                                     QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
        
        if reply == QMessageBox.Yes:
            self.manipulaor.close_connection()
            del self.manipulaor
            event.accept()
            
        else:
            event.ignore()

######################################################################################
##################################Toolbars############################################
######################################################################################

    def toolbars(self):
    
        toolbar = QToolBar("Funkcje") #stworzenie toolbara
        self.addToolBar(toolbar)
        action_6 = self.qactiontoolbar("Snap obraz", lambda x: self.obraz.odczytaj_klatke())
        toolbar.addAction(action_6)
        

        seting_window = self.qactiontoolbar("Ustawienia osi", self.setings_for_axis)
        toolbar.addAction(seting_window)

    def qactiontoolbar(self,nazwa, funkcja):
            
        Button = QAction(nazwa, self) 
        #stworzenie czegos na kształt przycisku ale nie koniecznie muszacego posiadac jeden triger
        Button.triggered.connect(funkcja) 
        #dodanie trigera

        return Button 
 
    def setings_for_axis(self):
        
        self.axissetings = axissetingwindow(self)
        self.axissetings.show()
        
######################################################################################
##################################Leyout and widget###################################
######################################################################################

    def _createleyouts(self):
        #Głóny leyaut
        self.mainlayout = QHBoxLayout() 
        
        #leyaut
        self.secendarylayout = QVBoxLayout() 
        
        #leyauty przycisków i opisów
        self.kierunkowelayout = QGridLayout()
        self.przyciskilayout = QGridLayout() 


        self.sliderlegendsleyout = QVBoxLayout()
        self.sliderleyout = QHBoxLayout()

    def _layout_marging(self):
     
        self.mainlayout.addWidget(self.obraz)
 
        #łoczenie leyautów
        self.secendarylayout.addWidget(self.scroll)        
        self.secendarylayout.addLayout(self.kierunkowelayout)
        self.secendarylayout.addLayout(self.sliderleyout)
        self.secendarylayout.addLayout(self.przyciskilayout)
        self.mainlayout.addLayout(self.secendarylayout)

    def _set_central_widget(self):

        widget = QWidget()
        widget.setLayout(self.mainlayout)
        self.setCentralWidget(widget)

######################################################################################
############################Direction buttons#########################################
######################################################################################

    def _Direction_buttons(self):#Przyciski _kierunkowe

        self.kierunkowe = [QPushButton() for _ in range(4)]

        [button.setMaximumWidth(50) for button in self.kierunkowe]

        #nadanie nazw przyciska
        nazwy = ['/\\', "<", ">", '\/']
        [swich.setText(name) for name, swich in zip(nazwy, self.kierunkowe)]

        #przypiecie fukcji do przycisków
        fun = [self.key_dwn, self.key_left, self.key_right,self.key_up]

        self.actions = [QAction("&dw", self), QAction("&lf", self), QAction("&ri", self), QAction("&up", self)]

        [a.triggered.connect(f) for a, f in zip(self.actions, fun)]

        keyband = [Qt.Key_Up, Qt.Key_Left, Qt.Key_Right, Qt.Key_Down]
        #keyband = [QKeySequence("w"), QKeySequence('a'), QKeySequence("d"), QKeySequence("s")]

        [a.setShortcut(k) for a, k in zip(self.actions, keyband)]

        [swich.released.connect(f) for f, swich in zip(fun, self.kierunkowe)]

        #dodanie do leyatów przyciskó kierunkowych
        it = [3, 2, 4, 3]
        jt = [2, 3, 3, 4]
        [self.kierunkowelayout.addWidget(value, j, i) for j, i, value in zip(jt, it, self.kierunkowe)]

        menu = self.menuBar()
        test = menu.addMenu("directions")
        [test.addAction(f) for f in self.actions]
        
        self.position_labele = [QLabel(str(25.0)), QLabel(str(25.0)), QLabel(str(25.0))]
        

        labelexyz = [QLabel("X"), QLabel("Y"), QLabel("Z")]
        [self.kierunkowelayout.addWidget(value, 7, i) for i, value in zip(range(2,5,1), self.position_labele)]
  
    def key_up(self):
        self.key_move(self.manipulaor.przesun_w_gore, self.obraz.gura, 3, 0)

    def key_left(self):
        self.key_move(self.manipulaor.przesun_w_lewo, self.obraz.lewo, 2, 1)

    def key_right(self):
        self.key_move(self.manipulaor.przesun_w_prawo, self.obraz.prawo, 1, 2)
   
    def key_dwn(self):
        self.key_move(self.manipulaor.przesun_w_dul, self.obraz.dul, 0, 3)
  
    def key_move(self,fun_manipulator,fun_obraz,key_en,key_dis):
    
        t = fun_manipulator(self.krok/10)
        
        self.upadet_position_read()
        x,y,z = self.manipulaor.pobierz_pozycje_osi()
        
        fun_obraz()

        if t:
            self.kierunkowe[key_en].setEnabled(True)
        else:
            self.kierunkowe[key_dis].setEnabled(False)

    def upadet_position_read(self):
        [label.setText(str(position)) for label, position in zip(self.position_labele,
                                                                 self.manipulaor.pobierz_pozycje_osi())]

######################################################################################
##########################multipurpus buttons#########################################
######################################################################################

    def _Multipurpos_butons(self):

        #przyciski multipurpus
        self.przyciski = [QPushButton() for _ in range(9)]
        [button.setMaximumWidth(100) for button in self.przyciski] 
        
        nazwy = ["schow next", "dell all", "schow all", "schow privius", "map", "hide all","przemiesc to","stop","map clear"]
        
        [swich.setText(name) for name, swich in zip(nazwy, self.przyciski)]
        
        self.przyciski[2].clicked.connect(self.obraz.narysujcaloscs)
        self.przyciski[5].clicked.connect(self.obraz.schowajcalosc)
        
        self.przyciski[0].clicked.connect(self.obraz.nastempny)
        self.przyciski[3].clicked.connect(self.obraz.poprzedni)

        self.przyciski[1].clicked.connect(self.remove_ROI)

        self.przyciski[4].clicked.connect(self.schow_map)
        
        self.przyciski[6].setCheckable(True)
        self.przyciski[6].clicked.connect(self.togle_move_on_pres)
        
        self.przyciski[7].clicked.connect(self.manipulaor.simple_stop)

        self.przyciski[8].clicked.connect(self.obraz.reset_map)

        #dodanie przycisków
        it = [2, 3, 4, 2, 3, 4, 2, 3, 4]
        jt = [5, 5, 5, 6, 6, 6, 7, 7, 7]
        [self.przyciskilayout.addWidget(w, j, i) for w, i, j in zip(self.przyciski, it, jt)]

    def schow_map(self):
        if self.map is None:
            self.map = M.Map_window(self.obraz.ponbierz_map(), self)
            self.map.show()
        else:
            self.map.nowy_obraz(self.obraz.ponbierz_map())
            self.map.show()

    def togle_move_on_pres(self):

        if self.przyciski[6].isChecked():
             # setting background color to light-blue
             self.przyciski[6].setStyleSheet("background-color : lightblue")
             
             if self.map is not None:
                self.map.przemiesc_sie_do_pktu = False
             self.obraz.przemiesc_sie_do_pktu = False
             

        else:
             # set background color powrut to light-grey
             self.przyciski[6].setStyleSheet("background-color : lightgrey")

             if self.map is not None:
                self.map.przemiesc_sie_do_pktu = True
             self.obraz.przemiesc_sie_do_pktu = True
             

######################################################################################
##########################Scroll area#################################################
######################################################################################

    def _Scroll_arrea(self):
        
        self.defalaut_lable = QLabel("No Region of interest marked")
            
        self.scroll = QScrollArea()             
        self.widget = QWidget()                 
        self.vbox = QVBoxLayout()

        self.widget.setLayout(self.vbox)
        
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.scroll.setWidgetResizable(True)
        
        self.scroll.setWidget(self.widget)
        
        self.scroll.setMaximumSize(720, 650)
        
        self.vbox.addWidget(self.defalaut_lable)

######################################################################################
##########################ROI Menagment###############################################
######################################################################################

    def add_ROI(self, ROI):
        
        if self.defalaut_lable != 0:
            try:
                self.vbox.removeWidget(self.defalaut_lable)
            except Exception as e:
                print(e)
            self.defalaut_lable = 0
        
        test_obcjects = ROI.pobierz_podglond()

        self.vbox.addWidget(test_obcjects)

        self.ROI.append(ROI)

    def remove_ROI(self):

        while self.ROI != []:
            [r.__del__() for r in self.ROI]

    def remove_some_ROI(self, ROI):
        
        self.vbox.removeWidget(ROI.pobierz_podglond())

        if ROI in self.ROI:
            self.ROI.remove(ROI)

        if len(self.ROI) == 0 and self.defalaut_lable == 0:
            self.defalaut_lable = QLabel("No Region of interest marked")
            self.vbox.addWidget(self.defalaut_lable)

######################################################################################
##########################Slider menagment############################################
######################################################################################

    def slider_create(self):
        x = self.manipulaor.pobierz_pozycje_osi('x')[0]
        self.slide = slider(self,x-5,x+5,x,Qt.Horizontal)

        self.sliderleyout.addWidget(self.slide)

    def setkrok(self,value):
    
        self.krok = value
        

    

        
        
    #eof
