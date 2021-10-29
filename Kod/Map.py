from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import cv2

class Map_window(QWidget):

    def __init__(self,map,*args, **kwargs):
        super(Map_window, self).__init__(*args, **kwargs)

        #self.setGeometry(5, 30, 1920, 1080)

        self.setWindowTitle("Mapa Prubki")
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.layout = QVBoxLayout()

        self.map = Map(map)
        self.layout.addWidget(self.map, Qt.AlignCenter)

        self.setLayout(self.layout)


class Map(QLabel):

    def __init__(self, img, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)

        #img = cv2.resize(img, self.Rozmiar)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        self.img = QImage(img, img.shape[1],img.shape[0],img.strides[0],QImage.Format_RGB888)
        #QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.img = QPixmap.fromImage(self.img)

        self.setPixmap(self.img)


class squer:

    def __init__(self, py, px, ky, kx):

        self.px = px
        self.py = py
        self.kx = kx
        self.ky = ky

    def get_top_left(self):
        return self.px, self.py

    def get_top_right(self):
        return self.kx, self.py

    def get_botom_left(self):
        return self.px, self.ky

    def get_botom_right(self):
        return self.kx, self.ky

    def get_left(self):
        return self.px

    def get_right(self):
        return self.kx

    def get_top(self):
        return self.py

    def get_botom(self):
        return self.ky

    def get_all(self):
        return self.px, self.py, self.kx, self.ky

########################################################################################################################

    def set_left(self, new_left):
        self.px = new_left

    def set_right(self, new_righ):
        self.kx = new_righ

    def set_top(self, new_top):
        self.py = new_top

    def set_botom(self, new_botom):
        self.ky = new_botom

########################################################################################################################

    def is_in_check(self, x, y):

        temp = False

        if self.px < x < self.kx:
            temp = True

        if self.py < y < self.ky:
            return temp
        else:
            return False

    def extend(self, sqr):

        #print(self.get_all())

        #print(sqr.get_all())
        if self.get_right() == sqr.get_left() and sqr.get_top() == self.get_top() and sqr.get_botom() == self.get_botom():
            #print("tym1")
            self.set_right(sqr.get_right())
            return True

        elif self.get_left() == sqr.get_right():
            #print("tym2")
            self.set_left(sqr.get_left())
            return True

        elif self.get_top() == sqr.get_botom():
            #print("tym3")
            self.set_top(sqr.get_top())
            return True

        elif self.get_botom() == sqr.get_top():
            #print("tym4")
            self.set_botom(sqr.get_botom())
            return True

        else:
            return False


class shape:

    def __init__(self):

        self.squers = ()

    def cornercheck(self, x, y):
        return any([squer.is_in_check(x, y) for squer in self.squers])

    def marge_shape(self, sqr):
        return any([squer.extend(sqr) for squer in self.squers])

    def add_squer(self, sqr):

        if not self.marge_shape(sqr):
            self.squers += (sqr,)

        #print(self.squers)



