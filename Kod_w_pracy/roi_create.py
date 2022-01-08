import cv2
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtGui import QPixmap, QImage, QPalette, QColor,\
   QPainter, QBrush
from obszar_oznaczony_clasa import Obszar_zaznaczony


class oznacz_ROI(QLabel):
    '''
    Klasa dziedziczaca z Qlabel umozliwiajaca wyswietlenie
    obrazu oraz zaznaczenie na nim obszaru zaintersowania
    i edycji tego obszaru.
    '''
    # obiekt Klasy Glowne_okno podany jako argument
    # przy tworzeniu obiektu klasy Obraz_z_kamery -
    # pozwala na komunikacje z oknem glownym
    main_window = ' '

    # aktualna pozycja myszki nad widgetem
    x = 0
    y = 0
        
    # ostatnie 2 pozycje klikniec pozycja myszki nad widgetem
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0
        
    # pukty poczatkowe i koncowe prostokata
    poczatek = QPoint()
    koniec = QPoint()
       
    iloscklikniec = False
    
    # zmienne obslugujace wyswietlanie ROI
    # 'no_rectagle' nie rysuje zadnych obszarow oznaczoncyh
    # 'all_rectagls' rysuje wszytkie obszary oznaczone
    # 'One_rectagle' rysuje jeden wybrany obszar oznaczony
    # 'viue_muve'  obsluguje rysowanie podczas przemieszczenia
    # 'previu_rectagle' obsluguje rysowanie nowego obszaru
    co_narysowac = 'all_rectagls'
    
    # iterator do wyswietlenia poprzedniego, nastepnego zaznaczenia
    ktory = 0

    # wartosci offsetu aktualnego podgladu
    ofsetx = 0
    ofsety = 0
    
    # rozmiar obszaru
    rozmiar = (1024, 768)
    
    # zmienna umozliwiajaca przeliczenie pixeli na mm
    # 1 mm to 510 pixeli
    delta_pixeli = 510

    # zmiene obslugujace tryb edycji
    edit_tryb = False
    edited_roi = None

    #zmiena okreslajaca czy jestesmy w trybie edycji 
    #czy centrowania na kliknieciu
    przemiesc_sie_do_pktu = False
    
    # maxymalna pozycja manipulatora w mm
    manipulator_max = 50
    
    # skala mapy
    skala = 32
    
        
    def __init__(self, main_window, *args, **kwargs):
        super(oznacz_ROI, self).__init__(*args, **kwargs)

        #wskaznik do glownego okna programu
        self.main_window = main_window

        #ustawienie bazowej szaty graficznej
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('white'))
        self.setPalette(palette)

        # wylacza skalowanie okna
        self.setScaledContents(False)

        # wlaczenie sledzenia myszki
        self.setMouseTracking(True)

        # Tworzy biale tlo
        self.setAutoFillBackground(True)
        
####################################wgrywanie obrazu############

    def zaladuj_obraz(self, nasrysuj_opisy = False, 
                            narysuj_jeden_ROI = False):
        '''
        Metoda dodajoca opisy do podgladu oraz wgrywajaca 
        podglad do etykiety
        :param nasrysuj_opisy: warotsc logiczna okreslajaca
        czy wypisywac opisy czy nie
        :param narysuj_jeden_ROI: wartosc logiczna okreslajaca
        czy wywietlic jeden czy wsystkie ROIe
        '''

        # skalowanie obrazu
        klatka = self.image_opencv.copy()

        #skalowanie kopi obrazu
        self.klatka = self.image_opencv.copy()

        #dodanie opisow w odpowiednich miescach
        if nasrysuj_opisy:
            for i, rectangle in enumerate(self.main_window.ROI):
                rx, ry = rectangle.pobierz_lokacje_tekstu(self.ofsetx,
                                                          self.ofsety)

                cv2.putText(klatka, str(rectangle.pobierz_nazwe()),
                           (rx, ry), cv2.FONT_HERSHEY_SIMPLEX, 
                            1, (0, 0, 255), 2)

        #dodanie opisow pojedyczego Roi'a 
        #jesli ta opcja zostala wybrana
        if narysuj_jeden_ROI:

            rx, ry = self.main_window.ROI[self.ktory].\
                          pobierz_lokacje_tekstu(self.ofsetx,
                                                 self.ofsety)

            cv2.putText(klatka, str(self.main_window. \
                                    ROI[self.ktory].pobierz_nazwe()),
                        (rx, ry), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 2)
        
        # konwersja z open Cv obrazu na QImage
        obraz_z_klatki = QImage(klatka,
                                klatka.shape[1],
                                klatka.shape[0],
                                klatka.strides[0],
                                QImage.Format_RGB888)

        #konwersja obrazu z Qmage na pixmap
        self._obraz_z_klatki = QPixmap.fromImage(obraz_z_klatki)
        
        # wgranie obrazu
        self.setPixmap(self._obraz_z_klatki)

        #zablokowanie rozmiaru
        self.setMaximumSize(self._obraz_z_klatki.width(), 
                            self._obraz_z_klatki.height())
        

###############################mouse tracking##########################

    def mousePressEvent(self, e):
        '''
        Metoda nadpisajaca wbudowany event pyqt 
        wykonywany w momencie przycisniecia przycisku myszki
        :param e: odczytana pozycja myszki
        '''

        # Sprawdzenie trybu pracy
        if self.edit_tryb:
            #tryb edycji ROI'u
            self.edited_roi.wspolrzedne_nacisniecia(e, self.ofsetx, 
                                                       self.ofsety)
           
        elif self.przemiesc_sie_do_pktu:
            #tryb centrowania na punkcie
            self._wycentruj_na_pktcie_function(e)

        else:
            #podstawowa opcja umozliwiajaca oznaczenie ROI'u
            self._zapisz_pierwsze_klikniecie(e)

    def _zapisz_pierwsze_klikniecie(self, e):
        '''
        Prywatna metoda zapisujaca pozycje pierwszego klikniecia
        '''
        # zapis pozycji klikniecia
        self.x1 = e.x()
        self.y1 = e.y()

        # zapisanie pozycji pierwszego klikniecia 
        self.poczatek = e.pos()

        #Zapisanie ze juz raz doszlo do klikniecia
        self.iloscklikniec = True

        #podniesienie flagi ze nalezy narysowac podglad nowo
        #zaznaczanego ROI'u
        self.co_narysowac = 'previu_rectagle'

    def _wycentruj_na_pktcie_function(self, e):
        '''
        Prywatna metoda konwertujaca wspolrzedne w pixelach
        na mm i zadajaca manipulatorowi przemieszczenie
        w celu wycetrowania na wybranym punkcie
        '''

        x1, y1 = e.x(), e.y() #zapisanie pozycji klikniecia

        #ccx - polowa rozmiaru x
        #ccy - polowa rozmiaru y
        ccx, ccy = self.rozmiar[0] / 2, self.rozmiar[1] / 2

        #odleglosci ktore nalezy przemiescic manipulator w pixelach
        self.dxp, self.dyp = int(y1 - ccy), int(x1 - ccx)

        # konwersja odleglosci w pixelach na odleglosci w mm
        dx = (x1 - ccx) / self.delta_pixeli
        dy = (y1 - ccy) / self.delta_pixeli

        #zadanie przemieszczenia manipulatorowi
        self.main_window.manipulaor.move_axes_to_abs_woe_ofset('yz',
                                                            [dx, dy])

        #odswiezenie ofsetow
        self.ofsetx += self.dxp
        self.ofsety += self.dyp

        #odswiezenie mapy
        self._map_update()

    def mouseReleaseEvent(self, e):
        '''
        Metoda przeciazajaca Pqt5 event umozliwiajaca
        obsluzenie momentu puszczenia przycisku myszki
        :param e: pozycja myszki
        '''
        #wybranie odpowieniego trybu
        if self.edit_tryb:
            #przekazanie pozycji w celu edycji
            self.edited_roi.wspolrzedne_puszczenia(e, self.ofsetx,
                                                      self.ofsety)
        
        elif self.przemiesc_sie_do_pktu:
            #ignorowanie eventu w ramach przesuwania manipiulatora
            pass
        else:
            #zapisanie pozycji puszczenia przycisku
            self._zapisz_puszczenie_przycisku(e)

    def _zapisz_puszczenie_przycisku(self, e):
        '''
        Zapisanie miejsca puszczenia przycisku myszki
        '''
        # zapisanie wspolrzednych klikniecia
        self.x2 = e.x()
        self.y2 = e.y()

        # zapisanie pozycji klikniecia jako obiekt klasy qpoint
        self.koniec = e.pos()

        # dopisanie nowego prostokata do listy
        nowy_prostokat = self.stworz_prostokat()

        self.main_window.ROI.append(nowy_prostokat)

        # implementacja iteratora wyswietlanego prostokata
        self.ktory += 1

        #wyczszczenie licznika klikniec
        self.iloscklikniec = False

        #podniesienie flagi w celu wyrysowania wsystkich ROI
        self.co_narysowac = 'all_rectagls'

        self.update()

    def mouseMoveEvent(self, e):
        '''
        Metoda przeciazajaca Pqt5 event
        umozliwiajaca obsluzenie momentu przesuniecia myszki
        :param e: pozycja myszki
        '''

        if self.edit_tryb:
            # tryb edycji ROI'u
            self.edited_roi.przemiesc_kordynaty(e, self.ofsetx, 
                                                   self.ofsety)
            
        elif self.przemiesc_sie_do_pktu:
            # ignorowanie eventu w ramach przesuwania manipiulatora
            pass

        elif self.iloscklikniec:
            # paramtery umozliwiajace rysowanie
            # podgladu tworzonego ROI
            self._stworz_tymczasowy_ROI(e)

    def _stworz_tymczasowy_ROI(self, e):

        self.x2 = int(e.x())
        self.y2 = int(e.y())

        # zapis aktualnej pozycji myszki 
        # w celu wyswietlenia podgladu
        self.koniec = e.pos()

        #podniesienie odpoiwiedniej flagi
        self.co_narysowac = 'previu_rectagle'

        self.update()

###############################ROI edit################################

    def _map_update(self):
        '''
        Abstrakcyjna metoda odswiezajaca mape
        '''
        pass

    def edit_roi(self, roi):
        '''
        Metoda wywolywana przez ROI w celu samoedycji
        :param roi: Roi wyolujacy edycje
        '''
        #podnisienie odpowiedniej flagi
        self.edit_tryb = True
        self.przemiesc_sie_do_pktu = False

        #zapisanie wskaznika do edytowanego ROI'u
        self.edited_roi = roi
    
    def zakoncz_edit(self):
        '''
        Metoda konczaca edycje ROi
        '''
        #opuszczenie odpowieniej flagi
        self.edit_tryb = False
        #usuniecie wskaznika do ROI
        self.edited_roi = None
        #zwrocenie aktualnego podgladu w celu aktualizacji
        return self.klatka

#############################tworzenie prostokatow#####################
    def narysuj_prostokat(self, prostokat):
        '''
        Metoda zwracajaca Qrectagle
        w celu wyrysowania go na podgladzie
        :param prostokat: obiekt klasy ROI
        :return: obiekt klasy Qrectagle
        '''
        x = prostokat.pobierz_prostokat(self.ofsetx, self.ofsety,
                                                     1/self.skala)
        return x
        
    def stworz_prostokat(self):
        '''
        Metoda tworzoca obiekt klasy ROI
        :return: obiekt klasy roi stworzona na podstawie zapisanych dancyh
        '''
        #ponisienie nr domyslnej nazwy
        self.main_window.ostatnia_nazwa += 1
        
        ROI = Obszar_zaznaczony(self, self.x1, self.y1, self.x2, self.y2,
                                self.klatka, self.ofsetx, self.ofsety,
                                self.main_window.ostatnia_nazwa,
                                1 / self.skala)

        #zapisanie ROI do tablicy
        self.main_window.dodaj_ROI(ROI)

        return ROI
    
    def rmv_rectagle(self, roi):
        '''
        Metoda usywajaca ROI
        :param roi: Roi do usuniecia
        '''

        #jesli ROI jest w tablicy to go usuwamy
        if roi in self.main_window.ROI:
            self.main_window.ROI.remove(roi)

        #wywolanie metody sprzatajacej po ROI w glownym oknie
        self.main_window.usun_wybrany_ROI(roi)

        #podniesienie odpowiedniej flagi
        self.co_narysowac = 'all_rectagls'
        
        self.update()

#############################Paint Event###############################
    def paintEvent(self, event):
        '''
        Metoda przeciazajaca PyQt5 event
        obslugujaca wyswietlanie ROI i podgladu
        '''
        # inicializacja paintera
        qp = QPainter(self)

        # wyrysowaneie obrazu z kamery
        qp.drawPixmap(self.rect(), self._obraz_z_klatki)

        # wgranie stylu rysowania ROI'u
        qp.setBrush(QBrush(QColor(200, 10, 10, 200)))

        # zmienne decydujace o wypisywaniu opisow
        nasrysuj_opisy = True
        narysuj_jeden_ROI = False

        if self.co_narysowac == 'all_rectagls':
            # pokazuje wsystkie prostokaty
            self.wsystkie_prostokaty(qp)

        else:
            # podstawowa opcja rysuje nowy prostokat
            self.wsystkie_prostokaty(qp)
            qp.drawRect(QRect(self.poczatek, self.koniec))

        #odswiezenie podgladu
        self.zaladuj_obraz(nasrysuj_opisy, narysuj_jeden_ROI)

    def wsystkie_prostokaty(self, Painter):
        '''
        Metoda rysujaca wsystkie ROI'e
        :param Painter: Qt Painter
        '''
        for rectangle in self.main_window.ROI:
            Painter.drawRect(self.narysuj_prostokat(rectangle))
