from PyQt5.QtWidgets import QWidget
from Title_bar.Bar import MyBar
from PyQt5.QtCore import Qt

class Dock_in(QWidget):

    def __init__(self, name, *args, **kwargs):
        super(Dock_in, self).__init__(*args, **kwargs)

        self.setWindowTitle(name)

        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        self.titleBar = MyBar(self)
        self.titleBar.maxClicked()

        self.titleBar.normalClicked()
        self.setContentsMargins(0, self.titleBar.height(), 0, 0)

        self.resize(640, self.titleBar.height() + 480)

        palette = self.palette()
        palette.setColor(palette.Window, Qt.black)
        palette.setColor(palette.WindowText, Qt.white)
        palette.setColor(palette.Background, Qt.black)
        self.setPalette(palette)


    def changeEvent(self, event):
        if event.type() == event.WindowStateChange:
            self.titleBar.windowStateChanged(self.windowState())

    def resizeEvent(self, event):
        self.titleBar.resize(self.width(), self.titleBar.height())

    def dock(self):
        pass


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

        #okno.setCentralWidget()

        w = Dock_in("Widget_testowy")
        w.show()

        # wykonanie aplikacji
        app.exec_()

    except Exception as e:
        # wypisanie bledu
        print(e)