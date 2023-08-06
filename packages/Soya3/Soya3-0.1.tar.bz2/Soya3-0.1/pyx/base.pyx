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

# Base stuff, including :
#  - forward declarations
#  - struct declarations (cannot be forwarded)
#  - general function
#  - _CObj : mother of all Soya class.


# Reserve 'slot' for the Python final version of the class
# Pyrex class names start with '_' when the class is then extended in Python
# (_World => World) ; in such case, the Pyrex class should be considered as a
# virtual class.
# 
# If you want to instanciate them, use the Python version.
#
# The main reason for this is that Pyrex classes cannot be weakref'ed until they are
# extended in Python.

Image = Material = Model = SimpleModel = VertexBufferedModel = CellShadingModel = Point = Vector = Plane = Camera = Light = Vertex = Body = World = AnimatedModel = Portal = Face = Atmosphere = Particles = Terrain = Mass = Joint = None

mini_shaders_2_program = None

# Constants and structs are now in definitions/base.pxd



# Globals
cdef float LIGHT_NULL_ATTENUATION
LIGHT_NULL_ATTENUATION = 0.05
  
VERSION     = "2-0.1"

BLACK       = (0.0, 0.0, 0.0, 1.0)
WHITE       = (1.0, 1.0, 1.0, 1.0)
TRANSPARENT = (1.0, 1.0, 1.0, 0.0)

cdef int quality
quality = QUALITY_MEDIUM

def get_quality(): return quality

#cdef _Material current_material

cdef Renderer renderer

cdef GLint MAX_LIGHTS, MAX_CLIP_PLANES, MAX_TEXTURES, MAX_TEXTURE_SIZE

def get_max_texture_size(): return MAX_TEXTURE_SIZE

cdef float white      [4]
cdef float transparent[4]
white[0] = white[1] = white[2] = white[3] = 1.0
transparent[0] = transparent[1] = transparent[2] = 1.0
transparent[3] = 0.0

cdef _Material _DEFAULT_MATERIAL
def _set_default_material(_Material material):
  global _DEFAULT_MATERIAL
  _DEFAULT_MATERIAL = material


cdef object _DEFAULT_MODEL_BUILDER
def _set_default_model_builder(model_builder):
  global _DEFAULT_MODEL_BUILDER
  _DEFAULT_MODEL_BUILDER = model_builder


cdef _Program _DEFAULT_PROGRAM
cdef _Program _CURRENT_PROGRAM
_CURRENT_PROGRAM = _DEFAULT_PROGRAM = _FixedPipelineProgram()

def get_default_program(): return _DEFAULT_PROGRAM

def _set_mini_shaders_2_program(func):
  global mini_shaders_2_program
  mini_shaders_2_program = func


# Misc
cdef char* dup(char* data, int size):
  cdef char* buffer
  buffer = <char*> malloc(size)
  memcpy(buffer, data, size)
  return buffer


class ChunkError(MemoryError): pass

def _chunk_check_error():
  if chunk_check_error(): raise ChunkError


def _reconstructor(clazz):
  cdef _CObj obj
  obj = clazz.__new__(clazz)
  return obj

cdef class _CObj:
  cdef __getcstate__(self): pass
  
  cdef void __setcstate__(self, cstate): pass
  
  def __getstate__(self):
    cdef object d
    try:
      d = getattr(self, "__dict__", None)
    except:
      return (self.__getcstate__(),)
    else:
      if d: return (self.__getcstate__(), d)
      else: return (self.__getcstate__(),)
      
  def __setstate__(self, state):
    self.__setcstate__(state[0])
    if len(state) > 1: self.__dict__ = state[1]
    
  def __reduce__(self):
    return _reconstructor, (self.__class__,), self.__getstate__()
    
  def __deepcopy__(self, memo):
    cdef _CObj clone
    
    import copy
    clone = memo[id(self)] = self.__class__.__new__(self.__class__)
    
    state = self.__getstate__()
    state_clone = copy.deepcopy(state, memo)
    clone.__setstate__(state_clone)
    
    return clone


cdef drop_chunk_to_string(Chunk* chunk):
  cdef string
  string = PyString_FromStringAndSize(<char*> chunk.content, chunk.nb)
  drop_chunk(chunk)
  return string

cdef Chunk* string_to_chunk(string):
  cdef Chunk* chunk
  cdef int    length
  length = len(string)
  chunk  = get_chunk()
  chunk_register(chunk, length)
  if isinstance(string, str): string = string.encode("latin")
  memcpy(chunk.content, PyBytes_AS_STRING(string), length)
    
  chunk.nb = 0
  return chunk

