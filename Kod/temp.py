import sys

from PyQt5.QtWidgets import QApplication

import Main_window as m

import bootupwindow as bw


def main():
    app = QApplication(sys.argv) #stworzenie aplikacji

    loading = bw.Loading_window()
    loading.show()


    window = m.MainWindow() #stworzenie okna
    window.show() #pokazanie okna

    app.exec_() #zamkniecie

if __name__ == '__main__':

    main()

