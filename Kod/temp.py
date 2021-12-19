import sys
from time import sleep
from PyQt5.QtWidgets import QApplication

import Main_window as m



def main():
    app = QApplication(sys.argv) #stworzenie aplikacji
    
    window = m.MainWindow() #stworzenie okna
    window.show() #pokazanie okna

    app.exec_() #zamkniecie

if __name__ == '__main__':

    main()

