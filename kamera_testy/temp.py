import sys
from PyQt5.QtWidgets import QApplication
import okno as oko


app = QApplication(sys.argv) #stworzenie aplikacji

window = oko.MainWindow() #stworzenie okna
window.show() #pokazanie okna

app.exec_() #zamkniecie
