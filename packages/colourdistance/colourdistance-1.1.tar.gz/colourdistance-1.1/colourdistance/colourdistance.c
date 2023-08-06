#include <Python.h>

double _colour_distance(int e1r, int e1g, int e1b, int e2r, int e2g, int e2b) 
{
  long rmean = ( e1r + e2r ) / 2;
  long r = e1r - e2r;
  long g = e1g - e2g;
  long b = e1b - e2b;

  return sqrt((((512 + rmean) * r * r) >> 8) + 4 * g * g + (((767 - rmean) * b * b) >> 8));
}

static PyObject* colour_distance(PyObject *self, PyObject *args)
{
    int e1r, e1g, e1b, e2r, e2g, e2b;

    if (!PyArg_ParseTuple(args, "(iii)(iii)", &e1r, &e1g, &e1b, &e2r, &e2g, &e2b))
        return NULL;

    return Py_BuildValue("f", _colour_distance(e1r, e1g, e1b, e2r, e2g, e2b));
}

static PyObject* closest_by_palette(PyObject *self, PyObject *args)
{
  const PyObject *palette, *p_colour;
  int r, g, b, i, p_r, p_g, p_b, c;
  int was_list = 0;

  if (!PyArg_ParseTuple(args, "(iii)|O", &r, &g, &b, &palette))
      return NULL;

  double min_distance = 1E10;
  double curr_distance;
  
  if (PyList_Check(palette)) {
    palette = PyList_AsTuple(palette);
    was_list = 1;
  }
    

  for (i = 0; i < PyTuple_Size(palette); i++) {
    p_colour = PyTuple_GetItem(palette, i);
    
    p_r = PyInt_AsLong(PyTuple_GetItem(p_colour, 0));
    p_g = PyInt_AsLong(PyTuple_GetItem(p_colour, 1));
    p_b = PyInt_AsLong(PyTuple_GetItem(p_colour, 2));

    curr_distance = _colour_distance(r, g, b, p_r, p_g, p_b);

    if (curr_distance < min_distance) {
      min_distance = curr_distance;
      c = i;
    }
  }

  if (was_list == 1)
    Py_DECREF(palette);

  return Py_BuildValue("i", c);
}


static PyMethodDef ModuleMethods[] = {
    {"colour_distance",  colour_distance, METH_VARARGS,
     "Measures distance between 2 rgb colours"},

    {"closest_by_palette", closest_by_palette, METH_VARARGS,
      "Finds closest colour from a given palette"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initcolourdistance(void)
{
    (void) Py_InitModule("_speedups", ModuleMethods);
}