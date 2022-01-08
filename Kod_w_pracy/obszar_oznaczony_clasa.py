from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtGui import QImage, QPixmap
from kwadrat_label import Podglad_ROI


class Obszar_zaznaczony:
    '''
    klasa przechowujaca wspolrzedne probki
    w pixelach i mm oraz podglad
    '''

    # wspolrzedne bezwzgledne w geometrii probki w pixelach
    x0 = 0
    y0 = 0
    x1 = 1
    y1 = 1

    # wspolrzedne bezwzgledne w geometrii probki w mm
    xm0 = 0
    ym0 = 0
    xm1 = 0
    ym1 = 0

    #wartosci binarne przechowujace flagi do edycji
    pierwsze_klikniecie = False

    kanta_gora = False
    kanta_dol = False
    kanta_lewa = False
    kanta_prawy = False

    lewa_gora = False
    prawa_gora = False
    lewy_dol = False
    prawy_dol = False
    
    przemiesc_wszystkie = False

    szerokosc_obszaru_klikniecia = 10

    stala_przemieszczenia  = 10

    # konstruktor tworzocy obiekt ze wzglednych 
    # wspolrzednych probki w pixelach
    def __init__(self, obraz_obiekt, xp0, yp0, xp1, yp1, 
                                     image, px00=0, py00=0,
                                     nazwa="defalaut", s=1):

        #Nadrzedny obiekt (map lub kamera) w ktoyrym strworzono 
        #obiekt przekazanoy w celu komunikacji
        self.obraz_obiekt = obraz_obiekt

        #nazwa obiektu
        self.nazwa = nazwa

        #metoda tworzaca niezalezne wspolrzedne probki w pixelach
        self.x0, self.x1, self.y0, self.y1 = self.\
                                 _zalezne_to_niezalezne(xp0, yp0,
                                                        xp1, yp1,
                                                   px00, py00, s)

        #metoda tworzoca widget umozliwiajacy interakcje z obiektem
        self._stworz_podglad_ROI(image)

        #metoda tworzaca niezalezne wspolrzedne probki w mm
        self._ustaw_niezalezne_probki()

    def __del__(self):
        '''
        dekonstruktor klasy obsluguje usuniecie podgladu
        i wyloczenie edycji
        '''
       
        self.obraz_obiekt.rmv_rectagle(self)
        try:
             self.zakoncz_edit()
             del self.podglad
        except AttributeError:
            pass

    def usun(self):
        
        self.obraz_obiekt.rmv_rectagle(self)
        
        try:
             self.zakoncz_edit()
             del self.podglad
        except AttributeError:
            pass
       

    def pobierz_wzgledny_rectagle(self):
        '''
        metoda zwracajaca aktualne wzgledne wspolrzedne
        roiu w pixelach
        :return: x0, y0, x1, y1
        '''
        x0 = (self.x0 - self.obraz_obiekt.ofsetx)
        y0 = (self.y0 - self.obraz_obiekt.ofsety)

        x1 = (self.x1 - self.obraz_obiekt.ofsetx)
        y1 = (self.y1 - self.obraz_obiekt.ofsety)
    
        return x0, y0, x1, y1
        
    def pobierz_niezalezne_pixele(self):
        '''
        metoda zwracajaca niezalezne wspolrzedne w pixelach
        :return: x0, x1, y0, y1
        '''
        return self.x0, self.x1, self.y0, self.y1

    def _ustaw_niezalezne_probki(self):
        '''
        metoda konwetujaca wspolrzedne bezwgledne w pixelach
        na wspolrzedne probkki
        '''
        self.xm0 = self.x0/510
        self.ym0 = self.y0/510
        self.xm1 = self.x1/510
        self.ym1 = self.y1/510

    def _niezalezne_to_zalezne(self, px00, py00, s):
        '''
        metoda konwertujaca wspolrzedne niezalezne
        na zalezne
        w pixelach na zalezne
        :param px00: ofset x
        :param py00: ofset y
        :param s: skala
        :return:  x0, x1, y0, y1
        '''
        return self._konwersja(self.x0, self.y0, self.x1, self.y1,
                               -px00, -py00, s)

    def _zalezne_to_niezalezne(self, xp0, yp0, xp1, yp1, 
                                px00, py00, s):
        '''
        metoda konwertujaca wspolrzedne zalezne
        na niezalezne
        :param xp0:
        :param yp0:
        :param xp1:
        :param yp1:
        :param px00: ofset x
        :param py00: ofset y
        :param s: skala
        :return:  x0, x1, y0, y1
        '''
        return self._konwersja(xp0,yp0,xp1,yp1,px00,py00,s)

    def _konwersja(self, xp0, yp0, xp1, yp1, px00, py00, s):
        '''
        metoda konwertujaca wspolrzedne
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
        metoda zwracajaca prostokat w ukladzie
        aktualnie wyswietlanym
        :param px00: ofsetx
        :param py00: ofsety
        :param s: skala
        :return: Qrectagle
        '''
        xp0, xp1, yp0, yp1 = self._niezalezne_to_zalezne(px00,py00,1/s)

        return QRect(QPoint(xp0, yp0), QPoint(xp1, yp1))

    def ustaw_nazwe(self, nazwa):
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

    def _pobierz_gorny_naroznik(self, ox, oy):
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
        metoda zwracajaca lokacje nazwy wyswietlanej na podgladzie
        :param ox: ofset x
        :param oy: ofset y
        :return: x,y
        '''
        xp0, yp0 = self._pobierz_gorny_naroznik(ox, oy)

        return xp0 - 20, yp0 - 10

    def _stworz_podglad_ROI(self, obraz):
        '''
        Prywatna metoda tworzoca etykiete ROI'u
        wystwietlana na podgladzie
        :param obraz: klatka z podgladu
        '''

        obraz_qimage = QImage(obraz, 
                              obraz.shape[1],
                              obraz.shape[0],
                              obraz.strides[0],
                              QImage.Format_RGB888)

        self.obraz = QPixmap.fromImage(obraz_qimage)

        self.podglad = Podglad_ROI(str(self.nazwa),
                                   self.obraz, self)

    def pobierz_obraz(self):
        '''
        metoda zwracajaca obraz
        :return: obraz zawierajacy podglad probki
        zrobiony w momenciue tworzenia
        '''
        
        return self.obraz
    
    def pobierz_podglad(self):
        '''
        metoda zwracajaca widget podgladu ROI
        :return: obiekt klasy ROI stowarzyszony z ROI,em
        '''
        
        return self.podglad

############edycja obiektu za pomoca strzalek############################

    def przeksztalc_gorna_linie(self, mode):
        '''
        metoda wykonujaca edycje jednej z krawedzi o stala wartosc
        :param mode: jestli True to zwiekszamy wymiar jesli false
        to zmniejszamy
        '''
        
        if mode:
            self.y0 += self.stala_przemieszczenia
        else:
            self.y0 -= self.stala_przemieszczenia

    def przekstalc_dolna_linie(self, mode):
        '''
        metoda wykonujaca edycje jednej z krawedzi o stala wartosc
        :param mode: jestli True to zwiekszamy wymiar jesli 
        false to zmniejszamy
        '''
        
        if mode:
            self.y1 -= self.stala_przemieszczenia
        else:
            self.y1 += self.stala_przemieszczenia

    def przekstalc_lewa_linie(self, mode):
        '''
        metoda wykonujaca edycje jednej z krawedzi o stala wartosc
        :param mode: jestli True to zwiekszamy wymiar jesli 
        false to zmniejszamy
        '''
        
        if mode:
            self.x0 += self.stala_przemieszczenia
        else:
            self.x0 -= self.stala_przemieszczenia

    def przekstalc_prawa_linie(self, mode):
        '''
        metoda wykonujaca edycje jednej z krawedzi o stala wartosc
        :param mode: jestli True to zwiekszamy wymiar jesli 
        false to zmniejszamy
        '''
        if mode:
            self.x1 -= self.stala_przemieszczenia
        else:
            self.x1 += self.stala_przemieszczenia

    def przesun_w_gore(self):
        '''
        metoda przesuwajaca podglad w jednym z kierunkow
        '''
        self.y0 -= self.stala_przemieszczenia
        self.y1 -= self.stala_przemieszczenia

    def przesun_w_dol(self):
        '''
        metoda przesuwajaca podglad w jednym z kierunkow
        '''
        self.y0 += self.stala_przemieszczenia
        self.y1 += self.stala_przemieszczenia

    def przesun_w_lewo(self):
        '''
        metoda przesuwajaca podglad w jednym z kierunkow
        '''
        self.x0 -= self.stala_przemieszczenia
        self.x1 -= self.stala_przemieszczenia

    def przesun_w_prawo(self):
        '''
        metoda przesuwajaca podglad w jednym z kierunkow
        '''
        self.x0 += self.stala_przemieszczenia
        self.x1 += self.stala_przemieszczenia

################odbieranie i wysylanie flagi edycji######################

    def edit(self):
        '''
        metoda wlaczajaca tryb edycji
        '''
        self.obraz_obiekt.edit_roi(self)
        
    def zakoncz_edit(self):
        '''
        metoda konczoca tryb edycji
        '''

        #zakonczenie trybu edycji w obrazie i pobranie 
        #z niego nowej klatki podgladu
        klatka = self.obraz_obiekt.zakoncz_edit()

        #konwersja klatki na Qimage
        klatka_qimage = QImage(klatka, klatka.shape[1],
                               klatka.shape[0],
                               klatka.strides[0],
                               QImage.Format_RGB888)

        #zapisanie klatki
        self.obraz = QPixmap.fromImage(klatka_qimage)

        #odswiezenei klatki w podgladzie
        self.podglad.nowy_obraz(self.obraz)

###############################samo edycha###############################

    def wspolrzedne_nacisniecia(self, e, ofsetx, ofsety):
        '''
        Metoda wywolywana w trybie edycji przy nacisnieciu
        przycisku myszki
        :param e: wspolrzedne w ktorych myszka zostala nacisnieta
        :param ofsetx:
        :param ofsety:
        '''

        # restart paramterow edycji
        self.pierwsze_klikniecie = True
    
        self.kanta_gora = False
        self.kanta_dol = False
        self.kanta_lewa = False
        self.kanta_prawy = False
        
        self.przemiesc_wszystkie = False

        # odczyt i konwersja wspolrzednych klikniecia
        self.px0 , self.py0 = e.x() + ofsetx, e.y()+ofsety

        # rozpoznanie kant koro ktorych doszlo do klikniecia
        if self.x0-self.szerokosc_obszaru_klikniecia < self.px0 <\
                  self.x0+self.szerokosc_obszaru_klikniecia and\
                  self.y0-self.szerokosc_obszaru_klikniecia < self.py0 <\
                  self.y1+self.szerokosc_obszaru_klikniecia:

            self.kanta_prawy = True
        
        if self.x1-self.szerokosc_obszaru_klikniecia < self.px0 <\
                  self.x1+self.szerokosc_obszaru_klikniecia and \
                  self.y0-self.szerokosc_obszaru_klikniecia < self.py0 <\
                  self.y1+self.szerokosc_obszaru_klikniecia:

            self.kanta_lewa = True
            
        if self.y0-self.szerokosc_obszaru_klikniecia < self.py0 <\
                  self.y0+self.szerokosc_obszaru_klikniecia and\
                  self.x0-self.szerokosc_obszaru_klikniecia < self.px0 <\
                  self.x1+self.szerokosc_obszaru_klikniecia:

            self.kanta_gora = True
            
        if self.y1-self.szerokosc_obszaru_klikniecia < self.py0 <\
                  self.y1+self.szerokosc_obszaru_klikniecia and\
                  self.x0-self.szerokosc_obszaru_klikniecia < self.px0 <\
                  self.x1+self.szerokosc_obszaru_klikniecia:

            self.kanta_dol = True
        
        
        #sprawdzanie czy nie spelniamy warinkow ktoregos z rogow
        self.lewa_gora = self.kanta_lewa and self.kanta_gora
        self.prawa_gora = self.kanta_prawy and self.kanta_gora
        
        self.lewy_dol = self.kanta_lewa and self.kanta_dol
        self.prawy_dol = self.kanta_prawy and self.kanta_dol

        #sprawdzenie czy nie kliknelismy w srodek obszaru
        if self.y0+self.szerokosc_obszaru_klikniecia < self.py0 <\
                  self.y1-self.szerokosc_obszaru_klikniecia and \
                  self.x0+self.szerokosc_obszaru_klikniecia < self.px0 <\
                  self.x1-self.szerokosc_obszaru_klikniecia:

            self.przemiesc_wszystkie = True

        # odswierzenie kordynmatow na podgladzie
        self.podglad.odswierz_kordynaty()

    def wspolrzedne_puszczenia(self, e, ofsetx, ofsety):
        '''
        metoda wykonywana po puszczeniu przycisku myszki
        zapisuje wykonana edycjie ROI'u
        :param e: pozycja myszki
        :param ofsetx:
        :param ofsety:
        '''

        # reset licznika klikniec
        self.pierwsze_klikniecie = False

        #  odczyt i konwersja wspolrzednych klikniecia
        self.px1 , self.py1 = e.x() + ofsetx, e.y()+ofsety

        # sprawdzenie trybu pracy i adekwatna do niego edycja ROI'u
        if self.przemiesc_wszystkie:
            dx, dy = self.px1 - self.px0, self.py1 - self.py0
            self.x0 += dx
            self.x1 += dx
            self.y0 += dy
            self.y1 += dy
        
        elif self.lewa_gora:
            self.x1 = self.px1
            self.y0 = self.py1
            
        elif self.lewy_dol:
            self.x1 = self.px1
            self.y1 = self.py1
            
        elif self.prawy_dol:
            self.x0 = self.px1
            self.y1 = self.py1
            
        elif self.prawa_gora:
            self.x0 = self.px1
            self.y0 = self.py1
            
        elif self.kanta_dol:
            self.y1 = self.py1
  
  
        elif self.kanta_lewa:
            self.x1 = self.px1
            
        elif self.kanta_prawy:
            self.x0 = self.px1
            
        elif self.kanta_gora:
            self.y0 = self.py1

        # odswierzenie kordynmatow na podgladzie
        self.podglad.odswierz_kordynaty()
      
    def przemiesc_kordynaty(self, e, ofsetx, ofsety):

        # sprawdzenie licznika klikniec
        if self.pierwsze_klikniecie:

            # odczyt i konwersja wspolrzednych klikniecia
            self.px1 , self.py1 = e.x() + ofsetx, e.y()+ofsety
            
            # sprawdzenie trybu pracy i adekwatne obsluzenie 
            # edycji dla niego
            if self.przemiesc_wszystkie:
                dx, dy = self.px1 - self.px0, self.py1 - self.py0
                self.x0 += dx
                self.x1 += dx
                self.y0 += dy
                self.y1 += dy
                self.px0 , self.py0 = e.x() + ofsetx, e.y()+ofsety
        
            elif self.lewa_gora:
                self.x1 = self.px1
                self.y0 = self.py1
                
            elif self.lewy_dol:
                self.x1 = self.px1
                self.y1 = self.py1
                
            elif self.prawy_dol:
                self.x0 = self.px1
                self.y1 = self.py1
                
            elif self.prawa_gora:
                self.x0 = self.px1
                self.y0 = self.py1
                
            elif self.kanta_dol:
                self.y1 = self.py1
            elif self.kanta_lewa:
                self.x1 = self.px1
            elif self.kanta_prawy:
                self.x0 = self.px1
            elif self.kanta_gora:
                self.y0 = self.py1

            # odswierzenie kordynmatow na podgladzie
            self.podglad.odswierz_kordynaty()
