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
import Map as M


class Obraz(ROI_maping):
    # Klaza Obraz dziedziczy z QLabel, pozwala na lepszą obsługę eventu mouseMoveEvent

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
    
    #skala mapy
    skala = 4
    
    #maxymalna pozycja manipulatora w mm
    manipulator_max = 50
    
    # value that remember whot part of the sample have been seen save to map
    ofsetymax = 0
    ofsetxmax = 0

    ofsetymin = 0
    ofsetxmin = 0
    
    # boolean alowing to snap first schown image as a map prive
    first = True

    # pixmap object reded from camera/file
    frame = True

    map = np.zeros(100)
    map.shape = (10,10,1)
    
    # construvtor
    def __init__(self, main_window, *args, **kwargs):
        super(Obraz, self).__init__(main_window, *args, **kwargs)
        
        self.initCamera() # inicializacja camery
        
        self.h_cam.put_AutoExpoEnable(False)


###############################camera read##########################################

    def snap_img(self):
        self.h_cam.Snap(1)
    
    @pyqtSlot()
    def snap_image_event_signal(self):
         
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
            self.save_curent_viue()
            self.extend_map_exeqiute()
            # plt.imsave('img_frame_{}.png'.format(self.total), img)

    @staticmethod
    def cameracallback(nevent, ctx):
        if nevent == tcam.TOUPCAM_EVENT_IMAGE:
            ctx.eventImage.emit()
        elif nevent == tcam.TOUPCAM_EVENT_STILLIMAGE:
            ctx.snap_image_event.emit()

    @pyqtSlot()
    def eventImageSignal(self):

        if self.h_cam is not None:

            try:
                self.h_cam.PullImageV2(self.buf, 24, None)
                self.total += 1

            except tcam.HRESULTException:
                print('pull image failed')
                QMessageBox.warning(self, '', 'pull image failed', QMessageBox.Ok)

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
            QMessageBox.warning(self, '',"error during camera initialisation", QMessageBox.Ok)

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
                #creating bufer for image hold
                self.w, self.h = self.h_cam.get_Size()
                bufsize = ((self.w * 24 + 31) // 32 * 4) * self.h
                self.buf = bytes(bufsize)

                try:
                    if sys.platform == 'win32':
                        self.h_cam.put_Option(tcam.TOUPCAM_OPTION_BYTEORDER, 0) # QImage.Format_RGB888

                    self.h_cam.StartPullModeWithCallback(self.cameracallback, self)
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
                self.snap_img()

            else:
                # podstawowa obcja rysuje nowy prostokat
                self.all_Rectagles(qp)
                qp.drawRect(QRect(self.begin, self.end))
                # rysowanie prostokonta na bierzoco jak podglond do ruchu myszka

            self.loadImage(tym, num)
    

    def chosen_rectagle(self, Painter):
        Painter.drawRect(self.rectagledrow(self.main_window.rectangles[self.ktury]))
      

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
        self.update()
   
    def right(self):
        self.ofsety += self.delta_pixeli
        self.whot_to_drow = 'viue_muve'
        self.update()

    def dawn(self):
        self.ofsetx -= self.delta_pixeli
        self.whot_to_drow = 'viue_muve'
        self.update()

    def up(self):
        self.ofsetx += self.delta_pixeli
        self.whot_to_drow = 'viue_muve'
        self.update()
        
###########################map extetion##############################

    # save first viue to the map
    def save_curent_viue(self):
        if self.first:
           
            x, y, z = self.frame_2.shape
            
            map_size = int(x+self.manipulator_max*510/self.skala) #x size
            map_size *= int(y+self.manipulator_max*510/self.skala) #y size
            map_size *= 3 # RGB colors
            
            #stworzenie tablicy przechowujacej obraz mapy
            self.map = np.zeros(map_size,dtype=np.uint8)
            
            #okreslenei ksztaltu tej tabliczy
            self.map.shape = (int(x+50*510/self.skala),int(y+50*510/self.skala),3)
            
            #wykonanie fukcji wklejajacej aktualny podglond do mapy
            self.extend_map_exeqiute()
            
            #zapisanie ze mapa juz jest zainiciowana i nie trzeba tego robic
            self.first = False

    # metoda zapisujaca do mapy aktualny podglond we wskazane miejsce na którym znajduje sie manipulaor
    def extend_map_exeqiute(self):
        
        x, y, z = self.frame_2.shape
        
        xm,ym,zm, = self.main_window.manipulaor.get_axes_positions()
        
        #przeliczenie milimetrow na pixele i odwrucenie osi
        ym,zm = int((50-ym)*510/self.skala),int((50-zm)*510/self.skala)
        
        #przeskalowanei podglondu
        klatka = cv2.resize(self.frame_2,(int(x/self.skala),int(y/self.skala)))
        
        #wklejenie podglondu we własciwe miejsce na mapie
        try:
            self.map[zm:zm+int(y/self.skala),ym:ym+int(x/self.skala)] = klatka
        except Exception as e:
            print(e)
            print(self.map[ym:ym+int(x/self.skala),zm:zm+int(y/self.skala)].shape)
            print(klatka.shape)

        if self.main_window.map is None:
            self.main_window.map = M.Map_window(self.map, self.main_window)
        else:
            self.main_window.map.new_image(self.map)
            
    #wyczysczenie aktualnie zebranej mapy
    def reset_map(self):
        
        #zapytanei uzytkownika czy napewno chce to zrobic
        reply = QMessageBox.question(self,"mesage","Czy napewno chcesz usunac mape?",
                                     QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
        
        
        if reply == QMessageBox.Yes:
            #jesli odpowie tak to ustawienie ze nie zebrano zadnej mapy i stworzenie jej na nowo nadpisuajc stara
            self.first = True
            self.save_curent_viue()
            
    def get_map(self):
        return self.map