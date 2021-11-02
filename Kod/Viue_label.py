import numpy as np
from PyQt5.QtWidgets import * #QFileDialog ,QMainWindow,QToolBar ,QAction
import cv2
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *  # QFileDialog ,QMainWindow,QToolBar ,QAction
from Map import shape, squer

import Clasa as oC


class Obraz(QLabel):
    # Klaza Obraz dziedziczy z QLabel, pozwala na lepszą obsługę eventu mouseMoveEvent

    # obiekt Klasy MainWindow podany jako argument przy tworzeniu obiektu klasy Obraz - pozwala na komunikację z oknem głównym
    main_window = ' '

    #aktualna pozycja myszki nad widgetem
    x = 0
    y = 0
        
    #ostatnie 2 pozycje klikniec pozycja myszki nad widgetem
    x1 = 0
    y1 = 0

    x2 = 0
    y2 = 0
        
    #pukty poczotkowe i koncowe prostokonta
    begin = QPoint()
    end = QPoint()
        
    #prostokonty zaznaczone
    rectangles = []

    last_name  = 0        
       
    iloscklikniec = False
       
    #zmienne pozwalajace obejsc brak układu swichcaes
    # 'no_rectagle' 'all_rectagls' 'One_rectagle' 'viue_muve' 'previu_rectagle'
    whot_to_drow = 'all_rectagls'

    # '' 'up' 'dawn' 'right' 'left'
    direction_change = ''
        
    #iterator do wyswietlenia poprzedniego nastempego zaznaczenia
    ktury = 0

    #wartosci owsetu aktualnego podgloadu
    ofsetx = 0
    ofsety = 0

    ofsetymax = 0
    ofsetxmax = 0

    #scala
    scall = 1

    # rozmiar obszaru
    Rozmiar = (960, 540)

    #construvtor
    def __init__(self, main_window, *args, **kwargs):
        super(Obraz, self).__init__(*args, **kwargs)

        self.main_window = main_window
        
        #Tworzy białe tło
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('white'))
        self.setPalette(palette)

        #wyłacza skalowanie okna
        self.setScaledContents(False)

        self.setMouseTracking(True)  
        # Domyślnie ustawione na False - gdy False mouseMoveEvent wywoływany jest tylko gdy któryś z przycisków myszki jest wciśnięty

        # wgrywanie obrazu z pliku
        self.image = cv2.imread("5.jpg")# cv2.imread(path, flag)
        print(type(self.image[0][0][0]))
        #wczytanie podgladu z kamery
        self.loadImage()

        self.Save_curent_viue()
               
###############################mous tracking##########################################
   
    def mousePressEvent(self, e):#działąnia podczas klikniecia myszki

        #zapis pozycji klikniecia
        self.x1 = e.x()
        self.y1 = e.y()

        #zapisanie pozycji pierwszego klikniecia jako obiekt klasy qpoint
        self.begin = e.pos()

        self.iloscklikniec = True

        self.whot_to_drow = 'previu_rectagle'

    def mouseReleaseEvent(self, e):

        # zapisanie wspułrzedne klikniecia
        self.x2 = e.x()
        self.y2 = e.y()

        # zapisanie pozycji klikniecia jako obiekt klasy qpoint
        self.end = e.pos()

        # dopisanie nowego prostokata do listy
        tym = self.rectaglecreate()

        self.rectangles.append(tym)

        # implementacja iteratora wyswietlanego prostokata
        self.ktury += 1

        self.iloscklikniec = False
        self.whot_to_drow = 'all_rectagls'

        self.update()

    def mouseMoveEvent(self, e):
        if self.iloscklikniec:

            self.x2 = e.x()
            self.y2 = e.y()

            # konwersja pozycji myszki na stringi
            textx = f'{self.x2}'
            texty = f'{self.y2}'

            # zapis aktualnej pozycji myszki w celu wyswietlenia podglondu
            self.end = e.pos()

            self.whot_to_drow = 'previu_rectagle'

            self.update()

####################################wgrywanie obrazu##################################

    #wagranie obrazu z pliku    
    def loadImage(self,drow_deskription = False,drow_single_rectagle = False):#przestac to wyoływac co update

        #wybranie interesujacego nas fragmetu obrazu
        xHigh = int(self.Rozmiar[1]/2) + int(self.ofsetx/2)
        yHigh = int(self.Rozmiar[0]/2) + int(self.ofsety/2)
        self.C_image = self.image[int(self.ofsetx/2): xHigh, int(self.ofsety/2): yHigh]

        #wgranie obrazu do labela
        self.setPhoto(self.C_image,drow_deskription,drow_single_rectagle)
    
    #wstawienie obrazu do labela       
    def setPhoto(self, image, drow_deskription, drow_single_rectagle):

        #scalowanie obrazu
        frame = cv2.resize(image, self.Rozmiar)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.frame = cv2.resize(image,self.Rozmiar)
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)


        if drow_deskription:
            for i,rectangle in enumerate(self.rectangles):
                rX,rY = rectangle.gettextloc(self.ofsetx,self.ofsety,self.scall)
                cv2.putText(frame,str(rectangle.getName()),(rX,rY),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)


        if drow_single_rectagle:
            rX,rY = self.rectangles[self.ktury].gettextloc(self.ofsetx,self.ofsety,self.scall)
            cv2.putText(frame,str(self.rectangles[self.ktury].getName()),(rX,rY),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        
        #conwersja z open Cv image na Qimage
        self._img = QImage(frame, frame.shape[1],frame.shape[0],frame.strides[0],QImage.Format_RGB888)
        #QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self._img = QPixmap.fromImage(self._img)
        
        #wgranie obrazu
        self.setPixmap(self._img)
        self.setMaximumSize(self._img.width(),self._img.height())
        
#############################Paint Event###############################################

    def paintEvent(self, event):
        
        #inicializacja pintera
        qp = QPainter(self)

        #rysowanie obrazu
        qp.drawPixmap(self.rect(), self._img)

        #kolro i tlo
        br = QBrush(QColor(200, 10, 10, 200))
        
        #wgranie stylu 
        qp.setBrush(br)
        
        tym = True
        num = False
        
        if self.whot_to_drow == 'all_rectagls': #pokazuje wsystkie prostkoaty
            self.all_Rectagles(qp)
            

        elif self.whot_to_drow == 'no_rectagle': #howa wszystkie prostokaty
            tym = False
    
        elif self.whot_to_drow =='One_rectagle': #rysuje wybrany prostokat
            self.chosen_rectagle(qp)
            tym = False
            num = True
            
        elif self.whot_to_drow == 'viue_muve':

            self.all_Rectagles(qp)
            self.move_viue()
            self.extend_map()



   
        else: #podstawowa obcja rysuje nowy prostokat
            self.all_Rectagles(qp)
            qp.drawRect(QRect(self.begin, self.end))#rysowanie prostokonta na bierzoco jak podglond do ruchu myszka

        self.loadImage(tym, num)
        return

    def extend_map(self):
        if self.direction_change == 'dawn':
            self.exrend_map_up()
        elif self.direction_change == 'up':
            self.extend_map_dwn()
        elif self.direction_change == 'right':
            self.extend_map_right()
        elif self.direction_change == 'left':
            self.extend_map_left()
        else:
            pass
        self.direction_change = ''


    def all_Rectagles(self, Painter):
          
        for rectangle in self.rectangles: # wyrysowanie poprzednich prostokotów
            Painter.drawRect(self.rectagledrow(rectangle))
    
    def chosen_rectagle(self, Painter):
        Painter.drawRect(self.rectagledrow(self.rectangles[self.ktury]))
      
    def move_viue(self):        
        self.loadImage()
            

#############################create rectagle###############################################

    def rectagledrow(self,prostokat):
        x = prostokat.getrectangle(self.Rozmiar,self.ofsetx,self.ofsety)
        #print(x)
        return x

    def rectaglecreate(self):
        
        self.last_name += 1
        
        ROI =  oC.obszarzaznaczony(
                                self,
                                self.x1, self.y1,
                                self.x2, self.y2,
                                self.frame,
                                self.ofsetx,
                                self.ofsety,
                                self.scall,
                                self.last_name
                                )
        self.main_window.add_ROI(ROI)
        return ROI
    
    def rmv_rectagle(self,ROI):
        
        #print(self.rectangles,ROI)
        if ROI in  self.rectangles:
            self.rectangles.remove(ROI)
        
        self.main_window.remove_some_ROI(ROI)
            
        self.whot_to_drow = 'all_rectagls'
        
        self.update()

####################################fukcje wywoływane przez guziki z gluwnego okna####################################


    def Narysujcaloscs(self): #rysowanie wsystkich prostokontów po nacisnieciu odpowiedniego przyciusku

        self.whot_to_drow = 'all_rectagls'
        self.iloscklikniec = True
        self.update()
    
    def schowajcalosc(self): #schowanie wsystkich prostokontów

        self.whot_to_drow = 'no_rectagle'
        self.iloscklikniec = True
        self.update()
            
    def Next(self):#narysowanie nastempnego prostokata
    
        self.whot_to_drow = 'One_rectagle'
        self.iloscklikniec = True
        
        if self.ktury < len(self.rectangles)-1:
            self.ktury += 1
        else:
            self.ktury = 0
            
        self.update()
       
    def last(self):#narysowanie poprzedniego prostokonta
    
        self.whot_to_drow = 'One_rectagle'
        self.iloscklikniec = True
        
        if self.ktury == 0 :
            self.ktury = len(self.rectangles)-1
        else:
            self.ktury -= 1
        
        self.update()

###########################przesuwanie podgladu##############################    

    def left(self):

        if self.ofsety >= 10:
            self.ofsety -= 10
            self.whot_to_drow = 'viue_muve'
            self.direction_change = 'left'
            self.update()
    
    def right(self):

        if self.ofsety < self.Rozmiar[0]-10:
            self.ofsety += 10
            self.whot_to_drow = 'viue_muve'
            self.direction_change = 'right'
            self.update()

    def dawn(self):

        if self.ofsetx >= 10:
            self.ofsetx -= 10
            self.whot_to_drow = 'viue_muve'
            self.direction_change = 'dawn'
            self.update()

    def up(self):

        if self.ofsetx < self.Rozmiar[1]-10:
            self.ofsetx += 10
            self.whot_to_drow = 'viue_muve'
            self.direction_change = 'up'
            self.update()

###########################map extetion##############################

    #save first viue to the map
    def Save_curent_viue(self):

        self.map = self.frame

        self.map_shape = shape()
        temp = squer(0, 0, 540, 960)
        self.map_shape.add_squer(temp)

    #not finieshed
    def reset_map(self):
        pass

    #technicli ok
    def extend_map_right(self):

        dx = 10

        s = self._img.size() #wymiary podglondu
        x = s.height()
        y = s.width()

        xm, ym, zm = self.map.shape #wymiary aktualnej mapy

        #new = squer(x - xm + self.ofsetx, ym, xm + self.ofsetx, ym+10)
        #self.map_shape.add_squer(new)
        #tablica do któej wkopiujemy poszerzona mape
        tab = np.ones((xm, ym+dx, zm), dtype=np.uint8)

        #wkopiowanie nowego odkrytewgo fragmentu
        #print(np.shape(self.frame), np.shape(self.frame))
        #print(self.ofsetx, xm+self.ofsetx, ym, ym+dx)

        if self.ofsety+dx > self.ofsetymax:
            tab = np.ones((xm, ym + dx, zm), dtype=np.uint8)
            self.ofsetymax = self.ofsety
        else:
            tab = np.ones((xm, ym, zm), dtype=np.uint8)
        try:
            tab[self.ofsetx: x + self.ofsetx, ym:ym+dx] = self.frame[:, y - dx:]
        except ValueError:
            pass

        #tab[self.ofsetx: x+self.ofsetx, ym+self.ofsety-dx:ym+self.ofsety] = self.frame[:, y-dx:]

        #ym + self.ofsety: ym + dx + self.ofsety
        #Wkopoiowanie istniejocej mapy
        tab[0:xm, 0:ym] = self.map

        self.map = tab

    #technicli ok
    def extend_map_dwn(self):

        dx = 10

        s = self._img.size() #wymiary podglondu
        x = s.height()
        y = s.width()

        xm, ym, zm = self.map.shape #wymiary aktualnej mapy

        #tablica do któej wkopiujemy poszerzona mape
        tab = np.ones((xm+dx, ym, zm), dtype=np.uint8)

        #Wkopoiowanie istniejocej mapy
        tab[0:xm, 0:ym] = self.map
        
        #wkopiowanie nowego odkrytewgo fragmentu
        tab[xm:xm+dx, self.ofsety: y+self.ofsety] = self.frame[x-dx:, :]

        self.map = tab

    # technicli ok
    def extend_map_left(self):
        dx = 10

        s = self._img.size()  # wymiary podglondu
        x = s.height()
        y = s.width()

        xm, ym, zm = self.map.shape  # wymiary aktualnej mapy

        # new = squer(x - xm + self.ofsetx, ym, xm + self.ofsetx, ym+10)
        # self.map_shape.add_squer(new)
        # tablica do któej wkopiujemy poszerzona mape
        if self.ofsety < 0:
            tab = np.ones((xm, ym + dx, zm), dtype=np.uint8)
        else:
            tab = np.ones((xm, ym, zm), dtype=np.uint8)

        # Wkopoiowanie istniejocej mapy
        tab[0:xm, 0:ym + dx] = self.map

        # wkopiowanie nowego odkrytewgo fragmentu
        # print(np.shape(self.frame), np.shape(self.frame))
        # print(self.ofsetx, xm+self.ofsetx, ym, ym+dx)
        tab[self.ofsetx: x+self.ofsetx, self.ofsety:dx+self.ofsety] = self.frame[:, 0:dx]

        self.map = tab

    # technicli notok
    def exrend_map_up(self):

        dx = 10

        s = self._img.size()  # wymiary podglondu
        x = s.height()
        y = s.width()

        xm, ym, zm = self.map.shape  # wymiary aktualnej mapy

        if self.ofsetx + dx > self.ofsetxmax:
            tab = np.ones((xm + dx, ym, zm), dtype=np.uint8)
            self.ofsetxmax = self.ofsetx
        else:
            tab = np.ones((xm, ym, zm), dtype=np.uint8)

	    # Wkopoiowanie istniejocej mapy
        tab[0:xm, 0:ym] = self.map

        try:
            tab[self.ofsetx:self.ofsetx+dx, self.ofsety: y + self.ofsety] = self.frame[0:dx, :]
        except ValueError:
                pass
            
        self.map = tab


    def get_map(self):
        return self.map

