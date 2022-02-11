from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QRect

class Dock_in(QWidget):

    def __init__(self,width, hight,*args, **kwargs):
        super(Dock_in, self).__init__(*args, **kwargs)


        self.setGeometry(QRect(width,hight))




if __name__ == '__main__':
    print("hwdp")