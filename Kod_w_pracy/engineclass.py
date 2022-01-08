import ctypes
from time import sleep
from PyQt5.QtWidgets import QMessageBox


class manipulator:
    '''
    Klasa obslugujaca komunikacje z manipulatorem
    '''

    # wskaznik do glownego okna
    main = None


    def __init__(self):

        self.c848 = self.zaladuj_sterowniki()
        
        self.controller_id = self.podloczenie_kontroller()

        self.sprawdzenie_poloczenia()

        #proba odczytania pozycji z pliku
        try:
            self.ustaw_abs_positions_z_file()

        except Exception:
        # jesli nie uda sie odczytac pozycji wykonujemy centrowanie
            self.center()

        #odczytanie pozycji manipulatora i zapisanie go
        self.x, self.y, self.z = self.pobierz_pozycje_osi('xyz')
        
        self.wypisz_aktualna_pozycje_manipulatora()

    def __del__(self):
        
        try:
            self.zaopisz_pozycje()

            print('is connected:', self._sprawdz_poloczenie_prywatne())

            self.przerwij_poloczenie()

            print('is connected:', self._sprawdz_poloczenie_prywatne())
        
        except AttributeError as e:
            print(e)


    def glowne_okno(self, main):

        '''
        Metoda wykonywana po stworzeniu glowmnego okna
        przekazujaca je w celu komunikacji
        :param main: wskaznik do glownego okna
        '''

        self.main = main

    def center(self):

        '''
        Metoda wlaczajaca referecing mode i
        nastempnie centrujaca manipulator
        '''

        self.ustaw_referencing_mode()
        self.pobierz_pozycje_osi()
        self.reference_axes()
        self.poczekaj_na_osiagniecie_celu()
        
        #odczytanie pozycji manipulatora i zapisanie go
        self.x, self.y, self.z = self.pobierz_pozycje_osi('xyz')

    def _pobierz_skonwertowane_pozycje(self, osie='XYZ'):

        '''
        metoda konwertuje pozycje zadanych osi na
        tablice znakow zrozumiala przez manipulator
        :param osie: string zawierajacy nazwy osi
        :return: wskaznik do tablicy znakow
        '''

        axes_abs = self._conwert_axes(osie)
        return ctypes.c_char_p(axes_abs.encode('utf-8'))

    def ustaw_referencing_mode(self, osie='xyz', tryb=True):

        '''
        metoda wlacza lub wylacza mod referecyjny
        dla osi manipulatora
        :param osie: osie dla ktorych wlaczamy tryb referecji
        :param tryb: wartosc bitowa wlaczajaca 
        lub wylaczajaca mod
        :return: potwierdzenie powodzenia
        '''

        powodzenie = False
        c_id = self._convert_id(self.controller_id)
        for os_c in osie:
            os = self._pobierz_skonwertowane_pozycje(os_c)
            bool_array = self._stworz_tablice_booli(size=1, values=tryb)
            powodzenie = self.c848.C848_RON(c_id, os, bool_array)

        return bool(powodzenie)
        
    @staticmethod
    def odczyt_pozycji():
        '''
        statyczna metoda odczytujaca pozycje z pliku
        :return: slownik zawierajacy pozycje
        '''

        slownik_pozycji = {}
        with open('positions.txt', 'r') as file:
            for line in file:
                ax, position = line.split(':')
                slownik_pozycji[ax.strip()]=float(position.strip())
                
        return slownik_pozycji

    @staticmethod
    def split_axes_positions(position_dict):
        '''
        Statyczna metoda konwertujaca odczytany 
        slownik na dwie niezalezne tablice
        :param position_dict: slownik z osiami
        :return: tablica osi, tablica pozycji
        '''
        axes = []
        positions = []
        for ax, position in position_dict.items():
            axes.append(ax)
            positions.append(position)
            
        axes = ''.join(axes)
        return axes, positions
        
    def ustaw_abs_positions_z_file(self):
        '''
        metoda odczytuje pozycje z pliku,
        natempnie wylacza tryb referecyjny i
        ustawia ze manipulator znajduje sie
        na zadanych kordynatach
        :return: status czy udalo sie 
         ustawic odczytane pozycje czy nie
        '''

        self.ustaw_referencing_mode(tryb=False)
        position_dict = self.odczyt_pozycji()

        axes, positions = self.split_axes_positions(position_dict)

        return self.ustaw_absolutne_pozycje(axes=axes, 
                                            positions=positions)
        
    def zaopisz_pozycje(self):

        '''
        metoda zapisuje pozycje do pliku
        '''

        axes = 'xyz'
        positions = self.pobierz_pozycje_osi(axes)
        with open('positions.txt', 'w') as file:
            for ax, position in zip(axes, positions):
                file.write('{}: {}\n'.format(ax, position))

    def ustaw_absolutne_pozycje(self, axes='xyz', positions = None):
        '''
        Metoda wysyla do manipulatora zadane pozycje
        w celu przesuniecia manipulatora na nie
        :param axes:
        :param positions:
        :return: status czy sie udalo wykonac przemieszcenie
        '''

        #sprawdzenie czy zadano jakiekolwiek osie do przemieszczenia
        if positions == None:
            return None

        #sprawdzenie czy zadano odpowiednia ilosc osi i pozycji
        if len(axes) != len(positions):
            print('number of axes and positions must be the same!')
            return None

        # wykonanie przemieszczenia
        c_id = self._convert_id(self.controller_id)
        sz_axes = self._pobierz_skonwertowane_pozycje(axes)
        c_double_array = self._stworz_tablice_doubli(len(axes), positions)
        success = self.c848.C848_POS(c_id, sz_axes, c_double_array)
        
        return bool(success)

    @staticmethod
    def zaladuj_sterowniki(filename='C848_DLL.dll'):
    
        '''
        Statyczna metoda odczytujaca i ladujaca
        dynamiczna biblioteke do komunikacji z silnikiem
        :param filename: nazwa pliku biblioteki
        :return: status
        '''

        return ctypes.CDLL(r"C848_DLL.dll")

    def podloczenie_kontroller(self):
    
        '''
        podloczenie do kontrolera za pomoca zaladowanego
        sterownika
        return kontroler id albo
        None jesli nie udalo sie podloczyc
        '''

        connect_fun = self.c848.C848_ConnectRS232
        connect_fun.argtypes = [ctypes.c_int, ctypes.c_long]
        #conect_fun(port_szeregowy, predkosc bitow)
        controller_id = connect_fun(4, 57600)

        if controller_id != -1:
        
            return controller_id

        else:
        
            QMessageBox.warning(self.main, '',
                        "erore unable to conect", QMessageBox.Ok)
            return None

    def sprawdzenie_poloczenia(self):
    
        '''
        metoda sprawdzajaca stan poloczenia z kontrolerem
        jesli nie to wyskakuje okienko informuje o tym
        '''

        if not self._sprawdz_poloczenie_prywatne():
        
            QMessageBox.warning(self.main, '', 
                       "erore conection feiled", QMessageBox.Ok)

    def _sprawdz_poloczenie_prywatne(self):
        '''
        Prywatna metoda sprawdzajaca poloczenie
        :return: status poloczenia
        '''

        return bool(self.c848.C848_IsConnected(
                    ctypes.c_int(self.controller_id)))

    def przerwij_poloczenie(self):
        '''
        Przeywa poloczenie z kontrolerem silnikow
        :return:
        '''

        self.c848.C848_CloseConnection(ctypes.c_int(self.controller_id))

    def reference_axes(self, axes='xyz'):  
    
        '''
        Wykonuje ruch przkazanych osi do pkt referencyjnego
        :param axes:
        :return: status
        '''

        c_id = self._convert_id(self.controller_id)
        sz_axes = self._pobierz_skonwertowane_axes(axes)
        success = self.c848.C848_REF(c_id, sz_axes)
        return bool(success)

    @staticmethod
    def _conwert_axes(axes='XYZ'):
    
        '''
        konwertuje "xyz" string do "ABC"
        string zrozumialego dla kontrolera
        #A = x
        #B = y
        #C = z
        '''
        axes_map = {'x': 'A', 'y': 'B', 'z': 'C'}
        abc_list = [axes_map[ax] for ax in list(axes.lower())]
        return ''.join(abc_list)

    def _pobierz_skonwertowane_axes(self, axes='XYZ'):
        '''
        Przyjmuje osie w postaci stringu
        return wskaznik na tablice znakow zrozumiala przez kontroler
        '''

        axes_abc = self._conwert_axes(axes)
        return ctypes.c_char_p(axes_abc.encode('utf-8'))

    @staticmethod
    def _convert_id(controller_id):
        '''
        converts controller_id to c_int
        '''

        return ctypes.c_int(controller_id)

    @staticmethod
    def _stworz_tablice_booli(size=1, values=0):
    
        '''
        tworzy tablice boleanow o zadanej wielkosci
        i zwraca cpointer do niej
        '''

        b = (ctypes.c_bool * size)(*[values] * size)
        return ctypes.cast(b, ctypes.POINTER(ctypes.c_bool))

    @staticmethod
    def _stworz_tablice_doubli(size=1, positions=None):
    
        '''
        tworzy tablice doubli o zadanej wielkosci
        i zwraca cpointer do niej
        '''

        if positions == None:
            positions = [25.0] * size

        arr = (ctypes.c_double * size)(*positions)
        return ctypes.cast(arr, ctypes.POINTER(ctypes.c_double))

    def przsun_manipulator_do_zadanej_pozycji(self, axes='xyz',
           positions=[25.0, 25.0, 25.0]):
           
        '''
        Metoda zadajaca przesuniecie zadanych osi na zadana pozycje
        :param axes: znak osi
        :param positions: pozycje dla odpowiednich osi
        :return: status powodzenia
        '''

        return self._przsun_manipulator(axes, positions)

    def _przsun_manipulator(self,axes='xyz',positions=[25.0,25.0,25.0]):
    
        '''
        prywatnan metoda zadajaca przesuniecie
        zadanych osi na zadana pozycje
        :param axes: znak osi
        :param positions: pozycje dla odpowiednich osi
        :return: status powodzenia
        '''

        if len(axes) != len(positions):
            QMessageBox.warning(self.main, '', 
            'number of axes and positions must be the same!',
            QMessageBox.Ok)
            return None

        c_id = self._convert_id(self.controller_id)
        sz_axes = self._pobierz_skonwertowane_axes(axes)
        c_double_array = self._stworz_tablice_doubli(len(axes), positions)
        success = self.c848.C848_MOV(c_id, sz_axes, c_double_array)
        
        return bool(success)


    def pobierz_pozycje_osi(self, axes='xyz'):
        '''
        Metoda zwraca pozycje manipulatora
        '''
        c_id = self._convert_id(self.controller_id)
        sz_axes = self._pobierz_skonwertowane_axes(axes)
        c_double_array = self._stworz_tablice_doubli(size=len(axes))

        if self.c848.C848_qPOS(c_id, sz_axes, c_double_array):
            return c_double_array[:len(axes)]
        else:
            print('something went wrong while reading position')
            return False

    def wypisz_aktualna_pozycje_manipulatora(self):
        '''
        metoda czeka az manipulator przestanie sie poruszac
        po osiongnieciu pozycji wypisze pozycje
        :return:
        '''

        while not self.pobierz_pozycje_osi('xyz'):
            sleep(1)
            
        self.x, self.y, self.z = self.pobierz_pozycje_osi('xyz')
        print(self.x, self.y, self.z)

    def sprawdz_czy_u_celu(self, axes='xyz'):
        '''
        metoda sprawdza czy manipulator osiagnal zadana pozycje
        '''

        c_id = self._convert_id(self.controller_id)
        status = {}
        for c in axes:
            axis = self._pobierz_skonwertowane_axes(c)
            bool_array = self._stworz_tablice_booli(size=1)
            check = self.c848.C848_qONT(c_id, axis, bool_array)
            
            if check != 1:
                return {'':False}
            
            status[c] = bool_array[0]
        return status

    def poczekaj_na_osiagniecie_celu(self):
        '''
        metoda oczekujca az zostanie osiagnieta zadana pozycja.
        Jednoczesnie updatujaca napisy na glownym oknie
        '''

        while not all(self.sprawdz_czy_u_celu().values()):
            pass
            
        self.x, self.y, self.z = self.pobierz_pozycje_osi('xyz')

        if not self.main is None:
        
            self.main._upadet_position_read()


#################metody odbierajace wyslane poleca ruchu############

    def przesun_w_gore(self, krok):
        '''
        metoda przsuwajaca pozycje manipulatora o zadany krok
        i oczekujaca az zostanie osiagniety cel
        :param krok:
        :return: powodzenie przesuniecia
        '''

        self.z -= krok
        t = self.przsun_manipulator_do_zadanej_pozycji('z', [self.z])
        self.poczekaj_na_osiagniecie_celu()
        return t
       
    def przesun_w_dol(self, krok):
        '''
        metoda przsuwajaca pozycje manipulatora o zadany krok
        i oczekujaca az zostanie osiagniety cel
        :param krok:
        :return: powodzenie przesuniecia
        '''

        self.z+=krok
        t = self.przsun_manipulator_do_zadanej_pozycji('z', [self.z])

        self.poczekaj_na_osiagniecie_celu()
        
        return t
        
    def przesun_w_prawo(self, krok):
        '''
        metoda przsuwajaca pozycje manipulatora o zadany krok 
        i oczekujaca az zostanie osiagniety cel
        :param krok:
        :return: powodzenie przesuniecia
        '''

        self.y-=krok
        t = self.przsun_manipulator_do_zadanej_pozycji('y', [self.y])

        self.poczekaj_na_osiagniecie_celu()
        
        return t

    def przesun_w_lewo(self, krok):
        '''
        metoda przsuwajaca pozycje manipulatora o zadany krok
        i oczekujaca az zostanie osiagniety cel
        :param krok:
        :return: powodzenie przesuniecia
        '''

        self.y+=krok
        t = self.przsun_manipulator_do_zadanej_pozycji('y', [self.y])

        self.poczekaj_na_osiagniecie_celu()
        
        return t


    def przesun_x(self, wartosc):
        '''
        przesuwa os x na zadana wartosc
        :param wartosc:
        :return: status
        '''

        self.x = wartosc
        t = self.przsun_manipulator_do_zadanej_pozycji('x', [self.x])
        self.poczekaj_na_osiagniecie_celu()
        return t

    def simple_stop(self):
        '''
        zatrzymuje ruch manipulatora
        '''

        c_id = self._convert_id(self.controller_id)
        return self.c848.C848_STP(c_id)

    def move_axes_to_abs_woe_ofset(self, axes, tab):
        '''
        metoda umozliwiajaca przesuniecie wiecej niz 1 osi na raz
        umozliwai implementacje centrowania na zadanym pkcie
        :param axes: osie ktore przesuwamy
        :param tab: tablica wartosci o ktore przesuwamy manipulator
        '''

        ntab = []
        for a,v in zip(axes,tab):
            if a == 'x':
                self.x -= v
                ntab.append(self.x)
            if a == 'y':
                self.y -= v
                ntab.append(self.y)
            if a == 'z':
                self.z-=v
                ntab.append(self.z)

        self.przsun_manipulator_do_zadanej_pozycji(axes, ntab)
        self.poczekaj_na_osiagniecie_celu()
