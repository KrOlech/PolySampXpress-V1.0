from PyQt5.QtWidgets import QLabel, QWidget, QLineEdit,\
     QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton
from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtGui import QPainter, QBrush, QColor, QPixmap


class Prosty_Podglad(QLabel):

    '''
    Obiekt dziedziczacy z Qlabel specjalnie przystosowany
    do wyswietlania
    miniaturki podgladu obszaru oznaczonego
    '''

    def __init__(self, obraz, wspolrzedne, *args, **kwargs):
        super(Prosty_Podglad, self).__init__(*args, **kwargs)

        # zapisanie otrzymanych nie skalibrowanych wspolrzednych
        self.wspolrzedne = wspolrzedne

        #Metoda kalibrujaca prostokat
        self._prostkat = self._stworz_prostokat(wspolrzedne)

        #Metoda wgrywajaca podlad
        self._wgraj(obraz)

    def _stworz_prostokat(self, wspolrzedne):

        '''
        Prywatna metoda kalibrujaca otrzymane wspolrzedne
        i zwracajaca stworzony na ich podstawie prostokat
        :param wspolrzedne: wspolrzedne ROI'u (x0,y0,x1,y1)
        :return:QRectagle stworzony z przekazanych wspolrzednych
        '''

        skalibrowane_wspolrzedne = self._kalibracja_wspolrzednych(
                                                    wspolrzedne)

        poczatkowy_naroznik = QPoint(skalibrowane_wspolrzedne[0],
                                     skalibrowane_wspolrzedne[1])

        koncowy_naroznik = QPoint(skalibrowane_wspolrzedne[2],
                                  skalibrowane_wspolrzedne[3])

        return QRect(poczatkowy_naroznik, koncowy_naroznik)

    def _kalibracja_wspolrzednych(self, rect):

        '''
        Prywatna metoda kalibrujaca prazekazane wspolrzedne
        Roi do przeskalowanego obrazu
        :param rect: lista zawierajaca wspolrzedne (x0,y0,x1,y1)
        :return:skalibrowan lista wspolrzednych ROI
        '''

        # wielkosci umozliwiajace skalowanei ROI'u
        kalibracja = [6.36, 6.72, 6.33, 6.53]

        #kalibracja przekazanego Roi
        return [r / a for r, a in zip(rect, kalibracja)]

    def _wgraj(self, obraz):
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
        Metoda umozliwiajaca wykonanie kalibracji wielkosci podgladu
        :param kalibracja: tablica kalibracji
        '''

        #skalibrowanie podgladu
        Rect = [r / a for r, a in zip(self.wspolrzedne, kalibracja)]

        #nadpisanie prostokata oznaczonego nowo skalibrowanym
        self.rectangle = QRect(QPoint(Rect[0], Rect[1]), 
                               QPoint(Rect[2], Rect[3]))

    def paintEvent(self, QPaintEvent):
        '''
        Metoda nadpisujaca wbudowana metode QPinter z PyQt5
        wgrywajaca obraz oraz rysujaca na nim oznaczony ROI
        :param QPaintEvent: obiekt klasy event
        :return:
        '''

        # inicjalizacja pintera
        qp = QPainter(self)

        # rysowanie obrazu
        qp.drawPixmap(self.rect(), self._obraz)

        # stworzenie i wgranie stylu prostokata
        qp.setBrush(QBrush(QColor(200, 10, 10, 200)))

        # rysowanie prostokatu
        qp.drawRect(self._prostkat)

    def nowy_podglad(self, obraz, wspolrzedne):
        '''
        metoda odswierzajaca podglad
        :param obraz: nowy podglad
        :param wspolrzedne: nowe wspolrzedne ROI
        '''

        self._wgraj(obraz)

        self.wspolrzedne = wspolrzedne

        self._prostkat = self._stworz_prostokat(wspolrzedne)


class Podglad_ROI(QWidget):
    '''
    Obiekt przeciazajacy obiekt klasy QWidget
    Przezentuje on oznaczony ROI oraz umozliwia interakcje z nim
    nadanie mu nazwy edycje lub usuniecie
    '''


    def __init__(self, tekst, obraz, obiekt_oznaczony, *args, **kwargs):
        super(QWidget, self).__init__(*args, **kwargs)

        # obiekt klasy Qpiuxmap zawierajacy aktualny podglad 
        # na ktorym oznaczono ROI
        self.obraz = obraz

        # wskaznik do obiekt clasy obszar oznaczony
        self.obiekt_oznaczony = obiekt_oznaczony

#########################################################################
#############################Przyciski i labele##########################
#########################################################################

        # widget zawierajacy podglad na oznaczony ROI
        self.podglad = Prosty_Podglad(self.obraz, obiekt_oznaczony.\
                                      pobierz_wzgledny_rectagle())

        #widget zawierajacy nazwe ROI oraz umozliwiajacy jego edycje
        self.name_lable = QLineEdit(tekst)
        self.name_lable.textChanged.connect(self.nowa_nazwa)

        # stworzenie opisu wspolrzednych ROI
        self._stworz_legende()

#########################################################################
#############################Layout######################################
#########################################################################

        self._stworzenie_layoutow()

        self._wstawienie_widgetow_do_layoutow()

        self._polacz_layouty()

        # ustawienie glownego layoutu
        self.setLayout(self._glowny_layout)

        # stworzenie przyciskow
        self.glowne_przyciski()

        # zablokowanie rozmiaru
        self.zablokuj_rozmiar()
    
    def __del__(self):
        '''
        dekonstruktor klasy usuwa on oznaczony obiekt
        '''
        try:
            self.obiekt_oznaczony.usun()
            self.obiekt_oznaczony = 0
        except AttributeError:
            pass

    def _usun(self):
        ''' 
        Metoda umozliwiajaca usuniecie obiektu uzywajac przycisku
        '''
        
        try:
            self.obiekt_oznaczony.usun()
            self.obiekt_oznaczony = 0
        except AttributeError:
            pass

    def _stworzenie_layoutow(self):
        '''
        Prywatna metoda tworzaca layaouty
        '''

        self._przyciski_layout = QHBoxLayout()

        self._legenda_layout = QHBoxLayout()

        self._pole_layout = QHBoxLayout()

        self._kierunkowe_layout = QGridLayout()

        self._glowny_layout = QVBoxLayout()

        self._drugorzedny_layout = QVBoxLayout()

    def _wstawienie_widgetow_do_layoutow(self):
        '''
        Prywatna metoda wstawiajaca widgety do layoutow
        '''
        
        self._legenda_layout.addWidget(self.x_label)
        self._legenda_layout.addWidget(self.x0_label)
        self._legenda_layout.addWidget(self.x1_label)

        self._legenda_layout.addWidget(self.y_label)
        self._legenda_layout.addWidget(self.y0_label)
        self._legenda_layout.addWidget(self.y1_label)

        self._pole_layout.addWidget(self.pole_label)
        self._pole_layout.addWidget(self.poleL)

        self._drugorzedny_layout.addWidget(self.name_lable)

        self._glowny_layout.addWidget(self.podglad)

    def _polacz_layouty(self):
        '''
        Prywatna metoda laczaca layouty
        '''
   
        self._drugorzedny_layout.addLayout(self._legenda_layout)
        self._drugorzedny_layout.addLayout(self._pole_layout)
        self._drugorzedny_layout.addLayout(self._przyciski_layout)

        self._glowny_layout.addLayout(self._drugorzedny_layout)

        self._glowny_layout.addLayout(self._kierunkowe_layout)


    def zablokuj_rozmiar(self, x=180, y=225):
        '''
        metoda zablokowujaca rozmiar widgetu
        w celu zachowania poprawnosci rozmiaru podgladu
        :param x: szerokosc widgetu
        :param y: wysokosc widgetu
        '''
        
        self.setMaximumSize(x, y)
        self.setMinimumSize(x, y)


    def _stworz_legende(self):
        '''
        prywatna metoda towrzoaca legende zawierajaca wspolrzedne 
        ROI'u oraz jego pole
        '''
        
        # odczytanie wspolrzednych bezwzglednych 
        # ROI w celu wykonaniu opisu
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
    def przycisk(fun, text, clicable=False):
        '''
        Statyczna metoda tworzaca przycisk o zadancyh parametrach
        :param fun: funkcja wywolywana przy nacisnieiu przycisku
        :param text: napis na przycisku
        :param clicable: opcja umozliwiajaca zatrzymania stanu
        przycisku
        :return:
        '''

        przycisk = QPushButton()
        przycisk.setMaximumWidth(50)
        przycisk.setText(text)
        przycisk.setCheckable(clicable)
        przycisk.clicked.connect(fun)
        return przycisk


#########################################################################
#########################konfiguracja przyciskow#########################
#########################################################################

    def glowne_przyciski(self):
        '''
        Metoda tworzaca glowne przyciski
        '''

        self.przyciski = [QPushButton() for _ in range(3)]

        [self._przyciski_layout.addWidget(wartosc) for wartosc 
                                              in self.przyciski]

        nazwy = ["edit", "fine edit", "del"]

        [przycisk.setText(nazwa) for nazwa, przycisk 
                                 in zip(nazwy, self.przyciski)]

        funkcjie = [self.edit, self.fine_edit, self._usun]

        [b.clicked.connect(f) for b, f in zip(self.przyciski, funkcjie)]
  
        # ustawienie przycisku edycji jako przelacznika 
        # miedzy trybem normalnym a trybem edycji
        self.przyciski[0].setCheckable(True)

    def przyciski_kalibracyjne(self):
        '''
        Metoda umieszczajaca przyciski
        umozliwiajace kalibracje podgladu
        '''

        self.przyciski = [QPushButton() for _ in range(8)]

        [self._przyciski_layout.addWidget(wartosc) for wartosc 
                                                   in self.przyciski]

        nazwykalibracionmode = ['xp', "yp", "zp", 'sp',
              "xm", "ym", "zm", "sm"]

        [swich.setText(name) for name, swich in 
                    zip(nazwykalibracionmode, self.przyciski)]

        self.x, self.y, self.z, self.s = 6.36, 6.72, 6.33, 6.53

        funkalibracionmode = [self.xp, self.yp, self.zp, self.sp,
                              self.xm, self.ym, self.zm, self.sm]

        [b.clicked.connect(f) for b, f in
                    zip(self.przyciski, funkalibracionmode)]

    def _fine_edit_buttons(self):
            '''
            metoda tworzaca przyciski do edycji
            '''

            self.kierunkowe = [QPushButton() for _ in range(4)]

            [button.setMaximumWidth(50) for button in self.kierunkowe]


            # nazwy dla przyciskow
            nazwy = ['/\\', "<", ">", '\/']
            [swich.setText(name) for name, swich 
                                in zip(nazwy, self.kierunkowe)]

            # przypiecie funkcji do przyciskow
            funkcje = [self.gorny_przycisk, self.lewy_przycisk,
                       self.prawy_przycisk, self.dolny_przycisk]

            [przycisk.clicked.connect(funkcja) for funkcja, przycisk
                                        in zip(funkcje, self.kierunkowe)]

            # dodanie do layautow przyciskow kierunkowych
            it = [3, 2, 4, 3]
            jt = [2, 3, 3, 4]
            [self._kierunkowe_layout.addWidget(value, j, i) 
               for j, i, value in zip(jt, it, self.kierunkowe)]

            # Przywrocenie standardowych przyciskow
            self.powrot = self.przycisk(self.retyurn_to_normalbutons, 
                                                              "return")
            self._kierunkowe_layout.addWidget(self.powrot, 2, 2)
            self.kierunkowe.append(self.powrot)

            #przelaczanie pomiedzy ruszaniem ROI'em a jego rozszerzaniem
            self.przemiesc = self.przycisk(self.przelacz_przemiesc, 
                                                   "przemiesc", True)

            self._kierunkowe_layout.addWidget(self.przemiesc, 2, 4)
            self.kierunkowe.append(self.przemiesc)

            #przelaczanie pomiedzy kierunkiem zmian
            self.zwieksz = self.przycisk(self.przelacz_zwieksz,"+",True)

            self._kierunkowe_layout.addWidget(self.zwieksz, 4, 4)
            self.kierunkowe.append(self.zwieksz)


    def usun_fine_edit(self):
        '''
        metoda usuwajaca przyciski do edycji
        '''

        [self._kierunkowe_layout.removeWidget(b) for b in self.kierunkowe]
        self.kierunkowe = 0
        self.przemiesc = 0
        self.powrot = 0
        self.zwieksz = 0

    def usun_glowne_przyciski(self):
        '''
        metoda usuwajaca glowne przyciski
        :return:
        '''

        [self._przyciski_layout.removeWidget(b) for b in self.przyciski]
        self.przyciski = 0



#########################################################################
####################Obiekt oznaczony komunicacia#########################
#########################################################################
    def nowa_nazwa(self):
        '''
        metoda nadajaca nowa nazwe na glownym widoku roi'u
        '''
        self.obiekt_oznaczony.ustaw_nazwe(self.name_lable.text())


    def odswierz_kordynaty(self):
        '''
        metoda odswiezajca na biezaco 
        koordynaty wyswietlane na obiekcie
        '''

        self.podglad._wgraj(self.obraz)

        x, x1, y, y1 = self.obiekt_oznaczony.pobierz_niezalezne_pixele()
        
        
        self.x0_label.setText(str(x))
        self.x1_label.setText(str(x1))

        self.y0_label.setText(str(y))
        self.y1_label.setText(str(y1))
        
        self.poleL.setText(str(self.pole(x, x1, y, y1)))

    def pole(self, x, x1, y, y1):
        '''
        funkcja liczaca pole obszaru oznaczonego
        :param x: pierwsza wspolrzedna x
        :param x1: druga wspolrzedna x
        :param y: pierwsza wspolrzedna y
        :param y1: druga wspolrzedna y
        :return: pole
        '''
    
        xm = min(x, x1)
        xM = max(x, x1)
        
        ym = min(y, y1)
        yM = max(y, y1)
        
        return abs(xM-xm)*abs(yM-ym)
       
#########################################################################
###################### funkcje przyciskow ###############################
#########################################################################
    def edit(self):
        '''
        Metoda przypisana do przycisku edycji wlaczajaca
        i wylaczajaca tryb edycji
        '''
        if self.przyciski[0].isChecked():
            self.obiekt_oznaczony.edit()

        else:
            self.obiekt_oznaczony.zakoncz_edit()

    def nowy_obraz(self, obraz):
        '''
        Metoda wgrywajaca nowy obraz i prostokat do podgladu
        :param obraz: obraz odczytany po koncu edycji
        '''
        if type(obraz) == QPixmap:
            self.obraz = obraz

        self.podglad.nowy_podglad(self.obraz, self.obiekt_oznaczony. \
                                  pobierz_wzgledny_rectagle())

    def fine_edit(self):
        '''
        metoda wywolywana po nacisnieciu przycisku
        fine edit wlaczajaca tryb edycji
        z wykorzystaniem przyciskow
        :return:
        '''

        self.usun_glowne_przyciski()

        self._fine_edit_buttons()

        #poprawienie ksztaltu widgetu
        self.zablokuj_rozmiar(180, 270 + 15)

    def retyurn_to_normalbutons(self):
        '''
        metoda usuwajaca przyciski do edycji i
        ustawiajaca przyciski standardowe
        '''

        self.usun_fine_edit()

        self.glowne_przyciski()
        self.zablokuj_rozmiar()


##########################dwutrybowe przyciski _kierunkowe###############

    def gorny_przycisk(self):
    
        '''
        metoda wykonywana podczas nacisniecia jednego z przyciskow
        posiada 2 tryby
        w zaleznosci od ustawienia przelacznika przemiesc
        wywoluje odpowiednia metode obiektu oznaczonego w celu
        edycji/przemieszczenia ROI'u
        '''
        
        if self.przemiesc.isChecked():
        
            self.obiekt_oznaczony.przeksztalc_gorna_linie(
                                  self.zwieksz.isChecked())
        else:
        
            self.obiekt_oznaczony.przesun_w_gore()

        self.odswierz_kordynaty()


    def dolny_przycisk(self):
        '''
        metoda wykonywana podczas nacisniecia jednego z przyciskow
        posiada 2 tryby
        w zaleznosci od ustawienia przelacznika przemiesc
        wywoluje odpowiednia metode obiektu oznaczonego w celu
        edycji/przemieszczenia ROI'u
        '''
        if self.przemiesc.isChecked():
            self.obiekt_oznaczony.przekstalc_dolna_linie(
                                 self.zwieksz.isChecked())
        else:
            self.obiekt_oznaczony.przesun_w_dol()

        self.odswierz_kordynaty()
            
    def lewy_przycisk(self):
        '''
        metoda wykonywana podczas nacisniecia jednego z przyciskow
        posiada 2 tryby
        w zaleznosci od ustawienia przelacznika przemiesc
        wywoluje odpowiednia metode obiektu oznaczonego w celu
        edycji/przemieszczenia ROI'u
        '''
        if self.przemiesc.isChecked():
            self.obiekt_oznaczony.przekstalc_lewa_linie(
                                self.zwieksz.isChecked())
        else:
            self.obiekt_oznaczony.przesun_w_lewo()

        self.odswierz_kordynaty()
                
    def prawy_przycisk(self):
        '''
        metoda wykonywana podczas nacisniecia jednego z przyciskow
        posiada 2 tryby
        w zaleznosci od ustawienia przelacznika przemiesc
        wywoluje odpowiednia metode obiektu oznaczonego w celu
        edycji/przemieszczenia ROI'u
        '''
        if self.przemiesc.isChecked():
            self.obiekt_oznaczony.przekstalc_prawa_linie(
                                 self.zwieksz.isChecked())
        else:
            self.obiekt_oznaczony.przesun_w_prawo()

        self.odswierz_kordynaty()

#########################################################################
    def przelacz_przemiesc(self):
        '''
        metoda wywolyuwana przy przelaczeniu przycisku
        przemiesc zmienia napis na nim
        '''
        if self.przemiesc.isChecked():
             self.przemiesc.setText("ksztalt")

        else:
             self.przemiesc.setText("przemiesc")
             
                        
    def przelacz_zwieksz(self):
        '''
        metoda wywolywana przy przelaczeniu
        przycisku zwieksz zmienia napis na nim
        '''
     
        if self.zwieksz.isChecked():
            self.zwieksz.setText("-")

        else:
            self.zwieksz.setText("+")

#########################################################################
#######################metody uzyte do kalibracji podgladu###############
#########################################################################

    def xp(self):
        self.x += 0.001
        self.zmien()

    def yp(self):
        self.y += 0.001
        self.zmien()
        
    def zp(self):
        self.z += 0.001
        self.zmien()
        
    def sp(self):
        self.s += 0.001
        self.zmien()

    def xm(self):
        self.x -= 0.001
        self.zmien()
        
    def ym(self):
        self.y -= 0.001
        self.zmien()
        
    def zm(self):
        self.z -= 0.001
        self.zmien()
        
    def sm(self):
        self.s -= 0.001
        self.zmien()

    def zmien(self):
        self.podglad.update_rectagle((self.x, self.y,
                                      self.z, self.s))
        print(self.x, self.y, self.z, self.s)
        self.update()
