from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QLineEdit, QVBoxLayout, QPushButton
from PyQt5.QtGui import QIcon, QIntValidator

class axissetingwindow(QWidget):
    '''
    Obiekt dziedziczacy z QWidget umozliwiakjacy konfiguracje parametrów przesylanych do manipulatora
    '''

    def __init__(self, gluwneokno, *args, **kwargs):
        super(axissetingwindow, self).__init__(*args, **kwargs)

        self.glowneokno = gluwneokno
        
        self.setWindowIcon(QIcon('icon.png'))
        self.setWindowTitle("Ustawienia osi")

        #krotka zawierajaca obcje i wyrane dla nich odpowiedzi
        self.options = ()

        self.leyout = QGridLayout()

        self._stwurz_opcje("Minimum slidera osi X", 0, 20)

        self._stwurz_opcje("maximum slidera osi X", 1, 30)

        self._stwurz_opcje("Krok dla y i z w 0.1 mm", 2, 10)
        
        self.przycisk = QPushButton("Zapisz i zastosuj ustawienia")
        self.przycisk.clicked.connect(self._zwruc_odpowiedzi)
        self.przyciskleyout = QVBoxLayout()
        
        self.przyciskleyout.addLayout(self.leyout)
        self.przyciskleyout.addWidget(self.przycisk)
        
        self.setLayout(self.przyciskleyout)
        
    
    def _zwruc_odpowiedzi(self):
        '''
        metoda wyolywana po nacisnieciu przycisku przekazujaca odpowiedzi do odpowiednich obiektow
        '''
        self.glowneokno.slide.ustaw_min_max(int(self.options[0].text()), int(self.options[1].text()))
        self.glowneokno.ustaw_krok(int(self.options[2].text()))
        self.hide()
    
    def _stwurz_opcje(self, tekst, pozycja, wartosc):
        '''
        Metoda tworzaca obcje w obiekcie
        :param tekst: tresc obcji
        :param pozycja: pozycja obcji
        :param wartosc: wartosc startowa
        '''
        self.leyout.addWidget(QLabel(tekst), pozycja, 0)
        
        self.options += (self._stwurz_lineedit(),)
        self.options[-1].setText(str(wartosc))
        self.leyout.addWidget(self.options[-1], pozycja, 1)

    def _stwurz_lineedit(self):
        '''
        metoda tworzaca pole edycji z kontrola wpisania jedynie intigerow
        :return: linedit z kontrola
        '''
        lineEdit = QLineEdit()
        validator = QIntValidator()
        lineEdit.setValidator(validator)
        
        return lineEdit
