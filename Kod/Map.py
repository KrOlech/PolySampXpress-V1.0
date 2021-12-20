from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import cv2
from roi_create import ROI_maping


class Map(ROI_maping):
    
    #skale umozliwiajace konwersje na poprawny rozmiar ROI
    skaly = 1024/((50*510)+1024)
    skalx = 768/((50*510)+768)

    # wartosci owsetu aktualnego podgloadu
    #ofsety = 768*2
    #ofsetx = 1024

    #okreslenie flagi zeby wstempnie zabezpiczeyc zeby nie wykonac neiwłąsciwego przemiesczenia ROI
    move_to_point = False


    def __init__(self, img, main_window, *args, **kwargs):
        super(Map, self).__init__(main_window, *args, **kwargs)

        #skalowanei nowego obrazu
        self.image_opencv = cv2.resize(img, self.rozmiar)

        #zapisanie nowego obrazu
        img = self.image_opencv

        #ustawienie rozmiaru okna
        self.resize(self.rozmiar[0], self.rozmiar[1])

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
        self.image_opencv = cv2.resize(img, self.rozmiar)

        #konwersja obrazu na Qimage
        self.img = QImage(img, img.shape[1], img.shape[0], img.strides[0], QImage.Format_RGB888)

        #zapisanei obrazu
        self.img = QPixmap.fromImage(self.img)


class Map_window(QWidget):

    # rozmiar obszaru
    rozmiar = (1024, 768)

    def __init__(self, map, main_window, *args, **kwargs):
        super(Map_window, self).__init__(*args, **kwargs)

        self.setWindowTitle("Mapa Próbki")
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        #ustawienie rozmiaru
        self.setGeometry(0, 0, 1024, 720)
        self.resize(self.rozmiar[0],self.rozmiar[1])

        #stworzenie leyoutu
        self.layout = QVBoxLayout()

        #map object
        self.map = Map(map, main_window)

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
