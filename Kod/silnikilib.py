import ctypes
import engineclass as m

def load_drivers(filename='C848_DLL.dll'):
    return ctypes.CDLL(r'C:\Users\external\PycharmProjects\Inzynierka\silniki_sterowanie\C848_DLL.dll')


def conncect_to_controller(driver):
    '''
    connects to C848 controler using given driver
    return controller id or None if conection was not successful
    '''
    connect_fun = driver.C848_ConnectRS232
    connect_fun.argtypes = [ctypes.c_int, ctypes.c_long]
    controller_id = connect_fun(4, 57600)
    return controller_id if controller_id != -1 else None


def is_connected(controller_id):
    '''
    checks if connection to C848 was established
    return True if there connection a connection to controller with given controller_id, else returns false
    '''
    return bool(c848.C848_IsConnected(ctypes.c_int(controller_id)))


def close_connection(controller_id):
    '''
    closes connection to C848 controler with given controller_id
    '''
    c848.C848_CloseConnection(ctypes.c_int(controller_id))


def get_axes(axes = 'XYZ'):
    '''
    converts "xyz" string to "ABC" string needed to give axes to c848 controller
    #A = x
    #B = y
    #C = z
    '''
    axes_map = {'x': 'A', 'y': 'B', 'z': 'C'}
    abc_list = [axes_map[ax] for ax in list(axes.lower())]
    return ''.join(abc_list)


def get_szAxes(axes = 'XYZ'):
    '''
    Takes string defining axes as parameter (axes defined in XYZ string)
    return char pointer to string with axes, usually char *const szAxes parameter in c848 dll functions.
    '''
    axes_ABC = get_axes(axes)
    return ctypes.c_char_p(axes_ABC.encode('utf-8'))


def convert_id(controller_id):
    '''
    converts controller_id to c_int
    '''
    return ctypes.c_int(controller_id)


def create_bool_array(size = 1, values=0):
    '''
    takes size of array as parameter
    creates bool array of given size filled with true values
    returns c pointer to this array
    '''
    b = (ctypes.c_bool * size)(*[values] * size)
    return ctypes.cast(b, ctypes.POINTER(ctypes.c_bool))


def create_double_array(size=1, positions=None):
    '''
    takes size of array as parameter
    creates double array of given size filled with 25.0 values
    returns c pointer to this array
    '''
    if positions == None:
        positions = [25.0] * size

    arr = (ctypes.c_double * size)(*positions)
    return ctypes.cast(arr, ctypes.POINTER(ctypes.c_double))


def move_axes_to_abs(controller_id, axes='xyz', positions=[25.0, 25.0, 25.0]):
    '''
    moves axes to absolute positions given in parameter positions
    positions needs to be between 0 and 50,
    axes that should be moved are given in parameter axes
    '''
    if len(axes) != len(positions):
        print('number of axes and positions must be the same!')
        return None

    c_id = convert_id(controller_id)
    sz_axes = get_szAxes(axes)
    c_double_array = create_double_array(len(axes), positions)
    success = c848.C848_MOV(c_id, sz_axes, c_double_array)

    return bool(success)


# Niektóre funkcje dll dla C848 muszą wywoływać się na pojedyńczej osi na raz\
# Inaczej działają tylko na pierwszej podanej osi
# Jest to jakiś błąd

def check_reference_status(controller_id, axes='xyz'):
    '''
    function check if given axes have reference
    returns dictionary with axes as keys and boolean values
    '''
    c_id = convert_id(controller_id)
    status = {}
    for c in axes:
        axis = get_szAxes(c)
        bool_array = create_bool_array(size=1)
        check = c848.C848_IsReferenceOK(c_id, axis, bool_array)

        if check != 1:
            print('something went terribly wrong')
            return

        status[c] = bool_array[0]
    return status


def is_referencing(controller_id, axes):
    '''
    checks if any axis is referencing in the moment
    returns boolean value - True if any axis is in the middle of referencing
    '''
    c_id = convert_id(controller_id)
    status = {}
    for c in axes:
        axis = get_szAxes(c)
        bool_array = create_bool_array(size=1)
        check = c848.C848_IsReferencing(c_id, axis, bool_array)

        if check != 1:
            print('something went terribly wrong')
            return

        status[c] = bool_array[0]
    return any(status.values())


def reference_axes(controller_id, axes='xyz'):
    '''
    moves given axes to reference points and sets references
    '''
    c_id = convert_id(controller_id)
    sz_axes = get_szAxes(axes)
    success = c848.C848_REF(c_id, sz_axes)
    return bool(success)


def init_axes(controller_id, axes='xyz'):
    '''
    trzeba doczytac - kasuje refenrecje na pewno
    '''
    c_id = convert_id(controller_id)
    sz_axes = get_szAxes(axes)
    success = c848.C848_INI(c_id, sz_axes)
    return bool(success)


def emergency_stop(controller_id):
    '''
    emergency stop of movements for all axes
    '''
    c_id = convert_id(controller_id)
    return c848.C848_EmergencyStop(c_id)


def simple_stop(controller_id):
    '''
    stops movement of all axes
    '''
    c_id = convert_id(controller_id)
    return c848.C848_STP(c_id)


def check_on_target(controller_id, axes='xyz'):
    '''
    function check if given axes is on target
    returns dictionary with axes as keys and boolean values
    '''
    c_id = convert_id(controller_id)
    status = {}
    for c in axes:
        axis = get_szAxes(c)
        bool_array = create_bool_array(size=1)
        check = c848.C848_qONT(c_id, axis, bool_array)

        if check != 1:
            print('something went terribly wrong')
            return

        status[c] = bool_array[0]
    return status


def check_referencing_mode(controller_id, axes='xyz'):
    '''
    function check if given axes are in referencing mode
    returns dictionary with axes as keys and boolean values
    '''
    c_id = convert_id(controller_id)
    status = {}
    for c in axes:
        axis = get_szAxes(c)
        bool_array = create_bool_array(size=1)
        check = c848.C848_qRON(c_id, axis, bool_array)

        if check != 1:
            print('something went terribly wrong')
            return

        status[c] = bool_array[0]
    return status


def set_referencing_mode(controller_id, axes='xyz', on=True):
    '''
    function sets axes to referencing mode or turns it of
    '''
    c_id = convert_id(controller_id)
    for c in axes:
        axis = get_szAxes(c)
        bool_array = create_bool_array(size=1, values=on)
        check = c848.C848_RON(c_id, axis, bool_array)
    return bool(check)


def set_abs_positions(controller_id, axes='xyz', positions=None):
    '''
    set absolut positions for not referenced axes

    referencing mode has to be turned off (function set_referencing_mode)
    '''
    if positions == None:
        return None

    if len(axes) != len(positions):
        print('number of axes and positions must be the same!')
        return None

    c_id = convert_id(controller_id)
    sz_axes = get_szAxes(axes)
    c_double_array = create_double_array(len(axes), positions)
    success = c848.C848_POS(c_id, sz_axes, c_double_array)

    return bool(success)

def main():
    c848 = load_drivers()
    print(c848)

    controller_id = conncect_to_controller(c848)
    print('controller_id:', controller_id)
    print('is connected:', is_connected(controller_id))

    close_connection(controller_id)

    print('is connected:', is_connected(controller_id))

if __name__ == '__main__':

    t = m.manipulator()

    t.move_up()

    t.print_curent_position()

    del t



