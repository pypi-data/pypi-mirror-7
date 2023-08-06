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

cdef void glActiveTextureARB(int texture):
  glActiveTexture(texture)

cdef void glColor4fv(float* color):
  glColor4f(color[0], color[1], color[2], color[3])

cdef void glNormal3fv(float* normal):
  glNormal3f(normal[0], normal[1], normal[2])

cdef void glClearDepth(float f):
  glClearDepthf(f)

cdef void glLightModeli(int i, int j):
  glLightModelx(i, j)
  
cdef void glOrtho(float left, float right, float bottom, float top, float near_val, float far_val):
  glOrthof(left, right, bottom, top, near_val, far_val)

cdef void glFrustum(GLfloat left, GLfloat right, GLfloat bottom, GLfloat top, GLfloat near_val, GLfloat far_val):
  glFrustumf(left, right, bottom, top, near_val, far_val)

cdef void glClipPlane(GLenum plane, double *equation):
  cdef float[4] equation_f
  equation_f[0] = <float> equation[0]
  equation_f[1] = <float> equation[1]
  equation_f[2] = <float> equation[2]
  equation_f[3] = <float> equation[3]
  glClipPlanef(plane, equation_f)

cdef void glTexEnvi(GLenum target, GLenum pname, int param):
  glTexEnvx(target, pname, param)


