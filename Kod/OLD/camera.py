from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys, toupcam
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QDesktopWidget, QCheckBox, QMessageBox
import numpy as np
import matplotlib.pyplot as plt
import copy as copy
import cv2 as cv2
#import opencv.contrib

# plt.imsave('img_frame_{}.png'.format(self.total), obraz)
class camera(QLabel):
            
    eventImage = pyqtSignal()
    snap_image_event = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.hcam = None
        self.buf = None      # video buffer
        self.w = 0           # video width
        self.h = 0           # video height
        
        self.x = 10
        self.y = 152
        self.total = 0
        
        self.initUI() #inicializacja wymiarów obiektu pyqt
        
        self.initCamera() #inicializacja camery
        
        self.opencvimage = cv2.imread("5.jpg")
        
        #self.eventImageSignal()
        
      #  self.h_cam.put_AutoExpoEnable(True)


    def initUI(self):
     #   self.cb = QCheckBox('Auto Exposure', self)
     #   self.cb.stateChanged.connect(self.changeAutoExposure)
     #   self.label = QLabel(self)
        self.setScaledContents(True)
     #   self.label.przemiesc(0, 30)
        self.resize(self.geometry().width(), self.geometry().height())

# the vast majority of callbacks come from toupcam.dll/so/dylib internal threads, so we use qt signal to post this event to the UI thread  
    @staticmethod
    def cameraCallback(nEvent, ctx):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            ctx.nowy_obraz_z_kamery.emit()
        elif nEvent == toupcam.TOUPCAM_EVENT_STILLIMAGE:
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

                     
# run in the UI thread
    @pyqtSlot()
    def eventImageSignal(self):
        if self.hcam is not None:
            try:
                self.hcam.PullImageV2(self.buf, 24, None)
                self.total += 1
            except toupcam.HRESULTException:
                print('pull obraz failed')
                QMessageBox.warning(self, '', 'pull obraz failed', QMessageBox.Ok)
            else:
                   
                img = QImage(self.buf, self.w, self.h, (self.w * 24 + 31) // 32 * 4, QImage.Format_RGB888)
                self.opencvimage =  self.convertQImageToMat(img)
                self.setPixmap(QPixmap.fromImage(img))
   
          
   
 #   @pyqtSlot()                
    def snap_image_event_signal(self):
        
        if self.hcam is not None:
            w, h = self.hcam.get_Size()
           # w= 2048
           # h= 1536 
            bufsize = ((w * 24 + 31) // 32 * 4) * h
            still_img_buf = bytes(bufsize)
            self.hcam.PullStillImageV2(still_img_buf, 24, None)
            print('saving obraz')
        #    print(self.h_cam.get_ExpoTime())
            print(w, h)
            print()
            img = self.bytes_to_array(still_img_buf)
            plt.imsave('img_frame_{}.png'.format(self.total), img)

                        
    def bytes_to_array(self, still_img_buf, dtype=np.uint8):
        arr_1d = np.frombuffer(still_img_buf, dtype=dtype)
        return arr_1d.reshape(self.h, self.w, 3)
        #return arr_1d.reshape(1536, 2048, 3)

    def initCamera(self):
        
        a = toupcam.Toupcam.EnumV2()
        
        if len(a) <= 0:
            print("erore during camera inicialisation")
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
                #creating bufer for obraz hold
                self.w, self.h = self.hcam.get_Size()
                bufsize = ((self.w * 24 + 31) // 32 * 4) * self.h
                self.buf = bytes(bufsize)
                
         #       self.cb.setChecked(self.h_cam.get_AutoExpoEnable())
          
                try:
                    if sys.platform == 'win32':
                        self.hcam.put_Option(toupcam.TOUPCAM_OPTION_BYTEORDER, 0) # QImage.Format_RGB888
                        
                    self.hcam.StartPullModeWithCallback(self.cameraCallback, self)
                except toupcam.HRESULTException:
                    QMessageBox.warning(self, '', 'failed to start camera', QMessageBox.Ok)

    def changeAutoExposure(self, state):
        if self.hcam is not None:
            self.hcam.put_AutoExpoEnable(state)
            
    def pause(self, x):
        self.hcam.Pause(x)
        
    def snap_img(self):
        self.hcam.Snap(1)
        
    def restart(self):
        pass
      #  print(se;f)
       # self.h_cam.StartPullModeWithCallback(self.cameraCallback, self)

    def close(self):
        print('closing')
        if self.hcam is not None:
            self.hcam.Close()
            self.hcam = None

    def get_opencvimage(self):
        return self.opencvimage
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    t = QMainWindow()
    
    t.setCentralWidget(camera())
    
    t.show()
    app.exec_()
