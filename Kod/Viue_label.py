import numpy as np
import cv2
from PyQt5.QtWidgets import QMessageBox
import sys
import toupcam as tcam
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QRect
from PyQt5.QtGui import QImage, QPainter, QBrush, QColor
from roi_create import ROI_maping
from Map import Map_window


class Obraz_z_kamery(ROI_maping):
    '''
    Klaza Obraz_z_kamery dziedziczy z ROI_maping,
    pozwala na odczyt obrazu z kamery oraz zbieranie mapy.
    '''

    # własne sygnaly umozliwiajace obsluge kamery
    nowy_obraz_z_kamery = pyqtSignal()
    nowy_wymuszony_obraz_z_kamery = pyqtSignal()

    h_cam = None    # wskaznik do kamery
    buf = None      # bufor na wideo
    w = 0           # szerokosc wideo
    h = 0           # wysokosc wideo

    # '' 'up' 'dawn' 'right' 'left' 'multi'
    zmiana_kierunku = ''
    
    # boolean alowing to snap first shown obraz as a map prive
    first = True

    # pixmap object reded from camera/file
    klatka = True

    # numpay arrey która bendzie przechowywac mape
    map = np.zeros(100)
    map.shape = (10, 10, 1)
    
    # construvtor
    def __init__(self, main_window, *args, **kwargs):
        super(Obraz_z_kamery, self).__init__(main_window, *args, **kwargs)

        self._inicializacja_kamery()
        
        self.h_cam.put_AutoExpoEnable(False)

###############################camera read##########################################

    def odczytaj_klatke(self):
        '''
        Metoda wysyłajaca sygnal do kamery wymuszajacy odczyt nowej klatki
        :return:
        '''
        self.h_cam.Snap(1)
    
    @pyqtSlot()
    def nowy_wymuszony_obraz_z_kamery_sygnal(self):
        '''
        Metoda odczytujaca klatke z kamery konwertujaca ja na obraz openCV
        zapisujaca ja do freame_2 oraz image_opencv
        nastempnie wywolujaca metode roszerzajaca mape
        :return:
        '''

        # sprawdzamy komunikacje z kamera
        if self.h_cam is not None:

            #definiujemy rozmiar buforu na obraz
            w, h = self.h_cam.get_Size()
            bufsize = ((w * 24 + 31) // 32 * 4) * h
            still_img_buf = bytes(bufsize)

            #pobnieramy do buforu obraz z kamery
            self.h_cam.PullStillImageV2(still_img_buf, 24, None)

            #konwertujemy obraz z buforu do obrazu opencv
            img = self.obraz_bitowy_do_obrazu_opencv(still_img_buf)

            #zapisujemy odczytany obraz
            self.klatka_2 = cv2.resize(img, self.rozmiar)
            self.image_opencv  = img

            #rozszerezamy mape
            self.zapisz_aktualny_podglond()

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
        Metoda odczytujaca obraz z kamery konwertujaca ja na obraza openCV
        zapisujaca go
        oraz wgrywajaca go do podglondu
        '''

        #sprawdzenie komunikacji z kamera
        if self.h_cam is not None:

            #pruba odczytania klatki
            try:
                self.h_cam.PullImageV2(self.buf, 24, None)

            #obsluzenie błedu na wypadek  bledu odczytu
            except tcam.HRESULTException:
                print('pull obraz failed')
                QMessageBox.warning(self, '', 'pull obraz failed', QMessageBox.Ok)

            else:

                #konwersja i odczyt obrazu z bufora
                self.image_opencv = self.obraz_bitowy_do_obrazu_opencv(self.buf)

                #załadowanie obrazu
                self.update()
                #self.loadImage(True, False)

    def obraz_bitowy_do_obrazu_opencv(self, still_img_buf, dtype=np.uint8):
        '''
        metoda konwertujaca obraz z buferu bitów na tablice numpaya czytana przez openCV
        :param still_img_buf: bufor z obrazem
        :param dtype: typ danych
        :return: skonwettowana tabela z obrazem
        '''
        arr_1d = np.frombuffer(still_img_buf, dtype=dtype)
        return arr_1d.reshape(self.h, self.w, 3)

    def _inicializacja_kamery(self):
        '''
        Metoda inicializujaca kamere
        '''

        #wywolanie instrukcji inicializujacej
        a = tcam.Toupcam.EnumV2()

        #sprawdzenie czy adres komunikacyjny nie jest błedny
        if len(a) <= 0:
            QMessageBox.warning(self, '', "error during camera initialisation", QMessageBox.Ok)

        else:
            #pobranie nazwy kamery
            self.nazwa_kamery = a[0].displayname

            # stworzenie i podloczenie kustomowych pyqt5 signa
            self.nowy_obraz_z_kamery.connect(self.eventimagesignal)
            self.nowy_wymuszony_obraz_z_kamery.connect(self.nowy_wymuszony_obraz_z_kamery_sygnal)

            # otwarcie komunikacji z kamera
            try:
                self.h_cam = tcam.Toupcam.Open(a[0].id)

            except tcam.HRESULTException:
                QMessageBox.warning(self, '', 'failed to open camera', QMessageBox.Ok)

            else:
                # stworzenie buforu
                self.w, self.h = self.h_cam.get_Size()
                self.buf = bytes(((self.w * 24 + 31) // 32 * 4) * self.h)

                try:
                    #obsluzenie starszej wersji systemu widows
                    if sys.platform == 'win32':
                        self.h_cam.put_Option(tcam.TOUPCAM_OPTION_BYTEORDER, 0)  # QImage.Format_RGB888

                    #przekazanie kamerze metody do wywolywania i obiektu na którym ma byc wywolana
                    self.h_cam.StartPullModeWithCallback(self.metoda_wywolwana_przez_kamere, self)

                except tcam.HRESULTException:
                    QMessageBox.warning(self, '', 'failed to start camera', QMessageBox.Ok)		

#############################Paint Event###############################################

    def paintEvent(self, event):
        '''
        Metoda przeciozajace paintEvent z ROI_maping dodajaca obsluge dodatkowych tryby rysowania
        jest wywolywana automatycznie za kazdym razem kiedy obiekt jest odswierzany
        '''

        # inicializacja qpintera
        qp = QPainter(self)

        # rysowanie obrazu
        qp.drawPixmap(self.rect(), self._pixmapdromframe)

        # wgranie ustawien koloru i wypelnienia ROI
        qp.setBrush(QBrush(QColor(200, 20, 20, 255), Qt.CrossPattern))

        # zmiene okreslajace czy wyswietlamy numeracje czy nie
        tym = True
        num = False

        if self.whot_to_drow == 'all_rectagls':  # pokazuje wsystkie prostkoaty
            self.all_Rectagles(qp)

        elif self.whot_to_drow == 'no_rectagle':  # howa wszystkie prostokaty
            tym = False

        elif self.whot_to_drow =='One_rectagle':  # rysuje wybrany prostokat

            self._wybrany_prostokat(qp)
            tym = False
            num = True

        elif self.whot_to_drow == 'viue_muve': # rysuje wsystkie prostkoaty i obsluguje odswiezenie podglondu.

            self.all_Rectagles(qp)

            self.odczytaj_klatke()

        else: # podstawowa obcja rysuje nowy prostokat
            # rysowanie prostokonta na bierzoco jak podglond do ruchu myszka
            self.all_Rectagles(qp)
            qp.drawRect(QRect(self.begin, self.end))


        self.loadImage(tym, num)

    def _wybrany_prostokat(self, painter):
        '''
        metoda rysujaca wybrany prostokąt
        :param painter:
        :return:
        '''
        painter.drawRect(self.rectagledrow(self.main_window.ROI[self.ktury]))

####################################fukcje wywoływane przez guziki z gluwnego okna####################################

    def narysujcaloscs(self):
        '''
        podniesienie flagi odpowiedzialnej za narysowanie wsytkich prostokatów
        '''

        self.whot_to_drow = 'all_rectagls'
    
    def schowajcalosc(self):
        '''
        podniesienie flagi odpowiedzialnej za to zeby nie rysowac zadnych prostokatów
        :return:
        '''

        self.whot_to_drow = 'no_rectagle'
            
    def nastempny(self):
        '''
        podniesienie flagi i ustawienie odpoweiedniego iteratora
        odpowiedzialnego za narysowanie nastempnego prostokata
        '''
        
        if len(self.main_window.ROI) > 0:
        
            self.whot_to_drow = 'One_rectagle'
            
            if self.ktury < len(self.main_window.ROI)-1:
                self.ktury += 1
            else:
                self.ktury = 0

        else:
            pass
       
    def poprzedni(self):
        '''
        podniesienie flagi i ustawienie odpoweiedniego iteratora
        odpowiedzialnego za narysowanie poprzedniego prostokata
        '''
        if len(self.main_window.ROI) > 0:
            self.whot_to_drow = 'One_rectagle'
            self.iloscklikniec = True
            
            if self.ktury == 0:
                self.ktury = len(self.main_window.ROI)-1
            else:
                self.ktury -= 1
            
            self.update()
        else:
            pass

###########################przesuwanie podgladu##############################    

    def lewo(self):
        '''
        metoda obslugujaca przesuniecnie podglondu przez manipulator
        '''
        self.ofsetx -= self.delta_pixeli
        self._flagi_przemiesczenie()
   
    def prawo(self):
        '''
        metoda obslugujaca przesuniecnie podglondu przez manipulator
        '''
        self.ofsetx += self.delta_pixeli
        self._flagi_przemiesczenie()

    def dul(self):
        '''
        metoda obslugujaca przesuniecnie podglondu przez manipulator
        '''
        self.ofsety -= self.delta_pixeli
        self._flagi_przemiesczenie()

    def gura(self):
        '''
        metoda obslugujaca przesuniecnie podglondu przez manipulator
        '''
        self.ofsety += self.delta_pixeli
        self._flagi_przemiesczenie()
 
    def _flagi_przemiesczenie(self):
        '''
        metoda podnoszaca odpowiednia flage oraz wylacajaca tryb edycji jesli jest wloczony
        '''

        if self.edit_trybe:
            self.edited_roi.podglond.przyciski[0].toggle()
            self.edited_roi.end_edit()
            self.edit_trybe = False
            
        self.whot_to_drow = 'viue_muve'
        self.update()

    def odswierz_ofsets(self):
        '''
        metoda obslugujaca owsety zadajaca im wartosci startowe w zaleznosci od pozycji startowej manipulatora
        '''
        xm, ym, zm, = self.main_window.manipulaor.get_axes_positions()
        
        ym, zm = int((50-ym)*510), int((50-zm)*510)
 
        self.ofsetx = ym
        self.ofsety = zm
 
###########################map extetion##############################

    def zapisz_aktualny_podglond(self):
        '''
        metoda zapisujaca aktualna klatke do mapy
        jesli mapa nie zostala jesce zadefiniowana tworzy tablice do zbierania mapy
        oraz tworzy obiekt wyswietlajacy mape jesli nie zostal on jesce stworzony
        '''

        if self.first:
           self._stwurz_pojemnik_na_mape()

        # wykonanie fukcji wklejajacej aktualny podglond do mapy
        self.extend_map_exeqiute()

        if self.main_window.map is None:
            self.main_window.map = Map_window(self.map, self.main_window)
        else:
            self.main_window.map.new_image(self.map)

    def _stwurz_pojemnik_na_mape(self):
        '''
        prywatna metoda tworzca pojemnik na mape
        '''

        x, y, z = self.klatka_2.shape

        rozmiar_mapy = int((x + self.manipulator_max * self.delta_pixeli) / self.skala)  # x rozmiar
        rozmiar_mapy *= int((y + self.manipulator_max * self.delta_pixeli) / self.skala)  # y rozmiar
        rozmiar_mapy *= 3  # RGB kolory

        # stworzenie tablicy przechowujacej obraz mapy
        self.map = np.zeros(rozmiar_mapy, dtype=np.uint8)
        # print(self.map.shape,"przed reshapem")

        # okreslenei ksztaltu tej tabliczy
        self.map.shape = (int((y + self.manipulator_max * self.delta_pixeli) / self.skala),
                          int((x + self.manipulator_max * self.delta_pixeli) / self.skala), 3)

        # zapisanie ze mapa juz jest zainiciowana
        self.first = False

    def wklejenie_klatki_do_mapy(self):
        '''
        metoda zapisujaca do mapy aktualny podglond we wskazane miejsce na którym znajduje sie manipulaor
        '''

        x, y, z = self.klatka_2.shape
        
        xm, ym, zm, = self.main_window.manipulaor.get_axes_positions()
        
        # przeliczenie milimetrow na pixele i odwrucenie osi
        ym, zm = int((50-ym)*510/self.skala), int((50-zm)*510/self.skala)
        
        #przeskalowanei podglondu
        klatka = cv2.resize(self.klatka_2, (int(y / self.skala), int(x / self.skala)))

        #wklejenie podglondu we własciwe miejsce na mapie
        try:
            self.map[zm:zm+int(x/self.skala), ym:ym+int(y/self.skala)] = klatka
        except Exception as e:
            print(e)
            print(self.map[zm:zm+int(x/self.skala), ym:ym+int(y/self.skala)].shape)

    def reset_map(self):
        '''
        metoda czyczaca zebrana aktualnie mape
        :return:
        '''
        
        # zapytanei uzytkownika czy napewno chce to zrobic
        reply = QMessageBox.question(self, "mesage", "Czy napewno chcesz usunac mape?",
                                     QMessageBox.Yes|QMessageBox.No, QMessageBox.Yes)
        
        
        if reply == QMessageBox.Yes:
            # jesli odpowie tak to ustawienie ze nie zebrano zadnej mapy i stworzenie jej na nowo nadpisuajc stara
            self.first = True
            self.zapisz_aktualny_podglond()
            
    def ponbierz_map(self):
        return self.map
          
    def mapupdate(self):
        self.whot_to_drow = 'viue_muve'
        self.update()
