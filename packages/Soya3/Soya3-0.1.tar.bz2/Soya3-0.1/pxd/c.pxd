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

cdef extern from "stdlib.h":
  void* malloc (int size)
  void* calloc (int nb, int size)
  void* realloc(void* old, int size)
  void  free(void* ptr)
  void  printf(char* s)
  
cdef extern from "string.h":
  void memcpy(void* des, void* src, int size)
  int  memcmp(void*  s1, void*  s2, int size)
  
cdef extern from "math.h":
  float sqrt(float x)
  float fabs(float x)
  float cos (float x)
  float sin (float x)
  float tan (float x)
  float exp (float x)
  float pow (float x, float n)
  float ceil (float x)
  float floor (float x)

cdef extern from "stdint.h":
  ctypedef unsigned long long uintptr_t
