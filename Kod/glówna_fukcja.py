import sys
from PyQt5.QtWidgets import QApplication
import Main_window as M


def glowna():
    '''
    glówna fukcja programu tworzaca gluwne okno programu oraz
    nawiozujaca poloczenie z manipulatorem i przerywajaca go
    w przypadku napotkania krytycnego bledu
    '''

    #stworzenie aplikacji
    app = QApplication(sys.argv)

    manipulaor_obiekt = None

    try:
        # stworzenie glównego okna programu
        window = M.MainWindow()
        
        manipulaor_obiekt = window.pobierz_manipulator()
        #wyswietlenie glównego okna
        window.show()

        # zamkniecie aplikacji
        app.exec_()

    except Exception as e:
        #wypisanie bledu
        print(e)
        
        if manipulaor_obiekt is not None:
            #przerwanie komunikacji z manipulatorem
            del manipulaor_obiekt

#wywołanie głównej fukcji programu
if __name__ == '__main__':
   
    glowna()

