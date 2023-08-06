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


cdef class _LODModel(_Model):
  #cdef _Model _render_model, _collision_model
  #cdef _low_quality_filename, _medium_quality_filename, _high_quality_filename, _collision_filename
  
  def __init__(self, low_quality_filename, medium_quality_filename, high_quality_filename, collision_filename):
    self._low_quality_filename    = low_quality_filename
    self._medium_quality_filename = medium_quality_filename
    self._high_quality_filename   = high_quality_filename
    self._collision_filename      = collision_filename
    self._init()
    
  cdef void _init(self):
    global quality
    import soya3 as soya
    if   quality == 0: self._render_model = soya.Model.get(self._low_quality_filename)
    elif quality == 1: self._render_model = soya.Model.get(self._medium_quality_filename)
    else:              self._render_model = soya.Model.get(self._high_quality_filename)
    self._collision_model = soya.Model.get(self._collision_filename)
    
  cdef __getcstate__(self):
    return self._filename, self._low_quality_filename, self._medium_quality_filename, self._high_quality_filename, self._collision_filename
  
  cdef void __setcstate__(self, cstate):
    self._filename, self._low_quality_filename, self._medium_quality_filename, self._high_quality_filename, self._collision_filename = cstate
    self._init()
    
  cdef void _batch               (self, _Body body): self._render_model._batch (body)
  cdef void _render              (self, _Body body): self._render_model._render(body)
  cdef void _get_box             (self, float* box, float* matrix): self._collision_model._get_box(box, matrix)
  cdef void _raypick             (self, RaypickData raypick_data, CoordSyst raypickable): self._collision_model._raypick(raypick_data, raypickable)
  cdef int  _raypick_b           (self, RaypickData raypick_data, CoordSyst raypickable): return self._collision_model._raypick_b(raypick_data, raypickable)
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, CoordSyst parent): self._collision_model._collect_raypickables(items, rsphere, sphere, parent)
  
  cdef list _get_mini_shaders(self): return self._render_model._get_mini_shaders()
  cdef list _get_materials   (self): return self._render_model._get_materials()
  
  cdef void _instanced(self, _Body body, opt):
    body._data = _VertexBufferedModelData(body, self)
