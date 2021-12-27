from PyQt5.QtWidgets import QLabel, QWidget, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton
from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtGui import QPainter, QBrush, QColor, QPixmap


class Prsty_Podglond(QLabel):
    '''
    Obiekt dziedziczacy z Qlabel specialnie przystosowany do wyswietlania
    miniaturki podglondu obszaru oznaczonego
    '''


    def __init__(self, obraz, wspulrzedne, *args, **kwargs):
        super(Prsty_Podglond, self).__init__(*args, **kwargs)

        # zapisanie otrzymanych nie skalibrowanych wspulrzednych
        self.wspulrzedne = wspulrzedne

        #Metoda kalibrujaca prostokat
        self._prostkat = self._stwurz_prostokat(wspulrzedne)

        #Metoda wgrywajaca podlond
        self._wwgraj(obraz)

    def _stwurz_prostokat(self, wspulrzedne):
        '''
        Prywatna metoda kalibrujaca otrzymane wspulrzedne i zwracajaca
        stworzony na ich podstawie prostokat
        :param wspulrzedne: wspulrzedne ROI'u (x0,y0,x1,y1)
        :return:QRectagle stworzony z przekazanych wspulrzednych
        '''
        skalibrowane_wspulrzedne = self._kalibracja_wspulrzednych(wspulrzedne)

        poczatkowy_naroznik = QPoint(skalibrowane_wspulrzedne[0], skalibrowane_wspulrzedne[1])
        koncowy_naroznik = QPoint(skalibrowane_wspulrzedne[2], skalibrowane_wspulrzedne[3])

        return QRect(poczatkowy_naroznik, koncowy_naroznik)

    def _kalibracja_wspulrzednych(self, rect):
        '''
        Prywatna metoda kalibrujaca prazekazane wspulrzedne Roi do przeskalowanego obrazu
        :param rect: lista zawierajaca wsoulrzedne (x0,y0,x1,y1)
        :return:skalibrowan lista wspulrzednych ROI
        '''
        # wielkosci umozliwiajace skalowanei ROI'u
        kalibracja = [6.36, 6.72, 6.33, 6.53]

        #kalibracja przekazanego Roi
        return [r / a for r, a in zip(rect, kalibracja)]

    def _wwgraj(self, obraz):
        '''
        Prywatna metoda wgrywajaca przekazaony obraz
        :param obraz: obiekt klasy Qpixmap
        :return:
        '''
        #zapisanie obrazu
        self._obraz = obraz

        #wgranie obrazu
        self.setPixmap(self._obraz)

    def update_rectagle(self, kalibracja):
        '''
        Metoda umozliwajaca wykonanie kalibracji wielkosci podglondu
        :param kalibracja: tablica kalibracji
        '''

        #skalibrowanie podfladu
        Rect = [r/a for r, a in zip(self.wspulrzedne, kalibracja)]

        #nadpisanie kwadratu oznaczonego nowo skalibrowanym
        self.rectangle = QRect(QPoint(Rect[0], Rect[1]), QPoint(Rect[2], Rect[3]))

    def paintEvent(self, QPaintEvent):
        '''
        Metoda nadpisujaca wbudowana metode QPinter z PyQt5
        wgrywajaca obraz oraz rysujaca na nim oznaczony ROI
        :param QPaintEvent: obiekt klasy event
        :return:
        '''

        # inicializacja pintera
        qp = QPainter(self)

        # rysowanie obrazu
        qp.drawPixmap(self._prostkat, self._obraz)

        # stworzenie i wgranie stylu prostokata
        qp.setBrush(QBrush(QColor(200, 10, 10, 200)))

        # rysowanie prostokątu
        qp.drawRect(self.rectangle)

    def nowy_podglond(self, obraz, wspulrzedne):

        self._wwgraj(obraz)

        self.wspulrzedne = wspulrzedne

        self._prostkat = self._stwurz_prostokat(wspulrzedne)

class Podglond_ROI(QWidget):
    '''
    Obiekt przeciozajacy obiekt klasy QWidget
    Przezentuje on oznaczony ROI oraz umozliwia interakcje z nim
    nadanie mu nazwy edyche lub usuniecie
    '''


    def __init__(self, tekst, obraz, obiekt_oznaczony, *args, **kwargs):
        super(QWidget, self).__init__(*args, **kwargs)

        # obiekt klasy Qpiuxmap zawierajacy aktualny podglad na którym oznaczono ROI
        self.obraz = obraz

        # wskaznik do obiekt clasy obszar oznaczony
        self.obiekt_oznaczony = obiekt_oznaczony

        ######################################################################################
        ##################################Przyciski i labele##################################
        ######################################################################################

        # widget zawierajacy podglad na oznaczony ROI
        self.podglond = Prsty_Podglond(self.obraz, obiekt_oznaczony.pobierz_wzgledny_rectagle())

        # widget zawierajacy nazwe ROI oraz umozliwiajacy jegj edycje
        self.name_lable = QLineEdit(tekst)
        self.name_lable.textChanged.connect(self.nowa_nazwa)

        # stworzenie opisu wspulrzednych ROI
        self._stwurz_legende()

        ######################################################################################
        ##################################Leyout##############################################
        ###################################################################################### 

        self._stworzenie_layoutow()

        self._wstawienie_widgetow_do_layoutow()

        self._polacz_layouty()

        # ustawienie głównego leyautu
        self.setLayout(self._glowny_layout)

        # stworzenie przycisków
        self.glowne_przyciski()

        # zablokowanie rozmiaru
        self.zablokuj_rozmiar()
    
    def __del__(self):
        '''
        dekonstruktor klasy usuwa on oznaczony obiekt oznaczony
        '''
        self.obiekt_oznaczony.__del__()
        self.obiekt_oznaczony = 0

    def _usun(self):
        ''' Metoda umozliwiajaca usuniecie obiektu uzywajac przycisku'''
        del self

    def _stworzenie_layoutow(self):
        '''
        Prywatna  metoda tworzaca layaouty
        '''

        self._przyciski_layout = QHBoxLayout()

        self._legenda_layout = QHBoxLayout()

        self._pole_layout = QHBoxLayout()

        self._kierunkowe_layout = QGridLayout()

        self._glowny_layout = QVBoxLayout()

        self._drugorzendny_layout = QVBoxLayout()

    def _wstawienie_widgetow_do_layoutow(self):
        '''
        Prywatna  metoda wstawiajaca widgety do layoutów
        '''
        self._legenda_layout.addWidget(self.x_label)
        self._legenda_layout.addWidget(self.x0_label)
        self._legenda_layout.addWidget(self.x1_label)

        self._legenda_layout.addWidget(self.y_label)
        self._legenda_layout.addWidget(self.y0_label)
        self._legenda_layout.addWidget(self.y1_label)

        self._pole_layout.addWidget(self.pole_label)
        self._pole_layout.addWidget(self.poleL)

        self._drugorzendny_layout.addWidget(self.name_lable)

        self._glowny_layout.addWidget(self.podglond)

    def _polacz_layouty(self):
        '''
        Prywatna  metoda łącząca layouty
        '''
        self._drugorzendny_layout.addLayout(self._legenda_layout)
        self._drugorzendny_layout.addLayout(self._pole_layout)
        self._drugorzendny_layout.addLayout(self._przyciski_layout)

        self._glowny_layout.addLayout(self._drugorzendny_layout)

        self._glowny_layout.addLayout(self._kierunkowe_layout)

    def zablokuj_rozmiar(self, x=180, y=225):
        '''
        metoda zablokowujaca rozmiar widgetu
        w celu zachowania poprawnosci rozmiaru podglondu
        :param x: szerokosc widgetu
        :param y: wysokosc widgetu
        '''
        self.setMaximumSize(x, y)
        self.setMinimumSize(x, y)

    def _stwurz_legende(self):
        '''
        prywatna metoda towrzoaca legende zawierajaca wspulrzedne ROI'u oraz jego pole
        '''
        # odczytanie wspulrzednych bezwzglednych ROI w celu wykonaniu opisu
        x, x1, y, y1 = self.obiekt_oznaczony.pobierz_niezalezne_pixele()

        #obliczenie pola ROI'u w pixelach
        p_pixele = self.pole(x, x1, y, y1)

        self.pole_label = QLabel("Pole obszaru:")
        self.poleL = QLabel(str(p_pixele))

        self.x_label = QLabel("x")
        self.x0_label = QLabel(str(x))
        self.x1_label = QLabel(str(x1))

        self.y_label = QLabel("y")
        self.y0_label = QLabel(str(y))
        self.y1_label = QLabel(str(y1))

    @staticmethod
    def przycisk(fun, text, clicable = False):
        '''
        Statyczna metoda tworzaca przycisk o zadancyh paramterach
        :param fun: fukcja wywoływana przy nacisnieciu przycisku
        :param text: napis na przycisku
        :param clicable: obcja umozliwiajaca zatrzymania stanu przycisku
        :return:
        '''

        przycisk = QPushButton()
        przycisk.setMaximumWidth(50)
        przycisk.setText(text)
        przycisk.setCheckable(clicable)
        przycisk.clicked.connect(fun)
        return przycisk

######################################################################################
##################################boton config########################################
######################################################################################

    def glowne_przyciski(self):
        '''
        Metoda tworzaca glówne przyciski
        '''

        self.przyciski = [QPushButton() for _ in range(3)]

        [self._przyciski_layout.addWidget(wartosc) for wartosc in self.przyciski]

        nazwy = ["edit", "fine edit", "del"]

        [przycisk.setText(nazwa) for nazwa, przycisk in zip(nazwy, self.przyciski)]

        funkcjie = [self.edit, self.fine_edit, self._usun]

        [b.clicked.connect(f) for b, f in zip(self.przyciski, funkcjie)]

        # ustawienie przycisku edycji jako przelocznika miedzy trybem normalnym a trybem edycji
        self.przyciski[0].setCheckable(True)

    def przyciski_kalibracyjne(self):
        '''
        Metoda umieszcajaca przyciski umozliwiajace kalibracje podglondu
        '''

        self.przyciski = [QPushButton() for _ in range(8)]

        [self._przyciski_layout.addWidget(wartosc) for wartosc in self.przyciski]

        nazwykalibracionmode = ['xp', "yp", "zp", 'sp', "xm", "ym", "zm", "sm"]

        [swich.setText(name) for name, swich in zip(nazwykalibracionmode, self.przyciski)]

        self.x, self.y, self.z, self.s = 6.36, 6.72, 6.33, 6.53

        funkalibracionmode = [self.xp, self.yp, self.zp, self.sp, self.xm, self.ym, self.zm, self.sm]
        [b.clicked.connect(f) for b, f in zip(self.przyciski, funkalibracionmode)]

    def _fine_edit_buttons(self):
            '''
            metoda tworzaca przyciski do edycji
            '''

            self.kierunkowe = [QPushButton() for _ in range(4)]

            [button.setMaximumWidth(50) for button in self.kierunkowe]

            # nazwy dla przycisków
            nazwy = ['/\\', "<", ">", '\/']
            [swich.setText(name) for name, swich in zip(nazwy, self.kierunkowe)]

            # przypiecie fukcji do przycisków
            funkcje = [self.gurny_przycisk, self.lewy_przycisk, self.prawy_przycisk, self.dolny_przycisk]

            [przycisk.clicked.connect(funkcja) for funkcja, przycisk in zip(funkcje, self.kierunkowe)]

            # dodanie do leyatów przyciskó kierunkowych
            it = [3, 2, 4, 3]
            jt = [2, 3, 3, 4]
            [self._kierunkowe_layout.addWidget(value, j, i) for j, i, value in zip(jt, it, self.kierunkowe)]

            # Przywrucenie standardowych przycisków
            self.powrut = self.przycisk(self.retyurn_to_normalbutons, "return")
            self._kierunkowe_layout.addWidget(self.powrut, 2, 2)
            self.kierunkowe.append(self.powrut)

            #przelaczanie pomiedzy ruszaniem obszarem a jego rozszerzaniem
            self.przemiesc = self.przycisk(self.przelacz_przemiesc, "przemiesc", True)
            self._kierunkowe_layout.addWidget(self.przemiesc, 2, 4)
            self.kierunkowe.append(self.przemiesc)
            
            #przelaczanie pomiedzy kierunkiem zmian
            self.zwieksz = self.przycisk(self.przelacz_zwieksz, "+", True)
            self._kierunkowe_layout.addWidget(self.zwieksz, 4, 4)
            self.kierunkowe.append(self.zwieksz)

    def usun_fine_edit(self):
        '''
        metoda usuwajaca przyciski do edycji
        '''
        [self._kierunkowe_layout.removeWidget(b) for b in self.kierunkowe]
        self.kierunkowe = 0
        self.przemiesc = 0
        self.powrut = 0
        self.zwieksz = 0

    def usun_glowne_przyciski(self):
        '''
        metoda usuwajaca glówne przyciski
        :return:
        '''
        [self._przyciski_layout.removeWidget(b) for b in self.przyciski]
        self.przyciski = 0

######################################################################################
##################################Obiekt oznaczony komunication#######################
######################################################################################

    def nowa_nazwa(self):
        '''
        metoda nadajaca nowa nazwe na glównym widoku roiu
        '''
        self.obiekt_oznaczony.ustawnazwe(self.name_lable.text())


    def odswierz_kordynaty(self):
        '''
        metoda updatujaca na bierzoco kordynaty wyswietlane na obiekcie
        '''
    
        self.podglond._wwgraj(self.obraz)
        
        x, x1, y, y1 = self.obiekt_oznaczony.pobierz_niezalezne_pixele()
        
        
        self.x0_label.setText(str(x))
        self.x1_label.setText(str(x1))

        self.y0_label.setText(str(y))
        self.y1_label.setText(str(y1))
        
        self.poleL.setText(str(self.pole(x, x1, y, y1)))

    def pole(self, x, x1, y, y1):
        '''
        fukcja liczaca pole obszaru oznaczonego
        :param x: pierwsza wspulrzedna x
        :param x1: druga wspulrzedna x
        :param y: pierwsza wspulredna y
        :param y1: druga wspulrzedna y
        :return: pole
        '''
    
        xm = min(x, x1)
        xM = max(x, x1)
        
        ym = min(y, y1)
        yM = max(y, y1)
        
        return abs(xM-xm)*abs(yM-ym)
        
######################################################################################
##################################fukcje przyciskow ##################################
######################################################################################

    def edit(self):
        '''
        Metoda przypisana do przycisku edycji wlaczajaca i wylaczajaca tryb edycji
        '''
        if self.przyciski[0].isChecked():
            self.obiekt_oznaczony.edit()

        else:
            self.obiekt_oznaczony.zakoncz_edit()

    def nowy_obraz(self, obraz):
        '''
        Metoda wgrywajaca nowy obraz i prostokat do podglondu
        :param obraz: obraz odczytany po koncu edycji
        '''
        if type(obraz) == QPixmap:
            self.obraz = obraz

        self.podglond.nowy_podglond(self.obraz, self.obiekt_oznaczony.pobierz_wzgledny_rectagle())

    def fine_edit(self):
        '''
        metoda wywolywana po nacisnieciu przycisku fine edit właczajaca tryb edycji
        z wykorzystaniem przycisków
        :return:
        '''

        self.usun_glowne_przyciski()

        self._fine_edit_buttons()

        #poprawienie ksztaltu widgetu
        self.zablokuj_rozmiar(180, 270 + 15)

    def retyurn_to_normalbutons(self):
        '''
        metoda usuwajaca przyciski do edycji i ustawiajaca przyciski standardowe
        '''

        self.usun_fine_edit()

        self.glowne_przyciski()
        self.zablokuj_rozmiar()

##########################dwutrybowe przyciski _kierunkowe############################

    def gurny_przycisk(self):
        '''
        metoda wykonywana podczas nacisniecia jednego z przycisków
        posiada 2 tryby w zaleznosci od ustawienia przelocznika przemiesc
        wywoluje odpowiednia metode obiektu oznaczonego w celu
        edycji/przemiesczenia ROI'u
        '''
        if self.przemiesc.isChecked():
            self.obiekt_oznaczony.przeksztalc_gorna_linie(self.zwieksz.isChecked())
        else:
            self.obiekt_oznaczony.przesun_w_gore()

        self.odswierz_kordynaty()

    def dolny_przycisk(self):
        '''
        metoda wykonywana podczas nacisniecia jednego z przycisków
        posiada 2 tryby w zaleznosci od ustawienia przelocznika przemiesc
        wywoluje odpowiednia metode obiektu oznaczonego w celu
        edycji/przemiesczenia ROI'u
        '''
        if self.przemiesc.isChecked():
            self.obiekt_oznaczony.przekstalc_dolna_linie(self.zwieksz.isChecked())
        else:
            self.obiekt_oznaczony.przesun_w_dul()

        self.odswierz_kordynaty()
            
    def lewy_przycisk(self):
        '''
        metoda wykonywana podczas nacisniecia jednego z przycisków
        posiada 2 tryby w zaleznosci od ustawienia przelocznika przemiesc
        wywoluje odpowiednia metode obiektu oznaczonego w celu
        edycji/przemiesczenia ROI'u
        '''
        if self.przemiesc.isChecked():
            self.obiekt_oznaczony.przekstalc_lewa_linie(self.zwieksz.isChecked())
        else:
            self.obiekt_oznaczony.przesun_w_lewo()

        self.odswierz_kordynaty()
                
    def prawy_przycisk(self):
        '''
        metoda wykonywana podczas nacisniecia jednego z przycisków
        posiada 2 tryby w zaleznosci od ustawienia przelocznika przemiesc
        wywoluje odpowiednia metode obiektu oznaczonego w celu
        edycji/przemiesczenia ROI'u
        '''
        if self.przemiesc.isChecked():
            self.obiekt_oznaczony.przekstalc_prawa_linie(self.zwieksz.isChecked())
        else:
            self.obiekt_oznaczony.przesun_w_prawo()

        self.odswierz_kordynaty()

######################################################################################
    def przelacz_przemiesc(self):
        '''
        metoda wywolyuwana przy przeloczeniu przycisku przemiesc zmienia
        napis na nim
        '''
        if self.przemiesc.isChecked():
             self.przemiesc.setText("ksztalt")

        else:
             self.przemiesc.setText("przemiesc")
             
                        
    def przelacz_zwieksz(self):
        '''
        metoda wywolyuwana przy przeloczeniu przycisku zwieksz zmienia
        napis na nim
        '''
     
        if self.zwieksz.isChecked():
            self.zwieksz.setText("-")

        else:
            self.zwieksz.setText("+")

######################################################################################
##################################metody uzyte do kalibracji podglondu################
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
