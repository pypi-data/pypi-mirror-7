//
//  _tnetstring.c:  python module for fast encode/decode of typed-netstrings
//
//  You get the following functions:
//
//    dumps:  dump a python object to a tnetstring
//    loads:  parse tnetstring into a python object
//    load:   parse tnetstring from a file-like object
//    pop:    parse tnetstring into a python object,
//            return it along with unparsed data.

#include <Python.h>


#define TNS_MAX_LENGTH 999999999
#include "tns_core.c"

//  We have one static tns_ops struct for parsing bytestrings.
static tns_ops _tnetstring_ops_bytes;

//  _tnetstring_loads:  parse tnetstring-format value from a string.
//
static PyObject*
_tnetstring_loads(PyObject* self, PyObject *args) 
{
  PyObject *string = NULL;
  PyObject *val = NULL;
  tns_ops *ops = &_tnetstring_ops_bytes;
  char *data;
  size_t len;

  if(!PyArg_UnpackTuple(args, "loads", 1, 1, &string)) {
      return NULL;
  }
  if(!PyBytes_Check(string)) {
      PyErr_SetString(PyExc_TypeError, "arg must be of bytes type");
      return NULL;
  }
  Py_INCREF(string);

  data = PyBytes_AS_STRING(string);
  len = PyBytes_GET_SIZE(string);
  val = tns_parse(ops, data, len, NULL);

  Py_DECREF(string);
  return val;
}


//  _tnetstring_load:  parse tnetstring-format value from a file.
//
//  This takes care to read no more data than is required to get the
//  full tnetstring-encoded value.  It might read arbitrarily-much
//  data if the file doesn't begin with a valid tnetstring.
//
static PyObject*
_tnetstring_load(PyObject* self, PyObject *args) 
{
  PyObject *val = NULL;
  PyObject *file = NULL;
  PyObject *methnm = NULL;
  PyObject *metharg = NULL;
  PyObject *res = NULL;
  tns_ops *ops = &_tnetstring_ops_bytes;
  char c, *data;
  size_t datalen = 0;

  if(!PyArg_UnpackTuple(args, "load", 1, 1, &file)) {
      goto error;
  }
  Py_INCREF(file);

  //  We're going to read one char at a time
  if((methnm = PyUnicode_FromString("read")) == NULL) {
      goto error;
  }
  if((metharg = PyLong_FromLong(1)) == NULL) {
      goto error;
  }

  //  Read the length prefix one char at a time
  res = PyObject_CallMethodObjArgs(file, methnm, metharg, NULL);
  if(res == NULL) {
      goto error;
  }
  Py_INCREF(res);
  if(!PyBytes_Check(res) || !PyBytes_GET_SIZE(res)) {
      PyErr_SetString(PyExc_ValueError,
                      "Not a tnetstring: invalid or missing length prefix");
      goto error;
  }
  c = PyBytes_AS_STRING(res)[0];
  Py_DECREF(res); res = NULL;
  //  Note that the netstring spec explicitly forbids padding zeroes.
  //  If the first char is zero, it must be the only char.
  if(c < '0' || c > '9') {
      PyErr_SetString(PyExc_ValueError,
                      "Not a tnetstring: invalid or missing length prefix");
      goto error;
  } else if (c == '0') {
      res = PyObject_CallMethodObjArgs(file, methnm, metharg, NULL);
      if(res == NULL) {
          goto error;
      }
      Py_INCREF(res);
      if(!PyBytes_Check(res) || !PyBytes_GET_SIZE(res)) {
          PyErr_SetString(PyExc_ValueError,
                      "Not a tnetstring: invalid or missing length prefix");
          goto error;
      }
      c = PyBytes_AS_STRING(res)[0];
      Py_DECREF(res); res = NULL;
  } else {
      do {
          datalen = (10 * datalen) + (c - '0');
          check(datalen <= TNS_MAX_LENGTH,
                "Not a tnetstring: absurdly large length prefix"); 
          res = PyObject_CallMethodObjArgs(file, methnm, metharg, NULL);
          if(res == NULL) {
              goto error;
          }
          Py_INCREF(res);
          if(!PyBytes_Check(res) || !PyBytes_GET_SIZE(res)) {
              PyErr_SetString(PyExc_ValueError,
                        "Not a tnetstring: invalid or missing length prefix");
              goto error;
          }
          c = PyBytes_AS_STRING(res)[0];
          Py_DECREF(res); res = NULL;
      } while(c >= '0' && c <= '9');
  }

  //  Validate end-of-length-prefix marker.
  if(c != ':') {
      PyErr_SetString(PyExc_ValueError,
                      "Not a tnetstring: missing length prefix");
      goto error;
  }
  
  //  Read the data plus terminating type tag.
  Py_DECREF(metharg);
  if((metharg = PyLong_FromSize_t(datalen + 1)) == NULL) {
      goto error;
  } 
  res = PyObject_CallMethodObjArgs(file, methnm, metharg, NULL);
  if(res == NULL) {
      goto error;
  }
  Py_INCREF(res);
  Py_DECREF(file); file = NULL;
  Py_DECREF(methnm); methnm = NULL;
  Py_DECREF(metharg); metharg = NULL;
  if(!PyBytes_Check(res) || PyBytes_GET_SIZE(res) != datalen + 1) {
      PyErr_SetString(PyExc_ValueError,
                      "Not a tnetstring: invalid length prefix");
      goto error;
  }

  //  Parse out the payload object
  data = PyBytes_AS_STRING(res);
  val = tns_parse_payload(ops, data[datalen], data, datalen);
  Py_DECREF(res); res = NULL;

  return val;

error:
  if(file != NULL) {
      Py_DECREF(file);
  }
  if(methnm != NULL) {
      Py_DECREF(methnm);
  }
  if(metharg != NULL) {
      Py_DECREF(metharg);
  }
  if(res != NULL) {
      Py_DECREF(res);
  }
  if(val != NULL) {
      Py_DECREF(val);
  }
  return NULL;
}


static PyObject*
_tnetstring_pop(PyObject* self, PyObject *args) 
{
  PyObject *string = NULL;
  PyObject *val = NULL;
  PyObject *rest = NULL;
  PyObject *result = NULL;
  tns_ops *ops = &_tnetstring_ops_bytes;
  char *data, *remain;
  size_t len;

  if(!PyArg_UnpackTuple(args, "pop", 1, 1, &string)) {
      return NULL;
  }
  if(!PyBytes_Check(string)) {
      PyErr_SetString(PyExc_TypeError, "arg must be of bytes type");
      return NULL;
  }
  Py_INCREF(string);

  data = PyBytes_AS_STRING(string);
  len = PyBytes_GET_SIZE(string);
  val = tns_parse(ops, data, len, &remain);
  Py_DECREF(string);
  if(val == NULL) {
      return NULL;
  }

  rest = PyBytes_FromStringAndSize(remain, len-(remain-data));
  if(rest == NULL) {
      result = NULL;
  } else {
      result = PyTuple_Pack(2, val, rest);
      Py_DECREF(rest);
  }
  Py_DECREF(val);
  return result;
}


static PyObject*
_tnetstring_dumps(PyObject* self, PyObject *args)
{
  PyObject *object = NULL;
  PyObject *string = NULL;
  tns_ops *ops = &_tnetstring_ops_bytes;
  tns_outbuf outbuf;

  if(!PyArg_UnpackTuple(args, "dumps", 1, 1, &object)) {
      return NULL;
  }
  Py_INCREF(object);

  if(tns_outbuf_init(&outbuf) == -1) {
      goto error;
  }
  if(tns_render_value(ops, object, &outbuf) == -1) {
      goto error;
  }

  Py_DECREF(object);
  string = PyBytes_FromStringAndSize(NULL,tns_outbuf_size(&outbuf));
  if(string == NULL) {
      goto error;
  }

  tns_outbuf_memmove(&outbuf, PyBytes_AS_STRING(string));
  free(outbuf.buffer);

  return string;

error:
  Py_DECREF(object);
  return NULL;
}

//  Functions to hook the parser core up to python.

static void*
tns_parse_string(const tns_ops *ops, const char *data, size_t len)
{
  return PyBytes_FromStringAndSize(data, len);
}


static void*
tns_parse_integer(const tns_ops *ops, const char *data, size_t len)
{
  long l = 0;
  long long ll = 0;
  int sign = 1;
  char c;
  char *dataend;
  const char *pos, *eod;
  PyObject *v = NULL;

  //  Anything with less than 10 digits, we can fit into a long.
  //  Hand-parsing, as we need tighter error-checking than strtol.
  if (len < 10) {
      pos = data;
      eod = data + len;
      c = *pos++;
      switch(c) {
        case '0':
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9':
          l = c - '0';
          break;
        case '+':
          break;
        case '-':
          sign = -1;
          break;
        default:
          sentinel("invalid integer literal: %c", c);
      }
      while(pos < eod) {
          c = *pos++;
          check(c >= '0' && c <= '9', "invalid integer literal: %c", c);
          l = (l * 10) + (c - '0');
      }
      return PyLong_FromLong(l * sign);
  }
  //  Anything with less than 19 digits fits in a long long.
  //  Hand-parsing, as we need tighter error-checking than strtoll.
  else if(len < 19) {
      pos = data;
      eod = data + len;
      c = *pos++;
      switch(c) {
        case '0':
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9':
          ll = c - '0';
          break;
        case '+':
          break;
        case '-':
          sign = -1;
          break;
        default:
          sentinel("invalid integer literal: %c", c);
      }
      while(pos < eod) {
          c = *pos++;
          check(c >= '0' && c <= '9', "invalid integer literal: %c", c);
          ll = (ll * 10) + (c - '0');
      }
      return PyLong_FromLongLong(ll * sign);
  }
  //  Really big numbers are passed to python's native parser.
  else { 
      // PyLong_FromString allows leading whitespace, so we have to check
      // that there is none present in the string.
      c = *data;
      switch(c) {
        case '0':
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9':
          break;
        case '+':
        case '-':
          c = *(data+1);
          check(c >= '0' && c <= '9', "invalid big integer literal: %c", c);
          break;
        default:
          sentinel("invalid big integer literal: %c", c);
      }
      // PyLong_FromString insists that the string end in a NULL byte.
      // I am *not* copying all that data.  Instead we lie a little bit
      // about the const-ness of data, write a NULL over the format terminator
      // and restore the original character when we're done.
      c = data[len];
      ((char*)data)[len] = '\0';
      v = PyLong_FromString((char *)data, &dataend, 10);
      ((char*)data)[len] = c;
      check(dataend == data + len, "invalid big integer literal");
      return v;
  }
  sentinel("invalid code branch, check your compiler...");

error:
  return NULL;
}


static void*
tns_parse_float(const tns_ops *ops, const char *data, size_t len)
{
  double d = 0;
  char *dataend;

  //  Technically this allows whitespace around the float, which
  //  isn't valid in a tnetstring.  But I don't want to waste the
  //  time checking and I am *not* reimplementing strtod.
  d = strtod(data, &dataend);
  if(dataend != data + len) {
      return NULL;
  }
  return PyFloat_FromDouble(d);
}


static void*
tns_get_null(const tns_ops *ops)
{
  Py_INCREF(Py_None);
  return Py_None;
}


static void*
tns_get_true(const tns_ops *ops)
{
  Py_INCREF(Py_True);
  return Py_True;
}


static void*
tns_get_false(const tns_ops *ops)
{
  Py_INCREF(Py_False);
  return Py_False;
}


static void*
tns_new_dict(const tns_ops *ops)
{
  return PyDict_New();
}


static void*
tns_new_list(const tns_ops *ops)
{
  return PyList_New(0);
}


static void
tns_free_value(const tns_ops *ops, void *value)
{
  Py_XDECREF(value);
}


static int
tns_add_to_dict(const tns_ops *ops, void *dict, void *key, void *item)
{
  int res;
  res = PyDict_SetItem(dict, key, item);
  Py_DECREF(key);
  Py_DECREF(item);
  if(res == -1) {
      return -1;
  }
  return 0;
}


static int
tns_add_to_list(const tns_ops *ops, void *list, void *item)
{
  int res;
  res = PyList_Append(list, item);
  Py_DECREF(item);
  if(res == -1) {
      return -1;
  }
  return 0;
}


static int
tns_render_string(const tns_ops *ops, void *val, tns_outbuf *outbuf)
{
  return tns_outbuf_puts(outbuf, PyBytes_AS_STRING(val),
                                 PyBytes_GET_SIZE(val));
}


static int
tns_render_integer(const tns_ops *ops, void *val, tns_outbuf *outbuf)
{
  PyObject *string = NULL;
  int res = 0;

  string = PyUnicode_AsUTF8String(PyObject_Str(val));
  if(string == NULL) {
      return -1;
  }

  res = tns_render_string(ops, string, outbuf);
  Py_DECREF(string);
  return res;
}


static int
tns_render_float(const tns_ops *ops, void *val, tns_outbuf *outbuf)
{
  PyObject *string;
  int res = 0;

  string = PyUnicode_AsUTF8String(PyObject_Repr(val));
  if(string == NULL) {
      return -1;
  }

  res = tns_render_string(ops, string, outbuf);
  Py_DECREF(string);
  return res;
}


static int
tns_render_bool(const tns_ops *ops, void *val, tns_outbuf *outbuf)
{
  if(val == Py_True) {
      return tns_outbuf_puts(outbuf, "true", 4);
  } else {
      return tns_outbuf_puts(outbuf, "false", 5);
  }
}


static int
tns_render_dict(const tns_ops *ops, void *val, tns_outbuf *outbuf)
{
  PyObject *key, *item;
  Py_ssize_t pos = 0;

  while(PyDict_Next(val, &pos, &key, &item)) {
      if(tns_render_value(ops, item, outbuf) == -1) {
          return -1;
      }
      if(tns_render_value(ops, key, outbuf) == -1) {
          return -1;
      }
  }
  return 0;
}


static int
tns_render_list(const tns_ops *ops, void *val, tns_outbuf *outbuf)
{
  PyObject *item;
  Py_ssize_t idx;

  //  Remember, all output is in reverse.
  //  So we must write the last element first.
  idx = PyList_GET_SIZE(val) - 1;
  while(idx >= 0) {
      item = PyList_GET_ITEM(val, idx);
      if(tns_render_value(ops, item, outbuf) == -1) {
          return -1;
      }
      idx--;
  }
  return 0;
}


static
tns_type_tag tns_get_type(const tns_ops *ops, void *val)
{
  if(val == Py_True || val == Py_False) {
    return tns_tag_bool;
  }
  if(val == Py_None) {
    return tns_tag_null;
  }
  if(PyLong_Check((PyObject*)val) || PyLong_Check((PyObject*)val)) {
    return tns_tag_integer;
  }
  if(PyFloat_Check((PyObject*)val)) {
    return tns_tag_float;
  }
  if(PyBytes_Check((PyObject*)val)) {
    return tns_tag_string;
  }
  if(PyList_Check((PyObject*)val)) {
    return tns_tag_list;
  }
  if(PyDict_Check((PyObject*)val)) {
    return tns_tag_dict;
  }
  return 0;
}

// Module initialization

static PyMethodDef _tnetstring_methods[] = {
    {"load",
     (PyCFunction)_tnetstring_load,
     METH_VARARGS,
     PyDoc_STR("load(file_handle: file) -> object\n"
               "This function reads a tnetstring from a file and parses it\n"
               " into a python object.")},

    {"loads",
     (PyCFunction)_tnetstring_loads,
     METH_VARARGS,
     PyDoc_STR("loads(string: bytes) -> object\n"
               "This function parses a tnetstring into a python object.")},

    {"pop",
     (PyCFunction)_tnetstring_pop,
     METH_VARARGS,
     PyDoc_STR("pop(string: bytes) -> (object, remain)\n"
               "This function parses a tnetstring into a python object.\n"
               "It returns a tuple giving the parsed object and a string\n"
               "containing any unparsed data.")},

    {"dumps",
     (PyCFunction)_tnetstring_dumps,
     METH_VARARGS,
     PyDoc_STR("dumps(value: object) -> bytes\n"
               "This function dumps a python object as a tnetstring.")},

    {NULL, NULL, 0, NULL}
};

PyDoc_STRVAR(_tnetstring_doc, "Fast encoding/decoding of typed-netstrings.");

static struct PyModuleDef _tnetstring_module = {
   PyModuleDef_HEAD_INIT,
   "_tnetstring",   /* name of module */
   _tnetstring_doc, /* module documentation, may be NULL */
   -1,              /* size of per-interpreter state of the module,
                       or -1 if the module keeps state in global variables. */
   _tnetstring_methods
};

PyMODINIT_FUNC
PyInit__tnetstring(void) {
  //  Initialize function pointers for parsing bytes.
  _tnetstring_ops_bytes.get_type = &tns_get_type;
  _tnetstring_ops_bytes.free_value = &tns_free_value;

  _tnetstring_ops_bytes.parse_string = tns_parse_string;
  _tnetstring_ops_bytes.parse_integer = tns_parse_integer;
  _tnetstring_ops_bytes.parse_float = tns_parse_float;
  _tnetstring_ops_bytes.get_null = tns_get_null;
  _tnetstring_ops_bytes.get_true = tns_get_true;
  _tnetstring_ops_bytes.get_false = tns_get_false;

  _tnetstring_ops_bytes.render_string = tns_render_string;
  _tnetstring_ops_bytes.render_integer = tns_render_integer;
  _tnetstring_ops_bytes.render_float = tns_render_float;
  _tnetstring_ops_bytes.render_bool = tns_render_bool;

  _tnetstring_ops_bytes.new_dict = tns_new_dict;
  _tnetstring_ops_bytes.add_to_dict = tns_add_to_dict;
  _tnetstring_ops_bytes.render_dict = tns_render_dict;

  _tnetstring_ops_bytes.new_list = tns_new_list;
  _tnetstring_ops_bytes.add_to_list = tns_add_to_list;
  _tnetstring_ops_bytes.render_list = tns_render_list;

  return PyModule_Create(&_tnetstring_module);
};

