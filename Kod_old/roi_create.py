import cv2
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtGui import QPixmap, QImage, QPalette, QColor, QPainter, QBrush
from obszaroznaczony_clasa import Obszarzaznaczony


class ROI_maping(QLabel):
    '''
    Classa dziedziczaca z Qlabel umozliwiajaca wyswietlenie obrazu zaznaczenie na nim obszaru zaintersowania
    edycji tego obszaru.
    '''

    # obiekt Klasy MainWindow podany jako argument przy tworzeniu obiektu klasy Obraz_z_kamery -
    # pozwala na komunikację z oknem głównym
    main_window = ' '

    # aktualna pozycja myszki nad widgetem
    x = 0
    y = 0
        
    # ostatnie 2 pozycje klikniec pozycja myszki nad widgetem
    x1 = 0
    y1 = 0

    x2 = 0
    y2 = 0
        
    # pukty poczotkowe i koncowe prostokonta
    poczatek = QPoint()
    koniec = QPoint()
       
    iloscklikniec = False
    
    # zmienne pozwalajace obejsc brak układu swichcaes
    # 'no_rectagle' nie rysuje zadnych obsarów oznaczoncyh
    # 'all_rectagls' rysuje wsytkie obszary oznaczone
    # 'One_rectagle' rysuje jeden wybrany obszar oznaczony
    # 'viue_muve'  obsluguje rysowanie podczas przemiesczenia
    # 'previu_rectagle' obsluguje rysowanie nowego obszaru
    co_narysowac = 'all_rectagls'
    
    # iterator do wyswietlenia poprzedniego nastempego zaznaczenia
    ktury = 0

    # wartosci owsetu aktualnego podgloadu
    ofsetx = 0
    ofsety = 0
    
    # rozmiar obszaru
    rozmiar = (1024, 768)
    
    # calibration value
    delta_pixeli = 510

    # zmiene obslugujace tryb edycji
    edit_tryb = False
    edited_roi = None

    #zmiena okreslajaca czy jestesmy w trybie edycji czy centrowania na kliknieciu
    przemiesc_sie_do_pktu = False
    
    # maxymalna pozycja manipulatora w mm
    manipulator_max = 50
    
    # skala mapy
    skala = 32
    
        
    def __init__(self, main_window, *args, **kwargs):
        super(ROI_maping, self).__init__(*args, **kwargs)

        #wskaznik do glownego okna programu
        self.main_window = main_window

        #ustawienie bazowej szaty graficznej
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('white'))
        self.setPalette(palette)

        # wyłacza skalowanie okna
        self.setScaledContents(False)

        # włączenie sledzenia myszki
        self.setMouseTracking(True)

        # Tworzy białe tło
        self.setAutoFillBackground(True)
        
####################################wgrywanie obrazu##################################

    def zaladuj_obraz(self, nasrysuj_opisy = False, narysuj_jeden_ROI = False):
        '''
        Metoda dodajoca opisy do podglondu oraz wgrywajaca podglond do labela
        :param nasrysuj_opisy: warotsc logiczna okreslajaca czy wypisywac opisy czy nie
        :param narysuj_jeden_ROI: wartosc logiczna okreslajaca czy wywietlic 1 czy wsystkie ROIe
        '''

        # scalowanie obrazu
        klatka = self.image_opencv.copy()

        #scalowanie kopi obrazu
        self.klatka = self.image_opencv.copy()

        #dodanie opisów w odpowiednich miescach
        if nasrysuj_opisy:
            for i, rectangle in enumerate(self.main_window.ROI):
                rx, ry = rectangle.pobierz_lokacje_tekstu(self.ofsetx, self.ofsety)
                cv2.putText(klatka, str(rectangle.pobierz_nazwe()), (rx, ry), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        #dodanie opisuw pojedyczego Roia jesli ta obcja została wybrana
        if narysuj_jeden_ROI:
            rx, ry = self.main_window.ROI[self.ktury].pobierz_lokacje_tekstu(self.ofsetx, self.ofsety)
            cv2.putText(klatka, str(self.main_window.ROI[self.ktury].pobierz_nazwe()), (rx, ry), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # konwersja z open Cv obraz na QImage
        obraz_z_klatki = QImage(klatka, klatka.shape[1], klatka.shape[0], klatka.strides[0], QImage.Format_RGB888)

        #konwersja obrazu z Qmage na pixmap
        self._obraz_z_klatki = QPixmap.fromImage(obraz_z_klatki)
        
        # wgranie obrazu
        self.setPixmap(self._obraz_z_klatki)

        #zablokwnie rozmiaru
        self.setMaximumSize(self._obraz_z_klatki.width(), self._obraz_z_klatki.height())
        

###############################mous tracking##########################################

    def mousePressEvent(self, e):
        '''
        Metoda nadpisajaca wbudowany event pyqt wykonywany w mommecie przycisniencia przycisku myszki
        :param e: odczytana pozycja myszki
        '''

        # Sprawdzenie trybu pracy
        if self.edit_tryb:
            #tryb edycji ROI'u
            self.edited_roi.wspulrzedne_nacisniecia(e, self.ofsetx, self.ofsety)
           
        elif self.przemiesc_sie_do_pktu:
            #tryb centrowania na pktcie
            self._wycentruj_na_pktcie_function(e)

        else:
            #podstawowa obcja umozliwiajaca oznaczenie ROI'u
            self._zapisz_pierwsze_klikniecie(e)

    def _zapisz_pierwsze_klikniecie(self, e):
        '''
        Prywatna metoda zapisujaca pozycje pierwszego klikniecia
        '''

        # zapis pozycji klikniecia
        self.x1 = e.x()
        self.y1 = e.y()

        # zapisanie pozycji pierwszego klikniecia jako obiekt klasy qpoint
        self.poczatek = e.pos()  # QPoint(self.x1,self.y1)#e.pos()

        #Zapisanie ze juz raz doszło do klikniecia
        self.iloscklikniec = True

        #podniesienie flagi ze nalezy narysowac podglond nowo zaznaczanego ROI'u
        self.co_narysowac = 'previu_rectagle'

    def _wycentruj_na_pktcie_function(self, e):
        '''
        Prywatna metoda konwerttujaca wspułrzedne w pixelach na mm i zadajaca manipulatorowi przemiecenie
        w celu wycetrowania na wybranym pktcie
        '''

        x1, y1 = e.x(), e.y() #zapisanie pozycji klikniecia

        #ccx - połowa rozmiaru x
        #ccy - połowa rozmiaru y
        ccx, ccy = self.rozmiar[0] / 2, self.rozmiar[1] / 2

        #odległosci któe nalezy przemiescic manipulator w pixelach
        self.dxp, self.dyp = int(y1 - ccy), int(x1 - ccx)

        # konwersja odległosci w pixelach na odległosci w mm
        dx, dy = (x1 - ccx) / self.delta_pixeli, (y1 - ccy) / self.delta_pixeli

        #zadanie przemiesczenia manipulatorowi
        self.main_window.manipulaor.move_axes_to_abs_woe_ofset('yz', [dx, dy])

        #updet ofsetów
        self.ofsetx += self.dxp
        self.ofsety += self.dyp

        #update mapy
        self._mapupdate()

    def mouseReleaseEvent(self, e):
        '''
        Metoda przeciozajaca Pqt5 event umozliwiajaca obsluzednie momentu pusczenia przycisku myszki
        :param e: pozycja myszki
        '''

        #wybranie odpowieniego trybu
        if self.edit_tryb:
            #przekazanie pozycji w celu edycji
            self.edited_roi.wspulrzedne_puszcenia(e, self.ofsetx, self.ofsety)
        
        elif self.przemiesc_sie_do_pktu:
            #ignorowanie eventu w ramach przesuwania manipiulatora
            pass
        
        else:
            #zapisanie pozycji puszczenia przycisku
            self._zapisz_pusczenie_przycisku(e)

    def _zapisz_pusczenie_przycisku(self, e):
        '''
        Zapisanei miejsca puszcenia przycisku myszki
        '''

        # zapisanie wspułrzedne klikniecia
        self.x2 = e.x()
        self.y2 = e.y()

        # zapisanie pozycji klikniecia jako obiekt klasy qpoint
        self.koniec = e.pos()  # QPoint(self.x2,self.y2)

        # dopisanie nowego prostokata do listy
        nowy_prostokat = self.stwurz_prostokat()

        self.main_window.ROI.append(nowy_prostokat)

        # implementacja iteratora wyswietlanego prostokata
        self.ktury += 1

        #wyczsczenie licznika klikniec
        self.iloscklikniec = False

        #podniesienie flagi w celu wyrysowania wsystkich ROI
        self.co_narysowac = 'all_rectagls'

        self.update()

    def mouseMoveEvent(self, e):
        '''
        Metoda przeciozajaca Pqt5 event umozliwiajaca obsluzednie momentu przesuniecia myszki
        :param e: pozycja myszki
        '''

        if self.edit_tryb:
            # tryb edycji ROI'u
            self.edited_roi.move_cords(e, self.ofsetx, self.ofsety)
            
        elif self.przemiesc_sie_do_pktu:
            # ignorowanie eventu w ramach przesuwania manipiulatora
            pass

        elif self.iloscklikniec:
            # paramtery umozliwiajace rysowanei podglondu tworzonego ROI
            self._stwurz_tymczasowy_ROI(e)

    def _stwurz_tymczasowy_ROI(self, e):

        self.x2 = int(e.x())
        self.y2 = int(e.y())

        # zapis aktualnej pozycji myszki w celu wyswietlenia podglondu
        self.koniec = e.pos()

        #podniesienie odpoiwiedniej flagi
        self.co_narysowac = 'previu_rectagle'

        self.update()

###############################ROI edit##########################################

    def _mapupdate(self):
        '''
        Abstrakcyjna metoda updatujaca mape
        '''
        pass

    def edit_roi(self, roi):
        '''
        Metoda wywoływana przez ROI w celu samoedycji
        :param roi: Roi wyołujacy edycje
        '''
        #podnisienie odpowiedniej flagi
        self.edit_tryb = True
        self.przemiesc_sie_do_pktu = False

        #zapisanie wskaznika do edytowanego ROI'u
        self.edited_roi = roi
    
    def zakoncz_edit(self):
        '''
        Metoda konconca edycje ROi
        '''
        #opusczenie odpowieniej flagi
        self.edit_tryb = False
        #usuniecie wskaznika do ROI
        self.edited_roi = None
        #zwrucenie aktualnego podglondu w celu aktualizacji
        return self.klatka

#############################create rectagle###############################################

    def narysuj_prostokat(self, prostokat):
        '''
        Metoda zwracajaca Qrectagle w celu wyrysowani go na podglodzie
        :param prostokat: obiekt klasy ROI
        :return: obiekt klasy Qrectagle
        '''
        x = prostokat.pobierz_prostokat(self.ofsetx, self.ofsety, 1/self.skala)
        return x
        
    def stwurz_prostokat(self):
        '''
        Metoda tworzoca obiekt klasy ROI
        :return: obiekt klasy roi stworzony na podstawie zapisanych dancyh
        '''
        #ponisienie nr defaltowej nazwy
        self.main_window.ostatnia_nazwa += 1
        
        ROI = Obszarzaznaczony(self, self.x1, self.y1, self.x2, self.y2, self.klatka, self.ofsetx, self.ofsety,
                               self.main_window.ostatnia_nazwa, 1/self.skala)
        #zapisanei ROI dao tablicy
        self.main_window.dodaj_ROI(ROI)
        return ROI
    
    def rmv_rectagle(self, roi):
        '''
        Metoda usywajhaca ROI
        :param roi: Roi do usuniecia
        '''

        #jesli ROI jest w tablicy to go usuwamy
        if roi in self.main_window.ROI:
            self.main_window.ROI.remove(roi)

        #wywolanei metody sprotajacej po ROI w mainwidow
        self.main_window.usun_wybrany_ROI(roi)

        #podniesienie odpoiwedniej flagi
        self.co_narysowac = 'all_rectagls'
        
        self.update()

#############################Paint Event###############################################

    def paintEvent(self, event):
        '''
        Metoda przeciozajaca PyQt5 event obslugujaca wyswietlanie ROI i podglondu
        '''
        
        # inicializacja paintera
        qp = QPainter(self)

        # wyrysowaneie obrazu z kamery
        qp.drawPixmap(self.rect(), self._obraz_z_klatki)

        # wgranie stylu rysowania ROI'u
        qp.setBrush(QBrush(QColor(200, 10, 10, 200)))

        # zmienne decydujace o wypisywaniu opisów
        nasrysuj_opisy = True
        narysuj_jeden_ROI = False


        if self.co_narysowac == 'all_rectagls':
            # pokazuje wsystkie prostkoaty
            self.wsystkie_prostokaty(qp)

        else:
            # podstawowa obcja rysuje nowy prostokat
            self.wsystkie_prostokaty(qp)
            qp.drawRect(QRect(self.poczatek, self.koniec))
            # rysowanie prostokonta na bierzoco jak podglond do ruchu myszka

        #odswiezenie podglondu
        self.zaladuj_obraz(nasrysuj_opisy, narysuj_jeden_ROI)

    def wsystkie_prostokaty(self, Painter):
        '''
        Metoda rysujaca wsystkie ROI'e
        :param Painter: Qt Painter
        '''
        for rectangle in self.main_window.ROI:
            Painter.drawRect(self.narysuj_prostokat(rectangle))
