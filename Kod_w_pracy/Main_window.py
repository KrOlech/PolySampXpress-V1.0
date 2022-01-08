from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QToolBar,\
    QAction, QHBoxLayout, QVBoxLayout, QGridLayout, QWidget,\
    QLabel, QPushButton, QScrollArea
from podglad_z_kamery import Obraz_z_kamery
from Map import Map_window
from slider import Slider
from setingswindows import Okno_ustawien
from engineclass import manipulator

class Glowne_okno(QMainWindow):

    #prostokaty zaznaczone
    ROI = []

    #bazowa wartosc ile ma sie przesunac manipulator (0.1mm-1)
    krok = 10

    #zmienna przechowujaca okno mapy
    map = None
    
    #ostatni numer nadany ROI'owi
    ostatnia_nazwa = 0
    
    tekst_placeholdera = "nie oznaczono zadnego ROI'u"

    def __init__(self, *args, **kwargs):
        super(Glowne_okno, self).__init__(*args, **kwargs)
        '''
        Konstruktor glonego okna programu.
        Tworzy glowne okno nawiazuje polaczenie z kamera 
        i manipulatorem.
        Przechowuje parametry oznaczonych obszarow.
        '''

        # ustawienie ikony
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        # ustawienie tytulu okna
        self.setWindowTitle("Mapowanie probek")

        #ustawienie geometrii okna
        self.setGeometry(5, 30, 1280, 1024)

        #wylaczenie sledzenia myszki
        self.setMouseTracking(False)

        #stworzenie podgladu probki i umieszczenie go w leyaucie
        self.obraz = Obraz_z_kamery(self)

        # polaczenie z manipulatorem
        self.manipulaor = manipulator()
        self.manipulaor.glowne_okno(self)

        #stworzenie layoutow
        self._stworz_layouty()

        #stworzenie przyciskow do przemieszczania podgladu
        self._Przyciski_kierunkowe()

        self._stworz_slider()

        #stworzenie i dodanie przyciskow do wszelkich zastosowan
        self._przyciski_wielozadaniowe()

        #stworzenie i dodanie obszaru skrolowania
        self._Scroll_arrea()

        #polaczenie layoutow
        self._polacz_layouty()

        self._ustaw_centralny_widget()

        self._toolbars()

        self._upadet_position_read()

        self.obraz.odczytaj_klatke()

        self.obraz.odswierz_ofsets()

    def closeEvent(self, event):
        '''
        Dekonstruktor glownego okna zapisuje pozycje manipulatora
        oraz upewnia sie ze komunikacja z oknem zostala zatrzymana
        oraz usuwa zebrana mape
        '''

        reply = QMessageBox.question(self,"mesage",
                           "Czy napewno chcesz zamknac program?",
                           QMessageBox.Yes|QMessageBox.No,
                           QMessageBox.Yes)
        
        if reply == QMessageBox.Yes:

            del self.manipulaor
            event.accept()
            
            if self.map != None:
                del self.map
            
        else:
            event.ignore()
    
    def pobierz_manipulator(self):
        return self.manipulaor

#########################################################################
##################################Toolbars###############################
#########################################################################

    def _toolbars(self):

        '''
        metoda prywatna generujaca paski zadan do glownego okna
        '''

        #pierwszy pasek zawierajacy funkcje umozliwiajace:
        toolbar = QToolBar("Funkcje")
        self.addToolBar(toolbar)
        #zapisanie podgladu
        action_1 = self._qactiontoolbar("Odswierz obraz",
                   lambda x: self.obraz.odczytaj_klatke())
        toolbar.addAction(action_1)
        #wysrodkowanie manipulatora
        action_2 = self._qactiontoolbar("Wycentruj manipipulator", 
                   lambda x: self.manipulaor.center())
        toolbar.addAction(action_2)

        #wywolanie okna akcji
        seting_window = self._qactiontoolbar("Ustawienia osi",
                        self._ustawienia_osi)
        toolbar.addAction(seting_window)

    def _qactiontoolbar(self, nazwa, funkcja):
        '''
        metoda prywatna tworzaca Qaction 
        z podanej funkcji o podanej nazwie
        '''
            
        Button = QAction(nazwa, self) 
        
        #dodanie trigera
        Button.triggered.connect(funkcja) 
        

        return Button 
 
    def _ustawienia_osi(self):

        '''
        metoda prywatna tworzaca i otwierajaca okno ustawien
        '''

        self.ustawienia_osi = Okno_ustawien(self)
        self.ustawienia_osi.show()
        
#########################################################################
##################################Layout and widget######################
#########################################################################

    def _stworz_layouty(self):

        '''
        Prywatna metoda tworzaca layouty GUI
        '''

        #Glony layaut
        self._mainlayout = QHBoxLayout()
        
        #layaut
        self._secendarylayout = QVBoxLayout()
        
        #layauty przyciskow i opisow
        self._kierunkowelayout = QGridLayout()
        self._przyciskilayout = QGridLayout()


        self._sliderlegendslayout = QVBoxLayout()
        self._sliderlayout = QHBoxLayout()

    def _polacz_layouty(self):
        '''
        Prywatna metoda laczaca layouty GUI
        '''
        self._mainlayout.addWidget(self.obraz)
 
        #laczenie layoutow
        self._secendarylayout.addWidget(self.scroll)
        self._secendarylayout.addLayout(self._kierunkowelayout)
        self._secendarylayout.addLayout(self._sliderlayout)
        self._secendarylayout.addLayout(self._przyciskilayout)
        self._mainlayout.addLayout(self._secendarylayout)

    def _ustaw_centralny_widget(self):
        '''
        Prywatna metoda Wstawiajacca glowny layout jako glowny widget
        '''
        widget = QWidget()
        widget.setLayout(self._mainlayout)
        self.setCentralWidget(widget)

#########################################################################
############################przyciski kierunkowe#########################
#########################################################################

    def _nazwij_przyciski_kierunkowe(self):
        '''
        Prywatna metoda nadajaca nazwy przyciskom kierunkowym
        '''
        nazwy = ['/\\', "<", ">", '\/']
        [swich.setText(name) for name, swich in 
                             zip(nazwy, self._kierunkowe)]

    def _podepnij_funkcje_do_przyciskow(self):
        '''
        prywatna metoda przypisujaca funkcje
        i skroty klawiszowe do przyciskow kierunkowych
        '''

        #tablica funkcji bedaca przypisana do przyciskow
        fun = [self._key_dwn, self._key_left,
         self._key_right, self._key_up]

        #Stworzenie tablicy Qaction w celu dolaczenia 
        #skrotow klawiszowych
        self.actions = [QAction("&dw", self),
                        QAction("&lf", self), 
                        QAction("&ri", self), 
                        QAction("&up", self)]

        #przypiecie funkcji do Qactio
        [a.triggered.connect(f) for a, f in zip(self.actions, fun)]

        #tablica klawiszy kierunkowych
        keyband = [Qt.Key_Up,
                   Qt.Key_Left,
                   Qt.Key_Right,
                   Qt.Key_Down]

        #przypisanie skrotu klawiszowego do akcji
        [a.setShortcut(k) for a, k in zip(self.actions, keyband)]

        #przypisanie funkcji do przyciskow
        [swich.released.connect(f) for f, swich in zip(fun, 
                                               self._kierunkowe)]

        menu = self.menuBar()
        test = menu.addMenu("directions")
        [test.addAction(f) for f in self.actions]

    def _dodaj_przyciski_do_layout(self):
        '''
        Prywatna metoda dodajaca przyciski kierunkowe do layoutu
        '''
        it = [3, 2, 4, 3]
        jt = [2, 3, 3, 4]
        [self._kierunkowelayout.addWidget(value, j, i) for j, i, value 
                                       in zip(jt, it, self._kierunkowe)]

    def _dodaj_legende_pozycji_do_layout(self):
        '''
        Prywatna metoda tworzaca opisy pozycji manipulatora
        '''

        self.position_labele = [QLabel(str(25.0)), 
                                QLabel(str(25.0)), 
                                QLabel(str(25.0))]

        labelexyz = [QLabel("X"), QLabel("Y"), QLabel("Z")]

        [self._kierunkowelayout.addWidget(value, 7, i) for i, value 
                       in zip(range(2, 5, 1), self.position_labele)]

    def _Przyciski_kierunkowe(self):
        '''
        Prywatna metoda tworzaca przyciski kierunkowe
        Nastepnie przypisuajca im funkcje
        '''
        # stworzenie przyciskow
        self._kierunkowe = [QPushButton() for _ in range(4)]

        # zablokowanie rozmiarow przyciskow
        [button.setMaximumWidth(50) for button in self._kierunkowe]

        #nadanie nazw przyciskow
        self._nazwij_przyciski_kierunkowe()

        # przypiecie funkcji do przyciskow
        self._podepnij_funkcje_do_przyciskow()

        #dodanie do layatow przyciskow kierunkowych
        self._dodaj_przyciski_do_layout()

        #dodanie i stworzenie odczytu pozycji manipulatora
        self._dodaj_legende_pozycji_do_layout()
  
    def _key_up(self):
        '''
        metoda wywolujaca metode _key_move 
        z parametrami do przemiszczenia w gore
        '''
        self._key_move(self.manipulaor.przesun_w_gore,self.obraz.gora,3,0)
    def _key_left(self):
        '''
        metoda wywolujaca metode _key_move 
        z parametrami do przemiszczenia w lewo
        '''
        self._key_move(self.manipulaor.przesun_w_lewo, self.obraz.lewo,
                                                                   2,1)
    def _key_right(self):
        '''
        metoda wywolujaca metode _key_move 
        z parametrami do przemiszczenia w prawo
        '''
        self._key_move(self.manipulaor.przesun_w_prawo, self.obraz.prawo,
                                                                    1, 2)
    def _key_dwn(self):
        '''
        metoda wywolujaca metode _key_move
        z parametrami do przemiszczenia w dol
        '''
        self._key_move(self.manipulaor.przesun_w_dol, self.obraz.dol, 0,
                       3)
    def _key_move(self,fun_manipulator,fun_obraz, key_en, key_dis):
        '''
        Prywatna metoda wykonujaca przemieszczenie.
        :param fun_manipulator: Funkcja kierunkowa 
         wykonywana przez manipulator
        :param fun_obraz:  Funkcja kierunkowa 
        wykonywana przez obraz
        :param key_en: nr. przycisku ktory moze zostac
        odblokwany jesli bedzie mozliwe wykonanie
        ruchu w tym kierunku
        :param key_dis: nr. przycisku ktory moze zostac
        zablokowany jesli zostanie osiagniety limit
        '''
        # blokada przyciskow zeby nie wyslac dwukrotnie polecen do manipulatora
        [k.setEnabled(False) for k in self._kierunkowe]

        #Zapisanie aktualnej mapy jesli nie zostala jeszcze stworzona
        self.obraz.zapisz_aktualny_podglad()

        #wykonanie kroku na manipolatorze
        t = fun_manipulator(self.krok/10)

        #zapisanie nowych pozycji manipipulatora
        self._upadet_position_read()

        #wykonanie odpoweiedniej funkcji kierunkowej
        # na manipulatorze
        fun_obraz()

        #odblokwanie przyciskow
        [k.setEnabled(True) for k in self._kierunkowe]
        '''
        ewentualne zablokwanie przyciskow 
        jesli zostal osiagniety limit
        lub odblokwanie przycisku jesli zostal cofniety
        '''
        if t:
            self._kierunkowe[key_en].setEnabled(True)
        else:
            self._kierunkowe[key_dis].setEnabled(False)

    def _upadet_position_read(self):
        '''
        Prywatna metoda wpisujaca odczytanie nowej
        pozycji manipulatora
        '''
        [label.setText(str(position)) for label, position 
                           in zip(self.position_labele,
                                  self.manipulaor.pobierz_pozycje_osi())]
#########################################################################
########################przyciski wielozadaniowe#########################
#########################################################################
    def _podlacz_functie_do_przyciskow_wielozadaniowych(self):
        '''
        Prywatna metoda 
        przypinajaca funkcje do przyciskow wielozadaniowych
        '''
        self.przyciski[0].clicked.connect(self.obraz.nastempny)
        self.przyciski[1].clicked.connect(self.usun_ROI)
        self.przyciski[2].clicked.connect(self.obraz.narysuj_calosc)
        self.przyciski[3].clicked.connect(self.obraz.poprzedni)
        self.przyciski[4].clicked.connect(self.pokaz_mape)
        self.przyciski[5].clicked.connect(self.obraz.schowajcalosc)
        self.przyciski[6].setCheckable(True)
        self.przyciski[6].clicked.connect(
        self.przelacz_tryb_move_on_pres)
        self.przyciski[7].clicked.connect(
        self.manipulaor.simple_stop)
        self.przyciski[8].clicked.connect(self.obraz.reset_map)

    def _nazwij_przyciski_wielozadaniowe(self):
        '''
        Przypisanie nazw do wielozadaniowych przyciskow
        '''

        nazwy = ["Nastempny", "Usun ROI", 
                 "Wszystkie", "Poprzedni",
                 "Mapa", "Zadne", 
                 "Przemiesc to", "Stop",
                 "Wyczysc mape"]

        [switch.setText(name) for name, switch 
                              in zip(nazwy, self.przyciski)]

    def _dodaj_przyciski_wielozadaniowe_do_layout(self):
        '''
        Prywatna metoda dodajaca przyciski wielozadaniowe do layoutu
        '''
        it = [2, 3, 4, 2, 3, 4, 2, 3, 4]
        jt = [5, 5, 5, 6, 6, 6, 7, 7, 7]
        [self._przyciskilayout.addWidget(w, j, i) for w, i, j 
                                         in zip(self.przyciski, it, jt)]

    def _przyciski_wielozadaniowe(self):
        '''
        Prywatna metoda tworzaca i organizujaca
        przyciski wielozadaniowe
        '''
        #przyciski multipurpous
        self.przyciski = [QPushButton() for _ in range(9)]

        [button.setMaximumWidth(100) for button in self.przyciski]

        self._nazwij_przyciski_wielozadaniowe()

        self._podlacz_functie_do_przyciskow_wielozadaniowych()

        #dodanie przyciskow
        self._dodaj_przyciski_wielozadaniowe_do_layout()

    def pokaz_mape(self):
        '''
        Wyswietlenie mapy probki
        ewentualne jej stworzenie jesli jeszcze nie zostala stworzona
        '''

        if self.map is None:
            self.map = Map_window(self.obraz.ponbierz_map(), self)
            self.map.show()
        else:
            self.map.new_image(self.obraz.ponbierz_map())
            self.map.show()

    def przelacz_tryb_move_on_pres(self):

        '''
        Metoda obslugujaca centrowanie podgladu 
        na wybranym fragmencie
        '''

        if self.przyciski[6].isChecked():
             
             if self.map is not None:
                self.map.move_to_point = True
             self.obraz.przemiesc_sie_do_pktu = True

        else:  
             if self.map is not None:
                self.map.move_to_point = False
             self.obraz.przemiesc_sie_do_pktu = False

#########################################################################
##########################Scroll area####################################
#########################################################################

    def _Scroll_arrea(self):
        '''
        Prywatna metoda tworzaca obszar przewijany umozliwiajacy
        podglad labeli opisujacych oznaczone obszary
        '''
        self.defalaut_lable = QLabel(self.tekst_placeholdera)
            
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

#########################################################################
##########################zarzodzanie Roi'ami############################
#########################################################################

    def dodaj_ROI(self, ROI):
        '''
        Metoda obslugujaca dodanie nowego obszaru zaintesowania
        :param ROI: Obniekt ROI
        '''

        #obsluzenie usuwania domyslnej etykiety
        if self.defalaut_lable != 0:
            try:
                self.vbox.removeWidget(self.defalaut_lable)
            except Exception as e:
                print(e)
            self.defalaut_lable = 0

        #dodanie podgladu ROI
        self.vbox.addWidget(ROI.pobierz_podglad())

        #dodanie ROia do listy ROI
        self.ROI.append(ROI)

    def usun_ROI(self):
        '''
        Metoda usuwajaca wszystkie oznaczone obszary
        '''

        #zapytanie uzytkownika czy na pewno chce to zrobic
        reply = QMessageBox.question(self,"mesage",
                "Czy na pewno chcesz usunac wszystkie oznaczone ROI?",
                QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
                                     
        if reply == QMessageBox.Yes:
            while self.ROI != []:
                [r.__del__() for r in self.ROI]

    def usun_wybrany_ROI(self, ROI):
        '''
        metoda usuwajaca podany ROI
        :param ROI: obiekt klasy ROI
        :return:
        '''
        
        try:
            #usuniecie podgladu
            self.vbox.removeWidget(ROI.pobierz_podglad())
        except AttributeError:
            pass

        #usuniecie ROI'a z listy
        if ROI in self.ROI:
            self.ROI.remove(ROI)

        #wrzucenie placeholdera jesli nie ma ROI
        if len(self.ROI) == 0 and self.defalaut_lable == 0:
            self.defalaut_lable = QLabel(self.tekst_placeholdera)
            self.vbox.addWidget(self.defalaut_lable)

#########################################################################
##########################Zarzadzanie Sliderem###########################
#########################################################################

    def _stworz_slider(self):
        '''
        Metoda dodajaca slider osi Z
        '''
        x = self.manipulaor.pobierz_pozycje_osi('x')[0]
        self.slide = Slider(self, x - 5, x + 5, x, Qt.Horizontal)

        self._sliderlayout.addWidget(self.slide)

    def ustaw_krok(self, value):
        '''
        Metoda ustawiajaca krok dla manipulatora
        :param value: wartosc liczbowa
        '''

        self.krok = value
