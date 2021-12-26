import sys
from PyQt5.QtWidgets import QApplication
from engineclass import manipulator
import Main_window as M

def glowna():
    '''
    glówna fukcja programu tworzaca gluwne okno programu oraz
    nawiozujaca poloczenie z manipulatorem i przerywajaca go
    w przypadku napotkania krytycnego bledu
    '''

    #stworzenie aplikacji
    app = QApplication(sys.argv)

    # stworzenie obiektu manipulatora nawiozujocego poloczenie z manipulatorem
    manipulaor_obiekt = manipulator()

    try:
        # stworzenie glównego okna programu
        window = M.MainWindow(manipulaor_obiekt)

        #wyswietlenie glównego okna
        window.show()

        # zamkniecie aplikacji
        app.exec_()

    except Exception as e:
        #wypisanie bledu
        print(e)

        #przerwanie komunikacji z manipulatorem
        del manipulaor_obiekt

#wywołanie głównej fukcji programu
if __name__ == '__main__':
    glowna()

