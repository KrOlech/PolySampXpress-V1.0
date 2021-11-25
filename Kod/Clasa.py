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
    
    first_pres = False
    
    kanta_top = False
    kanta_botom = False
    kanta_left = False
    kanta_right = False
    
    left_top = False
    right_top = False
    left_botom = False
    right_bootom = False
    
    move_all = False

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
        self.end_edit()
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

        frame = image

        img = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0],QImage.Format_RGB888)  

        self.image = QPixmap.fromImage(img)

        self.podglond = kw.podglond_roi(str(self.getName()),self.get_image(),self)

    def get_image(self):
        return self.image
    
    def get_podglond(self):
        return self.podglond

    def move_top_line(self):
        pass

    def move_dwn_line(self):
        pass

    def move_lft_line(self):
        pass

    def move_rig_line(self):
        pass

    def move_top(self):
        pass

    def move_dwn(self):
        pass

    def move_lft(self):
        pass

    def move_rig(self):
        pass
        
    def edit(self):
        self.Obraz_obcet.edit_roi(self)
        
    def end_edit(self):
        self.Obraz_obcet.end_edit()
        
        
        
###############################self edit##########################################

    def pres_cords(self,e,ofsetx, ofsety):
    
        self.first_pres = True
    
        self.kanta_top = False
        self.kanta_botom = False
        self.kanta_left = False
        self.kanta_right = False
        
        self.move_all = False
        
        wopszaru = 10
    
        self.px0 , self.py0 = e.x() + ofsetx, e.y()+ofsety 
        
        if self.x0-wopszaru<self.px0<self.x0+wopszaru and self.y0-wopszaru<self.py0<self.y1+wopszaru:
            self.kanta_right = True
        
        if self.x1-wopszaru<self.px0<self.x1+wopszaru and self.y0-wopszaru<self.py0<self.y1+wopszaru:
            self.kanta_left = True
            
        if self.y0-wopszaru<self.py0<self.y0+wopszaru and self.x0-wopszaru<self.px0<self.x1+wopszaru:
            self.kanta_top = True
            
        if self.y1-wopszaru<self.py0<self.y1+wopszaru and self.x0-wopszaru<self.px0<self.x1+wopszaru:
            self.kanta_botom = True
        
            
        self.left_top = self.kanta_left and self.kanta_top
        self.right_top = self.kanta_right and self.kanta_top
        
        self.left_botom = self.kanta_left and self.kanta_botom
        self.right_bootom = self.kanta_right and self.kanta_botom
        
        if self.y0-wopszaru<self.py0<self.y1+wopszaru and self.x0-wopszaru<self.px0<self.x1+wopszaru:
            self.move_all = True
        
        #print(self.px0 , self.py0, self.x0,self.x1, self.y0, self.y1)
        #print(self.x1-wopszaru<self.px0<self.x1+wopszaru and self.y0-wopszaru<self.py0<self.y1+wopszaru)

    def relise_cords(self,e,ofsetx, ofsety):
    
        self.first_pres  = False
    
        self.px1 , self.py1 = e.x() + ofsetx, e.y()+ofsety 
        
        if self.move_all:
            dx, dy = self.px1 - self.px0, self.py1 - self.py0
            self.x0 += dx
            self.x1 += dx
            self.y0 += dy
            self.y1 += dy
        
        elif self.left_top:
            self.x1 = self.px1
            self.y0 = self.py1
            
        elif self.left_botom:
            self.x1 = self.px1
            self.y1 = self.py1
            
        elif self.right_bootom:
            self.x0 = self.px1
            self.y1 = self.py1
            
        elif self.right_top:
            self.x0 = self.px1
            self.y0 = self.py1
            
        elif self.kanta_botom:
            self.y1 = self.py1
        elif self.kanta_left:
            self.x1 = self.px1
        elif self.kanta_right:
            self.x0 = self.px1
        elif self.kanta_top:
            self.y0 = self.py1

            
            

    def move_cords(self,e,ofsetx, ofsety):
        if self.first_pres:
            
            self.px1 , self.py1 = e.x() + ofsetx, e.y()+ofsety 
            
            
            if self.move_all:
                dx, dy = self.px1 - self.px0, self.py1 - self.py0
                self.x0 += dx
                self.x1 += dx
                self.y0 += dy
                self.y1 += dy
                self.px0 , self.py0 = e.x() + ofsetx, e.y()+ofsety
        
            elif self.left_top:
                #print("left_top")
                self.x1 = self.px1
                self.y0 = self.py1
                
            elif self.left_botom:
                #print("left_botom")
                self.x1 = self.px1
                self.y1 = self.py1
                
            elif self.right_bootom:
                #print("right_bootom")
                self.x0 = self.px1
                self.y1 = self.py1
                
            elif self.right_top:
                #print("right_top")
                self.x0 = self.px1
                self.y0 = self.py1
                
            elif self.kanta_botom:
                #print("kanta_botom")
                self.y1 = self.py1
            elif self.kanta_left:
                #print("kanta_left")
                self.x1 = self.px1
            elif self.kanta_right:
                #print("kanta_right")
                self.x0 = self.px1
            elif self.kanta_top:
                #print("kanta_TOP")
                self.y0 = self.py1
