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


# Config
include "config.pxd"

# External libs
include "pxd/c.pxd"
include "pxd/python.pxd"
include "pxd/sdl.pxd"

include "pxd/macro.pxd"

IF   OPENGL == "full":
  include "pxd/c_opengl.pxd"
  
ELIF OPENGL == "es":
  include "pxd/egl.pxd"
  include "pxd/c_opengles.pxd"

# Parts of Soya that are still in C
include "pxd/chunk.pxd"
include "pxd/matrix.pxd"

# Soya base
include "pxd/base.pxd"

IF HAS_CAL3D:
  include "pxd/cal3d.pxd"
  
IF HAS_TEXT:
  include "pxd/freetype.pxd"
  
IF HAS_SOUND:
  include "pxd/al.pxd"
  include "pxd/vorbis.pxd"
    
IF HAS_ODE:
  include "pxd/ode.pxd"
  include "pxd/soya3_ode.pxd"

# Soya
include "pxd/soya3.pxd"
