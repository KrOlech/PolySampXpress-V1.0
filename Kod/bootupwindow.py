from PyQt5.QtWidgets import QWidget
import PyQt5.QtGui as QtGui


class Loading_window(QWidget):



    def __init__(self,*args, **kwargs):
        super(Loading_window, self).__init__(*args, **kwargs)

        self.setWindowTitle("Mapowanie prubek")  # nazwa
        self.setWindowIcon(QtGui.QIcon('icon.png'))



