import numpy as np
from PyQt5.QtWidgets import *
import cv2
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *  # QFileDialog ,QMainWindow,QToolBar ,QAction
import sys
import toupcam as tcam
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QImage
import Clasa as oC
import matplotlib.pyplot as plt
from threading import Thread
from time import sleep, time
from roi_create import ROI_maping


class Obraz(ROI_maping):
    # Klaza Obraz_z_kamery dziedziczy z QLabel, pozwala na lepszą obsługę eventu mouseMoveEvent

# signals for camera action
    eventImage = pyqtSignal()
    snap_image_event = pyqtSignal()	

    h_cam = None
    buf = None      # video buffer
    w = 0           # video width
    h = 0           # video height

    x = 10
    y = 152
    total = 0

    # '' 'up' 'dawn' 'right' 'left' 'multi'
    direction_change = ''

    # rozmiar obszaru
    rozmiar = (1024, 768)
    
    # value that remember whot part of the sample have been seen save to map
    ofsetymax = 0
    ofsetxmax = 0

    ofsetymin = 0
    ofsetxmin = 0
    
    # boolean alowing to snap first schown obraz as a map prive
    first = True

    # pixmap object reded from camera/file
    frame = True

    map = []
    
    # construvtor
    def __init__(self, main_window, *args, **kwargs):
        super(Obraz, self).__init__(main_window, *args, **kwargs)
        
        self.initCamera() # inicializacja camery
        
        self.h_cam.put_AutoExpoEnable(False)

###############################camera read##########################################

    def snap_img(self):
        self.save_curent_viue()
        print("wywolanie wymuszenia eventu")
        self.h_cam.Snap(1)
    
    @pyqtSlot()
    def snap_image_event_signal(self):
        print("wymuszony event")
        
        if self.h_cam is not None:
            w, h = self.h_cam.get_Size()
            bufsize = ((w * 24 + 31) // 32 * 4) * h
            still_img_buf = bytes(bufsize)
            self.h_cam.PullStillImageV2(still_img_buf, 24, None)
            
            img = self.bytes_to_array(still_img_buf)
            
            qimage_read_from_camera = QImage(still_img_buf,
                                      self.w, self.h,
                                      (self.w * 24 + 31) // 32 * 4,
                                      QImage.Format_RGB888)
                     
            #self.image_opencv_2 = self.convertQImageToMat(
            #        qimage_read_from_camera) self.image_opencv_2

            self.frame_2 = cv2.resize(img, self.rozmiar)
            self.extend_map_camera()

            # plt.imsave('img_frame_{}.png'.format(self.total), obraz)

    @staticmethod
    def cameraCallback(nEvent, ctx):
        if nEvent == tcam.TOUPCAM_EVENT_IMAGE:
            ctx.nowy_obraz_z_kamery.emit()
        elif nEvent == tcam.TOUPCAM_EVENT_STILLIMAGE:
            ctx.nowy_wymuszony_obraz_z_kamery.emit()

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

        if self.h_cam is not None:

            try:
                self.h_cam.PullImageV2(self.buf, 24, None)
                self.total += 1

            except tcam.HRESULTException:
                print('pull obraz failed')
                QMessageBox.warning(self, '', 'pull obraz failed', QMessageBox.Ok)

            else:
                self.Qimage_read_from_camera = QImage(self.buf,
                                      self.w, self.h,
                                      (self.w * 24 + 31) // 32 * 4,
                                      QImage.Format_RGB888)
                
                self.image_opencv = self.bytes_to_array(self.buf)
                
                self.loadImage()

    #conwert Qpixmap to numpy tab
    def bytes_to_array(self, still_img_buf, dtype=np.uint8):
        arr_1d = np.frombuffer(still_img_buf, dtype=dtype)
        return arr_1d.reshape(self.h, self.w, 3)

    def initCamera(self):

        a = tcam.Toupcam.EnumV2()

        if len(a) <= 0:
            QMessageBox.warning(self, '',"erore during camera inicialisation", QMessageBox.Ok)

        else:
            self.camname = a[0].displayname

            #create and conect custom pyqt5 signa
            self.eventImage.connect(self.eventImageSignal)

            self.snap_image_event.connect(self.snap_image_event_signal)

            #trying opening camera
            try:
                self.h_cam = tcam.Toupcam.Open(a[0].id)

            except tcam.HRESULTException:
                QMessageBox.warning(self, '', 'failed to open camera', QMessageBox.Ok)

            else:
                #creating bufer for obraz hold
                self.w, self.h = self.h_cam.get_Size()
                bufsize = ((self.w * 24 + 31) // 32 * 4) * self.h
                self.buf = bytes(bufsize)

                try:
                    if sys.platform == 'win32':
                        self.h_cam.put_Option(tcam.TOUPCAM_OPTION_BYTEORDER, 0) # QImage.Format_RGB888

                    self.h_cam.StartPullModeWithCallback(self.cameraCallback, self)
                except tcam.HRESULTException:
                    QMessageBox.warning(self, '', 'failed to start camera', QMessageBox.Ok)		


#############################Paint Event###############################################

    def paintEvent(self, event):
        
        # inicializacja pintera
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
            
            if self.whot_to_drow == 'all_rectagls':  #pokazuje wsystkie prostkoaty
                self.all_Rectagles(qp)

            elif self.whot_to_drow == 'no_rectagle':  #howa wszystkie prostokaty
                tym = False
        
            elif self.whot_to_drow =='One_rectagle':  #rysuje wybrany prostokat
                
                self.chosen_rectagle(qp)
                tym = False
                num = True
                
            elif self.whot_to_drow == 'viue_muve':

                self.all_Rectagles(qp)
                self.move_viue()
                self.extend_map()

            else:
                # podstawowa obcja rysuje nowy prostokat
                self.all_Rectagles(qp)
                qp.drawRect(QRect(self.begin, self.end))
                # rysowanie prostokonta na bierzoco jak podglond do ruchu myszka

            self.loadImage(tym, num)
    
    def extend_map(self):
        if self.direction_change:
            self.waite_for_manipulator()

    # waiting for manipulator and snap ne klatka
    def waite_for_manipulator(self):
        self.main_window.manipulaor.weaith_for_target()
        self.snap_img()

    # ches map change direction
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
        elif self.direction_change == 'multi':
            self.extend_map_multi()
        else:
            pass
        self.direction_change = ''
    
    def chosen_rectagle(self, Painter):
        Painter.drawRect(self.rectagledrow(self.main_window.rectangles[self.ktury]))
      
    def move_viue(self):        
        self.loadImage()

####################################fukcje wywoływane przez guziki z gluwnego okna####################################

    # rysowanie wsystkich prostokontów po nacisnieciu odpowiedniego przyciusku
    def narysujcaloscs(self):

        self.whot_to_drow = 'all_rectagls'
        self.iloscklikniec = True
        self.update()
    
    def schowajcalosc(self): #schowanie wsystkich prostokontów

        self.whot_to_drow = 'no_rectagle'
        self.iloscklikniec = True
        self.update()
            
    def next(self):#narysowanie nastempnego prostokata
    
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

    #metoda generujaca pusty
    def map_size_update(self):

        xm, ym, zm = self.map.shape

        if self.ofsetx < self.ofsetxmin:
            xm += abs(self.dxp)
            self.ofsetxmin = self.ofsetx
        elif self.ofsetx > self.ofsetxmax:
            xm += abs(self.dxp)
            self.ofsetxmax = self.ofsetx
        else:
            pass

        if self.ofsety < self.ofsetymin:
            ym += abs(self.dyp)
            self.ofsetymin = self.ofsety
        elif self.ofsety > self.ofsetymax:
            ym += abs(self.dyp)
            self.ofsetymax = self.ofsety
        else:
            pass

        return np.ones((xm, ym, zm), dtype=np.uint8)

    def inject_map(self):

        xm, ym, zm = self.map.shape
        try:
            if self.dxp >= 0 and  self.dyp >= 0:
                self.mape_impute_tab[:xm, :ym] = self.map

            elif self.dxp<0 and  self.dyp >= 0:
                self.mape_impute_tab[self.dxp:, :ym] = self.map

            elif self.dxp>=0 and  self.dyp < 0:
                self.mape_impute_tab[:xm, self.dyp:] = self.map

            elif self.dxp<0 and  self.dyp < 0:
                self.mape_impute_tab[self.dxp:, self.dyp:] = self.map
        except Exception as e:
            print(e)
    #update map on center on click metod WIP
    def mapupdate(self):
    
        self.save_curent_viue()

        self.mape_impute_tab = self.map_size_update()

        print(self.dxp, self.dyp)

        self.inject_map()

        self.whot_to_drow = 'viue_muve'
        self.direction_change = 'multi'
        self.update()

    # save first viue to the map
    def save_curent_viue(self):
        if self.first:
            self.map = self.frame
            self.first = False

    def reset_map(self):
        pass


    def extend_map_exeqiute(self, test_extend, ofset, borderofset, dx, dy, tx, ty, fx, fy):

        x, y, z = self.frame_2.shape  # wymiary podglondu

        xm, ym, zm = self.map.shape  # wymiary aktualnej mapy

        if test_extend:
            tab = np.ones((xm + dx[0], ym+dy[0], zm), dtype=np.uint8)
            borderofset = ofset
            tab[dx[1]:xm + dx[1], dy[1]:ym+dy[1]] = self.map # Wkopoiowanie istniejocej mapy
        else:
            tab = self.map

        try:
            tab[tx[0]:tx[1], ty[0]:ty[1]] = self.frame_2[fx[0]:fx[1], fy[0]:fy[1]]

        except ValueError as e:
            print(e)
            print(tab[tx[0]:tx[1], ty[0]:ty[1]].shape, "map")
            print(self.frame_2[fx[0]:fx[1], fy[0]:fy[1]].shape,"klatka")

        self.map = tab

    def extend_map_right(self):

        x, y, z = self.frame_2.shape  # wymiary podglondu

        xm, ym, zm = self.map.shape  # wymiary aktualnej mapy

        self.extend_map_exeqiute(self.ofsety > self.ofsetymax, self.ofsety, self.ofsetymax,
                                  (0,0), (self.delta_pixeli,0),
                                 (self.ofsetx-self.ofsetxmin, x + self.ofsetx-self.ofsetxmin),
                                 (ym, ym+self.delta_pixeli),
                                 (0, y),
                                 (y-self.delta_pixeli, y))

    def extend_map_dwn(self):
       
        x, y, z = self.frame_2.shape  # wymiary podglondu

        self.extend_map_exeqiute(self.ofsetx < self.ofsetxmin ,self.ofsetx, self.ofsetxmin,
                                (self.delta_pixeli,self.delta_pixeli), (0,0),
                                (0, self.delta_pixeli),
                                (self.ofsety - self.ofsetymin, y + self.ofsety - self.ofsetymin),
                                (0, self.delta_pixeli),
                                (0, y))

    def extend_map_left(self):

        x, y, z = self.frame_2.shape  # wymiary podglondu

        xm, ym, zm = self.map.shape  # wymiary aktualnej mapy

        self.extend_map_exeqiute(self.ofsety < self.ofsetymin, self.ofsety, self.ofsetymin,
                                 (0,0),(self.delta_pixeli,self.delta_pixeli),
                                 (self.ofsetx-self.ofsetxmin, x+self.ofsetx-self.ofsetxmin),
                                 (0, self.delta_pixeli),
                                 (0, y),
                                 (0, self.delta_pixeli))

    def extend_map_up(self):

        x, y, z = self.frame_2.shape  # wymiary podglondu
        
        xm, ym, zm = self.map.shape  # wymiary aktualnej mapy

        self.extend_map_exeqiute(self.ofsetx > self.ofsetxmax, self.ofsetx, self.ofsetxmax,
                                 (self.delta_pixeli,0), (0,0),
                                 (xm, self.delta_pixeli+xm),
                                 (self.ofsety - self.ofsetymin, y + self.ofsety - self.ofsetymin),
                                 (x-self.ofsety-self.ofsetymin, x),
                                 (0, y))

    def extend_map_multi(self):

        dy = abs(self.dyp)
        dx = abs(self.dxp)

        x, y, z = self.frame_2.shape  # wymiary podglondu

        xm, ym, zm = self.map.shape  # wymiary aktualnej mapy
    
        try:
            if self.dyp > 0:
                print('right')
                self.mape_impute_tab[self.ofsetx - self.ofsetxmin: x + self.ofsetx - self.ofsetxmin, ym: ym + dy] = \
                    self.frame_2[:, y - dy:]
            else:
                print('left')
                self.mape_impute_tab[self.ofsetx - self.ofsetxmin: x + self.ofsetx - self.ofsetxmin, 0: dy] = \
                    self.frame_2[:, 0:dy]

            if self.dxp > 0:
                print('up')
                self.mape_impute_tab[xm: dx + xm, self.ofsety - self.ofsetymin: y + self.ofsety - self.ofsetymin] = \
                    self.frame_2[x - dx:, :]
            else:
                print('dwn')
                self.mape_impute_tab[0:dx, self.ofsety - self.ofsetymin: y + self.ofsety - self.ofsetymin] = \
                    self.frame_2[0:dx, :]

            self.map = self.mape_impute_tab
        except Exception as e:
            print(e)
    def get_map(self):
        self.save_curent_viue()
        return self.map
