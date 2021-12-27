from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtGui import QImage, QPixmap
from kwadrat_label import Podglond_ROI


class Obszarzaznaczony():
    '''
    klasa przechowujaca wspulrzedne prubki w pixelach i mm oraz podglond
    '''

    # wspułrzedne bezwzgledne w geometri próbki w pixelach
    x0 = 0
    y0 = 0
    x1 = 1
    y1 = 1

    # wspułrzedne bezwzgledne w geometri prubki w mm
    xm0 = 0
    ym0 = 0
    xm1 = 0
    ym1 = 0

    #wartosci binarne przechowujace flagi do edycji
    pierwsze_klikniecie = False

    kanta_gora = False
    kanta_dul = False
    kanta_lewa = False
    kanta_prawy = False
    
    lewa_gora = False
    prawa_gora = False
    lewy_dul = False
    prawy_dul = False
    
    przemiesc_wsystkie = False

    szerokosc_obszaru_klikniecia = 10

    ####################################

    stala_przemiesczenia  = 10

    # konstruktor tworzocy obiekt ze wzglednych wspułrednych prubki w pixelach
    def __init__(self, obraz_obiekt, xp0, yp0, xp1, yp1, image, px00=0, py00=0, nazwa="defalaut", s=1):

        #Nadrzedny obiekt (map lub kamera) w któyrym strworzono obiektr przekazanoy w celu komunikacji
        self.obraz_obiekt = obraz_obiekt

        #nazwa obiektu
        self.nazwa = nazwa

        #metoda tworzoca niezalezne wspulrdzede prubki w pixelach
        self.x0, self.x1, self.y0, self.y1 = self._zalezne_to_niezalezne(xp0, yp0, xp1, yp1, px00, py00, s)

        #metoda tworzoca widget umozliwiajacy interakcje z obiektem
        self._stwurz_podglond_ROI(image)

        #metoda tworzoca niezalerzne wspułredne prubki w mm
        self._set_niezalezne_prubki()

    def __del__(self):
        '''
        dekonstruktor klasy obsluguje usuniecie podglondu i wyloczenie edycji
        '''
        self.zakoncz_edit()
        self.obraz_obiekt.rmv_rectagle(self)
        del self.podglond

    def pobierz_wzgledny_rectagle(self):
        '''
        metoda zwracajaca aktualne wzgledne wspulrzedne roiu w pixelach
        :return: x0, y0, x1, y1
        '''
        x0 = (self.x0 - self.obraz_obiekt.ofsetx)
        y0 = (self.y0 - self.obraz_obiekt.ofsety)

        x1 = (self.x1 - self.obraz_obiekt.ofsetx)
        y1 = (self.y1 - self.obraz_obiekt.ofsety)
    
        return x0, y0, x1, y1
        
    def pobierz_niezalezne_pixele(self):
        '''
        metoda zwracajaca niezalezne wspulrzedne w pixelach
        :return: x0, x1, y0, y1
        '''
        return self.x0, self.x1, self.y0, self.y1

    def _set_niezalezne_prubki(self):
        '''
        metoda konwetujaca wspułrzedne bezwgledne w pixelach na wspułredne prubkki
        '''
        self.xm0 = self.x0/510
        self.ym0 = self.y0/510
        self.xm1 = self.x1/510
        self.ym1 = self.y1/510

    def _niezalezne_to_zalezne(self, px00, py00, s):
        '''
        metoda konwertujaca wspulrzedne niezalezne w pixelach na zalezne
        :param px00: ofset x
        :param py00: ofset y
        :param s: skala
        :return:  x0, x1, y0, y1
        '''
        return self._konwersja(self.x0, self.y0, self.x1, self.y1, -px00, -py00, s)

    def _zalezne_to_niezalezne(self, xp0, yp0, xp1, yp1, px00, py00, s):
        '''

        :param xp0:
        :param yp0:
        :param xp1:
        :param yp1:
        :param px00: ofset x
        :param py00: ofset y
        :param s: skala
        :return:  x0, x1, y0, y1
        '''
        return self._konwersja(xp0, yp0, xp1, yp1, px00, py00, s)

    def _konwersja(self, xp0, yp0, xp1, yp1, px00, py00, s):
        '''
        metoda konwertujaca wspulrzedne
        :param xp0:
        :param yp0:
        :param xp1:
        :param yp1:
        :param px00: ofset x
        :param py00: ofset y
        :param s: skala
        :return: x0, x1, y0, y1
        '''
    
        x0 = int((xp0 + px00)/s)
        y0 = int((yp0 + py00)/s)

        x1 = int((xp1 + px00)/s)
        y1 = int((yp1 + py00)/s)
        
        return x0, x1, y0, y1

    def pobierz_prostokat(self, px00, py00, s):
        '''
        metoda zwracajaca prostokoat w układzei aktualnie wyswietlanym
        :param px00: ofsetx
        :param py00: ofsety
        :param s: skala
        :return: Qrectagle
        '''
    
        xp0, xp1, yp0, yp1 = self._niezalezne_to_zalezne(px00, py00, 1/s)

        poczatek = QPoint(xp0, yp0)
        koniec = QPoint(xp1, yp1)

        return QRect(poczatek, koniec)

    def ustawnazwe(self, nazwa):
        '''
        metoda umozliwiajaca nazwanie obiektu
        :param nazwa: string
        '''
        self.nazwa = nazwa

    def pobierz_nazwe(self):
        '''
        metoda zwracajaca nazwe obiektu
        :return: string
        '''
        return self.nazwa

    def _gettop_corner(self, ox, oy):
        '''
        metoda zwracajaca najwyszy prawy naroznik obiektu
        :param ox: ofset x
        :param oy: ofset y
        :return: x,y
        '''

        if self.x0 < self.x1 and self.y0 < self.y1:
            xp0 = (self.x0 - ox)
            yp0 = (self.y0 - oy)
        elif self.x0 < self.x1 and self.y0 > self.y1:
            xp0 = (self.x0 - ox)
            yp0 = (self.y1 - oy)
        elif self.x0 > self.x1 and self.y0 < self.y1:
            xp0 = (self.x1 - ox)
            yp0 = (self.y0 - oy)
        else:
            xp0 = (self.x1 - ox)
            yp0 = (self.y1 - oy)

        return xp0, yp0

    def pobierz_lokacje_tekstu(self, ox, oy):
        '''
        metoda zwracajaca lokacje nazwy wyswietlanej na podglondzie
        :param ox: ofset x
        :param oy: ofset y
        :return: x,y
        '''
        xp0, yp0 = self._gettop_corner(ox, oy)

        return xp0 - 20, yp0 - 10

    def _stwurz_podglond_ROI(self, obraz):
        '''
        Prywatna metoda tworzoca etykiete ROI'u wystwietlana na podglondzie
        :param obraz: klatka z podglondu
        '''

        obraz_qimage = QImage(obraz, obraz.shape[1], obraz.shape[0], obraz.strides[0], QImage.Format_RGB888)

        self.obraz = QPixmap.fromImage(obraz_qimage)

        self.podglond = Podglond_ROI(str(self.nazwa), self.obraz, self)

    def pobierz_obraz(self):
        '''
        metoda zwracajaca obraz
        :return: obraz zawierajacy podglond prubki zrobiony w momeciue tworzenia
        '''
        return self.obraz
    
    def pobierz_podglond(self):
        '''
        metoda zwracajaca widget podglondu ROI
        :return: obiekt klasy ROI stowarzyszony z ROI,em
        '''
        return self.podglond

############edycja obiektu za pomoca strzalek####################

    def przeksztalc_gorna_linie(self, mode):
        '''
        metoda wykonujaca edycje jednej z krawedzi o stala wartosc
        :param mode: jestli True to zwiekszamy wymiar jesli false to zmniejszamy
        '''
        if mode:
            self.y0 += self.stala_przemiesczenia
        else:
            self.y0 -= self.stala_przemiesczenia

    def przekstalc_dolna_linie(self, mode):
        '''
        metoda wykonujaca edycje jednej z krawedzi o stala wartosc
        :param mode: jestli True to zwiekszamy wymiar jesli false to zmniejszamy
        '''
        if mode:
            self.y1 -= self.stala_przemiesczenia
        else:
            self.y1 += self.stala_przemiesczenia

    def przekstalc_lewa_linie(self, mode):
        '''
        metoda wykonujaca edycje jednej z krawedzi o stala wartosc
        :param mode: jestli True to zwiekszamy wymiar jesli false to zmniejszamy
        '''
        if mode:
            self.x0 += self.stala_przemiesczenia
        else:
            self.x0 -= self.stala_przemiesczenia

    def przekstalc_prawa_linie(self, mode):
        '''
        metoda wykonujaca edycje jednej z krawedzi o stala wartosc
        :param mode: jestli True to zwiekszamy wymiar jesli false to zmniejszamy
        '''
        if mode:
            self.x1 -= self.stala_przemiesczenia
        else:
            self.x1 += self.stala_przemiesczenia

    def przesun_w_gore(self):
        '''
        metoda przesuwajaca podglad w jednym z kierunków
        '''
        self.y0 -= self.stala_przemiesczenia
        self.y1 -= self.stala_przemiesczenia

    def przesun_w_dul(self):
        '''
        metoda przesuwajaca podglad w jednym z kierunków
        '''
        self.y0 += self.stala_przemiesczenia
        self.y1 += self.stala_przemiesczenia

    def przesun_w_lewo(self):
        '''
        metoda przesuwajaca podglad w jednym z kierunków
        '''
        self.x0 -= self.stala_przemiesczenia
        self.x1 -= self.stala_przemiesczenia

    def przesun_w_prawo(self):
        '''
        metoda przesuwajaca podglad w jednym z kierunków
        '''
        self.x0 += self.stala_przemiesczenia
        self.x1 += self.stala_przemiesczenia

################odbieranie iw ysyłanie flagi edycji###########

    def edit(self):
        '''
        metoda wlaczajaca tryb edycji
        '''
        self.obraz_obiekt.edit_roi(self)
        
    def zakoncz_edit(self):
        '''
        metoda konczoca tryb edycji
        '''

        #zakonczenie trybu edycji w obrazie i pobranie z niego nowej klatki podglondu
        klatka = self.obraz_obiekt.zakoncz_edit()

        #konwersja klatki na Qimage
        klatka_qimage = QImage(klatka, klatka.shape[1], klatka.shape[0], klatka.strides[0], QImage.Format_RGB888)

        #zapisanie klatki
        self.obraz = QPixmap.fromImage(klatka_qimage)

        #odswiezenei klatki w podglondzie
        self.podglond.nowy_obraz(self.obraz)

###############################self edit##########################################

    def wspulrzedne_nacisniecia(self, e, ofsetx, ofsety):
        '''
        Metoda wywolywana w trybie edycji przy nacisnieciu przycisku myszki
        :param e: wspulrzedne w ktorych myszka zostala nacisnieta
        :param ofsetx:
        :param ofsety:
        '''

        # restart paramterów edycji
        self.pierwsze_klikniecie = True
    
        self.kanta_gora = False
        self.kanta_dul = False
        self.kanta_lewa = False
        self.kanta_prawy = False
        
        self.przemiesc_wsystkie = False

        # odczyt i konwersja wspulrzednych klikniecia
        self.px0 , self.py0 = e.x() + ofsetx, e.y()+ofsety

        # rozpoznanie kant koro których doszlo do klikniecia
        if self.x0-self.szerokosc_obszaru_klikniecia < self.px0 < self.x0+self.szerokosc_obszaru_klikniecia and\
                self.y0-self.szerokosc_obszaru_klikniecia < self.py0 < self.y1+self.szerokosc_obszaru_klikniecia:
            self.kanta_prawy = True
        
        if self.x1-self.szerokosc_obszaru_klikniecia < self.px0 < self.x1+self.szerokosc_obszaru_klikniecia and \
                self.y0-self.szerokosc_obszaru_klikniecia < self.py0 < self.y1+self.szerokosc_obszaru_klikniecia:
            self.kanta_lewa = True
            
        if self.y0-self.szerokosc_obszaru_klikniecia < self.py0 < self.y0+self.szerokosc_obszaru_klikniecia and\
                self.x0-self.szerokosc_obszaru_klikniecia < self.px0 < self.x1+self.szerokosc_obszaru_klikniecia:
            self.kanta_gora = True
            
        if self.y1-self.szerokosc_obszaru_klikniecia < self.py0 < self.y1+self.szerokosc_obszaru_klikniecia and\
                self.x0-self.szerokosc_obszaru_klikniecia < self.px0 < self.x1+self.szerokosc_obszaru_klikniecia:
            self.kanta_dul = True
        
        #sprawdzanie czy nie spelniamy warinkow ktorfos z rogow
        self.lewa_gora = self.kanta_lewa and self.kanta_gora
        self.prawa_gora = self.kanta_prawy and self.kanta_gora
        
        self.lewy_dul = self.kanta_lewa and self.kanta_dul
        self.prawy_dul = self.kanta_prawy and self.kanta_dul

        #sprawdzenie czy nie kliknelismy w srodek obszaru
        if self.y0+self.szerokosc_obszaru_klikniecia < self.py0 < self.y1-self.szerokosc_obszaru_klikniecia and \
                self.x0+self.szerokosc_obszaru_klikniecia < self.px0 < self.x1-self.szerokosc_obszaru_klikniecia:
            self.przemiesc_wsystkie = True

        # odswierzenie kordynmatow na podglodzie
        self.podglond.odswierz_kordynaty()

    def wspulrzedne_puszcenia(self, e, ofsetx, ofsety):
        '''
        metoda wykonywana po pusczeniu przycisku myszki zapisuje wykonana edycjie ROI'u
        :param e: pozycja myszki
        :param ofsetx:
        :param ofsety:
        '''

        # reset licznika klikniec
        self.pierwsze_klikniecie = False

        #  odczyt i konwersja wspulrzednych klikniecia
        self.px1 , self.py1 = e.x() + ofsetx, e.y()+ofsety

        # sprawdzenie trybu pracy i adekwatna do niego edycja ROI'u
        if self.przemiesc_wsystkie:
            dx, dy = self.px1 - self.px0, self.py1 - self.py0
            self.x0 += dx
            self.x1 += dx
            self.y0 += dy
            self.y1 += dy
        
        elif self.lewa_gora:
            self.x1 = self.px1
            self.y0 = self.py1
            
        elif self.lewy_dul:
            self.x1 = self.px1
            self.y1 = self.py1
            
        elif self.prawy_dul:
            self.x0 = self.px1
            self.y1 = self.py1
            
        elif self.prawa_gora:
            self.x0 = self.px1
            self.y0 = self.py1
            
        elif self.kanta_dul:
            self.y1 = self.py1
        elif self.kanta_lewa:
            self.x1 = self.px1
        elif self.kanta_prawy:
            self.x0 = self.px1
        elif self.kanta_gora:
            self.y0 = self.py1

        # odswierzenie kordynmatow na podglodzie
        self.podglond.odswierz_kordynaty()
      
    def move_cords(self, e, ofsetx, ofsety):

        # sprawdzenie licznika klikniec
        if self.pierwsze_klikniecie:

            # odczyt i konwersja wspulrzednych klikniecia
            self.px1 , self.py1 = e.x() + ofsetx, e.y()+ofsety
            
            # sprawdzenie trybu pracy i adekwatne obsluzenie edycji dla niego
            if self.przemiesc_wsystkie:
                dx, dy = self.px1 - self.px0, self.py1 - self.py0
                self.x0 += dx
                self.x1 += dx
                self.y0 += dy
                self.y1 += dy
                self.px0 , self.py0 = e.x() + ofsetx, e.y()+ofsety
        
            elif self.lewa_gora:
                self.x1 = self.px1
                self.y0 = self.py1
                
            elif self.lewy_dul:
                self.x1 = self.px1
                self.y1 = self.py1
                
            elif self.prawy_dul:
                self.x0 = self.px1
                self.y1 = self.py1
                
            elif self.prawa_gora:
                self.x0 = self.px1
                self.y0 = self.py1
                
            elif self.kanta_dul:
                self.y1 = self.py1
            elif self.kanta_lewa:
                self.x1 = self.px1
            elif self.kanta_prawy:
                self.x0 = self.px1
            elif self.kanta_gora:
                self.y0 = self.py1

            # odswierzenie kordynmatow na podglodzie
            self.podglond.odswierz_kordynaty()
