from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtGui import QImage, QPixmap
from kwadrat_label import Podglond_ROI


class obszarzaznaczony():
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

    kanta_gura = False
    kanta_dul = False
    kanta_lewa = False
    kanta_prawy = False
    
    lewa_gura = False
    prawa_gura = False
    lewy_dul = False
    prawy_dul = False
    
    przemiesc_wsystkie = False
    ####################################

    # konstruktor tworzocy obiekt ze wzglednych wspułrednych prubki w pixelach
    def __init__(self, obraz_obcet, xp0, yp0, xp1, yp1, image, px00=0, py00=0, nazwa="defalaut", s=1):

        #Nadrzedny obiekt (map lub kamera) w któyrym strworzono obiektr przekazanoy w celu komunikacji
        self.Obraz_obcet = obraz_obcet

        #nazwa obiektu
        self.nazwa = nazwa

        #metoda tworzoca niezalezne wspulrdzede prubki w pixelach
        self.x0, self.x1, self.y0, self.y1 = self._zalezne_to_niezalezne(xp0, yp0, xp1, yp1, px00, py00, s)

        #metoda tworzoca widget umozliwiajacy interakcje z obiektem
        self.create_Roi_label(image)

        #metoda tworzoca niezalerzne wspułredne prubki w mm
        self._set_niezalezne_prubki()

    def __del__(self):
        '''
        dekonstruktor klasy obsluguje usuniecie podglondu i wyloczenie edycji
        '''
        self.end_edit()
        self.Obraz_obcet.rmv_rectagle(self)
        del self.podglond

    def pobierz_wzgledny_rectagle(self):
        '''
        metoda zwracajaca aktualne wzgledne wspulrzedne roiu w pixelach
        :return: x0, y0, x1, y1
        '''
        x0 = (self.x0 - self.Obraz_obcet.ofsetx)
        y0 = (self.y0 - self.Obraz_obcet.ofsety)

        x1 = (self.x1 - self.Obraz_obcet.ofsetx)
        y1 = (self.y1 - self.Obraz_obcet.ofsety)
    
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
        return self._niezalezne_to_zalezne(self.x0, self.y0, self.x1, self.y1, -px00, -py00, s)

    def _zalezne_to_niezlezne(self, xp0, yp0, xp1, yp1, px00, py00, s):
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
        return self._niezalezne_to_zalezne(xp0, yp0, xp1, yp1, px00, py00, s)

    def konwersja(self, xp0, yp0, xp1, yp1, px00, py00, s):
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

    def poierznazwe(self):
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

    #metoda zwracajaca lokacje nazwy wyswietlanej na podglondzie
    def gettextloc(self, ox, oy):

        xp0, yp0 = self._gettop_corner(ox, oy)

        return xp0 - 20, yp0 - 10

    def create_Roi_label(self, image):

        frame = image

        img = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)

        self.image = QPixmap.fromImage(img)

        self.podglond = Podglond_ROI(str(self.poierznazwe()), self.get_image(), self)

    def get_image(self):
        return self.image
    
    def get_podglond(self):
        return self.podglond

############edycja obiektu za pomoca strzalek####################
    def move_top_line(self, mode):
        if mode:
            self.y0 += 10
        else:
            self.y0 -=10

    def move_dwn_line(self, mode):
        if mode:
            self.y1 -=10
        else:
            self.y1 +=10

    def move_lft_line(self, mode):
        if mode:
            self.x0 +=10
        else:
            self.x0 -=10

    def move_rig_line(self, mode):
        if mode:
            self.x1 -=10
        else:
            self.x1 +=10

    def move_top(self):
        self.y0 -=10
        self.y1 -=10

    def move_dwn(self):#left

        self.y0 +=10
        self.y1 +=10

    def move_lft(self):
        self.x0 -=10
        self.x1 -=10

    def move_rig(self):

        self.x0 +=10
        self.x1 +=10

################odbieranie iw ysyłanie flagi edycji###########

    def edit(self):
        self.Obraz_obcet.edit_roi(self)
        
    def end_edit(self):
        frame = self.Obraz_obcet.end_edit()

        img = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0],QImage.Format_RGB888)  

        self.image = QPixmap.fromImage(img)

        self.podglond.nowy_obraz(self.image)
###############################self edit##########################################

    def pres_cords(self, e, ofsetx, ofsety):

        #reseting previus paramiters
        self.pierwsze_klikniecie = True
    
        self.kanta_gura = False
        self.kanta_dul = False
        self.kanta_lewa = False
        self.kanta_prawy = False
        
        self.przemiesc_wsystkie = False
        
        wopszaru = 10
    
        self.px0 , self.py0 = e.x() + ofsetx, e.y()+ofsety

        #recognising neret eage eages
        if self.x0-wopszaru<self.px0<self.x0+wopszaru and self.y0-wopszaru<self.py0<self.y1+wopszaru:
            self.kanta_prawy = True
        
        if self.x1-wopszaru<self.px0<self.x1+wopszaru and self.y0-wopszaru<self.py0<self.y1+wopszaru:
            self.kanta_lewa = True
            
        if self.y0-wopszaru<self.py0<self.y0+wopszaru and self.x0-wopszaru<self.px0<self.x1+wopszaru:
            self.kanta_gura = True
            
        if self.y1-wopszaru<self.py0<self.y1+wopszaru and self.x0-wopszaru<self.px0<self.x1+wopszaru:
            self.kanta_dul = True
        
        #checkig for corners
        self.lewa_gura = self.kanta_lewa and self.kanta_gura
        self.prawa_gura = self.kanta_prawy and self.kanta_gura
        
        self.lewy_dul = self.kanta_lewa and self.kanta_dul
        self.prawy_dul = self.kanta_prawy and self.kanta_dul

        #checking for center of the marked region
        if self.y0+wopszaru<self.py0<self.y1-wopszaru and self.x0+wopszaru<self.px0<self.x1-wopszaru:
            self.przemiesc_wsystkie = True

        #update kordynat
        self.podglond.odswierz_kordynaty()

    def relise_cords(self,e,ofsetx, ofsety):

        #reset pres caount
        self.pierwsze_klikniecie = False

        #read and ofset cords
        self.px1 , self.py1 = e.x() + ofsetx, e.y()+ofsety

        #chec for trybe
        if self.przemiesc_wsystkie:
            dx, dy = self.px1 - self.px0, self.py1 - self.py0
            self.x0 += dx
            self.x1 += dx
            self.y0 += dy
            self.y1 += dy
        
        elif self.lewa_gura:
            self.x1 = self.px1
            self.y0 = self.py1
            
        elif self.lewy_dul:
            self.x1 = self.px1
            self.y1 = self.py1
            
        elif self.prawy_dul:
            self.x0 = self.px1
            self.y1 = self.py1
            
        elif self.prawa_gura:
            self.x0 = self.px1
            self.y0 = self.py1
            
        elif self.kanta_dul:
            self.y1 = self.py1
        elif self.kanta_lewa:
            self.x1 = self.px1
        elif self.kanta_prawy:
            self.x0 = self.px1
        elif self.kanta_gura:
            self.y0 = self.py1

        self.podglond.odswierz_kordynaty()
      
    def move_cords(self, e, ofsetx, ofsety):

        #chec if maouse is presed
        if self.pierwsze_klikniecie:

            #ofset reded cords
            self.px1 , self.py1 = e.x() + ofsetx, e.y()+ofsety
            
            #chec for trybe
            if self.przemiesc_wsystkie:
                dx, dy = self.px1 - self.px0, self.py1 - self.py0
                self.x0 += dx
                self.x1 += dx
                self.y0 += dy
                self.y1 += dy
                self.px0 , self.py0 = e.x() + ofsetx, e.y()+ofsety
        
            elif self.lewa_gura:
                #print("lewa_gura")
                self.x1 = self.px1
                self.y0 = self.py1
                
            elif self.lewy_dul:
                #print("lewy_dul")
                self.x1 = self.px1
                self.y1 = self.py1
                
            elif self.prawy_dul:
                #print("prawy_dul")
                self.x0 = self.px1
                self.y1 = self.py1
                
            elif self.prawa_gura:
                #print("prawa_gura")
                self.x0 = self.px1
                self.y0 = self.py1
                
            elif self.kanta_dul:
                self.y1 = self.py1
            elif self.kanta_lewa:
                self.x1 = self.px1
            elif self.kanta_prawy:
                self.x0 = self.px1
            elif self.kanta_gura:
                self.y0 = self.py1

            self.podglond.odswierz_kordynaty()
                
