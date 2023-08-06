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

def _couple_sorter(t):
  return t[0]
  

cdef class _Model(_CObj):
  #cdef public _filename
  
  def __repr__(self):
    return "<%s %s>" % (self.__class__.__name__, self._filename)
  
  cdef void _batch               (self, _Body body): pass
  cdef void _render              (self, _Body body): pass
  cdef void _get_box             (self, float* box, float* matrix): pass
  cdef void _raypick             (self, RaypickData raypick_data, CoordSyst raypickable): pass
  cdef int  _raypick_b           (self, RaypickData raypick_data, CoordSyst raypickable): return 0
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, CoordSyst parent): pass
  
  cdef void _attach(self, mesh_names): raise TypeError("This type of model doesn't support attach!")
  cdef void _detach(self, mesh_names): raise TypeError("This type of model doesn't support detach!")
  cdef int  _is_attached(self, mesh_name): return 0
  cdef void _attach_to_bone(self, CoordSyst coordsyst, bone_name): raise TypeError("This type of model doesn't support attach_to_bone!")
  cdef void _detach_from_bone(self, CoordSyst coordsyst): raise TypeError("This type of model doesn't support detach_from_bone!")
  cdef      _get_attached_meshes    (self): return []
  cdef      _get_attached_coordsysts(self): return []
  cdef void _animate_blend_cycle   (self, animation_name, float weight, float fade_in):   raise TypeError("This type of model doesn't support animation!")
  cdef void _animate_clear_cycle   (self, animation_name, float fade_out):                raise TypeError("This type of model doesn't support animation!")
  cdef void _animate_execute_action(self, animation_name, float fade_in, float fade_out): raise TypeError("This type of model doesn't support animation!")
  cdef void _animate_reset(self): pass
  cdef void _set_lod_level(self, float lod_level): raise TypeError("This type of model doesn't support LOD!")
  cdef void _begin_round  (self): pass
  cdef void _advance_time (self, float proportion): pass
  
  cdef list _get_mini_shaders(self): return []
  cdef list _get_materials   (self): return []
  cdef void _instanced(self, _Body body, opt): body._data = self
    
  def __deepcopy__(self, memo):
    """Models are immutable."""
    return self
  
  cdef void _invalidate_shaders(self): pass




cdef GLuint _tmp_face_buffer        =  0
cdef GLuint _tmp_vertex_buffer      =  0
cdef int    _tmp_vertex_buffer_size = -1
cdef short* _tmp_faces              =  NULL
cdef float* _tmp_vertices           =  NULL

cdef void _init_tmp_buffer():
  global _tmp_faces
  
  glGenBuffers(1, &_tmp_face_buffer)
  glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, _tmp_face_buffer)
  glBufferData(GL_ELEMENT_ARRAY_BUFFER, 192 * sizeof(short), NULL, GL_DYNAMIC_DRAW)
  glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
  _tmp_faces = <short*> malloc(192 * sizeof(short))
  _set_tmp_buffer_min_size(192) # 3 * 64
  
cdef void _set_tmp_buffer_min_size(int min_nb_vertices):
  global _tmp_vertex_buffer, _tmp_vertex_buffer_size, _tmp_vertices
  
  if _tmp_vertex_buffer == 0: glGenBuffers(1, &_tmp_vertex_buffer)
  
  if min_nb_vertices > _tmp_vertex_buffer_size:
    _tmp_vertex_buffer_size = min_nb_vertices
    
    _tmp_vertices = <float*> realloc(_tmp_vertices, _tmp_vertex_buffer_size * (3 + 3 + 2 + 4) * sizeof(float))
    
    glBindBuffer(GL_ARRAY_BUFFER, _tmp_vertex_buffer)
    glBufferData(GL_ARRAY_BUFFER, (3 + 3 + 2 + 2 + 4) * _tmp_vertex_buffer_size * sizeof(float), NULL, GL_DYNAMIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)


#ctypedef struct _VertexBufferModelFace:
#  int      option
#  Pack*    pack
#  float    normal[4] # normal[3] is optional (for shadows)
#  int      v[4]      # v[3]      is optional (only for quad, unused for triangle)

#ctypedef struct _VertexBufferModelFaceGroup:
#  int       option
#  int       start, nb_triangles
#  uintptr_t material_id

cdef class _VertexBufferedModel(_Model):
  #cdef int           _option
  #cdef               _materials
  #cdef float*        _sphere
  #cdef int           _nb_faces, _nb_quads, _nb_vertices
  #cdef float*        _coords, *_vnormals, *_diffuses, *_emissives, *_texcoords, *_texcoords2
  #cdef int*          _vertexids
  #cdef char*         _vertex_options
  #cdef list          _mini_shaders
  
  #cdef VertexBufferModelFace* _faces
  #cdef int*                   _neighbors, *_simple_neighbors
  #cdef signed char*           _neighbors_side, *_simple_neighbors_side
  
  #cdef int                          _nb_opaque_face_groups
  #cdef int                          _nb_face_groups
  #cdef short*                       _face_group_vertices
  #cdef _VertexBufferModelFaceGroup* _face_groups
  
  #cdef GLuint        _vertex_buffer, _texcoords2_buffer, _face_buffer
  #cdef int           _buffer_sizeof_vertex
  #cdef int           _vnormal_offset, _diffuse_offset, _emissive_offset, _texcoord_offset
  
  #cdef float     _outline_color[4]
  #cdef float     _outline_width, _outline_attenuation
  
  cdef void _instanced(self, _Body body, opt):
    body._data = _VertexBufferedModelData(body, self)
    
  cdef list _get_mini_shaders(self): return self._mini_shaders
  cdef list _get_materials   (self):
    if self._option & MODEL_OUTLINE: return self._materials + [_DEFAULT_MATERIAL]
    return self._materials
  
  property mini_shaders:
    def __get__(self):
      return self._mini_shaders
    
  def add_mini_shader(self, mini_shader):
    self._mini_shaders.append(mini_shader)
    #self._invalidate_shaders()
    
  def remove_mini_shader(self, mini_shader):
    self._mini_shaders.remove(mini_shader)
    #self._invalidate_shaders()
    
  def __dealloc__(self):
    free(self._faces)
    free(self._coords)
    free(self._vnormals)
    free(self._vertexids)
    free(self._face_group_vertices)
    free(self._face_groups)
    if self._option & MODEL_VERTEX_OPTIONS:   free(self._vertex_options)
    if self._option & MODEL_TEXCOORDS:        free(self._texcoords)
    if self._option & MODEL_TEXCOORDS2:       free(self._texcoords2)
    if self._option & MODEL_DIFFUSES:         free(self._diffuses)
    if self._option & MODEL_EMISSIVES:        free(self._emissives)
    if self._option & MODEL_HAS_SPHERE:       free(self._sphere)
    if self._option & MODEL_NEIGHBORS:        free(self._neighbors); free(self._neighbors_side)
    if self._option & MODEL_SIMPLE_NEIGHBORS: free(self._simple_neighbors); free(self._simple_neighbors_side)
    if self._option & MODEL_INITED:
      glDeleteBuffers(1, &self._face_buffer)
      glDeleteBuffers(1, &self._vertex_buffer)
      if self._option & MODEL_TEXCOORDS2: glDeleteBuffers(1, &self._texcoords2_buffer)
      
  cdef __getcstate__(self):
    cdef Chunk*                       chunk
    cdef int                          i
    cdef _VertexBufferModelFace*      face
    cdef _VertexBufferModelFaceGroup* face_group
    cdef                              material_id2index
    cdef uintptr_t                    ptr
    
    material_id2index = {}
    for i from 0 <= i < len(self._materials):
      ptr = id(self._materials[i]) # Required for Python 2.4
      material_id2index[ptr] = i
      
    chunk = get_chunk()
    chunk_add_int_endian_safe   (chunk, self._option)
    chunk_add_int_endian_safe   (chunk, self._nb_vertices)
    chunk_add_int_endian_safe   (chunk, self._nb_faces)
    chunk_add_int_endian_safe   (chunk, self._nb_quads)
    chunk_add_int_endian_safe   (chunk, self._nb_opaque_face_groups)
    chunk_add_int_endian_safe   (chunk, self._nb_face_groups)
    
    chunk_add_floats_endian_safe(chunk, self._coords   , 3 * self._nb_vertices)
    chunk_add_floats_endian_safe(chunk, self._vnormals , 3 * self._nb_vertices)
    chunk_add_ints_endian_safe  (chunk, self._vertexids,     self._nb_vertices)
    if self._option & MODEL_HAS_SPHERE:     chunk_add_floats_endian_safe(chunk, self._sphere        , 4)
    if self._option & MODEL_VERTEX_OPTIONS: chunk_add_chars_endian_safe (chunk, self._vertex_options,     self._nb_vertices)
    if self._option & MODEL_DIFFUSES:       chunk_add_floats_endian_safe(chunk, self._diffuses      , 4 * self._nb_vertices)
    if self._option & MODEL_EMISSIVES:      chunk_add_floats_endian_safe(chunk, self._emissives     , 4 * self._nb_vertices)
    if self._option & MODEL_TEXCOORDS:      chunk_add_floats_endian_safe(chunk, self._texcoords     , 2 * self._nb_vertices)
    # texcoords2 is for special effects, and do not need to be saved
    
    for i from 0 <= i < self._nb_faces:
      face = self._faces + i
      chunk_add_int_endian_safe   (chunk, face.option)
      chunk_add_floats_endian_safe(chunk, face.normal, 4)
      chunk_add_ints_endian_safe  (chunk, face.v     , 4)
      chunk_add_int_endian_safe   (chunk, material_id2index[face.pack.material_id])
      
    if self._option & MODEL_NEIGHBORS:
      chunk_add_ints_endian_safe (chunk, self._neighbors     , self._nb_faces * 4)
      chunk_add_chars_endian_safe(chunk, self._neighbors_side, self._nb_faces * 4)
      
    if self._option & MODEL_SIMPLE_NEIGHBORS:
      chunk_add_ints_endian_safe (chunk, self._simple_neighbors     , self._nb_faces * 4)
      chunk_add_chars_endian_safe(chunk, self._simple_neighbors_side, self._nb_faces * 4)
      
    for i from 0 <= i < self._nb_face_groups:
      face_group = self._face_groups + i
      chunk_add_int_endian_safe(chunk, face_group.option)
      chunk_add_int_endian_safe(chunk, face_group.start)
      chunk_add_int_endian_safe(chunk, face_group.nb_triangles)
      chunk_add_int_endian_safe(chunk, material_id2index[face_group.material_id])
      
    chunk_add_shorts_endian_safe(chunk, self._face_group_vertices, 3 * (self._nb_faces + self._nb_quads))
    
    chunk_add_float_endian_safe (chunk, self._outline_width)
    chunk_add_float_endian_safe (chunk, self._outline_attenuation)
    chunk_add_floats_endian_safe(chunk, self._outline_color, 4)
    
    return drop_chunk_to_string(chunk), self._filename, self._materials, self._mini_shaders
  
  cdef void __setcstate__(self, cstate):
    cdef int                          i
    cdef int                          temp
    cdef Chunk*                       chunk
    cdef _VertexBufferModelFace*      face
    cdef _VertexBufferModelFaceGroup* face_group
    
    cstate2, self.filename, materials, self._mini_shaders = cstate
    self._materials = list(materials)
    chunk = string_to_chunk(cstate2)
    
    chunk_get_int_endian_safe(chunk, &self._option)
    chunk_get_int_endian_safe(chunk, &self._nb_vertices)
    chunk_get_int_endian_safe(chunk, &self._nb_faces)
    chunk_get_int_endian_safe(chunk, &self._nb_quads)
    chunk_get_int_endian_safe(chunk, &self._nb_opaque_face_groups)
    chunk_get_int_endian_safe(chunk, &self._nb_face_groups)
    
    self._coords        = <float*>     malloc(3 * self._nb_vertices * sizeof(float))
    self._vnormals      = <float*>     malloc(3 * self._nb_vertices * sizeof(float))
    self._vertexids     = <int*>       malloc(    self._nb_vertices * sizeof(int  ))
    chunk_get_floats_endian_safe(chunk, self._coords   , 3 * self._nb_vertices)
    chunk_get_floats_endian_safe(chunk, self._vnormals , 3 * self._nb_vertices)
    chunk_get_ints_endian_safe  (chunk, self._vertexids,     self._nb_vertices)
    if self._option & MODEL_HAS_SPHERE:     self._sphere         = <float*> malloc(4                     * sizeof(float)); chunk_get_floats_endian_safe(chunk, self._sphere        , 4)
    if self._option & MODEL_VERTEX_OPTIONS: self._vertex_options = <char* > malloc(    self._nb_vertices * sizeof(char )); chunk_get_chars_endian_safe (chunk, self._vertex_options,     self._nb_vertices)
    if self._option & MODEL_DIFFUSES:       self._diffuses       = <float*> malloc(4 * self._nb_vertices * sizeof(float)); chunk_get_floats_endian_safe(chunk, self._diffuses      , 4 * self._nb_vertices)
    if self._option & MODEL_EMISSIVES:      self._emissives      = <float*> malloc(4 * self._nb_vertices * sizeof(float)); chunk_get_floats_endian_safe(chunk, self._emissives     , 4 * self._nb_vertices)
    if self._option & MODEL_TEXCOORDS:      self._texcoords      = <float*> malloc(2 * self._nb_vertices * sizeof(float)); chunk_get_floats_endian_safe(chunk, self._texcoords     , 2 * self._nb_vertices)
    if self._option & MODEL_TEXCOORDS2:     self._texcoords2     = <float*> malloc(2 * self._nb_vertices * sizeof(float)) # texcoords2 is for special effects, and do not need to be saved
    
    
    self._faces = <_VertexBufferModelFace*> malloc(self._nb_faces * sizeof(_VertexBufferModelFace))
    for i from 0 <= i < self._nb_faces:
      face = self._faces + i
      chunk_get_int_endian_safe    (chunk, &face.option)
      chunk_get_float_endian_safe  (chunk, &face.normal[0])
      chunk_get_float_endian_safe  (chunk, &face.normal[1])
      chunk_get_float_endian_safe  (chunk, &face.normal[2])
      chunk_get_float_endian_safe  (chunk, &face.normal[3])
      chunk_get_int_endian_safe    (chunk, &face.v     [0])
      chunk_get_int_endian_safe    (chunk, &face.v     [1])
      chunk_get_int_endian_safe    (chunk, &face.v     [2])
      chunk_get_int_endian_safe    (chunk, &face.v     [3])
      chunk_get_int_endian_safe    (chunk, &temp)
      face.pack = (<_Material> (<void*> (self._materials[temp])))._pack(face.option)
      
    if self._option & MODEL_NEIGHBORS:
      self._neighbors      = <int        *> malloc(self._nb_faces * 4 * sizeof(int ))
      self._neighbors_side = <signed char*> malloc(self._nb_faces * 4 * sizeof(signed char))
      chunk_get_ints_endian_safe (chunk, self._neighbors     , self._nb_faces * 4)
      chunk_get_chars_endian_safe(chunk, self._neighbors_side, self._nb_faces * 4)
      
    if self._option & MODEL_SIMPLE_NEIGHBORS:
      self._simple_neighbors      = <int        *> malloc(self._nb_faces * 4 * sizeof(int ))
      self._simple_neighbors_side = <signed char*> malloc(self._nb_faces * 4 * sizeof(signed char))
      chunk_get_ints_endian_safe (chunk, self._simple_neighbors     , self._nb_faces * 4)
      chunk_get_chars_endian_safe(chunk, self._simple_neighbors_side, self._nb_faces * 4)
      
    self._face_groups = <_VertexBufferModelFaceGroup*> malloc(self._nb_face_groups * sizeof(_VertexBufferModelFaceGroup))
    for i from 0 <= i < self._nb_face_groups:
      face_group = self._face_groups + i
      chunk_get_int_endian_safe(chunk, &face_group.option)
      chunk_get_int_endian_safe(chunk, &face_group.start)
      chunk_get_int_endian_safe(chunk, &face_group.nb_triangles)
      chunk_get_int_endian_safe(chunk, &temp)
      face_group.material_id = id(<_Material> (<void*> (self._materials[temp])))
      
    self._face_group_vertices = <short*> malloc(3 * (self._nb_faces + self._nb_quads) * sizeof(short))
    chunk_get_shorts_endian_safe(chunk, self._face_group_vertices, 3 * (self._nb_faces + self._nb_quads))
    
    chunk_get_float_endian_safe (chunk, &self._outline_width)
    chunk_get_float_endian_safe (chunk, &self._outline_attenuation)
    chunk_get_floats_endian_safe(chunk,  self._outline_color, 4)
    
    drop_chunk(chunk)
    
    self._option = self._option & ~MODEL_INITED
    
  property option:
    def __get__(self): return self._option
    
  property materials:
    def __get__(self): return self._materials
    
  property nb_vertices:
    def __get__(self): return self._nb_vertices
    
  property nb_faces:
    def __get__(self): return self._nb_faces
    
  property sphere:
    def __get__(self): return (self._sphere[0], self._sphere[1], self._sphere[2], self._sphere[3])
    
  def get_face(self, int index):
    """Debugging functions"""
    cdef _VertexBufferModelFace* face
    face = self._faces + index
    if face.option & FACE_QUAD: return face.v[0], face.v[1], face.v[2], face.v[3]
    else:                       return face.v[0], face.v[1], face.v[2]
    
  def get_vertex(self, int index):
    """Debugging functions"""
    l = [self._coords[3 * index], self._coords[3 * index + 1], self._coords[3 * index + 2]]
    if self._option & MODEL_VERTEX_OPTIONS: l.append(self._vertex_options[index])
    else:                                   l.append(-1)
    if self._option & MODEL_TEXCOORDS:      l.append(self._texcoords[index])
    else:                                   l.append(-1)
    if self._option & MODEL_DIFFUSES:       l.append(self._colors[index])
    else:                                   l.append(-1)
    if self._option & MODEL_EMISSIVES:      l.append(self._emissives[index])
    else:                                   l.append(-1)
    return tuple(l)
  
  def get_neighbor(self, int index):
    if not (self._option & MODEL_NEIGHBORS): return None
    cdef int* neighbor
    neighbor = self._neighbors + (4 * index)
    return neighbor[0], neighbor[1], neighbor[2], neighbor[3]
    
  def get_neighbor_side(self, int index):
    if not (self._option & MODEL_NEIGHBORS): return None
    cdef signed char* neighbor_side
    neighbor_side = self._neighbors_side + (4 * index)
    return neighbor_side[0], neighbor_side[1], neighbor_side[2], neighbor_side[3]
    
  def get_simple_neighbor(self, int index):
    if not (self._option & MODEL_SIMPLE_NEIGHBORS): return None
    cdef int* neighbor
    neighbor = self._simple_neighbors + (4 * index)
    return neighbor[0], neighbor[1], neighbor[2], neighbor[3]
  
  def get_simple_neighbor_side(self, int index):
    if not (self._option & MODEL_SIMPLE_NEIGHBORS): return None
    cdef signed char* neighbor_side
    neighbor_side = self._simple_neighbors_side + (4 * index)
    return neighbor_side[0], neighbor_side[1], neighbor_side[2], neighbor_side[3]
    
  cdef object _identify_vertices(self, faces, float angle):
    """Finds which vertices are at the same position, for vertex sharing capabilities.
2 vertices are considered at the same position if the distance between them is > EPSILON,
and if the angle between their 2 faces is < ANGLE."""
    # "ivertex" means "identified vertex"
    cdef _Face   face
    cdef _Vertex vertex, ivertex, vertex2
    cdef int     i, j
    cdef float   p[3]
    cdef float   amin, a
    cdef         ivertices
    
    vertex2ivertex   = {}
    ivertex2vertices = {}
    hashcube         = {}
    for face in faces:
      for vertex in face._vertices:
        vertex._out(p)
        p[0] = (<float> (<int> (p[0] / EPSILON))) * EPSILON
        p[1] = (<float> (<int> (p[1] / EPSILON))) * EPSILON
        p[2] = (<float> (<int> (p[2] / EPSILON))) * EPSILON
        
        hash = (p[0], p[1], p[2])
        ivertex = hashcube.get(hash)
        if ivertex is None:
          vertex2ivertex[vertex] = hashcube[hash] = ivertex = vertex
          ivertex2vertices[ivertex] = [vertex]
        else:
          vertex2ivertex[vertex] = ivertex
          ivertex2vertices[ivertex].append(vertex)
          
    if angle > 180.0: return vertex2ivertex, ivertex2vertices
    
    # Take face angle into account for vertex identification.
    vertex2ivertex2   = {}
    ivertex2vertices2 = {}
    for vertices in ivertex2vertices.values():
      couples = []
      for i from 0 <= i < len(vertices):
        for j from i + 1 <= j < len(vertices):
          couples.append((vertices[i].face.normal.angle_to(vertices[j].face.normal), vertices[i], vertices[j]))
          
      couples.sort(key = _couple_sorter)
      
      shared_vertices = {}
      for vertex in vertices: shared_vertices[vertex] = frozenset([vertex])
      
      for a, vertex1, vertex2 in couples:
        if a > angle: break
        shared_vertex1 = shared_vertices.get(vertex1)
        shared_vertex2 = shared_vertices.get(vertex2)
        shared_vertex  = shared_vertex1 | shared_vertex2
        for vertex in shared_vertex: shared_vertices[vertex] = shared_vertex

      for shared_vertex in set(shared_vertices.values()):
        shared_vertex = list(shared_vertex)
        ivertex = shared_vertex[0]
        ivertex2vertices2[ivertex] = shared_vertex
        for vertex in shared_vertex:
          vertex2ivertex2[vertex] = ivertex
          
    return vertex2ivertex2, ivertex2vertices2
  
  cdef void _compute_face_normals(self, faces):
    cdef _Face face
    for face in faces: face._compute_normal()
    
  cdef void _compute_vertex_normals(self, faces, vertex2ivertex, ivertex2vertices):
    cdef _Vertex vertex, ivertex
    for ivertex in ivertex2vertices.keys():
      for vertex in ivertex2vertices[ivertex]:
        if vertex._face._option & FACE2_SMOOTH_LIT:
          if ivertex._normal is None: ivertex._normal = Vector(vertex._face.get_root())
          #vertex._face._compute_normal() # Needed ? Or already done ?
          ivertex._normal.add_mul_vector(vertex._angle_at(), vertex._face._normal)
          
  cdef void _compute_face_neighbors(self, faces, vertex2ivertex, ivertex2vertices, int* neighbor, signed char* neighbor_side):
    # 2 faces are neighbors <=> they share 2 vertices.
    cdef int          i, j, v1_neighbor_index, v2_neighbor_index
    cdef _Vertex      v1, v2, v1_neighbor, v2_neighbor
    cdef _Face        face
    
    i = 0
    face2index = {}
    for face in faces:
      face2index[face] = i
      i = i + 1
      
    for face in faces:
      for i from 0 <= i < len(face.vertices):
        neighbor[i] = -1 # default value meaning 'no neighbor'
        
        v1 = vertex2ivertex[face.vertices[i]]
        v2 = vertex2ivertex[((i + 1 < len(face.vertices)) and face.vertices[i + 1]) or face.vertices[0]]
        
        for v1_neighbor in ivertex2vertices[v1]:
          # A double sided face cannot be the neighbor of a non-double sided face
          if (face._option & FACE2_DOUBLE_SIDED) != (v1_neighbor._face._option & FACE2_DOUBLE_SIDED): continue
          
          if not v1_neighbor._face is face:
            for v2_neighbor in v1_neighbor._face.vertices:
              if vertex2ivertex[v2_neighbor] is v2:
                # one neighbor found
                neighbor[i] = face2index[v1_neighbor._face]
                
                if face._option & FACE2_DOUBLE_SIDED: # Check for "backside-neighbor"
                  v1_neighbor_index = v1_neighbor._face.vertices.index(v1_neighbor)
                  v2_neighbor_index = v1_neighbor._face.vertices.index(v2_neighbor)
                  if (v1_neighbor_index == v2_neighbor_index - 1) or ((v1_neighbor_index > 1) and (v2_neighbor_index == 0)): # Same rotation sens
                    neighbor_side[i] = 1
                  else: neighbor_side[i] = -1
                  
                else: neighbor_side[i] = 1
                break
            else: continue
            break
          
      if len(face.vertices) < 4: neighbor[3] = -1 # triangle can have only 3 neighbors
      neighbor      = neighbor      + 4
      neighbor_side = neighbor_side + 4
      
  def __init__(self, _World world, float angle, int option, lights, outline_color, float outline_width, float outline_attenuation):
    cdef CoordSyst coordsyst
    cdef _Face                   face
    cdef _VertexBufferModelFace* model_face
    cdef _Vertex                 vertex, ivertex
    cdef int                     i, j, k, face_nb_vertices
    cdef short*                  face_group_vertices
    cdef float*                  p
    cdef float                   pos[3]
    cdef float                   vec[3]
    cdef _Material               material
    cdef _Light                  light
    
    self._materials           = []
    self._mini_shaders        = []
    self._outline_width       = outline_width
    self._outline_attenuation = outline_attenuation
    for i from 0 <= i < 4: self._outline_color[i] = outline_color[i]
    
    # Collect faces  XXX collect models too (by loading the corresponding world)
    faces = []
    for coordsyst in world.recursive():
      if isinstance(coordsyst, _Face) and not(coordsyst._option & HIDDEN): faces.append(coordsyst)
      
    # check for additional options
    self._option = option
    if lights:              self._option = self._option | (MODEL_STATIC_LIT + MODEL_EMISSIVES)
    if outline_width > 0.0: self._option = self._option |  MODEL_OUTLINE | MODEL_PLANE_EQUATION | MODEL_NEIGHBORS
    
    for face in faces:
      for vertex in face._vertices:
        if (not face._material._texture is None) and ((vertex._tex_x != 0.0) or (vertex._tex_y != 0.0)): self._option = self._option | MODEL_TEXCOORDS
        if (not vertex._diffuse  is None) and ((vertex._diffuse [0] != 1.0) or (vertex._diffuse [1] != 1.0) or (vertex._diffuse [2] != 1.0) or (vertex._diffuse [3] != 1.0)): self._option = self._option | MODEL_DIFFUSES
        if (not vertex._emissive is None) and ((vertex._emissive[0] != 1.0) or (vertex._emissive[1] != 1.0) or (vertex._emissive[2] != 1.0) or (vertex._emissive[3] != 1.0)): self._option = self._option | MODEL_EMISSIVES
        
    self._compute_face_normals(faces)
    vertex2ivertex, ivertex2vertices = self._identify_vertices(faces, angle)
    self._compute_vertex_normals(faces, vertex2ivertex, ivertex2vertices)
    
    self._nb_vertices = len(vertex2ivertex)
    self._nb_faces    = len(faces)
    self._nb_quads    = 0
    self._coords      = <float*> malloc(3 * self._nb_vertices * sizeof(float))
    self._vnormals    = <float*> malloc(3 * self._nb_vertices * sizeof(float))
    self._vertexids   = <int*  > malloc(    self._nb_vertices * sizeof(int  ))
    if self._option & MODEL_DIFFUSES:   self._diffuses   = <float*> malloc(4 * self._nb_vertices * sizeof(float))
    if self._option & MODEL_EMISSIVES:  self._emissives  = <float*> malloc(4 * self._nb_vertices * sizeof(float))
    if self._option & MODEL_TEXCOORDS:  self._texcoords  = <float*> malloc(2 * self._nb_vertices * sizeof(float))
    if self._option & MODEL_TEXCOORDS2: self._texcoords2 = <float*> malloc(2 * self._nb_vertices * sizeof(float))
    
    vertex2index = {}
    vertices = vertex2ivertex.keys()
    i = 0
    for vertex in vertices:
      vertex2index[vertex] = i
      ivertex = vertex2ivertex[vertex]
      vertex._out(self._coords + 3 * i)
      if vertex._face._option & FACE2_SMOOTH_LIT:
        ivertex._normal._out(self._vnormals + 3 * i)
        vector_normalize    (self._vnormals + 3 * i)
      else:
        vertex._face._normal._out(self._vnormals + 3 * i)
        vector_normalize         (self._vnormals + 3 * i)
        
      if self._option & MODEL_TEXCOORDS:
        p = self._texcoords + 2 * i
        p[0] = vertex._tex_x
        p[1] = vertex._tex_y
        
      if self._option & MODEL_DIFFUSES:
        p = self._diffuses + 4 * i
        if not vertex._diffuse is None:
          p[0] = vertex._diffuse[0]
          p[1] = vertex._diffuse[1]
          p[2] = vertex._diffuse[2]
          p[3] = vertex._diffuse[3]
        else: # the face use diffuse color, but not for this vertex. but we need ALL the face's vertices to have a color => we take the material diffuse color as default.
          memcpy(&p[0], &vertex._face._material._diffuse[0], 4 * sizeof(float))
          
      if self._option & MODEL_EMISSIVES:
        p = self._emissives + 4 * i
        if not vertex._emissive is None:
          p[0] = vertex._emissive[0]
          p[1] = vertex._emissive[1]
          p[2] = vertex._emissive[2]
          p[3] = vertex._emissive[3]
        else: # the face use diffuse color, but not for this vertex. but we need ALL the face's vertices to have a color => we take the material diffuse color as default.
          p[0] = p[1] = p[2] = 0.0
          p[3] = 1.0
          
        if lights: # Apply static lighting as emissive colors
          for light in lights:
            vertex._into(light, pos)
            if vertex._face._option & FACE2_SMOOTH_LIT: ivertex     ._normal._into(light, vec)
            else:                                       vertex._face._normal._into(light, vec)
            light._static_light_at(pos, vec, self._option & MODEL_STATIC_SHADOW, p)
            
      i = i + 1

    i = 0
    for vertex in vertices:
      ivertex = vertex2ivertex[vertex]
      self._vertexids[i] = vertex2index[ivertex]
      i = i + 1
      
      
    self._faces = <_VertexBufferModelFace*> malloc(self._nb_faces * sizeof(_VertexBufferModelFace))
    i = 0
    for face in faces:
      model_face = self._faces + i
      model_face.option = 0
      face_nb_vertices = len(face._vertices)
      if   face_nb_vertices == 3: model_face.option = model_face.option | FACE_TRIANGLE
      elif face_nb_vertices == 4: model_face.option = model_face.option | FACE_QUAD; self._nb_quads = self._nb_quads + 1
      else:
        print "Face with %s vertices are not supported in model." % face_nb_vertices
        raise ValueError("Face with %s vertices are not supported in model." % face_nb_vertices)
      if face.is_alpha():                   model_face.option = model_face.option | FACE_ALPHA
      if face._option & FACE2_DOUBLE_SIDED: model_face.option = model_face.option | FACE_DOUBLE_SIDED
      if face._option & FACE2_SMOOTH_LIT:   model_face.option = model_face.option | FACE_SMOOTH_LIT
      if not(face._option & FACE2_LIT):     model_face.option = model_face.option | FACE_NON_LIT
      if face._option & NON_SOLID:          model_face.option = model_face.option | FACE_NON_SOLID

      model_face.v[0] = vertex2index[face._vertices[0]]
      model_face.v[1] = vertex2index[face._vertices[1]]
      model_face.v[2] = vertex2index[face._vertices[2]]
      if model_face.option & FACE_QUAD: model_face.v[3] = vertex2index[face._vertices[3]]
      
      if self._option & MODEL_PLANE_EQUATION:
        face._normal._out(model_face.normal)
        p = self._coords + 3 * model_face.v[0]
        model_face.normal[3] = -(p[0] * model_face.normal[0] + p[1] * model_face.normal[1] + p[2] * model_face.normal[2])
        plane_vector_normalize(model_face.normal)
      else:
        face._normal._out(model_face.normal)
        vector_normalize (model_face.normal)
        
      if not face._material in self._materials: self._materials.append(face._material)
      model_face.pack = face._material._pack(model_face.option)
      
      i = i + 1
      
      
    for material in self._materials:
      if material._option & MATERIAL_ALPHA: self._option = self._option | MODEL_HAS_ALPHA
      else:                                 self._option = self._option | MODEL_HAS_OPAQUE
    if (self._option & MODEL_DIFFUSES) and not(self._option == self._option & MODEL_HAS_ALPHA):
      p = self._diffuses
      for i from 0 <= i < self._nb_vertices:
        if p[3] != 1.0:
          self._option = self._option | MODEL_HAS_ALPHA
          break
        p = p + 4
        
        
    cdef _VertexBufferModelFaceGroup* face_group
    self._nb_face_groups        = 0
    self._nb_opaque_face_groups = 0
    self._face_groups           = <_VertexBufferModelFaceGroup*> malloc(sizeof(_VertexBufferModelFaceGroup))
    for k from 0 <= k < 2:
      for j from 0 <= j < self._nb_faces:
        model_face = self._faces + j
        if ((model_face.option & FACE_ALPHA) and (k == 1)) or ((not(model_face.option & FACE_ALPHA)) and (k == 0)):
          for i from 0 <= i < self._nb_face_groups:
            face_group = self._face_groups + i
            if (face_group.material_id == model_face.pack.material_id) and (face_group.option == (model_face.option & VERTEX_BUFFER_OPTIONS)):
              break
          else:
            self._face_groups = <_VertexBufferModelFaceGroup*> realloc(self._face_groups, (self._nb_face_groups + 1) * sizeof(_VertexBufferModelFaceGroup))
            face_group = self._face_groups + self._nb_face_groups
            face_group.material_id = model_face.pack.material_id
            face_group.option      = model_face.option & VERTEX_BUFFER_OPTIONS
            if k == 0: self._nb_opaque_face_groups = self._nb_opaque_face_groups + 1
            self._nb_face_groups = self._nb_face_groups + 1
            
            
    self._face_group_vertices = <short*> malloc(3 * (self._nb_faces + self._nb_quads) * sizeof(short))
    face_group_vertices = self._face_group_vertices
    k = 0
    for i from 0 <= i < self._nb_face_groups:
      face_group = self._face_groups + i
      face_group.start        = k
      face_group.nb_triangles = 0
      for j from 0 <= j < self._nb_faces:
        model_face = self._faces + j
        if (face_group.material_id == model_face.pack.material_id) and (face_group.option == (model_face.option & VERTEX_BUFFER_OPTIONS)):
          face_group_vertices[0]  = <short> model_face.v[0]
          face_group_vertices[1]  = <short> model_face.v[1]
          face_group_vertices[2]  = <short> model_face.v[2]
          face_group_vertices     = face_group_vertices     + 3
          k                       = k                       + 3
          face_group.nb_triangles = face_group.nb_triangles + 1
          if model_face.option & FACE_QUAD:
            face_group_vertices[0]  = <short> model_face.v[2]
            face_group_vertices[1]  = <short> model_face.v[3]
            face_group_vertices[2]  = <short> model_face.v[0]
            face_group_vertices     = face_group_vertices     + 3
            k                       = k                       + 3
            face_group.nb_triangles = face_group.nb_triangles + 1
            
    # find face neighbors
    if self._option & MODEL_NEIGHBORS:
      self._neighbors      = <       int *> malloc(self._nb_faces * 4 * sizeof(int ))
      self._neighbors_side = <signed char*> malloc(self._nb_faces * 4 * sizeof(char))
      self._compute_face_neighbors(faces, vertex2ivertex, ivertex2vertices, self._neighbors, self._neighbors_side)
      
    if self._option & MODEL_SIMPLE_NEIGHBORS: # find face simple neighbors (doesn't take angle into account)
      vertex2ivertex, ivertex2vertices = self._identify_vertices(faces, 360.0) # Re-identify vertices, because for simple neighbors we don't take angle into account
      self._simple_neighbors      = <       int *> malloc(self._nb_faces * 4 * sizeof(int ))
      self._simple_neighbors_side = <signed char*> malloc(self._nb_faces * 4 * sizeof(char))
      self._compute_face_neighbors(faces, vertex2ivertex, ivertex2vertices, self._simple_neighbors, self._simple_neighbors_side)
      
    # Build sphere
    if self._nb_vertices > 0:
      self._sphere = <float*> malloc(4 * sizeof(float))
      sphere_from_points(self._sphere, self._coords, self._nb_vertices)
      self._option = self._option | MODEL_HAS_SPHERE
      
  cdef void _get_box(self, float* box, float* matrix):
    cdef float* coord
    cdef float  coord2[3]
    
    coord = self._coords
    for i from 0 <= i < self._nb_vertices:
      point_by_matrix_copy(coord2, coord, matrix)
      
      if coord2[0] < box[0]: box[0] = coord2[0]
      if coord2[1] < box[1]: box[1] = coord2[1]
      if coord2[2] < box[2]: box[2] = coord2[2]
      if coord2[0] > box[3]: box[3] = coord2[0]
      if coord2[1] > box[4]: box[4] = coord2[1]
      if coord2[2] > box[5]: box[5] = coord2[2]
      
      coord = coord + 3
      
      
  cdef void _init_vertex_buffers(self):
    cdef int*                    faces
    cdef _VertexBufferModelFace* face
    cdef int                     i, alpha, offset
    
    glGenBuffers(1, &self._face_buffer)
    glGenBuffers(1, &self._vertex_buffer)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._face_buffer)
    glBindBuffer(GL_ARRAY_BUFFER        , self._vertex_buffer)
    
    self._buffer_sizeof_vertex = 6 * sizeof(float)
    if self._option & MODEL_DIFFUSES:   self._buffer_sizeof_vertex = self._buffer_sizeof_vertex + 4 * sizeof(float)
    if self._option & MODEL_EMISSIVES:  self._buffer_sizeof_vertex = self._buffer_sizeof_vertex + 4 * sizeof(float)
    if self._option & MODEL_TEXCOORDS:  self._buffer_sizeof_vertex = self._buffer_sizeof_vertex + 2 * sizeof(float)
    
    if self._option & MODEL_STATIC_FACE:   glBufferData(GL_ELEMENT_ARRAY_BUFFER, 3 * (self._nb_faces + self._nb_quads) * sizeof(short), self._face_group_vertices, GL_STATIC_DRAW)
    else:                                  glBufferData(GL_ELEMENT_ARRAY_BUFFER, 3 * (self._nb_faces + self._nb_quads) * sizeof(short), self._face_group_vertices, GL_DYNAMIC_DRAW)
    if self._option & MODEL_STATIC_VERTEX: glBufferData(GL_ARRAY_BUFFER, self._nb_vertices * self._buffer_sizeof_vertex, NULL, GL_STATIC_DRAW)
    else:                                  glBufferData(GL_ARRAY_BUFFER, self._nb_vertices * self._buffer_sizeof_vertex, NULL, GL_DYNAMIC_DRAW)
    
    self._vnormal_offset = 3 * self._nb_vertices * sizeof(float)
    offset = self._vnormal_offset + 3 * self._nb_vertices * sizeof(float)
    glBufferSubData(GL_ARRAY_BUFFER, 0                   , 3 * self._nb_vertices * sizeof(float), self._coords  )
    glBufferSubData(GL_ARRAY_BUFFER, self._vnormal_offset, 3 * self._nb_vertices * sizeof(float), self._vnormals)
    
    if self._option & MODEL_DIFFUSES:
      self._diffuse_offset = offset
      glBufferSubData(GL_ARRAY_BUFFER, self._diffuse_offset, 4 * self._nb_vertices * sizeof(float), self._diffuses)
      offset = offset + 4 * self._nb_vertices * sizeof(float)
      
    if self._option & MODEL_EMISSIVES:
      self._emissive_offset = offset
      glBufferSubData(GL_ARRAY_BUFFER, self._emissive_offset, 4 * self._nb_vertices * sizeof(float), self._emissives)
      offset = offset + 4 * self._nb_vertices * sizeof(float)
      
    if self._option & MODEL_TEXCOORDS:
      self._texcoord_offset = offset
      glBufferSubData(GL_ARRAY_BUFFER, self._texcoord_offset, 2 * self._nb_vertices * sizeof(float), self._texcoords)
      offset = offset + 2 * self._nb_vertices * sizeof(float)
      
    if self._option & MODEL_TEXCOORDS2:
      glGenBuffers(1, &self._texcoords2_buffer)
      glBindBuffer(GL_ARRAY_BUFFER, self._texcoords2_buffer)
      glBufferData(GL_ARRAY_BUFFER, 2 * self._nb_vertices * sizeof(float), NULL, GL_DYNAMIC_DRAW)
      
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ARRAY_BUFFER        , 0)
    
    self._option = self._option | MODEL_INITED
    
  cdef void _batch(self, _Body body):
    if body._option & HIDDEN: return
    
    cdef float sphere[4]
    if self._option & MODEL_HAS_SPHERE:
      sphere_by_matrix_copy(sphere, self._sphere, body._root_matrix())
      if sphere_in_frustum(renderer.root_frustum, sphere) == 0: return
      
    if self._option & MODEL_HAS_OPAQUE: renderer._batch(renderer.opaque    , body._data, body, NULL)
    if self._option & MODEL_HAS_ALPHA : renderer._batch(renderer.alpha     , body._data, body, NULL)
    if self._option & MODEL_OUTLINE:    renderer._batch(renderer.secondpass, body._data, body, NULL)
    
  cdef void _render(self, _Body body):
    cdef _VertexBufferModelFaceGroup* face_groupe
    cdef int i, start, end
    
    cdef dict material_programs
    material_programs = (<_VertexBufferedModelData> (body._data))._material_programs
    cdef _Material material
    cdef _Program  program
    
    
    if renderer.state == RENDERER_STATE_SECONDPASS:
      frustum = renderer._frustum(body)
      self._render_outline(body._data, frustum)
      
    else:
      if not(self._option & MODEL_INITED): self._init_vertex_buffers()
      
      model_option_activate(self._option)
      if body._option & LEFTHANDED: glFrontFace(GL_CW)
      
      glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._face_buffer)
      glBindBuffer(GL_ARRAY_BUFFER        , self._vertex_buffer)
      glEnableClientState(GL_VERTEX_ARRAY)
      glEnableClientState(GL_NORMAL_ARRAY)
      glVertexPointer(3, GL_FLOAT, 0, BUFFER_OFFSET(0))
      glNormalPointer(   GL_FLOAT, 0, BUFFER_OFFSET(self._vnormal_offset))
      
      if self._option & MODEL_DIFFUSES:
        glEnableClientState(GL_COLOR_ARRAY)
        glColorPointer(4, GL_FLOAT, 0, BUFFER_OFFSET(self._diffuse_offset))
        
      if self._option & MODEL_EMISSIVES:
        IF OPENGL == "full":
          glColorMaterial(GL_FRONT_AND_BACK, GL_EMISSION)
        glEnableClientState(GL_COLOR_ARRAY)
        glColorPointer(4, GL_FLOAT, 0, BUFFER_OFFSET(self._emissives_offset))
        IF OPENGL == "full":
          glColorMaterial(GL_FRONT_AND_BACK, GL_DIFFUSE)
        
      if self._option & MODEL_TEXCOORDS:
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glTexCoordPointer(2, GL_FLOAT, 0, BUFFER_OFFSET(self._texcoord_offset))
        
      if self._option & MODEL_TEXCOORDS2:
        glClientActiveTexture(GL_TEXTURE1)
        glBindBuffer(GL_ARRAY_BUFFER, self._texcoords2_buffer)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glTexCoordPointer(2, GL_FLOAT, 0, BUFFER_OFFSET(0))
        glClientActiveTexture(GL_TEXTURE0)
        glBindBuffer(GL_ARRAY_BUFFER, self._vertex_buffer)
        
      if renderer.state == RENDERER_STATE_OPAQUE:
        start = 0
        end   = self._nb_opaque_face_groups
      else:
        start = self._nb_opaque_face_groups
        end   = self._nb_face_groups
        
      for i from start <= i < end:
        face_group = self._face_groups + i
        face_option_activate(face_group.option)
        
        #(<_Material> (face_group.material_id))._activate()
        #material = (<_Material> (face_group.material_id))
        material = (<_Material> (<void*> (face_group.material_id)))
        material._activate()
        program  = material_programs[material]
        program._activate()
        program._set_all_user_params(body, self._mini_shaders, material._mini_shaders)
        
        glDrawElements(GL_TRIANGLES, 3 * face_group.nb_triangles, GL_UNSIGNED_SHORT, BUFFER_OFFSET(face_group.start * sizeof(short)))
        face_option_inactivate(face_group.option)
        
      glDisableClientState(GL_VERTEX_ARRAY)
      glDisableClientState(GL_NORMAL_ARRAY)
      
      if self._option & MODEL_DIFFUSES: glDisableClientState(GL_COLOR_ARRAY)
      if self._option & MODEL_EMISSIVES:
        IF OPENGL == "full":
          glColorMaterial(GL_FRONT_AND_BACK, GL_EMISSION)
        glDisableClientState(GL_COLOR_ARRAY)
        IF OPENGL == "full":
          glColorMaterial(GL_FRONT_AND_BACK, GL_DIFFUSE)
          
      if self._option & MODEL_TEXCOORDS: glDisableClientState(GL_TEXTURE_COORD_ARRAY)
      
      if self._option & MODEL_TEXCOORDS2:
        glClientActiveTexture(GL_TEXTURE1)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glClientActiveTexture(GL_TEXTURE0)
        
      glBindBuffer(GL_ARRAY_BUFFER        , 0)
      glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
      
      if body._option & LEFTHANDED:  glFrontFace(GL_CCW)
      model_option_inactivate(self._option)


    
  cdef void _raypick(self, RaypickData data, CoordSyst parent):
    cdef float* raydata
    cdef int    i
    raydata = parent._raypick_data(data)
    if (self._option & MODEL_HAS_SPHERE) and (sphere_raypick(raydata, self._sphere) == 0): return
    for i from 0 <= i < self._nb_faces:
      self._face_raypick(self._faces + i, raydata, data, parent)
      
  cdef int _raypick_b(self, RaypickData data, CoordSyst parent):
    cdef float* raydata
    cdef int    i
    raydata = parent._raypick_data(data)
    if (self._option & MODEL_HAS_SPHERE) and (sphere_raypick(raydata, self._sphere) == 0): return 0
    for i from 0 <= i < self._nb_faces:
      if self._face_raypick_b(self._faces + i, raydata, data): return 1
    return 0
  
  cdef void _face_raypick(self, _VertexBufferModelFace* face, float* raydata, RaypickData data, CoordSyst parent):
    cdef float z, root_z
    cdef int   r, option
    
    option = data.option
    if  face.option & FACE_NON_SOLID: return
    if (face.option & FACE_DOUBLE_SIDED) and (option & RAYPICK_CULL_FACE): option = option - RAYPICK_CULL_FACE
    if  face.option & FACE_QUAD:
      r = quad_raypick    (raydata, self._coords + 3 * face.v[0], self._coords + 3 * face.v[1], self._coords + 3 * face.v[2], self._coords + 3 * face.v[3], face.normal, option, &z)
    else:
      r = triangle_raypick(raydata, self._coords + 3 * face.v[0], self._coords + 3 * face.v[1], self._coords + 3 * face.v[2], face.normal, option, &z)
      
    if r != 0:
      root_z = parent._distance_out(z)
      if (data.result_coordsyst is None) or (fabs(root_z) < fabs(data.root_result)):
        data.result           = z
        data.root_result      = root_z
        data.result_coordsyst = parent
        if   r == RAYPICK_DIRECT: memcpy(&data.normal[0], face.normal, 3 * sizeof(float))
        elif r == RAYPICK_INDIRECT:
          if face.option & FACE_DOUBLE_SIDED:
            data.normal[0] = -face.normal[0]
            data.normal[1] = -face.normal[1]
            data.normal[2] = -face.normal[2]
          else: memcpy(&data.normal[0], face.normal, 3 * sizeof(float))
          
  cdef int _face_raypick_b(self, _VertexBufferModelFace* face, float* raydata, RaypickData data):
    cdef float z
    cdef int   option
    
    option = data.option
    if  face.option & FACE_NON_SOLID: return 0
    if (face.option & FACE_DOUBLE_SIDED) and (option & RAYPICK_CULL_FACE): option = option - RAYPICK_CULL_FACE
    if  face.option & FACE_QUAD:
      if quad_raypick    (raydata, self._coords + 3 * face.v[0], self._coords + 3 * face.v[1], self._coords + 3 * face.v[2], self._coords + 3 * face.v[3], face.normal, option, &z) != 0: return 1
    else:
      if triangle_raypick(raydata, self._coords + 3 * face.v[0], self._coords + 3 * face.v[1], self._coords + 3 * face.v[2], face.normal, option, &z) != 0: return 1
    return 0
  
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, CoordSyst parent):
    if not(self._option & MODEL_HAS_SPHERE) or (sphere_distance_sphere(sphere, self._sphere) < 0.0):
      chunk_add_ptr(items, <void*> parent)

      
  cdef void _render_outline(self, _VertexBufferedModelData data, Frustum* frustum):
    cdef int                     i, j, k, ns, nb, buf
    cdef float                   d
    cdef _VertexBufferModelFace* face
    cdef _VertexBufferModelFace  neighbor_face
    cdef _Program                program
    
    # Compute outline width, which depends on distance to camera
    d = sphere_distance_point(self._sphere, frustum.position) * self._outline_attenuation
    if d < 1.0: d = self._outline_width
    else:
      d = self._outline_width / d
      if d < 2.0: d = 2.0
      
    # mark faces as either front or back
    for i from 0 <= i < self._nb_faces:
      face  = self._faces + i
      if face.normal[0] * frustum.position[0] + face.normal[1] * frustum.position[1] + face.normal[2] * frustum.position[2] + face.normal[3] > 0.0: face.option = (face.option & ~FACE_BACK ) | FACE_FRONT
      else:                                                                                                                                         face.option = (face.option & ~FACE_FRONT) | FACE_BACK
      
    _DEFAULT_MATERIAL._activate()
    
    glLineWidth(d)
    glColor4fv (self._outline_color)
    glEnable   (GL_BLEND)
    #glEnable   (GL_LINE_SMOOTH) # No longer needed with fullscreen antialiasing
    glDisable  (GL_LIGHTING)
    glDepthFunc(GL_LEQUAL)
    glPointSize(d * 0.7)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, _tmp_face_buffer)
    glBindBuffer(GL_ARRAY_BUFFER, self._vertex_buffer)
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, BUFFER_OFFSET(0))
    
    program = data._material_programs[_DEFAULT_MATERIAL]
    program._activate()
    program._set_all_user_params(data._body, self._mini_shaders, _DEFAULT_MATERIAL._mini_shaders)
    
    # find and draw edges
    buf = 0
    for i from 0 <= i < self._nb_faces:
      face = self._faces + i
      if face.option & FACE_ALPHA: continue
      
      if face.option & FACE_QUAD: nb = 4
      else:                       nb = 3
      
      if face.option & FACE_SMOOTH_LIT:
        if face.option & FACE_DOUBLE_SIDED:
          for j from 0 <= j < nb:
            k = self._neighbors[4 * i + j]
            if k == -1: # No neighbor, but double-sided face => the face is its own neighbor
              _tmp_faces[buf] = face.v[j] # draw edge between vertices j and j + 1
              if j < nb - 1: _tmp_faces[buf + 1] = face.v[j + 1]
              else:          _tmp_faces[buf + 1] = face.v[0]
              buf = buf + 2
              
            else:
              ns = self._neighbors_side[4 * i + j]
              neighbor_face = self._faces[k]
              if (
                (ns == -1) and (((face.option & FACE_FRONT) and (neighbor_face.option & FACE_BACK )) or ((face.option & FACE_BACK) and (neighbor_face.option & FACE_FRONT)))
                  ) or (
                (ns ==  1) and (((face.option & FACE_FRONT) and (neighbor_face.option & FACE_FRONT)) or ((face.option & FACE_BACK) and (neighbor_face.option & FACE_BACK)))
                ):
                _tmp_faces[buf] = face.v[j] # draw edge between vertices j and j + 1
                if j < nb - 1: _tmp_faces[buf + 1] = face.v[j + 1]
                else:          _tmp_faces[buf + 1] = face.v[0]
                buf = buf + 2
                
        else:
          if face.option & FACE_FRONT:
            for j from 0 <= j < nb:
              k = self._neighbors[4 * i + j]
              if (k == -1) or (self._faces[k].option & FACE_BACK): # test if neighbors are back
                _tmp_faces[buf] = face.v[j] # draw edge between vertices j and j + 1
                if j < nb - 1: _tmp_faces[buf + 1] = face.v[j + 1]
                else:          _tmp_faces[buf + 1] = face.v[0]
                buf = buf + 2
                
      else: # Not smoothlit
        if (face.option & FACE_FRONT) or (face.option & FACE_DOUBLE_SIDED):
          for j from 0 <= j < nb:
            _tmp_faces[buf] = face.v[j] # draw edge between vertices j and j + 1
            if j < nb - 1: _tmp_faces[buf + 1] = face.v[j + 1]
            else:          _tmp_faces[buf + 1] = face.v[0]
            buf = buf + 2
            
      if buf >= 180: # A face has at maximum 4 edges => 8 vertex => render now !
        glBufferSubData(GL_ELEMENT_ARRAY_BUFFER, 0, buf * sizeof(short), _tmp_faces)
        glDrawElements(GL_LINES, buf, GL_UNSIGNED_SHORT, BUFFER_OFFSET(0))
        glDrawElements(GL_POINTS, buf, GL_UNSIGNED_SHORT, BUFFER_OFFSET(0))
        buf = 0
        
    if buf > 0: # Some lines are pending, draw them !
      glBufferSubData(GL_ELEMENT_ARRAY_BUFFER, 0, buf * sizeof(short), _tmp_faces)
      glDrawElements(GL_LINES, buf, GL_UNSIGNED_SHORT, BUFFER_OFFSET(0))
      glDrawElements(GL_POINTS, buf, GL_UNSIGNED_SHORT, BUFFER_OFFSET(0))
      buf = 0
    
    glDisableClientState(GL_VERTEX_ARRAY)
    glBindBuffer (GL_ARRAY_BUFFER        , 0)    
    glBindBuffer (GL_ELEMENT_ARRAY_BUFFER, 0)
    glLineWidth(1.0) # Reset to
    glPointSize(1.0) # default
    glEnable   (GL_LIGHTING)
    glDepthFunc(GL_LESS)
    glColor4fv (white)














cdef void model_option_activate(int option):
  if option & MODEL_STATIC_LIT: disable_static_lights()
  
cdef void model_option_inactivate(int option):
  if option & MODEL_STATIC_LIT: enable_static_lights()
  
cdef void face_option_activate(int option):
  if option & FACE_DOUBLE_SIDED:
    glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
    glEnable(GL_VERTEX_PROGRAM_TWO_SIDE)
    glDisable(GL_CULL_FACE)
  if option & FACE_NON_LIT: glDisable(GL_LIGHTING)
  
cdef void face_option_inactivate(int option):
  if option & FACE_DOUBLE_SIDED:
    glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_FALSE)
    glDisable(GL_VERTEX_PROGRAM_TWO_SIDE)
    glEnable(GL_CULL_FACE)
  if option & FACE_NON_LIT: glEnable(GL_LIGHTING)
  
    



      

cdef class _ModelData(_Model):
  def __init__(self, _Body body, _Model model): pass


cdef class _VertexBufferedModelData(_ModelData):
  #cdef int    _option
  #cdef _Body  _body
  #cdef _Model _model
  #cdef dict   _material_programs
  
  def __init__(self, _Body body, _Model model):
    self._body              = body
    self._model             = model
    self._option            = 0
    self._material_programs = {}
    
  cdef __getcstate__(self):
    return self._body, self._model
  
  cdef void __setcstate__(self, cstate):
    self._body, self._model = cstate
    self._option            = 0
    self._material_programs = {}
    
  cdef list _get_materials(self): return self._model._get_materials()
  
  cdef void _invalidate_shaders(self):
    self._option = self._option & ~MODELDATA_SHADERS_VALID
    
  cdef void _batch(self, _Body body):
    cdef list      mini_shaders
    cdef CoordSyst ancestor
    cdef _Material material

    if not(self._option & MODELDATA_SHADERS_VALID):
      mini_shaders = self._model._get_mini_shaders()[:]
      ancestor     = body
      while ancestor:
        for mini_shader in ancestor._mini_shaders: mini_shaders.insert(0, mini_shader)
        ancestor = ancestor._parent

      for material in self._model._get_materials():
        self._material_programs[material] = mini_shaders_2_program(mini_shaders + material._mini_shaders)

      self._option = self._option | MODELDATA_SHADERS_VALID
      
    self._model._batch(body)
    
  cdef void _render              (self, _Body body): self._model._render(body)
  cdef void _get_box             (self, float* box, float* matrix): self._model._get_box(box, matrix)
  
  cdef void _raypick             (self, RaypickData raypick_data, CoordSyst raypickable):
    self._model._raypick  (raypick_data, raypickable)
    
  cdef int  _raypick_b           (self, RaypickData raypick_data, CoordSyst raypickable):
    return self._model._raypick_b(raypick_data, raypickable)
  
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, CoordSyst parent):
    self._model._collect_raypickables(items, rsphere, sphere, parent)
  
