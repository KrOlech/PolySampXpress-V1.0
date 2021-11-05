from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys, toupcam
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QDesktopWidget, QCheckBox, QMessageBox
import numpy as np
import matplotlib.pyplot as plt

import cv2 as cv2


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
        
      #  self.setFixedSize(800, 600)
      #  qtRectangle = self.frameGeometry()
      #  centerPoint = QDesktopWidget().availableGeometry().center()
      # qtRectangle.moveCenter(centerPoint)
      #  self.move(qtRectangle.topLeft())
        self.initUI()
        self.initCamera()
        
      #  self.hcam.put_AutoExpoEnable(True)


    def initUI(self):
     #   self.cb = QCheckBox('Auto Exposure', self)
     #   self.cb.stateChanged.connect(self.changeAutoExposure)
     #   self.label = QLabel(self)
        self.setScaledContents(True)
     #   self.label.move(0, 30)
        self.resize(self.geometry().width(), self.geometry().height())

# the vast majority of callbacks come from toupcam.dll/so/dylib internal threads, so we use qt signal to post this event to the UI thread  
    @staticmethod
    def cameraCallback(nEvent, ctx):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            ctx.eventImage.emit()
        elif nEvent == toupcam.TOUPCAM_EVENT_STILLIMAGE:
            ctx.snap_image_event.emit()        
            

                     
# run in the UI thread
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
             #   self.setWindowTitle('{}: {}'.format(self.camname, self.total))
                nparr = np.fromstring(self.buf, np.uint8)
                #print(nparr)
                #nparr.shape = (self.w, self.h,3)
                #img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                print(self.buf)
                img = QImage(self.buf, self.w, self.h, (self.w * 24 + 31) // 32 * 4, QImage.Format_RGB888)
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
            print('saving image')
        #    print(self.hcam.get_ExpoTime())
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
            pass
   #        self.setWindowTitle('No camera found')
    #        self.cb.setEnabled(False)
        else:
            self.camname = a[0].displayname
       #     self.setWindowTitle(self.camname)
            self.eventImage.connect(self.eventImageSignal)
            self.snap_image_event.connect(self.snap_image_event_signal)

            try:
                self.hcam = toupcam.Toupcam.Open(a[0].id)
            except toupcam.HRESULTException:
                QMessageBox.warning(self, '', 'failed to open camera', QMessageBox.Ok)
            else:
                self.w, self.h = self.hcam.get_Size()
                bufsize = ((self.w * 24 + 31) // 32 * 4) * self.h
                self.buf = bytes(bufsize)
         #       self.cb.setChecked(self.hcam.get_AutoExpoEnable())            
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
       # self.hcam.StartPullModeWithCallback(self.cameraCallback, self)

    def close(self):
        print('closing')
        if self.hcam is not None:
            self.hcam.Close()
            self.hcam = None

