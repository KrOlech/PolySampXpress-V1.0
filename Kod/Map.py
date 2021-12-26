from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import cv2
from roi_create import ROI_maping
import Clasa as oC

class Map(ROI_maping):

    
    def __init__(self, img, main_window, ox, oy, *args, **kwargs):
        super(Map, self).__init__(main_window, *args, **kwargs)
        
        self.skalx = 1/self.skala#(441/12670+440/12671+468/13692)/3
        self.skaly = 1/self.skala

        #skalowanei nowego obrazu
        self.image_opencv = img#cv2.resize(, self.rozmiar)

        #konwersja obrazu z openCV na Qimage
        self.img = QImage(img, img.shape[1], img.shape[0], img.strides[0], QImage.Format_RGB888)

        #QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.img = QPixmap.fromImage(self.img)

        #seting pixmap
        self.setPixmap(self.img)
        

    def new_image(self, img):
        '''
        Metoda przyjmujaca nowy obraz open CV konwertujaca go na Qimage i zaposujaca
        :param img: open CV image
        '''

        #skalowanie obrazu
        #self.image_opencv = cv2.resize(obraz, self.rozmiar)

        #konwersja obrazu na Qimage
        self.img = QImage(img, img.shape[1], img.shape[0], img.strides[0], QImage.Format_RGB888)

        #zapisanei obrazu
        self.img = QPixmap.fromImage(self.img)


class Map_window(QWidget):

    # rozmiar obszaru
    #rozmiar = (1024, 768)

    def __init__(self, map, main_window, ox, oy, *args, **kwargs):
        super(Map_window, self).__init__(*args, **kwargs)

        self.setWindowTitle("Mapa Próbki"+ str(map.shape))
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        #ustawienie rozmiaru
        #self.setGeometry(0, 0, 1024, 720)
        #self.resize(self.rozmiar[0],self.rozmiar[1])

        #stworzenie leyoutu
        self.layout = QVBoxLayout()

        #map object
        self.map = Map(map, main_window, ox, oy)

        #dodanie mapy do podglondu
        self.layout.addWidget(self.map, Qt.AlignCenter)

        #ustawienie layoputu
        self.setLayout(self.layout)

    def new_image(self, img):
        '''
        Mtoda przekzujaca nowa mape do ROI'u
        :param img: nowa mapa klasy openCV
        '''
        self.map.new_image(img)
