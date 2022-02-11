from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QRect

class Dock_in(QWidget):

    def __init__(self, width, height, *args, **kwargs):
        super(Dock_in, self).__init__(*args, **kwargs)


        self.setMaximumWidth(width)
        self.setMaximumHeight(height)

        self.setMinimumWidth(width)
        self.setMinimumHeight(height)





if __name__ == '__main__':

    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtWidgets import QMainWindow
    import sys
    # stworzenie aplikacji
    app = QApplication(sys.argv)

    try:
        # stworzenie glownego okna programu
        okno = QMainWindow()

        # wyswietlenie glownego okna
        okno.show()

        okno.setCentralWidget(Dock_in(100,100))

        # wykonanie aplikacji
        app.exec_()

    except Exception as e:
        # wypisanie bledu
        print(e)