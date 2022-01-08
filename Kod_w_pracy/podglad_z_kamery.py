import numpy as np
import cv2
from PyQt5.QtWidgets import QMessageBox
import sys
import toupcam as tcam
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QRect
from PyQt5.QtGui import QImage, QPainter, QBrush, QColor
from roi_create import oznacz_ROI
from Map import Map_window



class Obraz_z_kamery(oznacz_ROI):

    '''
    Klasa Obraz_z_kamery dziedziczy z oznacz_ROI,
    pozwala na odczyt obrazu z kamery oraz zbieranie mapy.
    '''

    # wlasne sygnaly umozliwiajace obsluge kamery
    nowy_obraz_z_kamery = pyqtSignal()
    nowy_wymuszony_obraz_z_kamery = pyqtSignal()

    h_cam = None    # wskaznik do kamery
    buf = None      # bufor na wideo
    w = 0           # szerokosc wideo
    h = 0           # wysokosc wideo

    # '' 'up' 'dawn' 'right' 'left' 'multi'
    zmiana_kierunku = ''
    
    # zmienna binarna pozwalajaca na 
    # stworzenie obiektu mapa z pierwszej
    # klatki
    first = True

    # pixmap obiekt odczytany z kamery
    klatka = True

    # numpay arrey ktora bedzie przechowywac mape
    map = np.zeros(100)
    map.shape = (10, 10, 1)
    
    # skala mapy
    skala_mapy = 32
    
    # skala mapy
    skala = 1
    
    # konstruktor
    def __init__(self, main_window, *args, **kwargs):
        super(Obraz_z_kamery,self).__init__(main_window,*args,**kwargs)

        self._inicializacja_kamery()
        
        self.h_cam.put_AutoExpoEnable(False)
        
        self.odczytaj_klatke()


#########################################################################
###############################odczyt kamery#############################
#########################################################################

    def odczytaj_klatke(self):
        '''
        Metoda wysylajaca sygnal do kamery
        wymuszajacy odczyt nowej klatki
        '''

        self.h_cam.Snap(1)
    
    
    @pyqtSlot()
    def nowy_wymuszony_obraz_z_kamery_sygnal(self):
        '''
        Metoda odczytujaca klatke z kamery konwertujaca 
        ja na obraz openCV
        zapisujaca ja do freame_2 oraz image_opencv
        nastepnie wywolujaca metode roszerzajaca mape
        '''
        
        # sprawdzamy komunikacje z kamera
        if self.h_cam is not None:


            #definiujemy rozmiar buforu na obraz
            w, h = self.h_cam.get_Size()
            bufsize = ((w * 24 + 31) // 32 * 4) * h
            still_img_buf = bytes(bufsize)

            #pobieramy do buforu obraz z kamery
            self.h_cam.PullStillImageV2(still_img_buf, 24, None)

            #konwertujemy obraz z buforu do obrazu opencv
            obraz = self.obraz_bitowy_do_obrazu_opencv(still_img_buf)

            #zapisujemy odczytany obraz
            self.klatka_2 = obraz.copy()

            self.image_opencv = obraz.copy()
            
            #rozszerezamy mape
            self.zapisz_aktualny_podglad()
            self.zaladuj_obraz(True, False)

    @staticmethod
    def metoda_wywolwana_przez_kamere(nevent, ctx):
        '''
        Statyczna metoda wywolywana przez kamere
        :param nevent: event wemitowany przez kamere
        :param ctx: self
        '''

        if nevent == tcam.TOUPCAM_EVENT_IMAGE:
            ctx.nowy_obraz_z_kamery.emit()

        elif nevent == tcam.TOUPCAM_EVENT_STILLIMAGE:
            ctx.nowy_wymuszony_obraz_z_kamery.emit()


    @pyqtSlot()
    def nowy_obraz_z_kamery_sygnal(self):
        '''
        Metoda odczytujaca obraz z kamery,
        konwertujaca go na obraza openCV,
        zapisujaca go
        oraz wgrywajaca go do podgladu
        '''

        #sprawdzenie komunikacji z kamera
        if self.h_cam is not None:

            #proba odczytania klatki
            try:
                self.h_cam.PullImageV2(self.buf, 24, None)

            #obsluzenie bledu na wypadek  bledu odczytu
            except tcam.HRESULTException:
            
                print('pull obraz failed')
                QMessageBox.warning(self, '','pull obraz failed', 
                                    QMessageBox.Ok)

            else:

                #konwersja i odczyt obrazu z bufora
                self.image_opencv = self.\
                     obraz_bitowy_do_obrazu_opencv(self.buf)

                #zaladowanie obrazu
                self.zaladuj_obraz(True, False)
         

    def obraz_bitowy_do_obrazu_opencv(self, 
    still_img_buf, dtype=np.uint8):
        '''
        metoda konwertujaca obraz z buforu bitow na
        tablice numpaya obslugiwana przez openCV
        :param still_img_buf: bufor z obrazem
        :param dtype: typ danych
        :return: skonwertowana tabela z obrazem
        '''

        arr_1d = np.frombuffer(still_img_buf, dtype=dtype)
        
        return arr_1d.reshape(self.h, self.w, 3)

    def _inicializacja_kamery(self):
        '''
        Metoda inicializujaca kamere
        '''

        #wywolanie instrukcji inicializujacej
        a = tcam.Toupcam.EnumV2()

        #sprawdzenie czy adres komunikacyjny nie jest bledny
        if len(a) <= 0:
            QMessageBox.warning(self, '',
                                "error during camera initialisation",
                                QMessageBox.Ok)

        else:
            #pobranie nazwy kamery
            self.nazwa_kamery = a[0].displayname

            # stworzenie i podlaczenie wlasnych pyqt5 signal
            self.nowy_obraz_z_kamery.connect(
                       self.nowy_obraz_z_kamery_sygnal)
            self.nowy_wymuszony_obraz_z_kamery.connect(
                 self.nowy_wymuszony_obraz_z_kamery_sygnal)

            # otwarcie komunikacji z kamera
            try:
                self.h_cam = tcam.Toupcam.Open(a[0].id)

            except tcam.HRESULTException:
                QMessageBox.warning(self, '',
                       'failed to open camera', QMessageBox.Ok)

            else:
                # stworzenie buforu
                self.w, self.h = self.h_cam.get_Size()
                self.buf = bytes(((self.w * 24 + 31) // 32 * 4)
                                 * self.h)

                try:
                    #obsluzenie starszej wersji systemu widows
                    if sys.platform == 'win32':
                        self.h_cam.put_Option(tcam.\
                             TOUPCAM_OPTION_BYTEORDER, 0)  

                    #przekazanie kamerze metody do wywolywania 
                    #i obiektu na ktorym ma byc wywolana
                    self.h_cam.StartPullModeWithCallback(
                         self.metoda_wywolwana_przez_kamere, self)

                except tcam.HRESULTException:
                    QMessageBox.warning(self, '', 
                           'failed to start camera', QMessageBox.Ok)

#############################Paint Event#################################

    def paintEvent(self, event):
        '''
        Metoda przeciazajaca paintEvent
        z oznacz_ROI dodajaca obsluge
        dodatkowych trybow rysowania
        jest wywolywana automatycznie za
        kazdym razem kiedy obiekt jest odswiezany
        '''
       
        # inicializacja qpintera
        qp = QPainter(self)

        # rysowanie obrazu
        qp.drawPixmap(self.rect(), self._obraz_z_klatki)

        # wgranie ustawien koloru i wypelnienia ROI
        qp.setBrush(QBrush(QColor(200, 20, 20, 255),
           Qt.CrossPattern))


        # zmienne okreslajace czy wyswietlamy numeracje czy nie
        nasrysuj_opisy = True
        narysuj_jeden_ROI = False

        if self.co_narysowac == 'all_rectagls': 

            # pokazuje wszystkie prostokaty
            self.wsystkie_prostokaty(qp)

        elif self.co_narysowac == 'no_rectagle':  

            # chowa wszystkie prostokaty
            nasrysuj_opisy = False

        elif self.co_narysowac =='One_rectagle': 
 
            # rysuje wybrany prostokat
            self._wybrany_prostokat(qp)
            nasrysuj_opisy = False
            narysuj_jeden_ROI = True

        elif self.co_narysowac == 'viue_muve': 

            # rysuje wsystkie prostokaty
            #i obsluguje odswiezenie podgladu.
            self.wsystkie_prostokaty(qp)

            self.odczytaj_klatke()

        else: 
            # podstawowa opcja rysuje nowy prostokat
            self.wsystkie_prostokaty(qp)
            qp.drawRect(QRect(self.poczatek, self.koniec))

        self.zaladuj_obraz(nasrysuj_opisy, narysuj_jeden_ROI)

    def _wybrany_prostokat(self, painter):
        '''
        metoda rysujaca wybrany prostokat
        '''

        painter.drawRect(self.narysuj_prostokat(
                                    self.main_window.ROI[self.ktory]))

#######funkcje wywolywane przez guziki z glownego okna###################

    def narysuj_calosc(self):
        '''
        podniesienie flagi odpowiedzialnej
        za narysowanie wszytkich prostokatow
        '''
        self.co_narysowac = 'all_rectagls'
    
    def schowajcalosc(self):
        '''
        podniesienie flagi odpowiedzialnej
        za to zeby nie rysowac zadnych prostokatow
        :return:
        '''
        self.co_narysowac = 'no_rectagle'
            
    def nastempny(self):
        '''
        podniesienie flagi i ustawienie
        odpoweiedniego iteratora
        odpowiedzialnego za narysowanie
        nastepnego prostokata
        '''
        
        if len(self.main_window.ROI) > 0:
        
            self.co_narysowac = 'One_rectagle'
            
            if self.ktory < len(self.main_window.ROI)-1:
                self.ktory += 1
            else:
                self.ktory = 0

        else:
            pass
       
    def poprzedni(self):
        '''
        podniesienie flagi i ustawienie odpoweiedniego iteratora
        odpowiedzialnego za narysowanie poprzedniego prostokata
        '''
        if len(self.main_window.ROI) > 0:
            self.co_narysowac = 'One_rectagle'
            self.iloscklikniec = True
            
            if self.ktory == 0:
                self.ktory = len(self.main_window.ROI)-1
            else:
                self.ktory -= 1
            
            self.update()
        else:
            pass

###########################przesuwanie podgladu##########################

    def lewo(self):
        '''
        metoda obslugujaca przesuniecie podgladu przez manipulator
        '''
        self.ofsetx -= self.delta_pixeli
        self._flagi_przemieszczenie()
   
    def prawo(self):
        '''
        metoda obslugujaca przesuniecnie podgladu przez manipulator
        '''
        self.ofsetx += self.delta_pixeli
        self._flagi_przemieszczenie()

    def dol(self):
        '''
        metoda obslugujaca przesuniecnie podgladu przez manipulator
        '''
        self.ofsety -= self.delta_pixeli
        self._flagi_przemieszczenie()

    def gora(self):
        '''
        metoda obslugujaca przesuniecnie podgladu przez manipulator
        '''
        self.ofsety += self.delta_pixeli
        self._flagi_przemieszczenie()
 
    def _flagi_przemieszczenie(self):
        '''
        metoda podnoszaca odpowiednia flage 
        oraz wylaczajaca tryb edycji jesli jest wlaczony
        '''

        if self.edit_tryb:
            self.edited_roi.podglad.przyciski[0].toggle()
            self.edited_roi.zakoncz_edit()
            self.edit_trybe = False
            
        self.co_narysowac = 'viue_muve'
        self.update()

    def odswierz_ofsets(self):
        '''
        metoda obslugujaca zrownowazone polaczenie
        startowe w zaleznosci od pozycji startowej manipulatora
        '''
        xm, ym, zm, = self.main_window.manipulaor.pobierz_pozycje_osi()
        
        ym, zm = int((50-ym)*510), int((50-zm)*510)
 
        self.ofsetx = ym
        self.ofsety = zm
 
##########################edycja mapy##################################

    def zapisz_aktualny_podglad(self):
        '''
        metoda zapisujaca aktualna klatke do mapy
        jesli mapa nie zostala jeszcze zdefiniowana
        tworzy tablice do zbierania mapy
        oraz tworzy obiekt wyswietlajacy mape jesli
        nie zostal on jeszcze stworzony
        '''

        if self.first:
            self._stworz_pojemnik_na_mape()

        # wykonanie funkcji wklejajacej aktualny podglad do mapy
        self.wklejenie_klatki_do_mapy()

        if self.main_window.map is None:
            self.main_window.map = Map_window(self.map, self.main_window)
        else:
            self.main_window.map.new_image(self.map)

    def _stworz_pojemnik_na_mape(self):
        '''
        prywatna metoda tworzca pojemnik na mape
        '''
        x, y, z = self.klatka_2.shape
        
        # x rozmiar
        rozmiar_mapy = int((x + self.manipulator_max * self.delta_pixeli)
                             / self.skala_mapy)
        # y rozmiar
        rozmiar_mapy *= int((y + self.manipulator_max * self.delta_pixeli)
                              / self.skala_mapy)
        rozmiar_mapy *= 3  # RGB kolory
        # stworzenie tablicy przechowujacej obraz mapy
        self.map = np.zeros(rozmiar_mapy, dtype=np.uint8)
        # okreslenie ksztaltu tej tablicy
        self.map.shape = (int((y + self.manipulator_max 
                                * self.delta_pixeli)/ self.skala_mapy),
                          int((x + self.manipulator_max 
                                * self.delta_pixeli)/ self.skala_mapy), 3)
        # zapisanie ze mapa juz jest zainicjowana
        self.first = False

    def wklejenie_klatki_do_mapy(self):
        '''
        metoda zapisujaca do mapy aktualny podglad we wskazane
        miejsce na ktorym znajduje sie manipulator
        '''
        x, y, z = self.klatka_2.shape  
        xm, ym, zm, = self.main_window.manipulaor.pobierz_pozycje_osi()
        
        # przeliczenie milimetrow na pixele i odwrocenie osi
        ym = int((50-ym)*510/self.skala_mapy)
        zm = int((50-zm)*510/self.skala_mapy)
        
        #przeskalowanie podgladu
        klatka = cv2.resize(self.klatka_2, (int(y / self.skala_mapy),
                                            int(x / self.skala_mapy)))
        #wklejenie podgladu we wlasciwe miejsce na mapie
        try:
            self.map[zm:zm+int(x/self.skala_mapy),
                     ym:ym+int(y/self.skala_mapy)] = klatka
        except Exception as e:
            print(e)

    def reset_map(self):
        '''
        metoda czyszczaca zebrana aktualnie mape
        '''
        # zapytanie uzytkownika czy napewno chce to zrobic
        reply = QMessageBox.question(self, "mesage",
                       "Czy napewno chcesz usunac mape?",
                       QMessageBox.Yes|QMessageBox.No, 
                       QMessageBox.Yes)
        
        if reply == QMessageBox.Yes:
            self.first = True
            self.zapisz_aktualny_podglad()
            
    def ponbierz_map(self):
        return self.map
          
    def _map_update(self):
        self.co_narysowac = 'viue_muve'
        self.update()
