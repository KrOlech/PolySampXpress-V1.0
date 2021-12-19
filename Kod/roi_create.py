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

    dxp, dyp = False, False

    def __init__(self, main_window, *args, **kwargs):
        super(ROI_maping, self).__init__(*args, **kwargs)
        
        self.main_window = main_window
        
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

    #wagranie obrazu
    def loadImage(self, drow_deskription = False, drow_single_rectagle = False):#przestac to wyoływac co update
        
        self.c_image = self.image_opencv

        # wgranie obrazu do labela
        self.setPhoto(self.c_image, drow_deskription, drow_single_rectagle)
    
    # wstawienie obrazu do labela
    def setPhoto(self, image, drow_deskription, drow_single_rectagle):

        # scalowanie obrazu
        frame = cv2.resize(image, self.rozmiar)

        self.frame = cv2.resize(image, self.rozmiar)

        if drow_deskription:
            for i, rectangle in enumerate(self.main_window.rectangles):
                rx, ry = rectangle.gettextloc(self.ofsetx, self.ofsety, self.scall)
                cv2.putText(frame, str(rectangle.getName()), (rx, ry), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if drow_single_rectagle:
            rx, ry = self.main_window.rectangles[self.ktury].gettextloc(self.ofsetx, self.ofsety, self.scall)
            cv2.putText(frame, str(self.main_window.rectangles[self.ktury].getName()), (rx, ry), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # conwersja z open Cv image na QImage
        self._imgfromframe = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)

        self._pixmapdromframe = QPixmap.fromImage(self._imgfromframe)
        
        # wgranie obrazu
        self.setPixmap(self._pixmapdromframe)
        self.setMaximumSize(self._pixmapdromframe.width(), self._pixmapdromframe.height())

###############################mous tracking##########################################

    # działąnia podczas klikniecia myszki
    def mousePressEvent(self, e):
        if self.edit_trybe:
            self.edited_roi.pres_cords(e, self.ofsetx,self.ofsety)
           
        elif self.move_to_point:
            x1 = int(e.x()/self.skalx)
            y1 = int(e.y()/self.skaly)
            ccx, ccy = self.rozmiar[0] / 2, self.rozmiar[1] / 2
            self.dxp, self.dyp = int(y1-ccy), int(x1-ccx)
            dx, dy = (x1-ccx)/self.delta_pixeli, (y1-ccy)/self.delta_pixeli
            self.main_window.manipulaor.move_axes_to_abs_woe_ofset('yz', [dx, dy])
            self.ofsetx += self.dxp
            self.ofsety += self.dyp
            self.mapupdate()

        else:
            # zapis pozycji klikniecia
            self.x1 = int(e.x()/self.skalx)
            self.y1 = int(e.y()/self.skaly)

            # zapisanie pozycji pierwszego klikniecia jako obiekt klasy qpoint
            self.begin = e.pos()# QPoint(self.x1,self.y1)#e.pos()

            self.iloscklikniec = True

            self.whot_to_drow = 'previu_rectagle'

    def mouseReleaseEvent(self, e):
        if self.edit_trybe:
            self.edited_roi.relise_cords(e, self.ofsetx, self.ofsety)
        
        elif self.move_to_point:
            pass
        
        else:    
            # zapisanie wspułrzedne klikniecia
            self.x2 = int(e.x()/self.skalx)
            self.y2 = int(e.y()/self.skaly)

            # zapisanie pozycji klikniecia jako obiekt klasy qpoint
            self.end = e.pos()# QPoint(self.x2,self.y2)

            # dopisanie nowego prostokata do listy
            tym = self.rectaglecreate()

            self.main_window.rectangles.append(tym)

            # implementacja iteratora wyswietlanego prostokata
            self.ktury += 1

            self.iloscklikniec = False
            self.whot_to_drow = 'all_rectagls'

            self.update()

    def mouseMoveEvent(self, e):
    
        if self.edit_trybe:
            self.edited_roi.move_cords(e, self.ofsetx, self.ofsety)
            
        elif self.move_to_point:
            pass
            
        elif self.iloscklikniec:

            self.x2 = int(e.x()/self.skalx)
            self.y2 = int(e.y()/self.skaly)

            # konwersja pozycji myszki na stringi
            textx = f'{self.x2}'
            texty = f'{self.y2}'

            # zapis aktualnej pozycji myszki w celu wyswietlenia podglondu
            self.end = e.pos()# QPoint(self.x2,self.y2)

            self.whot_to_drow = 'previu_rectagle'

            self.update()

###############################ROI edit##########################################

    def mapupdate(self):
        pass

    def edit_roi(self, roi):
        
        self.edit_trybe = True
        move_to_point = False
        self.edited_roi = roi
    
    def end_edit(self):
        self.edit_trybe = False
        self.edited_roi = None


#############################create rectagle###############################################

    def rectagledrow(self,prostokat):
        x = prostokat.getrectangle(self.rozmiar, self.ofsetx, self.ofsety, self.skalx, self.skaly)
        return x

    def rectaglecreate(self):
        
        self.main_window.last_name += 1
        
        ROI = oC.obszarzaznaczony(
                                self,
                                self.x1, self.y1,
                                self.x2, self.y2,
                                self.frame,
                                self.ofsetx,
                                self.ofsety,
                                self.scall,
                                self.main_window.last_name
                                )
        self.main_window.add_ROI(ROI)
        return ROI
    
    def rmv_rectagle(self, ROI):
        
        if ROI in  self.main_window.rectangles:
            self.main_window.rectangles.remove(ROI)
        
        self.main_window.remove_some_ROI(ROI)
            
        self.whot_to_drow = 'all_rectagls'
        
        self.update()

#############################Paint Event###############################################

    def paintEvent(self, event):
        
        # inicializacja paintera
        qp = QPainter(self)
        
        try:
            # rysowanie obrazu
            qp.drawPixmap(self.rect(), self._pixmapdromframe)
        except AttributeError:
            pass
            
        finally:
            # kolro i tlo
            br = QBrush(QColor(200, 20, 20, 255),Qt.CrossPattern)
            
            # wgranie stylu
            qp.setBrush(br)

            # variable for chusing if we drow numbers and rectagled
            tym = True
            num = False
            
            if self.whot_to_drow == 'all_rectagls': #pokazuje wsystkie prostkoaty
                self.all_Rectagles(qp)

            else: # podstawowa obcja rysuje nowy prostokat
                self.all_Rectagles(qp)
                qp.drawRect(QRect(self.begin, self.end))# rysowanie prostokonta na bierzoco jak podglond do ruchu myszka

            self.loadImage(tym, num)
            

    def all_Rectagles(self, Painter):
        for rectangle in self.main_window.rectangles: # wyrysowanie poprzednich prostokotów
            Painter.drawRect(self.rectagledrow(rectangle))
       

