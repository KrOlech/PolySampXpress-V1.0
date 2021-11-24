# obraz Klasa dziedzicaca z Qlablel
import cv2
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import kwadrat_label as kw


class obszarzaznaczony():
    # stałe do konwersji z układu pixeli na układ prubki
    a = 2
    b = 0

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

    # skala
    s00 = 1

    # konstruktor tworzocy obiekt ze wzglednych wspułrednych prubki w pixelach
    def __init__(self, Obraz_obcet ,xp0, yp0, xp1, yp1, image, py00=0, px00=0, s00=1, Name="defalaut"):
        
        self.wzglednyRectagle = (xp0, yp0, xp1, yp1)
        
        self.Obraz_obcet = Obraz_obcet
        
        self.Name = Name

        self.set_niezalezne_pixele(xp0, yp0, xp1, yp1, px00, py00, s00)

        self.create_Roi_label(image, py00, px00, s00)

        self.set_niezalezne_Prubki()

    def get_wzgledny_rectagle(self):
        return self.wzglednyRectagle

    def kill(self):
        self.Obraz_obcet.rmv_rectagle(self)  # trece
        del self.podglond

    # metoda konwetujaca wspułrzedne bezwgledne w pixelach na wspułredne prubkki
    def set_niezalezne_Prubki(self):
        return
        # worki in progres

    # metoda konwertujaca wzgledne wspułredne w pixelach na bezwgledne
    def set_niezalezne_pixele(self, xp0, yp0, xp1, yp1, px00, py00, s00):

        self.x0 = (xp0 + px00)*s00
        self.y0 = (yp0 + py00)*s00

        self.x1 = (xp1 + px00)*s00
        self.y1 = (yp1 + py00)*s00

    # metoda zwracajaca prostokoat qrect w układzei waktualnie wyswietlanym
    def getrectangle(self, Rozmiar, py00, px00, s00=1):

        xp0 = (self.x0 - px00) * s00
        yp0 = (self.y0 - py00) * s00
        xp1 = (self.x1 - px00) * s00
        yp1 = (self.y1 - py00) * s00

        if xp0 < 0:
            xp0 = 0

        if yp0 < 0:
            yp0 = 0

        if xp1 > Rozmiar[0]:
            xp1 = Rozmiar[0]

        if yp1 > Rozmiar[1]:
            yp1 = Rozmiar[1]

        poczatek = QPoint(xp0, yp0)
        koniec = QPoint(xp1, yp1)

        return QRect(poczatek, koniec)

    def setName(self, name):
        self.Name = name

    def getName(self):
        return self.Name

    def gettop_corner(self, ox, oy, s00):

        if self.x0 < self.x1 and self.y0 < self.y1:
            xp0 = (self.x0 - oy) * s00
            yp0 = (self.y0 - ox) * s00
        elif self.x0 < self.x1 and self.y0 > self.y1:
            xp0 = (self.x0 - oy) * s00
            yp0 = (self.y1 - ox) * s00
        elif self.x0 > self.x1 and self.y0 < self.y1:
            xp0 = (self.x1 - oy) * s00
            yp0 = (self.y0 - ox) * s00
        else:
            xp0 = (self.x1 - oy) * s00
            yp0 = (self.y1 - ox) * s00

        return xp0, yp0

    def gettextloc(self, ox, oy, s00=1):

        xp0, yp0 = self.gettop_corner(ox, oy, s00)

        return xp0 - 20, yp0 - 10

    def create_Roi_label(self, image, py00, px00, s00):

        xpo, ypo = self.gettop_corner(py00, px00, s00)

        self.xpl = xpo
        self.ypl = ypo

        dx = abs(self.x0 - self.x1)
        dy = abs(self.y0 - self.y1)

        self.dxl = dx
        self.dyl = dy
        
        frame = image

        img = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0],QImage.Format_RGB888)  

        self.image = QPixmap.fromImage(img)

        self.podglond = kw.podglond_roi(str(self.getName()),self.get_image(),self)

    def get_image(self):
        return self.image, self.xpl, self.ypl, self.dxl, self.dyl
    
    def get_podglond(self):
        return self.podglond
