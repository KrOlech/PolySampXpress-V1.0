import ctypes
from time import sleep
from PyQt5.QtWidgets import QMessageBox
class manipulator:


    def __init__(self,main):

        self.main = main

        self.c848 = self.load_drivers()
        print(self.c848)

        self.conectioncheck()

        self.reference_axes()

        self.print_curent_position()

    def conect(self):
        self.controller_id = self.conncect_to_controller()
        return self.is_connected()

    def __del__(self):
        
        print('is connected:', self.is_connected())

        self.close_connection()

        print('is connected:', self.is_connected())

    def load_drivers(self, filename='C848_DLL.dll'):
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
        sz_axes = self._get_szAxes(axes)
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

    def _get_szAxes(self, axes='XYZ'):
        '''
        Takes string defining axes as parameter (axes defined in XYZ string)
        return char pointer to string with axes, usually char *const szAxes parameter in c848 dll functions.
        '''
        axes_ABC = self._get_axes(axes)
        return ctypes.c_char_p(axes_ABC.encode('utf-8'))

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

    #workinprogres
    def move_axes_to_abs_woe(self,axes='xyz', positions=[25.0, 25.0, 25.0]):

        if not self._move_axes_to_abs(axes, positions):
            QMessageBox.warning(self, '', "erore in move", QMessageBox.Ok)

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
        sz_axes = self._get_szAxes(axes)
        c_double_array = self._create_double_array(len(axes), positions)
        success = self.c848.C848_MOV(c_id, sz_axes, c_double_array)

        return bool(success)

    def get_axes_positions(self, axes='xyz'):
        '''
        function gives positions of given axes

        returns list of positions in order of given axes
        '''
        c_id = self._convert_id(self.controller_id)
        sz_axes = self._get_szAxes(axes)
        c_double_array = self._create_double_array(size=len(axes))
        if self.c848.C848_qPOS(c_id, sz_axes, c_double_array):
            return c_double_array[:len(axes)]
        else:
            #print('something went terribly wrong')
            return False

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
            axis = self._get_szAxes(c)
            bool_array = self._create_bool_array(size=1)
            check = self.c848.C848_qONT(c_id, axis, bool_array)
            
            if check != 1:
                QMessageBox.warning(self, '', 'something went terribly wrong', QMessageBox.Ok)
                return
            
            status[c] = bool_array[0]
        return status

    def weaith_for_target(self):
        while not all(self.check_on_target().values()):
            self.main.upadet_position_read()

    def move_up(self):
        t = self.move_axes_to_abs_woe('z',[self.z+1])
        self.weaith_for_target()
        return t
       
    def move_dwn(self):
        t = self.move_axes_to_abs_woe('z',[self.z-1])
        self.weaith_for_target()
        return t
        
    def move_right(self):
        t = self.move_axes_to_abs_woe('y',[self.y+1])
        self.weaith_for_target()
        return t

    def move_left(self):
        t = self.move_axes_to_abs_woe('y',[self.y-1])
        self.weaith_for_target()
        return t
