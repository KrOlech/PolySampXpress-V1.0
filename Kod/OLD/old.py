def mouseMoveEvent(self, e):  # działąnia podczas ruchu myszki

    if self.iloscklikniec == False:
        # odczyt pozycji myszki
        self.x2 = e.x()
        self.y2 = e.y()

        # konwersja pozycji myszki na stringi
        textx = f'{self.x2}'
        texty = f'{self.y2}'

        # zapis aktualnej pozycji myszki w celu wyswietlenia podglondu
        self.koniec = e.pos()

        self.co_narysowac = 'previu_rectagle'

        self.update()

        def getrectangle_map(self, Rozmiar, px00, py00, s, s00=1):

            # konwersja niezaleznych wspułrzednych prubki na zalezne dla obecnego ofsetu.
            xp0 = int((self.x0) * s00 * s) - px00
            yp0 = int((self.y0) * s00 * s) - py00
            xp1 = int((self.x1) * s00 * s) - px00
            yp1 = int((self.y1) * s00 * s) - py00

            # sprawdzenie czy obszar nie wychodzi poza podglond
            if xp0 < 0:
                xp0 = 0

            if yp0 < 0:
                yp0 = 0

            if xp1 > Rozmiar[0]:
                xp1 = Rozmiar[0]

            if yp1 > Rozmiar[1]:
                yp1 = Rozmiar[1]

            poczatek = QPoint(xp0, yp0)
            koniec = QPoint(xp1, yp1)

            return QRect(poczatek, koniec)