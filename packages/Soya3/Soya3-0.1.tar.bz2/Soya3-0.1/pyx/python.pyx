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

cdef inline char* python2cstring(object string):
  if isinstance(string, bytes): return PyBytes_AS_STRING(string)
  else:                         return PyBytes_AS_STRING(string.encode("utf8"))
cdef inline char* PyString_AS_STRING(string):
  if isinstance(string, bytes): return PyBytes_AS_STRING(string)
  else:                         return PyBytes_AS_STRING(string.encode("utf8"))
cdef inline int python2cstringlen(object string):
  if isinstance(string, bytes): return len(string)
  else:                         return len(string.encode("utf8"))
    
