import sys, os, inspect
from ctypes import *
import math

MY_DIR = os.path.dirname(os.path.abspath(inspect.getframeinfo(inspect.currentframe())[0]))
HELPER_DIR = os.path.abspath(os.path.join(MY_DIR, '..', 'helpers'))
sys.path.append(HELPER_DIR)
import dhlog

class _API:
    is_init = False

    @staticmethod 
    def init(debug=False):
        if _API.is_init:
            return

        postfix = ''
        if debug:
            postfix = '-dbg'

        if sys.platform == 'win32':
            shlib = 'dhcore' + postfix + '.dll'
        elif sys.platform == 'linux':
            shlib = 'libdhcore' + postfix + '.so'

        # load library
        try:
            dhcorelib = cdll.LoadLibrary(shlib)
        except:
            dhlog.Log.warn(str(sys.exc_info()[1]))
            dhlog.Log.fatal('could not load dynamic library %s' % shlib)
            sys.exit(-1)

        dhlog.Log.msgline('module "%s" loaded' % shlib, dhlog.TERM_GREEN)
        
        # core.h
        _API.core_init = dhcorelib.core_init
        _API.core_init.restype = c_int
        _API.core_init.argtypes = [c_uint]

        _API.core_release = dhcorelib.core_release
        _API.core_release.argtypes = [c_int]

        # err.h
        _API.err_getstring = dhcorelib.err_getstring
        _API.err_getstring.restype = c_char_p

        # log.h
        _API.log_outputconsole = dhcorelib.log_outputconsole
        _API.log_outputconsole.restype = c_uint
        _API.log_outputconsole.argtypes = [c_int]

        _API.log_outputfile = dhcorelib.log_outputfile
        _API.log_outputfile.restype = c_uint
        _API.log_outputfile.argtypes = [c_int, c_char_p]

        _API.log_isfile = dhcorelib.log_isfile
        _API.log_isfile.restype = c_int

        _API.log_isconsole = dhcorelib.log_isconsole
        _API.log_isconsole.restype = c_int

        _API.log_print = dhcorelib.log_print
        _API.log_print.argtypes = [c_uint, c_char_p]

        # file-io.h
        _API.fio_addvdir = dhcorelib.fio_addvdir
        _API.fio_addvdir.restype = c_int
        _API.fio_addvdir.argtypes = [c_char_p, c_int]

        # vec-math.h
        _API.mat3_muls = dhcorelib.mat3_muls
        _API.mat3_muls.restype = POINTER(Matrix3)
        _API.mat3_muls.argtypes = [POINTER(Matrix3), POINTER(Matrix3), c_float]

        _API.mat3_set_roteuler = dhcorelib.mat3_set_roteuler
        _API.mat3_set_roteuler.restype = POINTER(Matrix3)
        _API.mat3_set_roteuler.argtypes = [POINTER(Matrix3), c_float, c_float, c_float]

        _API.quat_slerp = dhcorelib.quat_slerp
        _API.quat_slerp.restype = POINTER(Quat)
        _API.quat_slerp.argtypes = [POINTER(Quat), POINTER(Quat), POINTER(Quat), c_float]

        _API.quat_fromaxis = dhcorelib.quat_fromaxis
        _API.quat_fromaxis.restype = POINTER(Quat)
        _API.quat_fromaxis.argtypes = [POINTER(Quat), POINTER(Vec3), c_float]

        _API.quat_fromeuler = dhcorelib.quat_fromeuler
        _API.quat_fromeuler.restype = POINTER(Quat)
        _API.quat_fromeuler.argtypes = [POINTER(Quat), c_float, c_float, c_float]

        _API.quat_frommat3 = dhcorelib.quat_frommat3
        _API.quat_frommat3.restype = POINTER(Quat)
        _API.quat_frommat3.argtypes = [POINTER(Quat), POINTER(Matrix3)]

        _API.mat3_inv = dhcorelib.mat3_inv
        _API.mat3_inv.restype = POINTER(Matrix3)
        _API.mat3_inv.argtypes = [POINTER(Matrix3), POINTER(Matrix3)]

        _API.mat3_set_rotaxis = dhcorelib.mat3_set_rotaxis
        _API.mat3_set_rotaxis.restype = POINTER(Matrix3)
        _API.mat3_set_rotaxis.argtypes = [POINTER(Matrix3), POINTER(Vec3), c_float]

        _API.mat3_set_roteuler = dhcorelib.mat3_set_roteuler
        _API.mat3_set_roteuler.restype = POINTER(Matrix3)
        _API.mat3_set_roteuler.argtypes = [POINTER(Matrix3), c_float, c_float, c_float]

        _API.mat3_set_rotquat = dhcorelib.mat3_set_rotquat
        _API.mat3_set_rotquat.restype = POINTER(Matrix3)
        _API.mat3_set_rotquat.argtypes = [POINTER(Matrix3), POINTER(Quat)]

        _API.mat3_inv = dhcorelib.mat3_inv
        _API.mat3_inv.restype = POINTER(Matrix3)
        _API.mat3_inv.argtypes = [POINTER(Matrix3), POINTER(Matrix3)]

        _API.mat3_det = dhcorelib.mat3_det
        _API.mat3_det.restype = c_float
        _API.mat3_det.argtypes = [POINTER(Matrix3)]

        _API.is_init = True 

def IS_FAIL(r):
    if r <= 0:  return True
    else:       return False

INVALID_HANDLE = 0xffffffffffffffff
INVALID_INDEX = 0xffffffff

def to_cstr(s):
    return create_string_buffer(s.encode('ascii'))

class Errors:
    @staticmethod
    def last_error():
        r = _API.err_getstring()
        return r.decode()

class Log:
    class LogType:
        TEXT = 0
        ERROR = 1
        WARNING = 3,
        INFO = 3,
        LOAD = 4

    @staticmethod
    def set_console_output(enable):
        _API.log_outputconsole(c_int(enable))

    @staticmethod
    def set_file_output(logfile):
        if logfile != None:
            _API.log_outputfile(c_int(True), create_string_buffer(logfile.encode('ascii')))
        else:
            _API.log_outputfile(c_int(False), None)

    @staticmethod
    def msg(log_type, msg):
        _API.log_print(c_uint(log_type), create_string_buffer(msg.encode('ascii')))

class Core:
    class InitFlags():
        TRACE_MEM = (1<<0)
        CRASH_DUMP = (1<<1)
        LOGGER = (1<<2)
        ERRORS = (1<<3)
        JSON = (1<<4)
        FILE_IO = (1<<5)
        TIMER = (1<<6)
        ALL = 0xffffffff

    @staticmethod
    def init(flags = InitFlags.ALL):
        if IS_FAIL(_API.core_init(c_uint(flags))):
            raise Exception(_API.err_getstring()) 

    @staticmethod
    def release(report_leaks = True):
        _API.core_release(c_int(report_leaks))


class Vec3(Structure):
    _fields_ = [('x', c_float), ('y', c_float), ('z', c_float), ('w', c_float)]

    def __init__(self, _x = 0, _y = 0, _z = 0, _w = 1):
        self.x = _x
        self.y = _y
        self.z = _z
        self.w = 1

    def __add__(a, b):
        return Vec3(a.x + b.x, a.y + b.y, a.z + b.z)

    def __mul__(a, b):
        if type(b) is float or type(b) is int:
            return Vec3(a.x*b, a.y*b, a.z*b)
        elif type(b) is Matrix3:
            return Vec3(\
                 a.x*b.m11 + a.y*b.m21 + a.z*b.m31 + b.m41,
                 a.x*b.m12 + a.y*b.m22 + a.z*b.m32 + b.m42,
                 a.x*b.m13 + a.y*b.m23 + a.z*b.m33 + b.m43);

    def copy(self):
        return Vec3(self.x, self.y, self.z)

    def __div__(a, b):
        return Vec3(a.x/b, a.y/b, a.z/b)

    def __eq__(a, b):
        if a.x == b.x and a.y == b.y and a.z == b.z:
            return True
        else:
            return False

    def __sub__(a, b):
        return Vec3(a.x - b.x, a.y - b.y, a.z - b.z)

    def get_length(self):
        return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
    length = property(get_length)

    @staticmethod
    def dot(a, b):
        return a.x*b.x + a.y*b.y + a.z*b.z

    @staticmethod
    def normalize(v):
        scale = 1.0 / v.length
        return Vec3(v.x*scale, v.y*scale, v.z*scale)

    @staticmethod
    def cross(v1, v2):
        return Vec3(v1.y*v2.z - v1.z*v2.y, v1.z*v2.x - v1.x*v2.z, v1.x*v2.y - v1.y*v2.x)     

    @staticmethod
    def lerp(v1, v2, t):
        return Vec3(\
            v1.x + t*(v2.x - v1.x),
            v1.y + t*(v2.y - v1.y),
            v1.z + t*(v2.z - v1.z))

    def __str__(self):
        return 'Vec3: %f, %f, %f' % (self.x, self.y, self.z)

class Vec2(Structure):
    _fields_ = [('x', c_float), ('y', c_float)]

    def __init__(self, _x = 0, _y = 0):
        self.x = _x
        self.y = _y

    def copy(self):
        return Vec2(self.x, self.y)

    def __add__(a, b):
        return Vec2(a.x + b.x, a.y + b.y)

    def __sub__(a, b):
        return Vec2(a.x - b.x, a.y - b.y)

    def __mul__(a, b):
        return Vec2(a.x*b, a.y*b)

    def __div__(a, b):
        return Vec2(a.x/b, a.y/b)

    def __str__(self):
        return 'Vec2: %f, %f' % (self.x, self.y)    

class Vec2i(Structure):
    _fields_ = [('x', c_int), ('y', c_int)]

    def __init__(self, _x = 0, _y = 0):
        self.x = int(_x)
        self.y = int(_y)
    
    def copy(self):
        return Vec2i(self.x, self.y)

    def __add__(a, b):
        return Vec2(a.x + b.x, a.y + b.y)

    def __sub__(a, b):
        return Vec2(a.x - b.x, a.y - b.y)

    def __mul__(a, b):
        return Vec2(a.x*b, a.y*b)

    def __str__(self):
        return 'Vec2i: %d, %d' % (self.x, self.y)        

class Vec4(Structure):
    _fields_ = [('x', c_float), ('y', c_float), ('z', c_float), ('w', c_float)]

    def __init__(self, _x = 0, _y = 0, _z = 0, _w = 1):
        self.x = _x
        self.y = _y
        self.z = _z
        self.w = 1

    def copy(self):
        return Vec4(self.x, self.y, self.z, self.w)

    def __add__(a, b):
        return Vec4(a.x + b.x, a.y + b.y, a.z + b.z, a.w + b.w)

    def __sub__(a, b):
        return Vec4(a.x - b.x, a.y - b.y, a.z - b.z, a.w - b.w)

    def __mul__(a, b):
        return Vec4(a.x*b, a.y*b, a.z*b, a.w*b)

    def __div__(a, b):
        return Vec4(a.x/b, a.y/b, a.z/b, a.w/b)

    def __str__(self):
        return 'Vec4: %f, %f, %f, %f' % (self.x, self.y, self.z, self.w)


class Color(Structure):
    _fields_ = [('r', c_float), ('g', c_float), ('b', c_float), ('a', c_float)]

    def __init__(self, _r = 0, _g = 0, _b = 0, _a = 1):
        self.r = _r
        self.g = _g
        self.b = _b
        self.a = _a

    def copy(self):
        return Color(self.r, self.g, self.b, self.a)

    def __mul__(a, b):
        return Color(a.r*b, a.g*b, a.g*b, a.a)

    def __mul__(a, b):
        return Color(a.r*b.r, a.g*b.g, a.g*b.b, min(a.a, b.a))

    def __add__(a, b):
        return Color(a.r+b.r, a.g+b.g, a.b+b.b, max(a.a, b.a))

    @staticmethod
    def lerp(c1, c2, t):
        tinv = 1 - t
        return Color(
            c1.r*t + c2.r*tinv,
            c1.g*t + c2.g*tinv,
            c1.b*t + c2.b*tinv,
            c1.a*t + c2.a*tinv)

class Quat(Structure):
    _fields_ = [('x', c_float), ('y', c_float), ('z', c_float), ('w', c_float)]

    def __init__(self, _x = 0, _y = 0, _z = 0, _w = 1):
        self.x = _x
        self.y = _y
        self.z = _z
        self.w = _w

    def copy(self):
        return Color(self.x, self.y, self.z, self.w)

    def __mul__(q1, q2):
        return Quat(\
            q1.w*q2.x + q1.x*q2.w + q1.z*q2.y - q1.y*q2.z,
            q1.w*q2.y + q1.y*q2.w + q1.x*q2.z - q1.z*q2.x,
            q1.w*q2.z + q1.z*q2.w + q1.y*q2.x - q1.x*q2.y,
            q1.w*q2.w - q1.x*q2.x - q1.y*q2.y - q1.z*q2.z)

    def __eq__(q1, q2):
        if q1.x == q2.x and q1.y == q2.y and q1.z == q2.z and q1.w == q2.w:
            return True
        else:
            return False

    def from_axis(self, axis, angle):
        _API.quat_fromaxis(byref(self), byref(axis), c_float(angle))

    def from_euler(self, pitch, yaw, roll):
        _API.quat_fromeuler(byref(self), c_float(pitch), c_float(yaw), c_float(roll))

    def from_matrix3(self, mat):
        _API.quat_frommat3(byref(self), byref(mat))

    @staticmethod
    def inverse(q):
        return Quat(-q.x, -q.y, -q.z, q.w)

    @staticmethod
    def slerp(q1, q2, t):
        q = Quat()
        _API.quat_slerp(byref(q), byref(q1), byref(q2), c_float(t))
        return q

    def __str__(self):
        return 'Quat: %f %f %f %f' % (self.x, self.y, self.z, self.w)

class Matrix3(Structure):
    _fields_ = [\
        ('m11', c_float), ('m12', c_float), ('m13', c_float), ('m14', c_float),
        ('m21', c_float), ('m22', c_float), ('m23', c_float), ('m24', c_float),
        ('m31', c_float), ('m32', c_float), ('m33', c_float), ('m34', c_float),
        ('m41', c_float), ('m42', c_float), ('m43', c_float), ('m44', c_float)]

    def __init__(self, _m11 = 1, _m12 = 0, _m13 = 0, _m21 = 0, _m22 = 1, _m23 = 0, 
        _m31 = 0, _m32 = 0, _m33 = 1, _m41 = 0, _m42 = 0, _m43 = 0):
        self.m11 = _m11
        self.m12 = _m12
        self.m13 = _m13
        self.m21 = _m21
        self.m22 = _m22
        self.m23 = _m23
        self.m31 = _m31
        self.m32 = _m32
        self.m33 = _m33
        self.m41 = _m41
        self.m42 = _m42
        self.m43 = _m43

    def copy(self):
        return Matrix3(\
            self.m11, self.m12, self.m13,
            self.m21, self.m22, self.m23,
            self.m31, self.m32, self.m33,
            self.m41, self.m42, self.m43)

    def __mul__(a, b):
        if type(b) is float or type(b) is int:
            return Matrix3(\
                a.m11*b,   a.m21*b,   a.m31*b,   a.m41*b,
                a.m12*b,   a.m22*b,   a.m32*b,   a.m42*b,
                a.m13*b,   a.m23*b,   a.m33*b,   a.m43*b)
        else:
            return Matrix3(\
                a.m11*b.m11 + a.m12*b.m21 + a.m13*b.m31,
                a.m11*b.m12 + a.m12*b.m22 + a.m13*b.m32,
                a.m11*b.m13 + a.m12*b.m23 + a.m13*b.m33,
                a.m21*b.m11 + a.m22*b.m21 + a.m23*b.m31,
                a.m21*b.m12 + a.m22*b.m22 + a.m23*b.m32,
                a.m21*b.m13 + a.m22*b.m23 + a.m23*b.m33,
                a.m31*b.m11 + a.m32*b.m21 + a.m33*b.m31,
                a.m31*b.m12 + a.m32*b.m22 + a.m33*b.m32,
                a.m31*b.m13 + a.m32*b.m23 + a.m33*b.m33,
                a.m41*b.m11 + a.m42*b.m21 + a.m43*b.m31 + b.m41,
                a.m41*b.m12 + a.m42*b.m22 + a.m43*b.m32 + b.m42,
                a.m41*b.m13 + a.m42*b.m23 + a.m43*b.m33 + b.m43);

    def translate(self, x, y, z):
        self.m41 = x
        self.m42 = y
        self.m43 = z

    def translate(self, v):
        self.m41 = v.x
        self.m42 = v.y
        self.m43 = v.z

    def rotate_euler(self, pitch, yaw, roll):
        _API.mat3_set_roteuler(byref(self), c_float(pitch), c_float(yaw), c_float(roll))

    def rotate_quat(self, q):
        _API.mat3_set_rotquat(byref(self), byref(q))

    def rotate_axis(self, axis, angle):
        _API.mat3_set_rotaxis(byref(self), byref(axis), c_float(angle))

    def scale(self, sx, sy, sz):
        self.m11 = sx
        self.m22 = sy
        self.m33 = sz

    def __get_determinant(self):
        return _API.mat3_det(byref(self))
    determinant = property(__get_determinant)

    def __get_translation(self):
        return Vec3(self.m41, self.m42, self.m43)
    translation = property(__get_translation)

    @staticmethod
    def transpose(m):
        return Matrix3(\
            self.m11, self.m21, self.m31, 
            self.m12, self.m22, self.m32, 
            self.m13, self.m23, self.m33, 
            self.m14, self.m24, self.m34)

    @staticmethod
    def invert(m):
        r = Matrix3()
        _API.mat3_inv(byref(r), byref(m))
        return r

class Matrix4(Structure):
    _fields_ = [\
        ('m11', c_float), ('m12', c_float), ('m13', c_float), ('m14', c_float),
        ('m21', c_float), ('m22', c_float), ('m23', c_float), ('m24', c_float),
        ('m31', c_float), ('m32', c_float), ('m33', c_float), ('m34', c_float),
        ('m41', c_float), ('m42', c_float), ('m43', c_float), ('m44', c_float)]

    def __init__(self,
        _m11 = 1, _m12 = 0, _m13 = 0, _m14 = 0, 
        _m21 = 0, _m22 = 1, _m23 = 0, _m24 = 0, 
        _m31 = 0, _m32 = 0, _m33 = 1, _m34 = 0, 
        _m41 = 0, _m42 = 0, _m43 = 0, _m44 = 1):
        self.m11 = _m11
        self.m12 = _m12
        self.m13 = _m13
        self.m14 = _m14
        self.m21 = _m21
        self.m22 = _m22
        self.m23 = _m23
        self.m24 = _m24
        self.m31 = _m31
        self.m32 = _m32
        self.m33 = _m33
        self.m34 = _m34
        self.m41 = _m41
        self.m42 = _m42
        self.m43 = _m43
        self.m44 = _m44

    def copy(self):
        return Matrix4(\
            self.m11, self.m12, self.m13, self.m14,
            self.m21, self.m22, self.m23, self.m24,
            self.m31, self.m32, self.m33, self.m34,
            self.m41, self.m42, self.m43, self.m44)

class Math:
    PI = 3.14159265

    @staticmethod
    def to_rad(x):
        return x*Math.PI/180.0

    @staticmethod
    def to_deg(x):
        return 180.0*x/Math.PI

class FileIO:
    @staticmethod
    def add_virtual_path(path, monitor=False):
        path = os.path.abspath(os.path.expanduser(path))
        if not _API.fio_addvdir(to_cstr(path), c_int(monitor)):
            raise Exception(Errors.last_error())

class Variant(Structure):
    class VarType:
        BOOL = 1
        INT = 2
        UINT = 3
        FLOAT = 4
        FLOAT2 = 5
        FLOAT3 = 6
        FLOAT4 = 7
        INT2 = 8
        INT3 = 9
        INT4 = 10
        STRING = 11

    class _Value(Union):
        _fields_ = [\
            ('b', c_int),
            ('i', c_int),
            ('ui', c_uint),
            ('f', c_float),
            ('fv', c_float*4),
            ('iv', c_int*4),
            ('s', c_char*16)]

    _fields_ = [('type', c_uint), ('value', _Value)]


    def set_value(self, v):
        if type(v) is bool:
            self.type = Variant.VarType.BOOL
            self.value.b = int(v)
        elif type(v) is int:
            self.type = Variant.VarType.INT
            self.value.i = v
        elif type(v) is float:
            self.type = Variant.VarType.FLOAT
            self.value.f = v
        elif type(v) is Vec2:
            self.type = Variant.VarType.FLOAT2
            self.value.fv[0] = v.x
            self.value.fv[1] = v.y
        elif type(v) is Vec3:
            self.type = Variant.VarType.FLOAT3
            self.value.fv[0] = v.x
            self.value.fv[1] = v.y
            self.value.fv[2] = v.z
        elif type(v) is Vec2i:
            self.type = Variant.VarType.INT2
            self.value.iv[0] = v.x
            self.value.iv[1] = v.y
        elif (type(v) is Color) or (type(v) is Vec4):
            self.type = Variant.VarType.FLOAT4
            self.value.fv[0] = v.x
            self.value.fv[1] = v.y
            self.value.fv[2] = v.z
            self.value.fv[3] = v.w
        elif type(v) is str:
            self.type = Variant.VarType.STRING
            self.value.s = to_cstr(v)
        else:
            raise Exception('unknown type')        

    def get_value(self):
        if self.type == Variant.VarType.BOOL:
            return self.value.b
        elif self.type == Variant.VarType.INT:
            return self.value.i
        elif self.type == Variant.VarType.FLOAT:
            return self.value.f
        elif self.type == Variant.VarType.FLOAT2:
            return Vec2(self.value.fv[0], self.value.fv[1])
        elif self.type == Variant.VarType.FLOAT3:
            return Vec3(self.value.fv[0], self.value.fv[1], self.value.fv[2])
        elif self.type == Variant.VarType.INT2:
            return Vec2i(self.value.iv[0], self.value.iv[1])
        elif self.type == Variant.VarType.FLOAT4:
            return Vec4(self.value.fv[0], self.value.fv[1], self.value.fv[2], self.value.fv[3])
        elif self.type == Variant.VarType.STRING:
            return self.value.s
        else:
            raise Exception('unknown type')

_API.init(debug = ('--debug' in sys.argv))