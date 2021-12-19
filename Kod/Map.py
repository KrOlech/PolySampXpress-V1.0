from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QEvent
import cv2
from roi_create import ROI_maping


class Map(ROI_maping):

    def __init__(self, img, main_window, *args, **kwargs):
        super(Map, self).__init__(main_window, *args, **kwargs)

        # zapisanie nowego obrazu
        self.image_opencv =  cv2.resize(img,self.rozmiar)
        
        img = self.image_opencv
        
        self.resize(self.rozmiar[0],self.rozmiar[1])

        self.img = QImage(img, img.shape[1],img.shape[0],img.strides[0],QImage.Format_RGB888)

        #QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.img = QPixmap.fromImage(self.img)

        #seting pixmap
        self.setPixmap(self.img)

    def new_image(self, img):

        #zapisanie nowego obrazu
        self.image_opencv =  cv2.resize(img,self.rozmiar)

        self.img = QImage(img, img.shape[1],img.shape[0],img.strides[0],QImage.Format_RGB888)
        #QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.img = QPixmap.fromImage(self.img)



class Map_window(QWidget):

    # rozmiar obszaru
    rozmiar = (1024, 768)

    def __init__(self, map, main_window, *args, **kwargs):
        super(Map_window, self).__init__(*args, **kwargs)

        self.setWindowTitle("Mapa Prubki")
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.setGeometry(0, 0, 1024, 720)
        self.resize(self.rozmiar[0],self.rozmiar[1])
        self.layout = QVBoxLayout()

        #map object
        self.map = Map(map, main_window)
        
        self.resize(self.height(), self.width())
        self.layout.addWidget(self.map, Qt.AlignCenter)
        self.setLayout(self.layout)

    #pass object to map object
    def new_image(self, img):
        self.map.new_image(img)
