import numpy as np
from PyQt5.QtWidgets import *
import cv2
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QImage
import Clasa as oC
import matplotlib.pyplot as plt
from threading import Thread
from time import sleep


class ROI_maping(QLabel):

    # obiekt Klasy MainWindow podany jako argument przy tworzeniu obiektu klasy Obraz -
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

    # skala okna wymagana do skalowania mapy
    skalx = 1
    skaly = 1
        
    # pukty poczotkowe i koncowe prostokonta
    begin = QPoint()
    end = QPoint()
       
    iloscklikniec = False
    
    # zmienne pozwalajace obejsc brak układu swichcaes
    # 'no_rectagle' 'all_rectagls' 'One_rectagle' 'viue_muve' 'previu_rectagle'
    whot_to_drow = 'all_rectagls'
    
    # iterator do wyswietlenia poprzedniego nastempego zaznaczenia
    ktury = 0

    # wartosci owsetu aktualnego podgloadu
    ofsetx = 0
    ofsety = 0
    
    # rozmiar obszaru
    rozmiar = (1024, 768)
    
    # calibration value
    delta_pixeli = 510
    
    # scala
    scall = 1

    # edit trybe
    edit_trybe = False
    edited_roi = None
    move_to_point = False
    
    #skale umozliwiajace wyswietlanei ROI na przeskalowanej mapie
    skaly = 1
    skalx = 1
    
    # maxymalna pozycja manipulatora w mm
    manipulator_max = 50
    
    # skala mapy
    skala = 4
        
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

        self.setMouseTracking(True)
        # Domyślnie ustawione na False - gdy False
        # mouseMoveEvent wywoływany jest tylko gdy któryś z przycisków myszki jest wciśnięty

        # Tworzy białe tło
        self.setAutoFillBackground(True)
        
####################################wgrywanie obrazu##################################


    def loadImage(self, drow_deskription = False, drow_single_rectagle = False):#przestac to wyoływac co update
        '''
        metoda przekazujaca wskaznik do obrazu i opisy do metody setPhoto
        :param drow_deskription: warotsc logiczna okreslajaca czy wypisywac opisy czy nie
        :param drow_single_rectagle: wartosc logiczna okreslajaca czy wywietlic 1 czy wsystkie ROIe
        '''

        #kopiowanei wskaznika
        self.c_image = self.image_opencv

        #wywołanie metody
        self.setPhoto(self.c_image, drow_deskription, drow_single_rectagle)
    

    def setPhoto(self, image, drow_deskription, drow_single_rectagle):
        '''
        Metoda dodajoca opisy do podglondu oraz wgrywajaca podglond do labela
        '''

        # scalowanie obrazu
        frame = cv2.resize(image, self.rozmiar)

        #scalowanie kopi obrazu
        self.frame = cv2.resize(image, self.rozmiar)

        #dodanie opisów w odpowiednich miescach
        if drow_deskription:
            for i, rectangle in enumerate(self.main_window.ROI):
                rx, ry = rectangle.gettextloc(self.ofsetx, self.ofsety, self.scall)
                cv2.putText(frame, str(rectangle.getName()), (rx, ry), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        #dodanie opisuw pojedyczego Roia jesli ta obcja została wybrana
        if drow_single_rectagle:
            rx, ry = self.main_window.ROI[self.ktury].gettextloc(self.ofsetx, self.ofsety, self.scall)
            cv2.putText(frame, str(self.main_window.ROI[self.ktury].getName()), (rx, ry), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # conwersja z open Cv image na QImage
        self._imgfromframe = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)

        self._pixmapdromframe = QPixmap.fromImage(self._imgfromframe)
        
        # wgranie obrazu
        self.setPixmap(self._pixmapdromframe)
        #zablokwnie rozmiaru
        self.setMaximumSize(self._pixmapdromframe.width(), self._pixmapdromframe.height())

###############################mous tracking##########################################

    def mousePressEvent(self, e):
        '''
        Metoda nadpisajaca wbudowany event pyqt wykonywany w mommecie przycisniencia przycisku myszki
        :param e: odczytana pozycja myszki
        '''

        # Sprawdzenie trybu pracy
        if self.edit_trybe:
            #tryb edycji ROI'u
            self.edited_roi.pres_cords(e, self.ofsetx, self.ofsety)
           
        elif self.move_to_point:
            self._move_to_point_function(e)

        else: #podstawowa obcja umozliwiajaca oznaczenie ROI'u
            self._save_first_pres(e)

    def _save_first_pres(self, e):
        '''
        Prywatna metoda zapisujaca pkt pierwszego klikniecia
        '''

        # zapis pozycji klikniecia
        self.x1 = e.x()
        self.y1 = e.y()

        # zapisanie pozycji pierwszego klikniecia jako obiekt klasy qpoint
        self.begin = e.pos()  # QPoint(self.x1,self.y1)#e.pos()

        #Zapisanie ze juz raz doszło do klikniecia
        self.iloscklikniec = True

        #podniesienie flagi ze nalezy narysowac podglond nowo zaznaczanego ROI'u
        self.whot_to_drow = 'previu_rectagle'

    def _move_to_point_function(self, e):
        '''
        Prywatna metoda konwerttujaca wspułrzedne w pixelach na mm i zadajaca manipulatorowi przemiecenie
        w celu wycetrowania na wybranym pktcie
        '''

        x1, y1 = e.x(), e.y() #zapisanie pozycji klikniecia

        #ccx - połowa rozmiaru x
        #ccy połowa rozmiaru y
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
        self.mapupdate()

    def mouseReleaseEvent(self, e):
        '''
        Metoda przeciozajaca Pqt5 event umozliwiajaca obsluzednie momentu pusczenia przycisku myszki
        :param e: pozycja myszki
        '''

        #wybranie odpowieniego trybu
        if self.edit_trybe:
            #przekazanie pozycji w celu edycji
            self.edited_roi.relise_cords(e, self.ofsetx, self.ofsety)
        
        elif self.move_to_point:
            #ignorowanie eventu w ramach przesuwania manipiulatora
            pass
        
        else:
            #zapisanie pozycji puszczenia przycisku
            self._save_relise_pres(e)

    def _save_relise_pres(self,e):
        '''
        Zapisanei miejsca puszcenia przycisku myszki
        '''

        # zapisanie wspułrzedne klikniecia
        self.x2 = e.x()
        self.y2 = e.y()

        # zapisanie pozycji klikniecia jako obiekt klasy qpoint
        self.end = e.pos()  # QPoint(self.x2,self.y2)

        # dopisanie nowego prostokata do listy
        tym = self.rectaglecreate()

        self.main_window.ROI.append(tym)

        # implementacja iteratora wyswietlanego prostokata
        self.ktury += 1

        #wyczsczenie licznika klikniec
        self.iloscklikniec = False

        #podniesienie flagi w celu wyrysowania wsystkich ROI
        self.whot_to_drow = 'all_rectagls'

        self.update()

    def mouseMoveEvent(self, e):
        '''
        Metoda przeciozajaca Pqt5 event umozliwiajaca obsluzednie momentu przesuniecia myszki
        :param e: pozycja myszki
        '''

        if self.edit_trybe:
            # tryb edycji ROI'u
            self.edited_roi.move_cords(e, self.ofsetx, self.ofsety)
            
        elif self.move_to_point:
            # ignorowanie eventu w ramach przesuwania manipiulatora
            pass

        elif self.iloscklikniec:
            # paramtery umozliwiajace rysowanei podglondu tworzonego ROI
            self._creat_roi_sample(e)

    def _creat_roi_sample(self,e):

        self.x2 = int(e.x() / self.skalx)
        self.y2 = int(e.y() / self.skaly)

        # konwersja pozycji myszki na stringi
        textx = f'{self.x2}'
        texty = f'{self.y2}'

        # zapis aktualnej pozycji myszki w celu wyswietlenia podglondu
        self.end = e.pos()  # QPoint(self.x2,self.y2)

        #podniesienie odpoiwiedniej flagi
        self.whot_to_drow = 'previu_rectagle'

        self.update()


###############################ROI edit##########################################

    def mapupdate(self):
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
        self.edit_trybe = True
        move_to_point = False

        #zapisanie wskaznika do edytowanego ROI'u
        self.edited_roi = roi
    
    def end_edit(self):
        '''
        Metoda konconca edycje ROi
        :return:
        '''
        #opusczenie odpowieniej flagi
        self.edit_trybe = False
        #usuniecie wskaznika do ROI
        self.edited_roi = None
        #zwrucenie aktualnego podglondu w celu aktualizacji
        return self.frame


#############################create rectagle###############################################

    def rectagledrow(self,prostokat):
        '''
        Metoda zwracajaca Qrectagle w celu wyrysowani go na podglodzie
        :param prostokat: obiekt klasy ROI
        :return: obiekt klasy Qrectagle
        '''
        x = self.get_rectagle(prostokat)
        return x

    def get_rectagle(self,prostokat):
        return prostokat.getrectangle(self.rozmiar, self.ofsetx, self.ofsety, self.skalx, self.skaly)
        
    def rectaglecreate(self):
        '''
        Metoda tworzoca obiekt klasy ROI
        :return: obiekt klasy roi stworzony na podstawie zapisanych dancyh
        '''
        #ponisienie nr defaltowej nazwy
        self.main_window.last_name += 1
        
        ROI = oC.obszarzaznaczony(
                                self,
                                self.x1, self.y1,
                                self.x2, self.y2,
                                self.frame,
                                self.ofsetx,
                                self.ofsety,
                                self.scall,
                                self.main_window.last_name,
                                self.skalx,self.skaly
                                )
        #zapisanei ROI dao tablicy
        self.main_window.add_ROI(ROI)
        return ROI
    
    def rmv_rectagle(self, roi):
        '''
        Metoda usywajhaca ROI
        :param roi: Roi do usuniecia
        :return:
        '''

        #jesli ROI jest w tablicy to go usuwamy
        if roi in self.main_window.ROI:
            self.main_window.ROI.remove(roi)

        #wywolanei metody sprotajacej po ROI w mainwidow
        self.main_window.remove_some_ROI(roi)

        #podniesienie odpoiwedniej flagi
        self.whot_to_drow = 'all_rectagls'
        
        self.update()

#############################Paint Event###############################################

    def paintEvent(self, event):
        '''
        Metoda przeciozajaca PyQt5 event obslugujaca wyswietlanie ROI i podglondu
        '''
        
        # inicializacja paintera
        qp = QPainter(self)
        
        try:
            # rysowanie obrazu
            qp.drawPixmap(self.rect(), self._pixmapdromframe)
        except AttributeError:
            pass
            
        finally:
            # kolro i tlo
            br = QBrush(QColor(200, 10, 10, 200))
            
            # wgranie stylu
            qp.setBrush(br)

            # variable for chusing if we drow numbers and rectagled
            tym = True
            num = False


            if self.whot_to_drow == 'all_rectagls':
                # pokazuje wsystkie prostkoaty
                self.all_Rectagles(qp)

            else:
                # podstawowa obcja rysuje nowy prostokat
                self.all_Rectagles(qp)
                qp.drawRect(QRect(self.begin, self.end))
                # rysowanie prostokonta na bierzoco jak podglond do ruchu myszka

            #odswiezenie podglondu
            self.loadImage(tym, num)
            

    def all_Rectagles(self, Painter):
        '''
        Metoda rysujaca wsystkie ROI'e
        :param Painter: Qt Painter
        '''
        for rectangle in self.main_window.ROI:
            Painter.drawRect(self.rectagledrow(rectangle))
       

