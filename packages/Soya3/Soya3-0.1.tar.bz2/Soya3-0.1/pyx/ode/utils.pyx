# -*- coding: utf-8 -*-

# Soya 3D
# Copyright (C) 2001-2014 Jean-Baptiste LAMY
# Copyright (C) 2004-2012 Marmoute - Pierre-Yves David - marmoute@nekeme.net
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


cdef _World _find_or_create_most_probable_ode_parent_from(_World world):
  while not (world._option & WORLD_HAS_ODE or world.parent is None):
    world = world.parent
  if not world._option & WORLD_HAS_ODE:
    world._activate_ode_world()
  return world

