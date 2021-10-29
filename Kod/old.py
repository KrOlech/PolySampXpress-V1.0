def mouseMoveEvent(self, e):  # działąnia podczas ruchu myszki

    if self.iloscklikniec == False:
        # odczyt pozycji myszki
        self.x2 = e.x()
        self.y2 = e.y()

        # konwersja pozycji myszki na stringi
        textx = f'{self.x2}'
        texty = f'{self.y2}'

        # zapis aktualnej pozycji myszki w celu wyswietlenia podglondu
        self.end = e.pos()

        self.whot_to_drow = 'previu_rectagle'

        self.update()