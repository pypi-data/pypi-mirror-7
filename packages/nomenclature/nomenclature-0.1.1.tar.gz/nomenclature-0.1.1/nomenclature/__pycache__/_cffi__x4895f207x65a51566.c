
#include <Python.h>
#include <stddef.h>

#ifdef MS_WIN32
#include <malloc.h>   /* for alloca() */
typedef __int8 int8_t;
typedef __int16 int16_t;
typedef __int32 int32_t;
typedef __int64 int64_t;
typedef unsigned __int8 uint8_t;
typedef unsigned __int16 uint16_t;
typedef unsigned __int32 uint32_t;
typedef unsigned __int64 uint64_t;
typedef unsigned char _Bool;
#endif

#if PY_MAJOR_VERSION < 3
# undef PyCapsule_CheckExact
# undef PyCapsule_GetPointer
# define PyCapsule_CheckExact(capsule) (PyCObject_Check(capsule))
# define PyCapsule_GetPointer(capsule, name) \
    (PyCObject_AsVoidPtr(capsule))
#endif

#if PY_MAJOR_VERSION >= 3
# define PyInt_FromLong PyLong_FromLong
#endif

#define _cffi_from_c_double PyFloat_FromDouble
#define _cffi_from_c_float PyFloat_FromDouble
#define _cffi_from_c_long PyInt_FromLong
#define _cffi_from_c_ulong PyLong_FromUnsignedLong
#define _cffi_from_c_longlong PyLong_FromLongLong
#define _cffi_from_c_ulonglong PyLong_FromUnsignedLongLong

#define _cffi_to_c_double PyFloat_AsDouble
#define _cffi_to_c_float PyFloat_AsDouble

#define _cffi_from_c_int(x, type)                                        \
    (((type)-1) > 0 ?   /* unsigned */                                   \
        (sizeof(type) < sizeof(long) ? PyInt_FromLong(x) :               \
         sizeof(type) == sizeof(long) ? PyLong_FromUnsignedLong(x) :     \
                                        PyLong_FromUnsignedLongLong(x))  \
      : (sizeof(type) <= sizeof(long) ? PyInt_FromLong(x) :              \
                                        PyLong_FromLongLong(x)))

#define _cffi_to_c_int(o, type)                                          \
    (sizeof(type) == 1 ? (((type)-1) > 0 ? _cffi_to_c_u8(o)              \
                                         : _cffi_to_c_i8(o)) :           \
     sizeof(type) == 2 ? (((type)-1) > 0 ? _cffi_to_c_u16(o)             \
                                         : _cffi_to_c_i16(o)) :          \
     sizeof(type) == 4 ? (((type)-1) > 0 ? _cffi_to_c_u32(o)             \
                                         : _cffi_to_c_i32(o)) :          \
     sizeof(type) == 8 ? (((type)-1) > 0 ? _cffi_to_c_u64(o)             \
                                         : _cffi_to_c_i64(o)) :          \
     (Py_FatalError("unsupported size for type " #type), 0))

#define _cffi_to_c_i8                                                    \
                 ((int(*)(PyObject *))_cffi_exports[1])
#define _cffi_to_c_u8                                                    \
                 ((int(*)(PyObject *))_cffi_exports[2])
#define _cffi_to_c_i16                                                   \
                 ((int(*)(PyObject *))_cffi_exports[3])
#define _cffi_to_c_u16                                                   \
                 ((int(*)(PyObject *))_cffi_exports[4])
#define _cffi_to_c_i32                                                   \
                 ((int(*)(PyObject *))_cffi_exports[5])
#define _cffi_to_c_u32                                                   \
                 ((unsigned int(*)(PyObject *))_cffi_exports[6])
#define _cffi_to_c_i64                                                   \
                 ((long long(*)(PyObject *))_cffi_exports[7])
#define _cffi_to_c_u64                                                   \
                 ((unsigned long long(*)(PyObject *))_cffi_exports[8])
#define _cffi_to_c_char                                                  \
                 ((int(*)(PyObject *))_cffi_exports[9])
#define _cffi_from_c_pointer                                             \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[10])
#define _cffi_to_c_pointer                                               \
    ((char *(*)(PyObject *, CTypeDescrObject *))_cffi_exports[11])
#define _cffi_get_struct_layout                                          \
    ((PyObject *(*)(Py_ssize_t[]))_cffi_exports[12])
#define _cffi_restore_errno                                              \
    ((void(*)(void))_cffi_exports[13])
#define _cffi_save_errno                                                 \
    ((void(*)(void))_cffi_exports[14])
#define _cffi_from_c_char                                                \
    ((PyObject *(*)(char))_cffi_exports[15])
#define _cffi_from_c_deref                                               \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[16])
#define _cffi_to_c                                                       \
    ((int(*)(char *, CTypeDescrObject *, PyObject *))_cffi_exports[17])
#define _cffi_from_c_struct                                              \
    ((PyObject *(*)(char *, CTypeDescrObject *))_cffi_exports[18])
#define _cffi_to_c_wchar_t                                               \
    ((wchar_t(*)(PyObject *))_cffi_exports[19])
#define _cffi_from_c_wchar_t                                             \
    ((PyObject *(*)(wchar_t))_cffi_exports[20])
#define _cffi_to_c_long_double                                           \
    ((long double(*)(PyObject *))_cffi_exports[21])
#define _cffi_to_c__Bool                                                 \
    ((_Bool(*)(PyObject *))_cffi_exports[22])
#define _cffi_prepare_pointer_call_argument                              \
    ((Py_ssize_t(*)(CTypeDescrObject *, PyObject *, char **))_cffi_exports[23])
#define _cffi_convert_array_from_object                                  \
    ((int(*)(char *, CTypeDescrObject *, PyObject *))_cffi_exports[24])
#define _CFFI_NUM_EXPORTS 25

typedef struct _ctypedescr CTypeDescrObject;

static void *_cffi_exports[_CFFI_NUM_EXPORTS];
static PyObject *_cffi_types, *_cffi_VerificationError;

static int _cffi_setup_custom(PyObject *lib);   /* forward */

static PyObject *_cffi_setup(PyObject *self, PyObject *args)
{
    PyObject *library;
    int was_alive = (_cffi_types != NULL);
    if (!PyArg_ParseTuple(args, "OOO", &_cffi_types, &_cffi_VerificationError,
                                       &library))
        return NULL;
    Py_INCREF(_cffi_types);
    Py_INCREF(_cffi_VerificationError);
    if (_cffi_setup_custom(library) < 0)
        return NULL;
    return PyBool_FromLong(was_alive);
}

static void _cffi_init(void)
{
    PyObject *module = PyImport_ImportModule("_cffi_backend");
    PyObject *c_api_object;

    if (module == NULL)
        return;

    c_api_object = PyObject_GetAttrString(module, "_C_API");
    if (c_api_object == NULL)
        return;
    if (!PyCapsule_CheckExact(c_api_object)) {
        Py_DECREF(c_api_object);
        PyErr_SetNone(PyExc_ImportError);
        return;
    }
    memcpy(_cffi_exports, PyCapsule_GetPointer(c_api_object, "cffi"),
           _CFFI_NUM_EXPORTS * sizeof(void *));
    Py_DECREF(c_api_object);
}

#define _cffi_type(num) ((CTypeDescrObject *)PyList_GET_ITEM(_cffi_types, num))

/**********/


#include <sched.h>


static int _cffi_const_CLONE_FILES(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (CLONE_FILES) && (CLONE_FILES) <= LONG_MAX)
    o = PyInt_FromLong((long)(CLONE_FILES));
  else if ((CLONE_FILES) <= 0)
    o = PyLong_FromLongLong((long long)(CLONE_FILES));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(CLONE_FILES));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CLONE_FILES", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return 0;
}

static int _cffi_const_CLONE_FS(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (CLONE_FS) && (CLONE_FS) <= LONG_MAX)
    o = PyInt_FromLong((long)(CLONE_FS));
  else if ((CLONE_FS) <= 0)
    o = PyLong_FromLongLong((long long)(CLONE_FS));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(CLONE_FS));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CLONE_FS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CLONE_FILES(lib);
}

static int _cffi_const_CLONE_NEWIPC(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (CLONE_NEWIPC) && (CLONE_NEWIPC) <= LONG_MAX)
    o = PyInt_FromLong((long)(CLONE_NEWIPC));
  else if ((CLONE_NEWIPC) <= 0)
    o = PyLong_FromLongLong((long long)(CLONE_NEWIPC));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(CLONE_NEWIPC));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CLONE_NEWIPC", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CLONE_FS(lib);
}

static int _cffi_const_CLONE_NEWNET(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (CLONE_NEWNET) && (CLONE_NEWNET) <= LONG_MAX)
    o = PyInt_FromLong((long)(CLONE_NEWNET));
  else if ((CLONE_NEWNET) <= 0)
    o = PyLong_FromLongLong((long long)(CLONE_NEWNET));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(CLONE_NEWNET));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CLONE_NEWNET", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CLONE_NEWIPC(lib);
}

static int _cffi_const_CLONE_NEWNS(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (CLONE_NEWNS) && (CLONE_NEWNS) <= LONG_MAX)
    o = PyInt_FromLong((long)(CLONE_NEWNS));
  else if ((CLONE_NEWNS) <= 0)
    o = PyLong_FromLongLong((long long)(CLONE_NEWNS));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(CLONE_NEWNS));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CLONE_NEWNS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CLONE_NEWNET(lib);
}

static int _cffi_const_CLONE_NEWUTS(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (CLONE_NEWUTS) && (CLONE_NEWUTS) <= LONG_MAX)
    o = PyInt_FromLong((long)(CLONE_NEWUTS));
  else if ((CLONE_NEWUTS) <= 0)
    o = PyLong_FromLongLong((long long)(CLONE_NEWUTS));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(CLONE_NEWUTS));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CLONE_NEWUTS", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CLONE_NEWNS(lib);
}

static int _cffi_const_CLONE_SYSVSEM(PyObject *lib)
{
  PyObject *o;
  int res;
  if (LONG_MIN <= (CLONE_SYSVSEM) && (CLONE_SYSVSEM) <= LONG_MAX)
    o = PyInt_FromLong((long)(CLONE_SYSVSEM));
  else if ((CLONE_SYSVSEM) <= 0)
    o = PyLong_FromLongLong((long long)(CLONE_SYSVSEM));
  else
    o = PyLong_FromUnsignedLongLong((unsigned long long)(CLONE_SYSVSEM));
  if (o == NULL)
    return -1;
  res = PyObject_SetAttrString(lib, "CLONE_SYSVSEM", o);
  Py_DECREF(o);
  if (res < 0)
    return -1;
  return _cffi_const_CLONE_NEWUTS(lib);
}

static PyObject *
_cffi_f_setns(PyObject *self, PyObject *args)
{
  int x0;
  int x1;
  int result;
  PyObject *arg0;
  PyObject *arg1;

  if (!PyArg_ParseTuple(args, "OO:setns", &arg0, &arg1))
    return NULL;

  x0 = _cffi_to_c_int(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  x1 = _cffi_to_c_int(arg1, int);
  if (x1 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = setns(x0, x1); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}

static PyObject *
_cffi_f_unshare(PyObject *self, PyObject *arg0)
{
  int x0;
  int result;

  x0 = _cffi_to_c_int(arg0, int);
  if (x0 == (int)-1 && PyErr_Occurred())
    return NULL;

  Py_BEGIN_ALLOW_THREADS
  _cffi_restore_errno();
  { result = unshare(x0); }
  _cffi_save_errno();
  Py_END_ALLOW_THREADS

  return _cffi_from_c_int(result, int);
}

static int _cffi_setup_custom(PyObject *lib)
{
  return _cffi_const_CLONE_SYSVSEM(lib);
}

static PyMethodDef _cffi_methods[] = {
  {"setns", _cffi_f_setns, METH_VARARGS},
  {"unshare", _cffi_f_unshare, METH_O},
  {"_cffi_setup", _cffi_setup, METH_VARARGS},
  {NULL, NULL}    /* Sentinel */
};

PyMODINIT_FUNC
init_cffi__x4895f207x65a51566(void)
{
  PyObject *lib;
  lib = Py_InitModule("_cffi__x4895f207x65a51566", _cffi_methods);
  if (lib == NULL || 0 < 0)
    return;
  _cffi_init();
  return;
}
