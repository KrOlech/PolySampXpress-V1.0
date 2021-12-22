from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import cv2
from roi_create import ROI_maping
import Clasa as oC

class Map(ROI_maping):
    
    #skale umozliwiajace konwersje na poprawny rozmiar ROI
    skalx = (441/12670+440/12671+468/13692)/3
    skaly = (341/12750+338/12749+368/13520)/3

    # wartosci owsetu aktualnego podgloadu
    ofsety = -100#13682-17392#1271+16381#
    ofsetx = 105#12751-9801#13509-10559
    
    def __init__(self, img, main_window, ox, oy, *args, **kwargs):
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
        
        #self.ofsetx = -ox + int(self.rozmiar[0]+self.manipulator_max*self.delta_pixeli/2) #self.rozmiar[0]+
        #self.ofsety = -oy + int(self.rozmiar[1]+self.manipulator_max*self.delta_pixeli/2) #

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

    def rectaglecreate(self):
        '''
        Metoda tworzoca obiekt klasy ROI
        :return: obiekt klasy roi stworzony na podstawie zapisanych dancyh
        #ponisienie nr defaltowej nazwy
        '''
        self.main_window.last_name += 1

        ROI = oC.obszarzaznaczony(
                                self,
                                self.x1, self.y1,
                                self.x2, self.y2,
                                self.frame,
                                0,
                                0,
                                self.scall,
                                self.main_window.last_name,
                                self.skalx,self.skaly
                                )
        #zapisanei ROI dao tablicy
        self.main_window.add_ROI(ROI)
        return ROI

    def get_rectagle(self,prostokat):
        return prostokat.getrectangle_map(self.rozmiar, self.ofsetx, self.ofsety, self.skalx, self.skaly)

class Map_window(QWidget):

    # rozmiar obszaru
    rozmiar = (1024, 768)

    def __init__(self, map, main_window, ox, oy, *args, **kwargs):
        super(Map_window, self).__init__(*args, **kwargs)

        self.setWindowTitle("Mapa Próbki")
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        #ustawienie rozmiaru
        self.setGeometry(0, 0, 1024, 720)
        self.resize(self.rozmiar[0],self.rozmiar[1])

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
