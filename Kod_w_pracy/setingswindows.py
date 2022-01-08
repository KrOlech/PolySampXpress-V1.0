from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, \
QLineEdit, QVBoxLayout, QPushButton
from PyQt5.QtGui import QIcon, QIntValidator

class Okno_ustawien(QWidget):
    '''
    Obiekt dziedziczacy z QWidget umozliwiajacy
    konfiguracje parametrow przesylanych do manipulatora
    '''
    def __init__(self, glowne_okno, *args, **kwargs):
        super(Okno_ustawien, self).__init__(*args, **kwargs)
        self.glowne_okno = glowne_okno
        
        self.setWindowIcon(QIcon('icon.png'))
        self.setWindowTitle("Ustawienia osi")

        self.opcje = ()

        self.layout = QGridLayout()
        self._stworz_opcje("Minimum slidera osi X", 0, 20)
        self._stworz_opcje("maximum slidera osi X", 1, 30)
        self._stworz_opcje("Krok dla y i z w 0.1 mm", 2, 10)
        
        self.przycisk = QPushButton("Zapisz i zastosuj ustawienia")
        self.przycisk.clicked.connect(self._zwroc_odpowiedzi)
        self.przycisklayout = QVBoxLayout()
        
        self.przycisklayout.addLayout(self.layout)
        self.przycisklayout.addWidget(self.przycisk)
        self.setLayout(self.przycisklayout)
        
    def _zwroc_odpowiedzi(self):
        '''
        metoda przekazujaca odpowiedzi do odpowiednich obiektow
        '''
        self.glowne_okno.slide.ustaw_min_max(int(self.opcje[0].text()),
                                             int(self.opcje[1].text()))
        self.glowne_okno.ustaw_krok(int(self.opcje[2].text()))
        self.hide()
    
    def _stworz_opcje(self, tekst, pozycja, wartosc):
        '''
        :param tekst: tresc opcji
        :param pozycja: pozycja opcji
        :param wartosc: wartosc startowa
        '''
        self.layout.addWidget(QLabel(tekst), pozycja, 0)
        
        self.opcje += (self._stworz_lineedit(),)
        self.opcje[-1].setText(str(wartosc))
        self.layout.addWidget(self.opcje[-1], pozycja, 1)

    def _stworz_lineedit(self):
        '''
        metoda tworzaca pole edycji z kontrola wpisywania
        '''
        lineEdit = QLineEdit()
        validator = QIntValidator()
        lineEdit.setValidator(validator)
        return lineEdit