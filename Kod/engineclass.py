import ctypes
from time import sleep,time
from PyQt5.QtWidgets import QMessageBox
class manipulator:


    def __init__(self,main):

        self.main = main

        self.c848 = self.load_drivers()
        print(self.c848)

        self.controller_id = self.connect()
        
        self.conectioncheck()
        
        try:
            self.set_abs_positions_from_file()
        except Exception:
            self.set_referencing_mode()
            self.get_axes_positions()
            self.reference_axes()
        
        self.print_curent_position()

        self.x, self.y, self.z = self.get_axes_positions('xyz')

    def connect(self):
        if not self.is_connected():
            return self.conncect_to_controller()
        return self.is_connected()


    def get_szaxes(self,axes = 'XYZ'):
        '''
        Takes string defining axes as parameter (axes defined in XYZ string)
        return char pointer to string with axes, usually char *const szAxes parameter in c848 dll functions.
        '''
        axes_abs = self._get_axes(axes)
        return ctypes.c_char_p(axes_abs.encode('utf-8'))

    def set_referencing_mode(self, axes='xyz', on=True):
        '''
        function sets axes to referencing mode or turns it of
        '''
        check = False
        c_id = self._convert_id(self.controller_id)
        for c in axes:
            axis = self.get_szaxes(c)
            bool_array = self._create_bool_array(size=1, values=on)
            check = self.c848.C848_RON(c_id, axis, bool_array)

        return bool(check)
        
    @staticmethod
    def read_positions():
        '''
        read positions of axes from a config file
        '''
        position_dict = {}
        with open('positions.txt', 'r') as file:
            for line in file:
                ax, position = line.split(':')
                position_dict[ax.strip()] = float(position.strip())
                
        return position_dict

    @staticmethod
    def split_axes_positions(position_dict):
        '''
        reads dictionary with posiotions and converts it to tuple with axes string and list of positions
        '''
        axes = []
        positions = []
        for ax, position in position_dict.items():
            axes.append(ax)
            positions.append(position)

        axes = ''.join(axes)
        return axes, positions
        
    def set_abs_positions_from_file(self):
        '''
        function turns off referencing mode and sets axes absolute positions read from conf file.
        '''
        self.set_referencing_mode(on=False)
        position_dict = self.read_positions()
       # print(position_dict)
        axes, positions = self.split_axes_positions(position_dict)
       # print(axes, positions)
        return self.set_abs_positions(axes=axes, positions=positions)    
        
    def save_positions(self):
        '''
        saves positions of axes in a config file
        '''
        axes = 'xyz'
        positions = self.get_axes_positions(axes)
        with open('positions.txt', 'w') as file:
            for ax, position in zip(axes, positions):
                file.write('{}: {}\n'.format(ax, position))


    def set_abs_positions(self, axes='xyz', positions = None):
        '''
        set absolut positions for not referenced axes
        
        referencing mode has to be turned off (function set_referencing_mode)
        '''
        if positions == None:
            return None
        
        if len(axes) != len(positions):
            print('number of axes and positions must be the same!')
            return None
        
        c_id = self._convert_id(self.controller_id)
        sz_axes = self.get_szaxes(axes)
        c_double_array = self._create_double_array(len(axes), positions)
        success = self.c848.C848_POS(c_id, sz_axes, c_double_array)
        
        return bool(success)
          
    def __del__(self):
        
        self.save_positions()
        
        print('is connected:', self.is_connected())

        self.close_connection()

        print('is connected:', self.is_connected())

    @staticmethod
    def load_drivers(filename='C848_DLL.dll'):
        return ctypes.CDLL(r'C:\Users\external\PycharmProjects\Inzynierka\silniki_sterowanie\C848_DLL.dll')

    #work in progres
    def conncect_to_controller(self):
        '''
        connects to C848 controler using given driver
        return controller id or None if conection was not successful
        '''

        connect_fun = self.c848.C848_ConnectRS232
        connect_fun.argtypes = [ctypes.c_int, ctypes.c_long]
        #conect_fun comport bitspeed
        controller_id = connect_fun(4, 57600)

        if controller_id != -1:
            print('controller_id:', controller_id)
            return controller_id

        else:
            QMessageBox.warning(self, '', "erore unable to conect", QMessageBox.Ok)
            return None

    #create erore mesage window if conection wos failed
    #work in progres
    def conectioncheck(self):

        if not self.is_connected():
            QMessageBox.warning(self, '', "erore conection feiled", QMessageBox.Ok)

    def is_connected(self):
        '''
        checks if connection to C848 was established
        return True if there connection a connection to controller with given controller_id, else returns false
        '''
        return bool(self.c848.C848_IsConnected(ctypes.c_int(self.controller_id)))

    def close_connection(self):
        '''
        closes connection to C848 controler with given controller_id
        '''
        self.c848.C848_CloseConnection(ctypes.c_int(self.controller_id))

    def reference_axes(self, axes='xyz'):  
        '''
        moves given axes to reference points and sets references
        '''
        c_id = self._convert_id(self.controller_id)
        sz_axes = self._get_szaxes(axes)
        success = self.c848.C848_REF(c_id, sz_axes)
        return bool(success)

    @staticmethod
    def _get_axes(axes='XYZ'):
        '''
        converts "xyz" string to "ABC" string needed to give axes to c848 controller
        #A = x
        #B = y
        #C = z
        '''
        axes_map = {'x': 'A', 'y': 'B', 'z': 'C'}
        abc_list = [axes_map[ax] for ax in list(axes.lower())]
        return ''.join(abc_list)

    def _get_szaxes(self, axes='XYZ'):
        '''
        Takes string defining axes as parameter (axes defined in XYZ string)
        return char pointer to string with axes, usually char *const szAxes parameter in c848 dll functions.
        '''
        axes_abc = self._get_axes(axes)
        return ctypes.c_char_p(axes_abc.encode('utf-8'))

    @staticmethod
    def _convert_id(controller_id):
        '''
        converts controller_id to c_int
        '''
        return ctypes.c_int(controller_id)

    @staticmethod
    def _create_bool_array(size=1, values=0):
        '''
        takes size of array as parameter
        creates bool array of given size filled with true values
        returns c pointer to this array
        '''
        b = (ctypes.c_bool * size)(*[values] * size)
        return ctypes.cast(b, ctypes.POINTER(ctypes.c_bool))

    @staticmethod
    def _create_double_array(size=1, positions=None):
        '''
        takes size of array as parameter
        creates double array of given size filled with 25.0 values
        returns c pointer to this array
        '''
        if positions == None:
            positions = [25.0] * size

        arr = (ctypes.c_double * size)(*positions)
        return ctypes.cast(arr, ctypes.POINTER(ctypes.c_double))

    #Metoda zadajaca przesuniecie zadanych osi na zadana pozycje
    def move_axes_to_abs_woe(self,axes='xyz', positions=[25.0, 25.0, 25.0]):
        return self._move_axes_to_abs(axes, positions)

    def _move_axes_to_abs(self, axes, positions):
        '''
        moves axes to absolute positions given in parameter positions
        positions needs to be between 0 and 50,
        axes that should be moved are given in parameter axes
        '''
        if len(axes) != len(positions):
            QMessageBox.warning(self, '', 'number of axes and positions must be the same!', QMessageBox.Ok)
            return None

        c_id = self._convert_id(self.controller_id)
        sz_axes = self._get_szaxes(axes)
        c_double_array = self._create_double_array(len(axes), positions)
        success = self.c848.C848_MOV(c_id, sz_axes, c_double_array)

        return bool(success)

    def get_axes_positions(self, axes='xyz'):
        '''
        function gives positions of given axes

        returns list of positions in order of given axes
        
        if manipulator in move returns False
        '''
        c_id = self._convert_id(self.controller_id)
        sz_axes = self._get_szaxes(axes)
        c_double_array = self._create_double_array(size=len(axes))
        if self.c848.C848_qPOS(c_id, sz_axes, c_double_array):
            return c_double_array[:len(axes)]
        else:
            #print('something went terribly wrong')
            return False

    #wypisanie aktualnych pozycji manipulatora
    def print_curent_position(self):   
        while not self.get_axes_positions('xyz'):
            sleep(1)
            
        self.x, self.y, self.z = self.get_axes_positions('xyz')
        print(self.x, self.y, self.z)

    def check_on_target(self, axes='xyz'):
        '''
        function check if given axes is on target
        returns dictionary with axes as keys and boolean values
        '''
        c_id = self._convert_id(self.controller_id)
        status = {}
        for c in axes:
            axis = self._get_szaxes(c)
            bool_array = self._create_bool_array(size=1)
            check = self.c848.C848_qONT(c_id, axis, bool_array)
            
            if check != 1:
                QMessageBox.warning(self, '', 'something went terribly wrong', QMessageBox.Ok)
                return
            
            status[c] = bool_array[0]
        return status

    #metoda oczekujca az zostanie osiognieta zadana pozycja. jednoczesnie updatujaca napisy na glównym oknie
    def weaith_for_target(self):
        while not all(self.check_on_target().values()):
            self.main._upadet_position_read()
            self.x, self.y, self.z = self.get_axes_positions('xyz')

  ########################metody odbierajace wysłąne poleca ruchu################
    def move_up(self,krok):
        self.z -= krok
        t = self.move_axes_to_abs_woe('z',[self.z])
        self.weaith_for_target()
        return t
       
    def move_dwn(self,krok):
        self.z+=krok
        t = self.move_axes_to_abs_woe('z',[self.z])
        self.weaith_for_target()
        return t
        
    def move_right(self,krok):
        self.y-=krok
        t = self.move_axes_to_abs_woe('y',[self.y])
        self.weaith_for_target()
        return t

    def move_left(self,krok):
        self.y+=krok
        t = self.move_axes_to_abs_woe('y',[self.y])
        self.weaith_for_target()
        return t

    def move_x(self,value):
        self.x = value
        t = self.move_axes_to_abs_woe('x',[self.x])
        self.weaith_for_target()
        return t

    def simple_stop(self):
        '''
        stops movement of all axes
        '''
        c_id = self._convert_id(self.controller_id)
        return self.c848.C848_STP(c_id)

    #metod alowing moving more than 1 axis at the time
    def move_axes_to_abs_woe_ofset(self,axes,tab):
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
            
        self.move_axes_to_abs_woe(axes,ntab)
        self.weaith_for_target()
