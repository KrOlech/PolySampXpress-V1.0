from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *  # QFileDialog ,QMainWindow,QToolBar ,QAction

import Viue_label as obs
import Map as M

class MainWindow(QMainWindow):

    ROI = []

    def __init__(self, *args, **kwargs):
        
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowIcon(QtGui.QIcon('icon.png'))
                
        self.setWindowTitle("Mapowanie prubek") #nazwa
        self.setGeometry(5, 30, 1920, 1080)
        
        self.setMouseTracking(False)

        #creating leyaut conteeiners for Gui formation
        self._createleyouts()

        #stworzenie podglondu prubki i umiescenie go w leyaucie
        self.obraz = obs.Obraz(self)

        #stworzenie przycisków do przemiesczania podglondu
        self._Direction_buttons()

        #stworzenie i dodanie przycisków do wszelkich zastosowan
        self._Multipurpos_butons()

        #stworzenie i dodanie obszaru skrolowania
        self._Scroll_arrea()

        #połoczenie leyoutów
        self._layout_marging()

        self._set_central_widget()


######################################################################################
##################################Fukcje##############################################
######################################################################################

    def _set_central_widget(self):

        widget = QWidget()
        widget.setLayout(self.mainlayout)
        self.setCentralWidget(widget)

    def _createleyouts(self):
        #Głóny leyaut
        self.mainlayout = QHBoxLayout() 
        
        #leyaut
        self.secendarylayout = QVBoxLayout() 
        
        #leyauty przycisków i opisów
        self.kierunkowelayout = QGridLayout()
        self.przyciskilayout = QGridLayout()           

    def _Direction_buttons(self):#Przyciski kierunkowe

        self.kierunkowe = [QPushButton() for _ in range(4)]

        [button.setMaximumWidth(50) for button in self.kierunkowe]

        #nadanie nazw przyciska
        nazwy = ['/\\',"<",">",'\/']
        [swich.setText(name) for name, swich in zip(nazwy, self.kierunkowe)]

        #przypiecie fukcji do przycisków
        fun = [self.obraz.up, self.obraz.left, self.obraz.right, self.obraz.dawn]
        [swich.clicked.connect(name) for name, swich in zip(fun, self.kierunkowe)]

        #dodanie do leyatów przyciskó kierunkowych
        it = [3, 2, 4, 3]
        jt = [2, 3, 3, 4]
        [self.kierunkowelayout.addWidget(value, j, i) for j, i, value in zip(jt, it, self.kierunkowe)]
 
    def _Multipurpos_butons(self):

        #przyciski multipurpus
        self.przyciski = [QPushButton() for _ in range(6)]
        [button.setMaximumWidth(100) for button in self.przyciski] 
        
        nazwy = ["schow next", "dell all", "schow all", "schow privius", "", "hide all"]
        
        [swich.setText(name) for name, swich in zip(nazwy, self.przyciski)]
        
        self.przyciski[2].clicked.connect(self.obraz.Narysujcaloscs)
        self.przyciski[5].clicked.connect(self.obraz.schowajcalosc)
        
        self.przyciski[0].clicked.connect(self.obraz.Next)
        self.przyciski[3].clicked.connect(self.obraz.last)

        self.przyciski[1].clicked.connect(self.remove_ROI)

        self.przyciski[4].clicked.connect(self.schow_map)

        #dodanie przycisków
        it = [2, 3, 4, 2, 3, 4]
        jt = [5, 5, 5, 6, 6, 6]
        [self.przyciskilayout.addWidget(w, j, i) for w, i, j in zip(self.przyciski, it, jt)]

    def schow_map(self):

        self.map = M.Map_window(self.obraz.get_map())
        self.map.show()

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

    def _layout_marging(self):
     
        self.mainlayout.addWidget(self.obraz)
 
        #łoczenie leyautów
        self.secendarylayout.addWidget(self.scroll)        
        self.secendarylayout.addLayout(self.kierunkowelayout)
        self.secendarylayout.addLayout(self.przyciskilayout)
        self.mainlayout.addLayout(self.secendarylayout)

    def qactiontoolbar(self,nazwa, funkcja):
            
        Button = QAction(nazwa, self) 
        #stworzenie czegos na kształt przycisku ale nie koniecznie muszacego posiadac jeden triger
        Button.triggered.connect(funkcja) 
        #dodanie trigera

        return Button 
     
    def add_ROI(self, ROI):
        
        if self.defalaut_lable != 0:
            try:
                self.vbox.removeWidget(self.defalaut_lable)
            except Exception as e:
                print(e)
            self.defalaut_lable = 0
        
        test_obcjects = ROI.get_podglond()

        self.vbox.addWidget(test_obcjects)

        self.ROI.append(ROI)

    def remove_ROI(self):

        while self.ROI != []:
            [r.kill() for r in self.ROI]

    def remove_some_ROI(self, ROI):
        
        self.vbox.removeWidget(ROI.get_podglond())

        if ROI in self.ROI:
            self.ROI.remove(ROI)

        if len(self.ROI) == 0 and self.defalaut_lable == 0:
            self.defalaut_lable = QLabel("No Region of interest marked")
            self.vbox.addWidget(self.defalaut_lable)