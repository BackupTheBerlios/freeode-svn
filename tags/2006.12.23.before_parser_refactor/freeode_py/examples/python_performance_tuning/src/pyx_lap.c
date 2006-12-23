/* Generated by Pyrex 0.9.3 on Sun Mar 26 23:51:46 2006 */

#include "Python.h"
#include "structmember.h"
#ifndef PY_LONG_LONG
  #define PY_LONG_LONG LONG_LONG
#endif
#include "math.h"
#include "numpy/arrayobject.h"


typedef struct {PyObject **p; char *s;} __Pyx_InternTabEntry; /*proto*/
typedef struct {PyObject **p; char *s; long n;} __Pyx_StringTabEntry; /*proto*/
static PyObject *__Pyx_UnpackItem(PyObject *, int); /*proto*/
static int __Pyx_EndUnpack(PyObject *, int); /*proto*/
static int __Pyx_PrintItem(PyObject *); /*proto*/
static int __Pyx_PrintNewline(void); /*proto*/
static void __Pyx_Raise(PyObject *type, PyObject *value, PyObject *tb); /*proto*/
static void __Pyx_ReRaise(void); /*proto*/
static PyObject *__Pyx_Import(PyObject *name, PyObject *from_list); /*proto*/
static PyObject *__Pyx_GetExcValue(void); /*proto*/
static int __Pyx_ArgTypeTest(PyObject *obj, PyTypeObject *type, int none_allowed, char *name); /*proto*/
static int __Pyx_TypeTest(PyObject *obj, PyTypeObject *type); /*proto*/
static int __Pyx_GetStarArgs(PyObject **args, PyObject **kwds, char *kwd_list[], int nargs, PyObject **args2, PyObject **kwds2); /*proto*/
static void __Pyx_WriteUnraisable(char *name); /*proto*/
static void __Pyx_AddTraceback(char *funcname); /*proto*/
static PyTypeObject *__Pyx_ImportType(char *module_name, char *class_name, long size);  /*proto*/
static int __Pyx_SetVtable(PyObject *dict, void *vtable); /*proto*/
static int __Pyx_GetVtable(PyObject *dict, void *vtabptr); /*proto*/
static PyObject *__Pyx_CreateClass(PyObject *bases, PyObject *dict, PyObject *name, char *modname); /*proto*/
static int __Pyx_InternStrings(__Pyx_InternTabEntry *t); /*proto*/
static int __Pyx_InitStrings(__Pyx_StringTabEntry *t); /*proto*/
static PyObject *__Pyx_GetName(PyObject *dict, PyObject *name); /*proto*/

static PyObject *__pyx_m;
static PyObject *__pyx_b;
static int __pyx_lineno;
static char *__pyx_filename;
staticforward char **__pyx_f;

/* Declarations from pyx_lap */

static PyTypeObject *__pyx_ptype_7pyx_lap_dtype = 0;
static PyTypeObject *__pyx_ptype_7pyx_lap_ndarray = 0;

/* Implementation of pyx_lap */


static PyObject *__pyx_n_numpy;
static PyObject *__pyx_n_pyrexTimeStep;

static PyObject *__pyx_n_chr;
static PyObject *__pyx_n_d;
static PyObject *__pyx_n_TypeError;
static PyObject *__pyx_n_ValueError;

static PyObject *__pyx_k3p;
static PyObject *__pyx_k4p;

static char (__pyx_k3[]) = "Double array required";
static char (__pyx_k4[]) = "2 dimensional array required";

static PyObject *__pyx_f_7pyx_lap_pyrexTimeStep(PyObject *__pyx_self, PyObject *__pyx_args, PyObject *__pyx_kwds); /*proto*/
static PyObject *__pyx_f_7pyx_lap_pyrexTimeStep(PyObject *__pyx_self, PyObject *__pyx_args, PyObject *__pyx_kwds) {
  PyArrayObject *__pyx_v_u = 0;
  double __pyx_v_dx;
  double __pyx_v_dy;
  int __pyx_v_nx;
  int __pyx_v_ny;
  double __pyx_v_dx2;
  double __pyx_v_dy2;
  double __pyx_v_dnr_inv;
  double __pyx_v_err;
  double (*__pyx_v_elem);
  int __pyx_v_i;
  int __pyx_v_j;
  double (*__pyx_v_uc);
  double (*__pyx_v_uu);
  double (*__pyx_v_ud);
  double (*__pyx_v_ul);
  double (*__pyx_v_ur);
  double __pyx_v_diff;
  double __pyx_v_tmp;
  PyObject *__pyx_r;
  PyObject *__pyx_1 = 0;
  PyObject *__pyx_2 = 0;
  PyObject *__pyx_3 = 0;
  int __pyx_4;
  double __pyx_5;
  double __pyx_6;
  long __pyx_7;
  long __pyx_8;
  static char *__pyx_argnames[] = {"u","dx","dy",0};
  extern double pow(double, double);
  if (!PyArg_ParseTupleAndKeywords(__pyx_args, __pyx_kwds, "Odd", __pyx_argnames, &__pyx_v_u, &__pyx_v_dx, &__pyx_v_dy)) return 0;
  Py_INCREF(__pyx_v_u);
  if (!__Pyx_ArgTypeTest(((PyObject *)__pyx_v_u), __pyx_ptype_7pyx_lap_ndarray, 1, "u")) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 33; goto __pyx_L1;}

  /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":34 */
  __pyx_1 = __Pyx_GetName(__pyx_b, __pyx_n_chr); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 34; goto __pyx_L1;}
  __pyx_2 = PyInt_FromLong(__pyx_v_u->descr->type); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 34; goto __pyx_L1;}
  __pyx_3 = PyTuple_New(1); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 34; goto __pyx_L1;}
  PyTuple_SET_ITEM(__pyx_3, 0, __pyx_2);
  __pyx_2 = 0;
  __pyx_2 = PyObject_CallObject(__pyx_1, __pyx_3); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 34; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  Py_DECREF(__pyx_3); __pyx_3 = 0;
  if (PyObject_Cmp(__pyx_2, __pyx_n_d, &__pyx_4) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 34; goto __pyx_L1;}
  __pyx_4 = __pyx_4 != 0;
  Py_DECREF(__pyx_2); __pyx_2 = 0;
  if (__pyx_4) {

    /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":35 */
    __pyx_1 = __Pyx_GetName(__pyx_b, __pyx_n_TypeError); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 35; goto __pyx_L1;}
    __pyx_3 = PyTuple_New(1); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 35; goto __pyx_L1;}
    Py_INCREF(__pyx_k3p);
    PyTuple_SET_ITEM(__pyx_3, 0, __pyx_k3p);
    __pyx_2 = PyObject_CallObject(__pyx_1, __pyx_3); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 35; goto __pyx_L1;}
    Py_DECREF(__pyx_1); __pyx_1 = 0;
    Py_DECREF(__pyx_3); __pyx_3 = 0;
    __Pyx_Raise(__pyx_2, 0, 0);
    Py_DECREF(__pyx_2); __pyx_2 = 0;
    {__pyx_filename = __pyx_f[0]; __pyx_lineno = 35; goto __pyx_L1;}
    goto __pyx_L2;
  }
  __pyx_L2:;

  /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":36 */
  __pyx_4 = (__pyx_v_u->nd != 2);
  if (__pyx_4) {

    /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":37 */
    __pyx_1 = __Pyx_GetName(__pyx_b, __pyx_n_ValueError); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 37; goto __pyx_L1;}
    __pyx_3 = PyTuple_New(1); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 37; goto __pyx_L1;}
    Py_INCREF(__pyx_k4p);
    PyTuple_SET_ITEM(__pyx_3, 0, __pyx_k4p);
    __pyx_2 = PyObject_CallObject(__pyx_1, __pyx_3); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 37; goto __pyx_L1;}
    Py_DECREF(__pyx_1); __pyx_1 = 0;
    Py_DECREF(__pyx_3); __pyx_3 = 0;
    __Pyx_Raise(__pyx_2, 0, 0);
    Py_DECREF(__pyx_2); __pyx_2 = 0;
    {__pyx_filename = __pyx_f[0]; __pyx_lineno = 37; goto __pyx_L1;}
    goto __pyx_L3;
  }
  __pyx_L3:;

  /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":42 */
  __pyx_v_nx = (__pyx_v_u->dimensions[0]);

  /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":43 */
  __pyx_v_ny = (__pyx_v_u->dimensions[1]);

  /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":44 */
  __pyx_5 = pow(__pyx_v_dx, 2);
  __pyx_6 = pow(__pyx_v_dy, 2);
  __pyx_v_dx2 = __pyx_5;
  __pyx_v_dy2 = __pyx_6;

  /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":45 */
  __pyx_v_dnr_inv = (0.5 / (__pyx_v_dx2 + __pyx_v_dy2));

  /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":46 */
  __pyx_v_elem = ((double (*))__pyx_v_u->data);

  /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":48 */
  __pyx_v_err = 0.0;

  /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":52 */
  __pyx_7 = (__pyx_v_nx - 1);
  for (__pyx_v_i = 1; __pyx_v_i < __pyx_7; ++__pyx_v_i) {

    /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":53 */
    __pyx_v_uc = ((__pyx_v_elem + (__pyx_v_i * __pyx_v_ny)) + 1);

    /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":54 */
    __pyx_v_ur = ((__pyx_v_elem + (__pyx_v_i * __pyx_v_ny)) + 2);

    /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":55 */
    __pyx_v_ul = (__pyx_v_elem + (__pyx_v_i * __pyx_v_ny));

    /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":56 */
    __pyx_v_uu = ((__pyx_v_elem + ((__pyx_v_i + 1) * __pyx_v_ny)) + 1);

    /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":57 */
    __pyx_v_ud = ((__pyx_v_elem + ((__pyx_v_i - 1) * __pyx_v_ny)) + 1);

    /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":59 */
    __pyx_8 = (__pyx_v_ny - 1);
    for (__pyx_v_j = 1; __pyx_v_j < __pyx_8; ++__pyx_v_j) {

      /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":60 */
      __pyx_v_tmp = (__pyx_v_uc[0]);

      /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":62 */
      (__pyx_v_uc[0]) = (((((__pyx_v_ul[0]) + (__pyx_v_ur[0])) * __pyx_v_dy2) + (((__pyx_v_uu[0]) + (__pyx_v_ud[0])) * __pyx_v_dx2)) * __pyx_v_dnr_inv);

      /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":63 */
      __pyx_v_diff = ((__pyx_v_uc[0]) - __pyx_v_tmp);

      /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":64 */
      __pyx_v_err = (__pyx_v_err + (__pyx_v_diff * __pyx_v_diff));

      /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":65 */
      __pyx_v_uc = (__pyx_v_uc + 1);

      /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":65 */
      __pyx_v_ur = (__pyx_v_ur + 1);

      /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":65 */
      __pyx_v_ul = (__pyx_v_ul + 1);

      /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":66 */
      __pyx_v_uu = (__pyx_v_uu + 1);

      /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":66 */
      __pyx_v_ud = (__pyx_v_ud + 1);
      __pyx_L6:;
    }
    __pyx_L7:;
    __pyx_L4:;
  }
  __pyx_L5:;

  /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":68 */
  __pyx_1 = PyFloat_FromDouble(sqrt(__pyx_v_err)); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 68; goto __pyx_L1;}
  __pyx_r = __pyx_1;
  __pyx_1 = 0;
  goto __pyx_L0;

  __pyx_r = Py_None; Py_INCREF(__pyx_r);
  goto __pyx_L0;
  __pyx_L1:;
  Py_XDECREF(__pyx_1);
  Py_XDECREF(__pyx_2);
  Py_XDECREF(__pyx_3);
  __Pyx_AddTraceback("pyx_lap.pyrexTimeStep");
  __pyx_r = 0;
  __pyx_L0:;
  Py_DECREF(__pyx_v_u);
  return __pyx_r;
}

static __Pyx_InternTabEntry __pyx_intern_tab[] = {
  {&__pyx_n_TypeError, "TypeError"},
  {&__pyx_n_ValueError, "ValueError"},
  {&__pyx_n_chr, "chr"},
  {&__pyx_n_d, "d"},
  {&__pyx_n_numpy, "numpy"},
  {&__pyx_n_pyrexTimeStep, "pyrexTimeStep"},
  {0, 0}
};

static __Pyx_StringTabEntry __pyx_string_tab[] = {
  {&__pyx_k3p, __pyx_k3, sizeof(__pyx_k3)},
  {&__pyx_k4p, __pyx_k4, sizeof(__pyx_k4)},
  {0, 0, 0}
};

static struct PyMethodDef __pyx_methods[] = {
  {"pyrexTimeStep", (PyCFunction)__pyx_f_7pyx_lap_pyrexTimeStep, METH_VARARGS|METH_KEYWORDS, 0},
  {0, 0, 0, 0}
};

DL_EXPORT(void) initpyx_lap(void); /*proto*/
DL_EXPORT(void) initpyx_lap(void) {
  PyObject *__pyx_1 = 0;
  __pyx_m = Py_InitModule4("pyx_lap", __pyx_methods, 0, 0, PYTHON_API_VERSION);
  if (!__pyx_m) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 6; goto __pyx_L1;};
  __pyx_b = PyImport_AddModule("__builtin__");
  if (!__pyx_b) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 6; goto __pyx_L1;};
  if (PyObject_SetAttrString(__pyx_m, "__builtins__", __pyx_b) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 6; goto __pyx_L1;};
  if (__Pyx_InternStrings(__pyx_intern_tab) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 6; goto __pyx_L1;};
  if (__Pyx_InitStrings(__pyx_string_tab) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 6; goto __pyx_L1;};
  __pyx_ptype_7pyx_lap_dtype = __Pyx_ImportType("numpy", "dtype", sizeof(PyArray_Descr)); if (!__pyx_ptype_7pyx_lap_dtype) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 15; goto __pyx_L1;}
  __pyx_ptype_7pyx_lap_ndarray = __Pyx_ImportType("numpy", "ndarray", sizeof(PyArrayObject)); if (!__pyx_ptype_7pyx_lap_ndarray) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 20; goto __pyx_L1;}

  /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":6 */
  __pyx_1 = __Pyx_Import(__pyx_n_numpy, 0); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 6; goto __pyx_L1;}
  if (PyObject_SetAttr(__pyx_m, __pyx_n_numpy, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 6; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;

  /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":31 */
  import_array();

  /* "/home/prabhu/work/assignments/cfd/structured/laplace/perf/laplace/src/pyx_lap.pyx":33 */
  return;
  __pyx_L1:;
  Py_XDECREF(__pyx_1);
  __Pyx_AddTraceback("pyx_lap");
}

static char *__pyx_filenames[] = {
  "pyx_lap.pyx",
};
statichere char **__pyx_f = __pyx_filenames;

/* Runtime support code */

static int __Pyx_ArgTypeTest(PyObject *obj, PyTypeObject *type, int none_allowed, char *name) {
    if (!type) {
        PyErr_Format(PyExc_SystemError, "Missing type object");
        return 0;
    }
    if ((none_allowed && obj == Py_None) || PyObject_TypeCheck(obj, type))
        return 1;
    PyErr_Format(PyExc_TypeError,
        "Argument '%s' has incorrect type (expected %s, got %s)",
        name, type->tp_name, obj->ob_type->tp_name);
    return 0;
}

static PyObject *__Pyx_Import(PyObject *name, PyObject *from_list) {
    PyObject *__import__ = 0;
    PyObject *empty_list = 0;
    PyObject *module = 0;
    PyObject *global_dict = 0;
    PyObject *empty_dict = 0;
    PyObject *list;
    __import__ = PyObject_GetAttrString(__pyx_b, "__import__");
    if (!__import__)
        goto bad;
    if (from_list)
        list = from_list;
    else {
        empty_list = PyList_New(0);
        if (!empty_list)
            goto bad;
        list = empty_list;
    }
    global_dict = PyModule_GetDict(__pyx_m);
    if (!global_dict)
        goto bad;
    empty_dict = PyDict_New();
    if (!empty_dict)
        goto bad;
    module = PyObject_CallFunction(__import__, "OOOO",
        name, global_dict, empty_dict, list);
bad:
    Py_XDECREF(empty_list);
    Py_XDECREF(__import__);
    Py_XDECREF(empty_dict);
    return module;
}

static PyObject *__Pyx_GetName(PyObject *dict, PyObject *name) {
    PyObject *result;
    result = PyObject_GetAttr(dict, name);
    if (!result)
        PyErr_SetObject(PyExc_NameError, name);
    return result;
}

static void __Pyx_Raise(PyObject *type, PyObject *value, PyObject *tb) {
    Py_XINCREF(type);
    Py_XINCREF(value);
    Py_XINCREF(tb);
    /* First, check the traceback argument, replacing None with NULL. */
    if (tb == Py_None) {
        Py_DECREF(tb);
        tb = 0;
    }
    else if (tb != NULL && !PyTraceBack_Check(tb)) {
        PyErr_SetString(PyExc_TypeError,
            "raise: arg 3 must be a traceback or None");
        goto raise_error;
    }
    /* Next, replace a missing value with None */
    if (value == NULL) {
        value = Py_None;
        Py_INCREF(value);
    }
    /* Next, repeatedly, replace a tuple exception with its first item */
    while (PyTuple_Check(type) && PyTuple_Size(type) > 0) {
        PyObject *tmp = type;
        type = PyTuple_GET_ITEM(type, 0);
        Py_INCREF(type);
        Py_DECREF(tmp);
    }
    if (PyString_Check(type))
        ;
    else if (PyClass_Check(type))
        ; /*PyErr_NormalizeException(&type, &value, &tb);*/
    else if (PyInstance_Check(type)) {
        /* Raising an instance.  The value should be a dummy. */
        if (value != Py_None) {
            PyErr_SetString(PyExc_TypeError,
              "instance exception may not have a separate value");
            goto raise_error;
        }
        else {
            /* Normalize to raise <class>, <instance> */
            Py_DECREF(value);
            value = type;
            type = (PyObject*) ((PyInstanceObject*)type)->in_class;
            Py_INCREF(type);
        }
    }
    else {
        /* Not something you can raise.  You get an exception
           anyway, just not what you specified :-) */
        PyErr_Format(PyExc_TypeError,
                 "exceptions must be strings, classes, or "
                 "instances, not %s", type->ob_type->tp_name);
        goto raise_error;
    }
    PyErr_Restore(type, value, tb);
    return;
raise_error:
    Py_XDECREF(value);
    Py_XDECREF(type);
    Py_XDECREF(tb);
    return;
}

static int __Pyx_InternStrings(__Pyx_InternTabEntry *t) {
    while (t->p) {
        *t->p = PyString_InternFromString(t->s);
        if (!*t->p)
            return -1;
        ++t;
    }
    return 0;
}

static int __Pyx_InitStrings(__Pyx_StringTabEntry *t) {
    while (t->p) {
        *t->p = PyString_FromStringAndSize(t->s, t->n - 1);
        if (!*t->p)
            return -1;
        ++t;
    }
    return 0;
}

static PyTypeObject *__Pyx_ImportType(char *module_name, char *class_name, 
    long size) 
{
    PyObject *py_module_name = 0;
    PyObject *py_class_name = 0;
    PyObject *py_name_list = 0;
    PyObject *py_module = 0;
    PyObject *result = 0;
    
    py_module_name = PyString_FromString(module_name);
    if (!py_module_name)
        goto bad;
    py_class_name = PyString_FromString(class_name);
    if (!py_class_name)
        goto bad;
    py_name_list = PyList_New(1);
    if (!py_name_list)
        goto bad;
    Py_INCREF(py_class_name);
    if (PyList_SetItem(py_name_list, 0, py_class_name) < 0)
        goto bad;
    py_module = __Pyx_Import(py_module_name, py_name_list);
    if (!py_module)
        goto bad;
    result = PyObject_GetAttr(py_module, py_class_name);
    if (!result)
        goto bad;
    if (!PyType_Check(result)) {
        PyErr_Format(PyExc_TypeError, 
            "%s.%s is not a type object",
            module_name, class_name);
        goto bad;
    }
    if (((PyTypeObject *)result)->tp_basicsize != size) {
        PyErr_Format(PyExc_ValueError, 
            "%s.%s does not appear to be the correct type object",
            module_name, class_name);
        goto bad;
    }
    goto done;
bad:
    Py_XDECREF(result);
    result = 0;
done:
    Py_XDECREF(py_module_name);
    Py_XDECREF(py_class_name);
    Py_XDECREF(py_name_list);
    return (PyTypeObject *)result;
}

#include "compile.h"
#include "frameobject.h"
#include "traceback.h"

static void __Pyx_AddTraceback(char *funcname) {
    PyObject *py_srcfile = 0;
    PyObject *py_funcname = 0;
    PyObject *py_globals = 0;
    PyObject *empty_tuple = 0;
    PyObject *empty_string = 0;
    PyCodeObject *py_code = 0;
    PyFrameObject *py_frame = 0;
    
    py_srcfile = PyString_FromString(__pyx_filename);
    if (!py_srcfile) goto bad;
    py_funcname = PyString_FromString(funcname);
    if (!py_funcname) goto bad;
    py_globals = PyModule_GetDict(__pyx_m);
    if (!py_globals) goto bad;
    empty_tuple = PyTuple_New(0);
    if (!empty_tuple) goto bad;
    empty_string = PyString_FromString("");
    if (!empty_string) goto bad;
    py_code = PyCode_New(
        0,            /*int argcount,*/
        0,            /*int nlocals,*/
        0,            /*int stacksize,*/
        0,            /*int flags,*/
        empty_string, /*PyObject *code,*/
        empty_tuple,  /*PyObject *consts,*/
        empty_tuple,  /*PyObject *names,*/
        empty_tuple,  /*PyObject *varnames,*/
        empty_tuple,  /*PyObject *freevars,*/
        empty_tuple,  /*PyObject *cellvars,*/
        py_srcfile,   /*PyObject *filename,*/
        py_funcname,  /*PyObject *name,*/
        __pyx_lineno,   /*int firstlineno,*/
        empty_string  /*PyObject *lnotab*/
    );
    if (!py_code) goto bad;
    py_frame = PyFrame_New(
        PyThreadState_Get(), /*PyThreadState *tstate,*/
        py_code,             /*PyCodeObject *code,*/
        py_globals,          /*PyObject *globals,*/
        0                    /*PyObject *locals*/
    );
    if (!py_frame) goto bad;
    py_frame->f_lineno = __pyx_lineno;
    PyTraceBack_Here(py_frame);
bad:
    Py_XDECREF(py_srcfile);
    Py_XDECREF(py_funcname);
    Py_XDECREF(empty_tuple);
    Py_XDECREF(empty_string);
    Py_XDECREF(py_code);
    Py_XDECREF(py_frame);
}
