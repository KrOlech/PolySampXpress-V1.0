import sys

from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QApplication, QStyle
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QToolButton, QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget, QTextEdit

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        self.titleBar = MyBar(self)
        self.setContentsMargins(0, self.titleBar.height(), 0, 0)

        self.resize(640, self.titleBar.height() + 480)

    def changeEvent(self, event):
        if event.type() == event.WindowStateChange:
            self.titleBar.windowStateChanged(self.windowState())

    def resizeEvent(self, event):
        self.titleBar.resize(self.width(), self.titleBar.height())


class MyBar(QWidget):

    clickPos = None

    colorNormal = 'palette(mid)'
    colorHover = 'palette(midlight)'

    def __init__(self, parent):
        super(MyBar, self).__init__(parent)
        self.setAutoFillBackground(True)

        self.setBackgroundRole(QPalette.Shadow)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.title = QLabel("Bar", self, alignment=Qt.AlignCenter)

        self.title.setForegroundRole(QPalette.Light)

        self.style = self.style()
        ref_size = self.fontMetrics().height()
        ref_size += self.style.pixelMetric(self.style.PM_ButtonMargin) * 2
        self.setMaximumHeight(ref_size + 2)


        self.btn_size = QSize(ref_size, ref_size)

        bt = QPushButton()
        bt.setFixedSize(self.btn_size)

        bt.setStyleSheet('''
                        QToolButton {{
                            background-color: {};
                        }}
                        QToolButton:hover {{
                            background-color: {}
                        }}
                    '''.format(self.colorNormal, self.colorHover))

        bt.setIcon(self.style.standardIcon(getattr(QStyle, "SP_DialogOkButton")))

        signal = getattr(self, 'dockClicked')
        bt.clicked.connect(signal)

        self.layout.addWidget(bt)

        #dodaje separacje przycisków
        self.layout.addStretch()

        [self._buton_create(target) for target in ('min', 'normal', 'max', 'close')]

        #self.normalButton.hide()

        self.updateTitle(parent.windowTitle())
        parent.windowTitleChanged.connect(self.updateTitle)


    def _buton_create(self, target):

        btn = QToolButton(self, focusPolicy=Qt.NoFocus)
        self.layout.addWidget(btn)
        btn.setFixedSize(self.btn_size)

        iconType = getattr(self.style,
                           'SP_TitleBar{}Button'.format(target.capitalize()))
        btn.setIcon(self.style.standardIcon(iconType))

        btn.setStyleSheet('''
                        QToolButton {{
                            background-color: {};
                        }}
                        QToolButton:hover {{
                            background-color: {}
                        }}
                    '''.format(self.colorNormal, self.colorHover))

        signal = getattr(self, target + 'Clicked')
        btn.clicked.connect(signal)

        setattr(self, target + 'Button', btn)

    def dockClicked(self):
        print("Docing")


    def updateTitle(self, title=None):
        if title is None:
            title = self.window().windowTitle()
        width = self.title.width()
        width -= self.style.pixelMetric(QStyle.PM_LayoutHorizontalSpacing) * 2
        self.title.setText(self.fontMetrics().elidedText(
            title, Qt.ElideRight, width))

    def windowStateChanged(self, state):
        self.normalButton.setVisible(state == Qt.WindowMaximized)
        self.maxButton.setVisible(state != Qt.WindowMaximized)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clickPos = event.windowPos().toPoint()

    def mouseMoveEvent(self, event):
        if self.clickPos is not None:
            self.window().move(event.globalPos() - self.clickPos)

    def mouseReleaseEvent(self, QMouseEvent):
        self.clickPos = None

    def closeClicked(self):
        self.window().close()

    def maxClicked(self):
        self.window().showMaximized()

    def normalClicked(self):
        self.window().showNormal()

    def minClicked(self):
        self.window().showMinimized()

    def resizeEvent(self, event):
        self.title.resize(self.minButton.x(), self.height())
        self.updateTitle()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    layout = QVBoxLayout(mw)
    widget = QTextEdit()
    layout.addWidget(widget)
    mw.show()
    mw.setWindowTitle('My custom window with a very, very long title')
    sys.exit(app.exec_())