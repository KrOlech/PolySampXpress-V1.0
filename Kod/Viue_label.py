import numpy as np
from PyQt5.QtWidgets import * #QFileDialog ,QMainWindow,QToolBar ,QAction
import cv2
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *  # QFileDialog ,QMainWindow,QToolBar ,QAction
from Map import shape, squer
import numpy as np
import sys, toupcam
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QImage
import Clasa as oC
import matplotlib.pyplot as plt
from threading import Thread
from time import sleep

class Obraz(QLabel):
    # Klaza Obraz dziedziczy z QLabel, pozwala na lepszą obsługę eventu mouseMoveEvent

#signals for camera action
    eventImage = pyqtSignal()
    snap_image_event = pyqtSignal()	

    hcam = None
    buf = None      # video buffer
    w = 0           # video width
    h = 0           # video height

    x = 10
    y = 152
    total = 0

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

    last_name = 0
       
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

    #scala
    scall = 1

    # rozmiar obszaru
    Rozmiar = (1024,768)
    
    ofsetymax = Rozmiar[1]
    ofsetxmax = Rozmiar[0]

    ofsetymin = 0
    ofsetxmin = 0
    
    first = True

    delta_pixeli = 510
    
    frame = True
    
    waitontarget = False
    
    edit_trybe = False
    edited_roi = None

    #construvtor
    def __init__(self, main_window, *args, **kwargs):
        super(Obraz, self).__init__(*args, **kwargs)

        self.initUI() #inicializacja wymiarów obiektu pyqt
        
        self.initCamera() #inicializacja camery
        
        self.hcam.put_AutoExpoEnable(False)
        
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
               
###############################mous tracking##########################################
   
    def mousePressEvent(self, e):#działąnia podczas klikniecia myszki
        if self.edit_trybe:
            self.edited_roi.pres_cords(e, self.ofsetx,self.ofsety)
        
        else:
            #zapis pozycji klikniecia
            self.x1 = e.x()
            self.y1 = e.y()

            #zapisanie pozycji pierwszego klikniecia jako obiekt klasy qpoint
            self.begin = e.pos()

            self.iloscklikniec = True

            self.whot_to_drow = 'previu_rectagle'

    def mouseReleaseEvent(self, e):
        if self.edit_trybe:
            self.edited_roi.relise_cords(e,self.ofsetx,self.ofsety)
            
        else:    
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
        if self.edit_trybe:
            self.edited_roi.move_cords(e,self.ofsetx,self.ofsety)
            
        elif self.iloscklikniec:

            self.x2 = e.x()
            self.y2 = e.y()

            # konwersja pozycji myszki na stringi
            textx = f'{self.x2}'
            texty = f'{self.y2}'

            # zapis aktualnej pozycji myszki w celu wyswietlenia podglondu
            self.end = e.pos()

            self.whot_to_drow = 'previu_rectagle'

            self.update()

###############################camera read##########################################

    def snap_img(self):
        self.hcam.Snap(1)
    
    @pyqtSlot()
    def snap_image_event_signal(self):
        if self.hcam is not None:
            w, h = self.hcam.get_Size() 
            bufsize = ((w * 24 + 31) // 32 * 4) * h
            still_img_buf = bytes(bufsize)
            self.hcam.PullStillImageV2(still_img_buf, 24, None)
            #print('saving image')
        #    print(self.hcam.get_ExpoTime())
            #print(w, h)
            
            img = self.bytes_to_array(still_img_buf)
            
            self.Qimage_read_from_camera = QImage(still_img_buf,
                                      self.w, self.h,
                                      (self.w * 24 + 31) // 32 * 4,
                                      QImage.Format_RGB888)
                     
            self.image_opencv = self.convertQImageToMat(
                    self.Qimage_read_from_camera)
            
            if all(self.main_window.manipulaor.check_on_target().values()):
                self.newframe = True
            else:
                self.newframe = False
            
            self.loadImage()
            
            #plt.imsave('img_frame_{}.png'.format(self.total), img)

    @staticmethod
    def cameraCallback(nEvent, ctx):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            ctx.eventImage.emit()
        elif nEvent == toupcam.TOUPCAM_EVENT_STILLIMAGE:
            ctx.snap_image_event.emit()

    @staticmethod
    def  convertQImageToMat(incomingImage):
        '''  Converts a QImage into an opencv MAT format  '''
        incomingImage = incomingImage.convertToFormat(4)

        width = incomingImage.width()
        height = incomingImage.height()

        ptr = incomingImage.bits()
        ptr.setsize(incomingImage.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)  #  Copies the data
        return arr 

    @pyqtSlot()
    def eventImageSignal(self):

        if self.hcam is not None:

            try:
                self.hcam.PullImageV2(self.buf, 24, None)
                self.total += 1

            except toupcam.HRESULTException:
                print('pull image failed')
                QMessageBox.warning(self, '', 'pull image failed', QMessageBox.Ok)

            else:
                self.Qimage_read_from_camera = QImage(self.buf,
                                      self.w, self.h,
                                      (self.w * 24 + 31) // 32 * 4,
                                      QImage.Format_RGB888)
                
                self.image_opencv = self.convertQImageToMat(
                    self.Qimage_read_from_camera)
                
                try:
                    if self.first:
                        self.Save_curent_viue()
                except ValueError:
                    pass
                    
                if all(self.main_window.manipulaor.check_on_target().values()):
                    self.newframe = True
                else:
                    self.newframe = False
                    
                    
                self.loadImage()

    def bytes_to_array(self, still_img_buf, dtype=np.uint8):
        arr_1d = np.frombuffer(still_img_buf, dtype=dtype)
        return arr_1d.reshape(self.h, self.w, 3)

    def initCamera(self):

        a = toupcam.Toupcam.EnumV2()

        if len(a) <= 0:
            QMessageBox.warning(self, '',"erore during camera inicialisation", QMessageBox.Ok)

        else:
            self.camname = a[0].displayname

            #create and conect custom pyqt5 signa
            self.eventImage.connect(self.eventImageSignal)

            self.snap_image_event.connect(self.snap_image_event_signal)

            #trying opening camera
            try:
                self.hcam = toupcam.Toupcam.Open(a[0].id)

            except toupcam.HRESULTException:
                QMessageBox.warning(self, '', 'failed to open camera', QMessageBox.Ok)

            else:
                #creating bufer for image hold
                self.w, self.h = self.hcam.get_Size()
                bufsize = ((self.w * 24 + 31) // 32 * 4) * self.h
                self.buf = bytes(bufsize)

                try:
                    if sys.platform == 'win32':
                        self.hcam.put_Option(toupcam.TOUPCAM_OPTION_BYTEORDER, 0) # QImage.Format_RGB888

                    self.hcam.StartPullModeWithCallback(self.cameraCallback, self)
                except toupcam.HRESULTException:
                    QMessageBox.warning(self, '', 'failed to start camera', QMessageBox.Ok)		

######################################camera########################################	

    def initUI(self):

        self.setScaledContents(True)

        self.resize(self.geometry().width(), self.geometry().height())

####################################wgrywanie obrazu##################################
    #wagranie obrazu z pliku    
    def loadImage(self, drow_deskription = False, drow_single_rectagle = False):#przestac to wyoływac co update
        
        self.C_image = self.image_opencv

        #wgranie obrazu do labela
        self.setPhoto(self.C_image, drow_deskription, drow_single_rectagle)
    
    #wstawienie obrazu do labela       
    def setPhoto(self, image, drow_deskription, drow_single_rectagle):

        #scalowanie obrazu
        frame = cv2.resize(image, self.Rozmiar)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.frame = cv2.resize(image, self.Rozmiar)
        self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)


        if drow_deskription:
            for i,rectangle in enumerate(self.rectangles):
                rX,rY = rectangle.gettextloc(self.ofsetx,self.ofsety,self.scall)
                cv2.putText(frame, str(rectangle.getName()),(rX,rY),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)


        if drow_single_rectagle:
            rX,rY = self.rectangles[self.ktury].gettextloc(self.ofsetx,self.ofsety,self.scall)
            cv2.putText(frame, str(self.rectangles[self.ktury].getName()),(rX,rY),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        
        #conwersja z open Cv image na Qimage
        self._imgfromframe = QImage(frame, frame.shape[1],frame.shape[0],frame.strides[0],QImage.Format_RGB888)
        #QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self._pixmapdromframe = QPixmap.fromImage(self._imgfromframe)
        
        #wgranie obrazu
        self.setPixmap(self._pixmapdromframe)
        self.setMaximumSize(self._pixmapdromframe.width(), self._pixmapdromframe.height())
        
#############################Paint Event###############################################
    @pyqtSlot()
    def eventImageSignalT(self):
        t = Thread(target=self.eventImageSignalT)
        t.start()

    def paintEvent(self, event):
        
        #inicializacja pintera
        qp = QPainter(self)
        
        try:
            #rysowanie obrazu
            qp.drawPixmap(self.rect(), self._pixmapdromframe)
        except AttributeError:
            pass
            
        finally:
            #kolro i tlo
            br = QBrush(QColor(200, 10, 10, 200))
            
            #wgranie stylu 
            qp.setBrush(br)

            #variable for chusing if we drow numbers and rectagled
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
            
    def extend_map(self):
        if self.direction_change == 'dawn':
            self.extend_map_dwn()
        elif self.direction_change == 'up':
            self.extend_map_up()
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
        self.ofsety -= self.delta_pixeli
        self.whot_to_drow = 'viue_muve'
        self.direction_change = 'left'
        self.update()
    
    def right(self):
        self.ofsety += self.delta_pixeli
        self.whot_to_drow = 'viue_muve'
        self.direction_change = 'right'
        self.update()

    def dawn(self):
        self.ofsetx -= self.delta_pixeli
        self.whot_to_drow = 'viue_muve'
        self.direction_change = 'dawn'
        self.update()

    def up(self):
        self.ofsetx += self.delta_pixeli
        self.whot_to_drow = 'viue_muve'
        self.direction_change = 'up'
        self.update()

###########################map extetion##############################

    #save first viue to the map
    def Save_curent_viue(self):
        self.waite_for_manipulator()
        if all(self.main_window.manipulaor.check_on_target().values()):   
            self.map = self.frame

            self.map_shape = shape()
            temp = squer(0, 0, 1024,768)
            self.map_shape.add_squer(temp)

            self.first = self.frame

    #not finieshed
    def reset_map(self):
        pass

    def waite_for_manipulator(self):
        self.main_window.manipulaor.weaith_for_target()
        self.snap_img()

    #technicli ok
    def extend_map_right(self):
    
        self.waite_for_manipulator()

        dx = self.delta_pixeli

        x,y,z = self.frame.shape #wymiary podglondu

        xm, ym, zm = self.map.shape #wymiary aktualnej mapy

       #tablica do któej wkopiujemy poszerzona mape
        if self.ofsety+dx > self.ofsetymax:
            tab = np.ones((xm, ym + dx, zm), dtype=np.uint8)
            self.ofsetymax = self.ofsety
        else:
            tab = np.ones((xm, ym, zm), dtype=np.uint8)
            
            
        try:
            #Wkopoiowanie istniejocej mapy
            tab[0:xm, 0:ym] = self.map
            
            #wkopiowanie nowego fragmentu
            tab[self.ofsetx: x + self.ofsetx, ym:ym+dx] = self.frame[:, y-dx:]
                
        except ValueError as e:
            print(e)
            
        self.map = tab

    #technicli ok
    def extend_map_dwn(self):
    
        self.snap_img()

        dx = self.delta_pixeli

        s = self._pixmapdromframe.size() #wymiary podglondu
        x = s.height()
        y = s.width()

        xm, ym, zm = self.map.shape #wymiary aktualnej mapy

        #tablica do któej wkopiujemy poszerzona mape
        if self.ofsety+dx > self.ofsetxmax:
            tab = np.ones((xm+dx, ym, zm), dtype=np.uint8)
            self.ofsetxmax = self.ofsetx
        else:
            tab = np.ones((xm, ym, zm), dtype=np.uint8)
            
        try:    
            #Wkopoiowanie istniejocej mapy
            tab[0:xm, 0:ym] = self.map
        
        except ValueError as e:
            print(e,'map')
        
        try: 
            #wkopiowanie nowego odkrytewgo fragmentu
            tab[xm:xm+dx, self.ofsety: y+self.ofsety] = self.frame[x-dx:, :]
        
        except ValueError as e:
            print(e,'frame')
            print(tab[xm:xm+dx, self.ofsety: y+self.ofsety].shape,self.frame[x-dx:, :].shape)
            print(xm,xm+dx)
        
        self.map = tab

    # technicli ok
    def extend_map_left(self):
    
        self.snap_img()
    
        dx = self.delta_pixeli

        s = self._pixmapdromframe.size()  # wymiary podglondu
        x = s.height()
        y = s.width()

        xm, ym, zm = self.map.shape  # wymiary aktualnej mapy


        # tablica do któej wkopiujemy poszerzona mape
        if self.ofsety < self.ofsetymin:
            tab = np.ones((xm, ym + dx, zm), dtype=np.uint8)
            self.ofsetymin = self.ofsety
        else:
            tab = np.ones((xm, ym, zm), dtype=np.uint8)

        try:
            
            if self.ofsety < 0:
                # Wkopoiowanie istniejocej mapy
                tab[0:xm, dx:] = self.map
                
            else:
                tab = self.map
             
            # wkopiowanie nowego odkrytewgo fragmentu
            tab[self.ofsetx: x+self.ofsetx, 0:dx] = self.frame[:, 0:dx]
            
        except Exception as e:
            print(e)
            print(tab[0:xm, dx:].shape,self.map.shape)
        

        self.map = tab

    # technicli notok
    def extend_map_up(self):
        
        self.snap_img()

        dx = self.delta_pixeli

        s = self._pixmapdromframe.size()  # wymiary podglondu
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

    def edit_roi(self,roi):
        
        self.edit_trybe = True
        self.edited_roi = roi
    
    def end_edit(self):
        self.edit_trybe = False
        self.edited_roi = None
