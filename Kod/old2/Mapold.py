from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QEvent
import cv2
from roi_create import ROI_maping


class Map(ROI_maping):

    def __init__(self, img, main_window, *args, **kwargs):
        super(Map, self).__init__(main_window, *args, **kwargs)

        # shape of a new obraz
        x,y, z = img.shape

        # zapisanie rozmiaru obrazu w celu implementacji przyszłego skalaowania.
        self.Rozmiar = (y, x)
        self.orgx = x
        self.orgy = y

        # zapisanie nowego obrazu
        self.image_opencv = img

        self.img = QImage(img, img.shape[1],img.shape[0],img.strides[0],QImage.Format_RGB888)
        #QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.img = QPixmap.fromImage(self.img)

        #seting pixmap
        self.setPixmap(self.img)

    def new_image(self, img):

        #shape of a new obraz
        x,y, z = img.shape

        #zapisanie rozmiaru obrazu w celu implementacji przyszłego skalaowania.
        self.Rozmiar = (y, x)
        self.orgx = x
        self.orgy = y

        #zapisanie nowego obrazu
        self.image_opencv = img

        self.img = QImage(img, img.shape[1],img.shape[0],img.strides[0],QImage.Format_RGB888)
        #QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.img = QPixmap.fromImage(self.img)

    #overload of pyqt5  resize event
    def resizeEvent(self, event):

        #read curent window size
        x, y = self.height(), self.width()

        #calculate scal for mouse reed
        self.skalx = x/self.orgx
        self.skaly = y/self.orgy
        
        #print(self.skal, self.skaly)


class Map_window(QWidget):

    def __init__(self, map, main_window, *args, **kwargs):
        super(Map_window, self).__init__(*args, **kwargs)

        self.setWindowTitle("Mapa Prubki")
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        #main layout
        self.layout = QVBoxLayout()

        #map object
        self.map = Map(map, main_window)

        self.layout.addWidget(self.map, Qt.AlignCenter)
        self.setLayout(self.layout)

    #pass object to map object
    def new_image(self, img):
        self.map.new_image(img)
