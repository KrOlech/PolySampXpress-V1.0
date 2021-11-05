import ctypes



class manipulator:


    def __init__(self):

        self.c848 = self.load_drivers()
        print(self.c848)

        self.controller_id = self.conncect_to_controller(self.c848)

        self.conectioncheck()


    def __del__(self):

        while self.is_connected():
            self.close_connection()

        print('is connected:', self.is_connected())\

    def load_drivers(self,filename='C848_DLL.dll'):
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

        if self.controller_id != -1:
            print('controller_id:', controller_id)
            return controller_id

        else:
            print("erore unable to conect")
            # eror mesege window and program close
            return None

    #create erore mesage window if conection wos failed
    #work in progres
    def conectioncheck(self):

        if not self.is_connected():
            #eror mesage window
            print("erore conection feiled")

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
            pass
            #eroremesage

    def _move_axes_to_abs(self, axes, positions):
        '''
        moves axes to absolute positions given in parameter positions
        positions needs to be between 0 and 50,
        axes that should be moved are given in parameter axes
        '''
        if len(axes) != len(positions):
            print('number of axes and positions must be the same!')
            return None

        c_id = self._convert_id(self.controller_id)
        sz_axes = self._get_szAxes(axes)
        c_double_array = self._create_double_array(len(axes), positions)
        success = self.c848.C848_MOV(c_id, sz_axes, c_double_array)

        return bool(success)