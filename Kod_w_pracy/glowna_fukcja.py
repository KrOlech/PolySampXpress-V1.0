import sys
from PyQt5.QtWidgets import QApplication
from Main_window import Glowne_okno


def glowna():
    '''
    glowna funkcja programu tworzaca glowne okno programu oraz
    nawiazujaca polaczenie z manipulatorem i przerywajaca go
    w przypadku napotkania krytycznego bledu
    '''

    #stworzenie aplikacji
    app = QApplication(sys.argv)

    manipulaor_obiekt = None

    try:
        # stworzenie glownego okna programu
        okno = Glowne_okno()
        
        manipulaor_obiekt = okno.pobierz_manipulator()
        #wyswietlenie glownego okna
        okno.show()

        # wykonanie aplikacji
        app.exec_()

    except Exception as e:
        #wypisanie bledu
        print(e)
        
        if manipulaor_obiekt is not None:
            #przerwanie komunikacji z manipulatorem
            del manipulaor_obiekt

#wywolanie glownej funkcji programu
if __name__ == '__main__':
   
    glowna()

