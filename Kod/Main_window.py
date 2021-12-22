from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from Viue_label import Obraz
from Map import Map_window
from engineclass import manipulator
from time import sleep
from slider import Slider
from setingswindows import axissetingwindow


class MainWindow(QMainWindow):

    #prostokonty zaznaczone
    ROI = []

    #bazowa wartosc ile ma sie przesunac manipulator (0.1mm-1)
    krok = 10

    #zmiena przechowujaca okno mapy
    map = None
    
    #ostatni numer nadany ROI'owi
    last_name = 0

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        '''
        Konstruktor glónego okna programu. Tworzy głowne okno nawiozuje poloczenie z kamera i manipulatorem.
        Przechowuje parametry oznaczonych obszarów.
        '''

        # ustawienie ikony
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        # ustawienie tytulu okna
        self.setWindowTitle("Mapowanie prubek")

        #ustawienie geometri okna
        self.setGeometry(5, 30, 1280, 1024)

        #wyłoczenie sledzenia myszki
        self.setMouseTracking(False)

        #stworzenie podglondu prubki i umiescenie go w leyaucie
        self.obraz = Obraz(self)

        # linking to manipulator for movment
        self.manipulaor = manipulator(self)
                
        #creating leyaut conteeiners for Gui formation
        self._createleyouts()

        #stworzenie przycisków do przemiesczania podglondu
        self._direction_buttons()
        
        #X axis slieder
        self._slider_create()

        #stworzenie i dodanie przycisków do wszelkich zastosowan
        self._multipurpos_butons()

        #stworzenie i dodanie obszaru skrolowania
        self._Scroll_arrea()

        #połoczenie leyoutów
        self._layout_marging()

        self._set_central_widget()

        self._toolbars()

        self._upadet_position_read()
        
        self.obraz.snap_img()
        
        self.obraz.update_ofsets()

    def closeEvent(self, event):
        '''
        Dekonstruktor glownego okna zapisuje pozycje manipulatora
        oraz upewnia sie ze komunikacja z oknem została zatrzymana
        oraz usuwa zebrana mape
        '''

        reply = QMessageBox.question(self,"mesage","Czy napewno chcesz zamknac program?",
                                     QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
        
        
        
        if reply == QMessageBox.Yes:
            #self.manipulaor.close_connection()
            del self.manipulaor
            event.accept()
            
            if self.map != None:
                del self.map
            
        else:
            event.ignore()

######################################################################################
##################################Toolbars############################################
######################################################################################

    def _toolbars(self):
        '''
        metoda prywatna generujaca toolbary do glónego okna
        '''

        #pierwszy toolbar zawierajacy fukcje umozliwiajace:
        toolbar = QToolBar("Funkcje")
        self.addToolBar(toolbar)
        #zapisanie podglondu
        action_6 = self._qactiontoolbar("Snap img", lambda x: self.obraz.snap_img())
        toolbar.addAction(action_6)
        #wysrodkowanie manipulatora
        action_7 = self._qactiontoolbar("center", lambda x: self.manipulaor.center())
        toolbar.addAction(action_7)

        #ywołanei okna akcji
        seting_window = self._qactiontoolbar("Ustawienia osi", self._setings_for_axis)
        toolbar.addAction(seting_window)

    def _qactiontoolbar(self,nazwa, funkcja):

        '''
        metoda prywatna tworzoca Qaction z podanej fukcji o ponanej nazwie
        '''
            
        Button = QAction(nazwa, self) 
        #stworzenie czegos na kształt przycisku ale nie koniecznie muszacego posiadac jeden triger
        Button.triggered.connect(funkcja) 
        #dodanie trigera

        return Button 
 
    def _setings_for_axis(self):
        '''
        metoda prywatna tworzaca i otwierajaca okno ustawien
        '''

        self.axissetings = axissetingwindow(self)
        self.axissetings.show()
        
######################################################################################
##################################Leyout and widget###################################
######################################################################################

    def _createleyouts(self):
        '''
        Prywatna metoda tworzoca leyouty GUI
        '''

        #Głóny leyaut
        self._mainlayout = QHBoxLayout()
        
        #leyaut
        self._secendarylayout = QVBoxLayout()
        
        #leyauty przycisków i opisów
        self._kierunkowelayout = QGridLayout()
        self._przyciskilayout = QGridLayout()


        self._sliderlegendsleyout = QVBoxLayout()
        self._sliderleyout = QHBoxLayout()

    def _layout_marging(self):
        '''
        Prywatna metoda łączoca leyouty GUI
        '''
        self._mainlayout.addWidget(self.obraz)
 
        #łoczenie leyautów
        self._secendarylayout.addWidget(self.scroll)
        self._secendarylayout.addLayout(self._kierunkowelayout)
        self._secendarylayout.addLayout(self._sliderleyout)
        self._secendarylayout.addLayout(self._przyciskilayout)
        self._mainlayout.addLayout(self._secendarylayout)

    def _set_central_widget(self):
        '''
        Prywatna metoda Wstawiajacca glówny leyout jako glówny widget
        '''
        widget = QWidget()
        widget.setLayout(self._mainlayout)
        self.setCentralWidget(widget)

######################################################################################
############################Direction buttons#########################################
######################################################################################

    def _name_direction_buttons(self):
        '''
        Prywatna metoda nadajaca nazwy przyciska kierunkowym
        '''
        nazwy = ['/\\', "<", ">", '\/']
        [swich.setText(name) for name, swich in zip(nazwy, self._kierunkowe)]

    def _conect_function_to_butons(self):
        '''
        prywatna metoda przypisujaca fukcje i skruty klawiszowe do przycisków kierunkowych
        '''

        #tablica fukcji bendaca przypisana do przycisków
        fun = [self._key_dwn, self._key_left, self._key_right, self._key_up]

        #Stworzenie tablicy Qaction w celu doloczenia skrutów klawiszowych
        self.actions = [QAction("&dw", self), QAction("&lf", self), QAction("&ri", self), QAction("&up", self)]

        #przypiecie fukcji do Qactio
        [a.triggered.connect(f) for a, f in zip(self.actions, fun)]

        #tablica klawiszy kierunkowych
        keyband = [Qt.Key_Up, Qt.Key_Left, Qt.Key_Right, Qt.Key_Down]

        #przypisanie skrutu klawiszowego do akcji
        [a.setShortcut(k) for a, k in zip(self.actions, keyband)]

        #przypisanie fukcji do przycisków
        [swich.released.connect(f) for f, swich in zip(fun, self._kierunkowe)]

        menu = self.menuBar()
        test = menu.addMenu("directions")
        [test.addAction(f) for f in self.actions]

    def _add_buton_to_leyout(self):
        '''
        Prywatna metoda doajaca przyciski kierunkowe do leyoutu
        '''
        it = [3, 2, 4, 3]
        jt = [2, 3, 3, 4]
        [self._kierunkowelayout.addWidget(value, j, i) for j, i, value in zip(jt, it, self._kierunkowe)]

    def _add_position_label_to_layout(self):
        '''
        Prywatna metoda tworzoca opisy pozycji manipulatora
        '''

        self.position_labele = [QLabel(str(25.0)), QLabel(str(25.0)), QLabel(str(25.0))]

        labelexyz = [QLabel("X"), QLabel("Y"), QLabel("Z")]
        [self._kierunkowelayout.addWidget(value, 7, i) for i, value in zip(range(2, 5, 1), self.position_labele)]

    def _direction_buttons(self):#Przyciski _kierunkowe
        '''
        Prywatna metoda tworzoca przyciski kierunkowe przypisuajca in fukcje
        '''


        # stworzenie przycisków
        self._kierunkowe = [QPushButton() for _ in range(4)]

        # zablokowanei rozmiarów przycisków
        [button.setMaximumWidth(50) for button in self._kierunkowe]

        #nadanie nazw przyciska
        self._name_direction_buttons()

        # przypiecie fukcji do przycisków
        self._conect_function_to_butons()

        #dodanie do leyatów przyciskó kierunkowych
        self._add_buton_to_leyout()

        #ddoanie i stworzenie odczytu pozycji manipulatora
        self._add_position_label_to_layout()
  
    def _key_up(self):
        '''
        metoda wyolujaca metode _key_move z parametrami do przemiczenia w gure
        '''
        self._key_move(self.manipulaor.move_up, self.obraz.up, 3, 0)

    def _key_left(self):
        '''
        metoda wyolujaca metode _key_move z parametrami do przemiczenia w lewo
        '''
        self._key_move(self.manipulaor.move_left, self.obraz.left, 2, 1)

    def _key_right(self):
        '''
        metoda wyolujaca metode _key_move z parametrami do przemiczenia w prawo
        '''
        self._key_move(self.manipulaor.move_right, self.obraz.right, 1, 2)
   
    def _key_dwn(self):
        '''
        metoda wyolujaca metode _key_move z parametrami do przemiczenia w duł
        '''
        self._key_move(self.manipulaor.move_dwn, self.obraz.dawn, 0, 3)
  
    def _key_move(self,fun_manipulator,fun_obraz, key_en, key_dis):
        '''
        Prywatna metoda wykonujaca przemiesczenie.
        :param fun_manipulator: Fukcja kierunkowa wykonywana przez manipulator
        :param fun_obraz:  Fukcja kierunkowa wykonywana przez obraz
        :param key_en: nr. przycisku który moze zostac odblokwany jesli bedzie mozliwe wykonanie rucy w tym kierunku
        :param key_dis: nr. przycisku który wywołał fuukcje jesli zostanie osiogniety limit
        '''

        #blokadaw wsttkich przycisków zeby nie wysłac 2krotnie polecen do manipulatora
        [k.setEnabled(False) for k in self._kierunkowe]

        #Zapisanei aktualnej mapy jesli nie została jesce stworzona
        self.obraz.save_curent_viue()

        #wykonanie kroku na manipolatorze
        t = fun_manipulator(self.krok/10)

        #zapisanei nowych pozuycji manipipulatora
        self._upadet_position_read()

        #wykonanie odpoweiedniej fukcji kierunkowej na manipulatorze
        fun_obraz()

        #odblokwanie przycisków
        [k.setEnabled(True) for k in self._kierunkowe]

        #ewentualne zablokwanie przycisków jesli został osiongniety limit
        #lub odblokwanie przycisku jesli został cofniety
        if t:
            self._kierunkowe[key_en].setEnabled(True)
        else:
            self._kierunkowe[key_dis].setEnabled(False)

    def _upadet_position_read(self):
        '''
        Prywatna metoda wpisujaca odczytane nowe pozycje manipulatora
        '''
        [label.setText(str(position)) for label, position in zip(self.position_labele,self.manipulaor.get_axes_positions())]

######################################################################################
##########################multipurpus buttons#########################################
######################################################################################

    def _conect_function_to_multipurpos_butons(self):

        '''
        Prywatna metoda przypinajaca fukcje do przycisków wielozadaniowych
        '''

        self.przyciski[0].clicked.connect(self.obraz.next)

        self.przyciski[1].clicked.connect(self.remove_ROI)

        self.przyciski[2].clicked.connect(self.obraz.narysujcaloscs)

        self.przyciski[3].clicked.connect(self.obraz.last)

        self.przyciski[4].clicked.connect(self.show_map)

        self.przyciski[5].clicked.connect(self.obraz.schowajcalosc)

        self.przyciski[6].setCheckable(True)
        self.przyciski[6].clicked.connect(self.togle_move_on_pres)

        self.przyciski[7].clicked.connect(self.manipulaor.simple_stop)

        self.przyciski[8].clicked.connect(self.obraz.reset_map)

    def _name_multiporpos_buttons(self):
        '''
        Przypisanie nazw do wielozadaniowych przycisków
        '''

        nazwy = ["show next", "dell all", "show all", "show privius", "map", "hide all", "move to", "stop", "map clear"]

        [switch.setText(name) for name, switch in zip(nazwy, self.przyciski)]

    def _add_direction_buton_to_leyout(self):
        '''
        Prywatna metoda doajaca przyciski wielozadaniowe do leyoutu
        '''
        it = [2, 3, 4, 2, 3, 4, 2, 3, 4]
        jt = [5, 5, 5, 6, 6, 6, 7, 7, 7]
        [self._przyciskilayout.addWidget(w, j, i) for w, i, j in zip(self.przyciski, it, jt)]

    def _multipurpos_butons(self):
        '''
        Prywatna metoda tworzoca i organizujaca przyciski wielozadaniowe
        '''
        #przyciski multipurpus
        self.przyciski = [QPushButton() for _ in range(9)]

        [button.setMaximumWidth(100) for button in self.przyciski]

        self._name_multiporpos_buttons()

        self._conect_function_to_multipurpos_butons()

        #dodanie przycisków
        self._add_direction_buton_to_leyout()

    def show_map(self):
        '''
        Wyswietlenie mapy prybki i ewentualne stworzenie jej jesli jesce nie została stworzona
        '''

        if self.map is None:
            self.map = Map_window(self.obraz.get_map(), self, self.obraz.ofsetx, self.obraz.ofsetx,)
            self.map.show()
        else:
            self.map.new_image(self.obraz.get_map())
            self.map.show()

    def togle_move_on_pres(self):

        '''
        Metoda obslugujaca centrowanie podglondu na wybranym fragmecei
        '''

        if self.przyciski[6].isChecked():
             # setting background color to light-blue
             self.przyciski[6].setStyleSheet("background-color : lightblue")
             
             if self.map is not None:
                self.map.move_to_point = True
             self.obraz.move_to_point = True

             

        else:
             # set background color back to light-grey
             self.przyciski[6].setStyleSheet("background-color : lightgrey")


             
             if self.map is not None:
                self.map.move_to_point = False
             self.obraz.move_to_point = False

######################################################################################
##########################Scroll area#################################################
######################################################################################O

    def _Scroll_arrea(self):
        '''
        Prywatna metoda tworzoca obszar przewijany umozliwiajacy podglond labeli opisujacych oznaczone obszary
        '''
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
        '''
        Metoda obslugujaca dodawnie nowego obsaru zaintesowania
        :param ROI: Obniekt ROI
        '''

        #obsluzenie usuwania defaltowego labela
        if self.defalaut_lable != 0:
            try:
                self.vbox.removeWidget(self.defalaut_lable)
            except Exception as e:
                print(e)
            self.defalaut_lable = 0

        #dodanie podglondu ROI
        self.vbox.addWidget(ROI.get_podglond())

        #dodanie ROia do listy ROI
        self.ROI.append(ROI)

    def remove_ROI(self):
        '''
        Metoda usuwajaca wsystkie oznaczone obszary
        '''

        #zapytanei uzytkownika czy napewno chce to zrobic
        reply = QMessageBox.question(self,"mesage","Czy napewno chcesz usunac wsystkie oznaczone ROI?",
                                     QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
                                     
        if reply == QMessageBox.Yes:
            while self.ROI != []:
                [r.kill() for r in self.ROI]

    def remove_some_ROI(self, ROI):
        '''
        metoda usuwajaca podany ROI
        :param ROI: obiekt klasy ROI
        :return:
        '''

        #usuniecie podglondu
        self.vbox.removeWidget(ROI.get_podglond())

        #usuniecie ROI'a z listy
        if ROI in self.ROI:
            self.ROI.remove(ROI)

        #wrzucenie plasholdera jesli nie ma ROI
        if len(self.ROI) == 0 and self.defalaut_lable == 0:
            self.defalaut_lable = QLabel("No Region of interest marked")
            self.vbox.addWidget(self.defalaut_lable)

######################################################################################
##########################Slider menagment############################################
######################################################################################

    def _slider_create(self):
        '''
        Metoda doajaca slider osi Z
        '''
        x = self.manipulaor.get_axes_positions('x')[0]
        self.slide = Slider(self, x - 5, x + 5, x, Qt.Horizontal)

        self._sliderleyout.addWidget(self.slide)

    def setkrok(self,value):
        '''
        Metoda ustrawiajaca krok dla manipulatora
        :param value: wartosc liczbowa
        '''

        self.krok = value
