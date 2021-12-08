import numpy as np
from PyQt5.QtWidgets import * #QFileDialog ,QMainWindow,QToolBar ,QAction
import cv2
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *  # QFileDialog ,QMainWindow,QToolBar ,QAction
import numpy as np
import sys, toupcam
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QImage
import Clasa as oC
import matplotlib.pyplot as plt
from threading import Thread
from time import sleep,time
from roi_create import ROI_maping

class Obraz(ROI_maping):
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

    # '' 'up' 'dawn' 'right' 'left'
    direction_change = ''
        
 

    # rozmiar obszaru
    Rozmiar = (1024,768)
    
    #value that remember whot part of the sample have been seen save to map
    ofsetymax = 0
    ofsetxmax = 0

    ofsetymin = 0
    ofsetxmin = 0
    
    #boolean alowing to snap first schown image as a map prive
    first = True
    

    
    #pixmap object reded from camera/file
    frame = True
    
    waitontarget = False
    
    move_to_point = True
    
    mape_impute_tab = []
    
    #construvtor
    def __init__(self, main_window, *args, **kwargs):
        super(Obraz, self).__init__(main_window,*args, **kwargs)
        
        self.initCamera() #inicializacja camery
        
        self.hcam.put_AutoExpoEnable(False)
        
        #Tworzy białe tło
        self.setAutoFillBackground(True)       
        

###############################camera read##########################################

    def snap_img(self):
        print("wywolanie wymuszenia eventu")
        self.hcam.Snap(1)
    
    @pyqtSlot()
    def snap_image_event_signal(self):
        print("wymuszony event")
        
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
            
            #self.loadImage()
            self.extend_map_camera()
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
                    
                    
                self.loadImage()

    #conwert Qpixmap to numpy tab
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


#############################Paint Event###############################################

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
            br = QBrush(QColor(200, 10, 10, 200))#,Qt.CrossPattern)
            
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
        if self.direction_change:
            self.waite_for_manipulator()

    #ches map change direction
    def extend_map_camera(self):
        print("extend_map")
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
    
    def chosen_rectagle(self, Painter):
        Painter.drawRect(self.rectagledrow(self.main_window.rectangles[self.ktury]))
      
    def move_viue(self):        
        self.loadImage()

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
        
        if self.ktury < len(self.main_window.rectangles)-1:
            self.ktury += 1
        else:
            self.ktury = 0
            
        self.update()
       
    def last(self):#narysowanie poprzedniego prostokonta
    
        self.whot_to_drow = 'One_rectagle'
        self.iloscklikniec = True
        
        if self.ktury == 0 :
            self.ktury = len(self.main_window.rectangles)-1
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

    #update map on center on click metod WIP
    def mapupdate(self):
    
        xm, ym, zm = self.map.shape #wymiary aktualnej mapy
        
        if self.ofsetx < self.ofsetxmin:
            xm += abs(self.dxp)
        elif self.ofsetx < self.ofsetxmin:
            xm += abs(self.dxp)
        else:
            pass
            
        if self.ofsetx > self.ofsetxmax:
            ym += abs(self.dyp)
        elif self.ofsety > self.ofsetymax:
            ym += abs(self.dyp)
        else:
            pass
            
        self.mape_impute_tab = np.ones((xm, ym, zm), dtype=np.uint8)
        print(self.dxp,self.dyp)
        
        if self.dyp > 0:
            #self.whot_to_drow = 'viue_muve'
            #self.direction_change = 'right'
            print('right')
        else:
            self.dyp = abs(self.dyp)
            print('left')
            #self.whot_to_drow = 'viue_muve'
            #self.direction_change = 'left'
            
        #self.update()
        
        if self.dxp > 0:
            #self.whot_to_drow = 'viue_muve'
            #self.direction_change = 'up'
            print('up')
            
        else:
            self.dxp = abs(self.dxp)
            print('dwn')
            #self.whot_to_drow = 'viue_muve'
            #self.direction_change = 'dawn'
        self.update() 
            
            
    #save first viue to the map
    def Save_curent_viue(self):
        self.waite_for_manipulator()
        
        if all(self.main_window.manipulaor.check_on_target().values()):   
            self.map = self.frame
            self.first = self.frame
            
    #not finieshed
    def reset_map(self):
        pass

    #waiting for manipulator and snap ne frame
    def waite_for_manipulator(self):
        self.main_window.manipulaor.weaith_for_target()
        self.snap_img()
          

    def extend_map_right(self,tab = False):
        
        dx = self.delta_pixeli if not self.dyp else self.dyp

        x,y,z = self.frame.shape #wymiary podglondu

        xm, ym, zm = self.map.shape #wymiary aktualnej mapy

       #tablica do któej wkopiujemy poszerzona mape
        if len(self.mape_impute_tab)==0:
            if self.ofsety > self.ofsetymax:
                tab = np.ones((xm, ym + dx, zm), dtype=np.uint8)
                self.ofsetymax = self.ofsety
            else:
                tab = np.ones((xm, ym, zm), dtype=np.uint8)
        else:
            tab = self.mape_impute_tab
            
        try: 
            #Wkopoiowanie istniejocej mapy
            tab[0:xm, 0:ym] = self.map
            
            #wkopiowanie nowego fragmentu 
            tab[self.ofsetx-self.ofsetxmin: x + self.ofsetx-self.ofsetxmin, ym:ym+dx] = self.frame[:, y-dx:]
                
        except ValueError as e:
            print(e)
            print(tab[self.ofsetx-self.ofsetxmin: x + self.ofsetx-self.ofsetxmin, ym:ym+dx].shape,'map')
            print(self.frame[:, y-dx:].shape,'frame')
            
            
        self.map = tab
        
        self.dxp = False
        
        self.mape_impute_tab = []


    def extend_map_dwn(self):
    
        dx = self.delta_pixeli if not self.dxp else self.dxp

        x,y,z = self.frame.shape #wymiary podglondu

        xm, ym, zm = self.map.shape  # wymiary aktualnej mapy
        
        if len(self.mape_impute_tab)==0:
            if self.ofsetx < self.ofsetxmin:
                tab = np.ones((xm + dx, ym, zm), dtype=np.uint8)
                self.ofsetxmin = self.ofsetx
                # Wkopoiowanie istniejocej mapy
                tab[dx:xm+dx, 0:ym] = self.map
            else:
                tab = self.map
        else:
            tab = self.mape_impute_tab
        try:
            tab[0:dx, self.ofsety-self.ofsetymin: y + self.ofsety-self.ofsetymin] = self.frame[0:dx, :]
        except ValueError as e:
            print(e)
            print(tab[0:dx, self.ofsety-self.ofsetymin: y + self.ofsety-self.ofsetymin].shape,'map')
            print(self.frame[0:dx, :].shape,'frame')

            
        self.map = tab
        self.dyp = False
        self.mape_impute_tab = []
        
    def extend_map_left(self):

    
        dx = self.delta_pixeli if not self.dyp else self.dyp

        x,y,z = self.frame.shape #wymiary podglondu

        xm, ym, zm = self.map.shape  # wymiary aktualnej mapy

        # tablica do któej wkopiujemy poszerzona mape
        if len(self.mape_impute_tab)==0:
            if self.ofsety < self.ofsetymin:
                tab = np.ones((xm, ym + dx, zm), dtype=np.uint8)
                self.ofsetymin = self.ofsety
                tab[0:xm, dx:] = self.map
            else:
                tab = self.map
        else:
            tab = self.mape_impute_tab
            
        try:
            # wkopiowanie nowego odkrytewgo fragmentu
            tab[self.ofsetx-self.ofsetxmin: x+self.ofsetx-self.ofsetxmin, 0:dx] = self.frame[:, 0:dx]
            
        except Exception as e:
            print(e)
            print(tab[self.ofsetx-self.ofsetxmin: x+self.ofsetx-self.ofsetxmin, 0:dx].shape,'map')
            print(self.frame[:, 0:dx].shape,'frame')
        

        self.map = tab
        self.dxp = False
        self.mape_impute_tab = []

    def extend_map_up(self):

        dx =  self.delta_pixeli if not self.dxp else self.dxp

        x,y,z = self.frame.shape #wymiary podglondu

        xm, ym, zm = self.map.shape #wymiary aktualnej mapy

        #tablica do któej wkopiujemy poszerzona mape
        if len(self.mape_impute_tab)==0:
            if self.ofsetx > self.ofsetxmax:
                tab = np.ones((xm+dx, ym, zm), dtype=np.uint8)
                self.ofsetxmax = self.ofsetx
                tab[0:xm, 0:ym] = self.map
            else:
                tab = self.map
                
        else:
            tab = self.mape_impute_tab   
            
        try:   
            
            #wkopiowanie nowego odkrytewgo fragmentu
            tab[xm:dx+xm, self.ofsety-self.ofsetymin: y+self.ofsety-self.ofsetymin] = self.frame[x-dx:, :]
            
        except ValueError as e:
            print(e)
            print(tab[xm:dx+xm, self.ofsety-self.ofsetymin: y+self.ofsety-self.ofsetymin].shape,'map')
            print(self.frame[x-dx:, :].shape,'frame')

        
        self.map = tab
        self.dyp = False
        self.mape_impute_tab = []
        
    def get_map(self):
        return self.map

