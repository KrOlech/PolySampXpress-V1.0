from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5 import QtGui
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from roi_create import oznacz_ROI

class Map(oznacz_ROI):

    def __init__(self, obraz, main_window, *args, **kwargs):
        super(Map, self).__init__(main_window, *args, **kwargs)
        #skalowanie nowego obrazu
        self.image_opencv = obraz

        #konwersja obrazu z openCV na Qimage
        self._obraz_z_klatki = QImage(obraz, obraz.shape[1], 
                                             obraz.shape[0], 
                                             obraz.strides[0],
                                             QImage.Format_RGB888)
        self._obraz_z_klatki = QPixmap.fromImage(self._obraz_z_klatki)

        #seting pixmap
        self.setPixmap(self._obraz_z_klatki)
        
    def new_image(self, img):
        '''
        Metoda przyjmujaca nowy obraz z open CV 
        konwertujaca go na Qimage i zapisujaca
        :param img: open CV obraz
        '''
        self._obraz_z_klatki = QImage(img, img.shape[1],img.shape[0],
                                img.strides[0], QImage.Format_RGB888)
        #zapisanie obrazu
        self._obraz_z_klatki = QPixmap.fromImage(self._obraz_z_klatki)

class Map_window(QWidget):

    def __init__(self, map, main_window, *args, **kwargs):
        super(Map_window, self).__init__(*args, **kwargs)
        self.setWindowTitle("Mapa Probki")
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        #stworzenie layoutu
        self.layout = QVBoxLayout()

        #map obiekt
        self.map = Map(map, main_window)

        #dodanie mapy do podgladu
        self.layout.addWidget(self.map, Qt.AlignCenter)

        #ustawienie layoutu
        self.setLayout(self.layout)

    def new_image(self, img):
        '''
        Mtoda przekzujaca nowa mape do ROI'u
        :param img: nowa mapa klasy openCV
        '''
        self.map.new_image(img)