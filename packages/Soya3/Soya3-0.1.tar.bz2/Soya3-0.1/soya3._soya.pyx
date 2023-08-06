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


# Optional modules
include "config.pxd"

IF OPENGL == "es":
  include "pyx/c_opengles.pyx"
  
include "pyx/python.pyx"
include "pyx/python_opengl.pyx"

# Pyrex modules
include "pyx/list.pyx"
include "pyx/base.pyx"
include "pyx/init.pyx"
include "pyx/math3d.pyx"
include "pyx/renderer.pyx"
include "pyx/main_loop.pyx"

include "pyx/atmosphere.pyx"
include "pyx/raypick.pyx"
include "pyx/coordsyst.pyx"
include "pyx/body.pyx"
include "pyx/world.pyx"
include "pyx/light.pyx"
include "pyx/camera.pyx"
include "pyx/portal.pyx"
include "pyx/traveling_camera.pyx"

include "pyx/image.pyx"
include "pyx/material.pyx"
include "pyx/face.pyx"
include "pyx/model.pyx"
include "pyx/lod_model.pyx"
include "pyx/sprite.pyx"
include "pyx/particle.pyx"
include "pyx/terrain.pyx"
include "pyx/shader_glsl.pyx"

IF HAS_CAL3D:
  include "pyx/animated_model.pyx"
  
IF HAS_TEXT:
  include "pyx/text.pyx"
  
IF HAS_SOUND:
  include "pyx/sound.pyx"
  
IF HAS_ODE:
  include "pyx/ode/utils.pyx"
  include "pyx/ode/mass.pyx"
  include "pyx/ode/joints.pyx"
  include "pyx/ode/geom.pyx"
  include "pyx/ode/space.pyx"
  include "pyx/ode/collision.pyx"
  include "pyx/ode/contact.pyx"
  include "pyx/ode/geom-primitive.pyx"
  include "pyx/ode/geom-terrain.pyx"
  include "pyx/ode/model.pyx"
