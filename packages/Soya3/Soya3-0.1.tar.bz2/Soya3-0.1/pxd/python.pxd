# -*- coding: utf-8 -*-

# Soya 3D
# Copyright (C) 2001-2014 Jean-Baptiste LAMY
# http://www.lesfleursdunormal.fr/static/informatique/soya3d/index_en.html

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

cdef extern from "Python.h":
  char*  PyBytes_AS_STRING(bytes string)
    
  # #defined in macro_python3.h
  #bytes PyString_FromString(char* raw)
  #bytes PyString_FromStringAndSize(char* raw, int length)
    
  char*  PyUnicode_AS_DATA(str   string)
    
  object PyTuple_GET_ITEM(object, int)
  double PyFloat_AS_DOUBLE(object)
  
  void   PyErr_CheckSignals()
  
  int    len "PyObject_Length" (object o) except -1


cdef char* python2cstring(object string)
cdef int   python2cstringlen(object string)

cdef char* PyString_AS_STRING(string)
