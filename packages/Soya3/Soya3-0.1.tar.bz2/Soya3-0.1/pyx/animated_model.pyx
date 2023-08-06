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

import os.path
import soya3 as soya

cdef int       _cal3d_nb_faces = 0
cdef int*      _cal3d_facesides = NULL


cdef void quit_cal3d():
  free(_cal3d_facesides)
  
def load_raw_image(filename):
  """Loads a ".raw" image file, which are used by Cal3D example (see cal3d_data).
Returns a Soya image object, suitable for model.material.image."""
  cdef int width, height, nb_colors, line_length, y
  import struct, array
  
  f = open(filename)
  width, height, nb_colors = struct.unpack("iii", f.read(12))
  data = array.array("c", f.read())
  
  # Flip texture around y-axis (-> opengl-style).
  data2 = array.array("c", " " * len(data))
  line_length = width * nb_colors
  for y from 0 <= y < height:
    data2[y * line_length : (y + 1) * line_length] = data[(height - y - 1) * line_length : (height - y) * line_length]
    
  return Image(data2.tostring(), width, height, nb_colors)

def parse_cal3d_cfg_file(filename):
  """Reads a the Cal3D .cfg file, and creates and returns a Cal3D model from it."""
#  import soya3 as soya
  cdef _AnimatedModel model
  cdef int         i
  
  lines = open(filename).read().split("\n")
  if lines[0] == "LOD":
    return "LOD" # Hack
    
  model                = soya.AnimatedModel()
  dirname              = os.path.dirname(filename)
  model.filename       = os.path.basename(dirname)
  model._full_filename = filename
  
  # Do NOT load several time the same materials / ...
  # (some exporter does import several time the same material)
  already_done        = {}
  
  for line in lines:
    if line and (line[0] != "#"):
      parts = line.split("=")
      if len(parts) == 2:
        key, value = parts
        value = value.rstrip()
        
        if already_done.get((key, value)): continue
        already_done[key, value] = 1
        
        if   key == "skeleton"           : model.load_skeleton (os.path.join(dirname, value))
        elif key == "mesh"               : model.load_mesh     (os.path.join(dirname, value))
        elif key == "material"           : model.load_material (os.path.join(dirname, value))
        elif key == "animation"          : model.load_animation(os.path.join(dirname, value))
        elif key == "double_sided"       : model.double_sided        = int(value)
        elif key == "sphere"             : model.sphere              = map(float, value.split())
        elif key == "outline_width"      : model.outline_width       = float(value)
        elif key == "outline_attenuation": model.outline_attenuation = float(value)
        elif key == "outline_color"      : model.outline_color       = [float(x) for x in value.split(",")]
        elif key == "mini_shader"        : model.add_mini_shader(soya.mini_shader.short_name_2_mini_shader(value))
        
        else: print "Warning: unknows Cal3D .cfg tag:   %s=%s" % (key, value)
  model.build_materials()
  return model

    

cdef class _Cal3dSubMesh:
  #cdef int       _option, _mesh, _submesh
  #cdef _Material _material
  #cdef int       _nb_faces, _nb_vertices
  #cdef short*    _faces
  #cdef int*      _face_neighbors
  #cdef GLuint    _face_buffer

  def __dealloc__(self):
    if self._faces          != NULL: free(self._faces)
    if self._face_neighbors != NULL: free(self._face_neighbors)
    
  cdef _build(self, _AnimatedModel model, CalRenderer* cal_renderer, CalCoreModel* cal_core_model, CalCoreMesh* cal_core_mesh, int mesh, int submesh):
    global _cal3d_nb_faces
    global _tmp_vertices, _cal3d_facesides
    
    cdef CalCoreSubmesh* cal_core_submesh
    cdef float*          vertices
    cdef int*            faces
    cdef int             i
    
    self._mesh       = mesh
    self._submesh    = submesh
    self._material   = model._materials[CalCoreSubmesh_GetCoreMaterialThreadId(CalCoreMesh_GetCoreSubmesh(cal_core_mesh, submesh))]
    
    cal_core_submesh = CalCoreMesh_GetCoreSubmesh(cal_core_mesh, submesh)
    
    # get faces
    self._nb_faces = CalCoreSubmesh_GetFaceCount(cal_core_submesh)
    self._faces = <short*> malloc(self._nb_faces * 3 * sizeof(short))
    faces       = <int  *> malloc(self._nb_faces * 3 * sizeof(int  ))
    
    CalRenderer_GetFaces(cal_renderer, faces)

    for i from 0 <= i < self._nb_faces * 3: self._faces[i] = <short> faces[i]
    free(faces)
    
    if _cal3d_nb_faces < self._nb_faces:
      _cal3d_facesides = <int*>   realloc(_cal3d_facesides, self._nb_faces * sizeof(int))
      _cal3d_nb_faces = self._nb_faces
      
    # get vertices
    self._nb_vertices = CalCoreSubmesh_GetVertexCount(cal_core_submesh)
    
  cdef void _init_vertex_buffers(self):
    glGenBuffers(1, &self._face_buffer)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self._face_buffer)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, 3 * self._nb_faces * sizeof(short), self._faces, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    
  cdef void _build_neighbors(self, full_filename, float* coords):
    cdef int    i, j, k, l
    cdef short  p1, p2
    cdef float* coord1
    cdef float* coord2
    cdef Chunk* chunk
    
    self._option = self._option | CAL3D_NEIGHBORS
    
    self._face_neighbors = <int*> malloc(self._nb_faces * 3 * sizeof(int))
    
    cache_filename = os.path.join(os.path.dirname(full_filename), "neighbors_%s-%s" % (self._mesh, self._submesh))
    
    # Read from the cache file, if it exist.
    if os.path.exists(cache_filename):
      if os.path.getmtime(cache_filename) > os.path.getmtime(full_filename):
        file = open(cache_filename, "rb")
        chunk = string_to_chunk(file.read())
        chunk_get_ints_endian_safe(chunk, self._face_neighbors, 3 * self._nb_faces)
        drop_chunk(chunk)
        return
      
    print "* Soya * Computing neighbor for Cal3D model, and caching the result in file %s..." % cache_filename
    
    for i from 0 <= i < self._nb_faces:
      for k from 0 <= k < 3:
        p1 = self._faces[3 * i + k]
        if k == 2: p2 = self._faces[3 * i]
        else:      p2 = self._faces[3 * i + k + 1]
        
        coord1 = coords + 3 * p1
        coord2 = coords + 3 * p2
        
        for j from 0 <= j < self._nb_faces:
          if i == j: continue
          
          if ((p1 == self._faces[3 * j]) or (p1 == self._faces[3 * j + 1]) or (p1 == self._faces[3 * j + 2])) and ((p2 == self._faces[3 * j]) or (p2 == self._faces[3 * j + 1]) or (p2 == self._faces[3 * j + 2])):
            self._face_neighbors[3 * i + k] = j
            break
          
          if ((point_distance_to(coord1, coords + 3 * self._faces[3 * j]) < EPSILON) or (point_distance_to(coord1, coords + 3 * self._faces[3 * j + 1]) < EPSILON) or (point_distance_to(coord1, coords + 3 * self._faces[3 * j + 2]) < EPSILON)) and ((point_distance_to(coord2, coords + 3 * self._faces[3 * j]) < EPSILON) or (point_distance_to(coord2, coords + 3 * self._faces[3 * j + 1]) < EPSILON) or (point_distance_to(coord2, coords + 3 * self._faces[3 * j + 2]) < EPSILON)):
            self._face_neighbors[3 * i + k] = j
            break
        else:
          self._face_neighbors[3 * i + k] = -1 # No neighbor
          
    # Try to save the neighbors
    try: file = open(cache_filename, "wb")
    except:
      print "* Soya * Can't cache Cal3D neighbor face data in file %s" % cache_filename
      return
    
    chunk = get_chunk()
    chunk_add_ints_endian_safe(chunk, self._face_neighbors, 3 * self._nb_faces)
    file.write(drop_chunk_to_string(chunk))
    
    
cdef class _AnimatedModel(_Model):
  #cdef int           _option
  #cdef int           _nb_faces, _nb_vertices
  #cdef float         _sphere[4]
  #cdef dict          _meshes, _animations
  #cdef list          _materials, _submeshes
  #cdef               _full_filename
  #cdef list          _mini_shaders
  #cdef CalCoreModel* _core_model
  #cdef float         _outline_color[4]
  #cdef float         _outline_width, _outline_attenuation
  
  cdef list _get_mini_shaders(self): return self._mini_shaders
  cdef list _get_materials   (self):
    if self._option & CAL3D_OUTLINE: return self._materials + [_DEFAULT_MATERIAL]
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
    
  property filename:
    def __get__(self): return self._filename
    
  property full_filename:
    def __get__(self): return self._full_filename
    
  property materials:
    def __get__(self): return self._materials
    
  property meshes:
    def __get__(self): return self._meshes
    
  property animations:
    def __get__(self): return self._animations
    
  property sphere:
    def __get__(self): return self._sphere[0], self._sphere[1], self._sphere[2], self._sphere[3]
    def __set__(self, sphere): self._sphere[0], self._sphere[1], self._sphere[2], self._sphere[3] = sphere
    
  property double_sided:
    def __get__(self): return self._option & CAL3D_DOUBLE_SIDED
    def __set__(self, int x):
      if x: self._option = self._option |  CAL3D_DOUBLE_SIDED
      else: self._option = self._option & ~CAL3D_DOUBLE_SIDED
      
  property outline_width:
    def __get__(self): return self._outline_width
    def __set__(self, float x):
      self._outline_width = x
      if self._outline_width > 0.0: self._option |=  CAL3D_OUTLINE
      else:                         self._option &= ~CAL3D_OUTLINE

  property outline_color:
    def __get__(self): return self._outline_color[0], self._outline_color[1], self._outline_color[2], self._outline_color[3]
    def __set__(self, color): self._outline_color[0], self._outline_color[1], self._outline_color[2], self._outline_color[3] = color
  
  property outline_attenuation:
    def __get__(self): return self._outline_attenuation
    def __set__(self, float x): self._outline_attenuation = x
    
  def __init__(self):
    self._meshes       = {} # Maps mesh / animation names to the
    self._animations   = {} # corresponding ID (index)
    self._materials    = []
    self._submeshes    = []
    self._mini_shaders = []
    self._sphere[3]    = -1.0
    self._core_model   = CalCoreModel_New("")
    self._outline_color[0] = self._outline_color[1] = self._outline_color[2] = 0.0
    self._outline_color[3] = 1.0
    if self._core_model == NULL: raise RuntimeError("CalCoreModel_Create failed: %s" % CalError_GetLastErrorDescription())
    
    self._option = CAL3D_DOUBLE_SIDED
    
  cdef void _instanced(self, _Body body, opt):
    body._data = _AnimatedModelData(body, self, opt)
    
    
  cdef void _build_submeshes(self):
    cdef CalRenderer*    cal_renderer
    cdef CalModel*       cal_model
    cdef CalCoreMesh*    cal_core_mesh
    cdef _Cal3dSubMesh   my_submesh
    cdef int             nb_mesh, nb_submesh, i, j
    
    cal_model = CalModel_New(self._core_model)
    nb_mesh = CalCoreModel_GetCoreMeshCount(self._core_model)
    for i from 0 <= i < nb_mesh: CalModel_AttachMesh(cal_model, i)
    CalModel_SetMaterialSet(cal_model, 0)
    
    cal_renderer = CalModel_GetRenderer(cal_model)
    if CalRenderer_BeginRendering(cal_renderer) == 0: raise RuntimeError("CalRenderer_BeginRendering failed: %s" % CalError_GetLastErrorDescription())
    
    self._nb_faces = self._nb_vertices = 0
    
    for i from 0 <= i < nb_mesh:
      cal_core_mesh = CalCoreModel_GetCoreMesh(self._core_model, i)
      nb_submesh    = CalCoreMesh_GetCoreSubmeshCount(cal_core_mesh)
      for j from 0 <= j < nb_submesh:
        CalRenderer_SelectMeshSubmesh(cal_renderer, i, j)
        # create my new submesh
        my_submesh = _Cal3dSubMesh()
        my_submesh._build(self, cal_renderer, self._core_model, cal_core_mesh, i, j)
        self._submeshes.append(my_submesh)
        self._nb_faces    = self._nb_faces    + my_submesh._nb_faces
        self._nb_vertices = self._nb_vertices + my_submesh._nb_vertices
        if my_submesh._material._option & MATERIAL_ALPHA: self._option = self._option | CAL3D_ALPHA
        
    CalRenderer_EndRendering(cal_renderer)
    CalModel_Delete (cal_model)
    
    _set_tmp_buffer_min_size(self._nb_vertices)
    
    self._option = self._option | CAL3D_INITED
    
#  cdef void _set_face_neighborhood(self, int index1, int index2, GLfloat* vertices):
#    # XXX TODO
#    pass
  
  
  cdef void _batch(self, _Body body):
    cdef _AnimatedModelData data
    cdef float sphere[4]
    data   = <_AnimatedModelData> body._data
    
    #data._build_vertices(0) # XXX descendre après le test de sphère ???
    if not body._option & HIDDEN:
      if self._sphere[3] != -1.0:
        sphere_by_matrix_copy(sphere, self._sphere, body._root_matrix())
        if sphere_in_frustum(renderer.root_frustum, sphere) == 0: return
        
      # Ok, we render the Cal3D model ; rendering implies computing vertices
      #data._build_vertices(0) # XXX descendre après le test de sphère ???
      if data._bones_ok == 0: data._build_bones()
      
      if self._option & CAL3D_ALPHA:   renderer._batch(renderer.alpha     , self, body, NULL)
      else:                            renderer._batch(renderer.opaque    , self, body, NULL)
      if self._option & CAL3D_OUTLINE: renderer._batch(renderer.secondpass, self, body, NULL)
      
  cdef void _render(self, _Body body):
    global _tmp_vertices
    
    cdef _AnimatedModelData data
    cdef _Cal3dSubMesh      submesh
    cdef _Program           program
    cdef CalRenderer*       cal_renderer
    cdef GLfloat*           coords
    cdef GLfloat*           vnormals
    cdef GLfloat*           texcoords
    cdef int                j
    cdef float*             plane
    cdef Frustum*           frustum
    
    data = body._data
    
    if renderer.state == RENDERER_STATE_SECONDPASS:
      if data._face_plane_ok == 0: data._build_face_planes()
      
      frustum  = renderer._frustum(body)
      coords   = data._coords
      vnormals = data._vnormals
      plane    = data._face_planes
      for submesh in self._submeshes:
        if data._attached_meshes[submesh._mesh]:
          if not (submesh._option & CAL3D_NEIGHBORS): submesh._build_neighbors(self._full_filename, coords)
          self._render_outline(data, submesh, frustum, coords, vnormals, plane)
        coords   = coords   + 3 * submesh._nb_vertices
        vnormals = vnormals + 3 * submesh._nb_vertices
        plane    = plane    + 4 * submesh._nb_faces
      return
    
    if not self._option & CAL3D_GL_INITED:
      for submesh in self._submeshes: submesh._init_vertex_buffers()
      self._option = self._option | CAL3D_GL_INITED
      
    cal_renderer = CalModel_GetRenderer(data._cal_model)
    
    if (CalRenderer_BeginRendering(cal_renderer) == 0):
      print "error 1", CalError_GetLastErrorDescription()
      raise RuntimeError("CalRenderer_BeginRendering failed: %s" % CalError_GetLastErrorDescription())
    
    glBindBuffer(GL_ARRAY_BUFFER, _tmp_vertex_buffer)
    
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    if body._option & LEFTHANDED: glFrontFace(GL_CW)
    if self._option & CAL3D_DOUBLE_SIDED:
      glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
      glEnable(GL_VERTEX_PROGRAM_TWO_SIDE)
      glDisable(GL_CULL_FACE)
      
    
    data._update()
    
    coords    = data._coords
    vnormals  = data._vnormals
    texcoords = _tmp_vertices
    for submesh in self._submeshes:
      if data._attached_meshes[submesh._mesh]:
        CalRenderer_SelectMeshSubmesh    (cal_renderer, submesh._mesh, submesh._submesh)
        CalRenderer_GetVertices          (cal_renderer, coords)
        CalRenderer_GetNormals           (cal_renderer, vnormals)
        CalRenderer_GetTextureCoordinates(cal_renderer, 0, texcoords)
        
        glBufferSubData(GL_ARRAY_BUFFER, 0                                       , 3 * submesh._nb_vertices * sizeof(float), coords)
        glBufferSubData(GL_ARRAY_BUFFER, 3 * submesh._nb_vertices * sizeof(float), 3 * submesh._nb_vertices * sizeof(float), vnormals)
        glBufferSubData(GL_ARRAY_BUFFER, 6 * submesh._nb_vertices * sizeof(float), 2 * submesh._nb_vertices * sizeof(float), texcoords)
        glVertexPointer  (3, GL_FLOAT, 0, BUFFER_OFFSET(0))
        glNormalPointer  (   GL_FLOAT, 0, BUFFER_OFFSET(3 * submesh._nb_vertices * sizeof(float)))
        glTexCoordPointer(2, GL_FLOAT, 0, BUFFER_OFFSET(6 * submesh._nb_vertices * sizeof(float)))
        
        submesh._material._activate()
        program = data._material_programs[submesh._material]
        program._activate()
        program._set_all_user_params(body, self._mini_shaders, submesh._material._mini_shaders)
        
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, submesh._face_buffer)
        glDrawElements(GL_TRIANGLES, 3 * submesh._nb_faces, GL_UNSIGNED_SHORT, BUFFER_OFFSET(0))
        
      coords    = coords    + 3 * submesh._nb_vertices
      vnormals  = vnormals  + 3 * submesh._nb_vertices
      texcoords = texcoords + 2 * submesh._nb_vertices
      
    data._vertex_ok = 1 # We built the vertex for the rendering
    
    CalRenderer_EndRendering(cal_renderer)
    glDisableClientState(GL_NORMAL_ARRAY)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)
    glDisableClientState(GL_VERTEX_ARRAY)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ARRAY_BUFFER        , 0)
    if body._option & LEFTHANDED: glFrontFace(GL_CCW)
    if self._option & CAL3D_DOUBLE_SIDED:
      glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_FALSE)
      glDisable(GL_VERTEX_PROGRAM_TWO_SIDE)
      glEnable(GL_CULL_FACE)
      
      
  cdef void _build_vertices(self, _AnimatedModelData data):
    cdef CalRenderer*    cal_renderer
    cdef _Cal3dSubMesh   submesh
    cdef GLfloat*        coords
    cdef GLfloat*        vnormals
    
    cal_renderer = CalModel_GetRenderer(data._cal_model)
    
    if (CalRenderer_BeginRendering(cal_renderer) == 0):
      print "error 1", CalError_GetLastErrorDescription()
      raise RuntimeError("CalRenderer_BeginRendering failed: %s" % CalError_GetLastErrorDescription())
    
    coords   = data._coords
    vnormals = data._vnormals
    for submesh in self._submeshes:
      if data._attached_meshes[submesh._mesh]:
        CalRenderer_SelectMeshSubmesh(cal_renderer, submesh._mesh, submesh._submesh)
        
        # get all vertices
        CalRenderer_GetVertices          (cal_renderer, coords)
        CalRenderer_GetNormals           (cal_renderer, vnormals)
        
      coords   = coords   + submesh._nb_vertices * 3
      vnormals = vnormals + submesh._nb_vertices * 3
      
    CalRenderer_EndRendering(cal_renderer)
    
    
  cdef void _render_outline(self, _AnimatedModelData data, _Cal3dSubMesh submesh, Frustum* frustum, float* coords, float* vnormals, float* plane):
    global _cal3d_facesides, _tmp_faces
    
    cdef int          i, j, k, buf
    cdef float        d
    cdef float        plane2[4]
    cdef _Program     program
    
    # Compute outline width, which depends on distance to camera
    d = sphere_distance_point(self._sphere, frustum.position) * self._outline_attenuation
    if d < 1.0: d = self._outline_width
    else:
      d = self._outline_width / d
      if d < 2.0: d = 2.0
      
    # mark faces as either front or back
    for i from 0 <= i < submesh._nb_faces:
      if plane[0] * frustum.position[0] + plane[1] * frustum.position[1] + plane[2] * frustum.position[2] + plane[3] > 0.0: _cal3d_facesides[i] = FACE_FRONT
      else:                                                                                                                 _cal3d_facesides[i] = FACE_BACK
      plane = plane + 4
      
    _DEFAULT_MATERIAL._activate()
    glLineWidth(d)
    glColor4fv (self._outline_color)
    glEnable   (GL_BLEND)
    #glEnable   (GL_LINE_SMOOTH) # No longer needed with fullscreen antialiasing
    glDisable  (GL_LIGHTING)
    glDepthFunc(GL_LEQUAL)
    glPointSize(d * 0.7)
   
    program = data._material_programs[_DEFAULT_MATERIAL]
    program._activate()
    program._set_all_user_params(data._body, self._mini_shaders, _DEFAULT_MATERIAL._mini_shaders)
    
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, _tmp_face_buffer)
    glBindBuffer(GL_ARRAY_BUFFER        , _tmp_vertex_buffer)
    glBufferSubData(GL_ARRAY_BUFFER, 0, 3 * submesh._nb_vertices * sizeof(float), coords)
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, BUFFER_OFFSET(0))
    
    # find and draw edges   
    buf = 0
    if self._option & CAL3D_DOUBLE_SIDED:
      for i from 0 <= i < submesh._nb_faces:
        for j from 0 <= j < 3:
          k = submesh._face_neighbors[3 * i + j]
          if (k == -1) or (_cal3d_facesides[k] != _cal3d_facesides[i]):
            _tmp_faces[buf] = submesh._faces[3 * i + j] # draw edge between vertices j and j + 1
            if j < 2: _tmp_faces[buf + 1] = submesh._faces[3 * i + j + 1]
            else:     _tmp_faces[buf + 1] = submesh._faces[3 * i]
            buf = buf + 2
            
        if buf >= 180: # A face has at maximum 4 edges => 8 vertex => render now !
          glBufferSubData(GL_ELEMENT_ARRAY_BUFFER, 0, buf * sizeof(short), _tmp_faces)
          glDrawElements(GL_LINES , buf, GL_UNSIGNED_SHORT, BUFFER_OFFSET(0))
          glDrawElements(GL_POINTS, buf, GL_UNSIGNED_SHORT, BUFFER_OFFSET(0))
          buf = 0
          
    else:
      for i from 0 <= i < submesh._nb_faces:
        if _cal3d_facesides[i] == FACE_FRONT:
          for j from 0 <= j < 3:
            k = submesh._face_neighbors[3 * i + j]
            if (k == -1) or (_cal3d_facesides[k] == FACE_BACK): # test if neighbors are back
              _tmp_faces[buf] = submesh._faces[3 * i + j] # draw edge between vertices j and j + 1
              if j < 2: _tmp_faces[buf + 1] = submesh._faces[3 * i + j + 1]
              else:     _tmp_faces[buf + 1] = submesh._faces[3 * i]
              buf = buf + 2
              
        if buf >= 180: # A face has at maximum 4 edges => 8 vertex => render now !
          glBufferSubData(GL_ELEMENT_ARRAY_BUFFER, 0, buf * sizeof(short), _tmp_faces)
          glDrawElements(GL_LINES , buf, GL_UNSIGNED_SHORT, BUFFER_OFFSET(0))
          glDrawElements(GL_POINTS, buf, GL_UNSIGNED_SHORT, BUFFER_OFFSET(0))
          buf = 0
          
    if buf > 0: # Some lines are pending, draw them !
      glBufferSubData(GL_ELEMENT_ARRAY_BUFFER, 0, buf * sizeof(short), _tmp_faces)
      glDrawElements(GL_LINES , buf, GL_UNSIGNED_SHORT, BUFFER_OFFSET(0))
      glDrawElements(GL_POINTS, buf, GL_UNSIGNED_SHORT, BUFFER_OFFSET(0))
      buf = 0
      
    glDisableClientState(GL_VERTEX_ARRAY)
    glBindBuffer (GL_ARRAY_BUFFER        , 0)    
    glBindBuffer (GL_ELEMENT_ARRAY_BUFFER, 0)
    glLineWidth(1.0) # Reset to default
    glPointSize(1.0) # Reset to default
    glEnable   (GL_LIGHTING)
    glDepthFunc(GL_LESS)
    glColor4fv (white)
    
    
  def __dealloc__(self):
    cdef _Cal3dSubMesh submesh
    
    CalCoreModel_Delete (self._core_model)
    if self._option & CAL3D_GL_INITED:
      for submesh in self._submeshes: glDeleteBuffers(1, &submesh._face_buffer)
      
      
  def load_skeleton(self, filename):
    if CalCoreModel_LoadCoreSkeleton(self._core_model, python2cstring(filename)) == 0: raise RuntimeError("CalCoreModel_LoadCoreSkeleton failed: %s" % CalError_GetLastErrorDescription())
    
  def load_mesh(self, filename):
    cdef int i
    i = CalCoreModel_LoadCoreMesh(self._core_model, python2cstring(filename))
    if i == -1: raise RuntimeError("CalCoreModel_LoadCoreMesh failed on file %s: %s" % (filename, CalError_GetLastErrorDescription()))
    self._meshes[os.path.basename(filename)[:-4]] = i
    return i
  
  def load_material(self, filename):
    cdef int i
    i = CalCoreModel_LoadCoreMaterial(self._core_model, python2cstring(filename))
    if i == -1: raise RuntimeError("CalCoreModel_LoadCoreMaterial failed on file %s: %s" % (filename, CalError_GetLastErrorDescription()))
    return i
  
  def load_animation(self, filename):
    cdef int i
    i = CalCoreModel_LoadCoreAnimation(self._core_model, python2cstring(filename))
    if i == -1: raise RuntimeError("CalCoreModel_LoadCoreAnimation failed on file %s: %s" % (filename, CalError_GetLastErrorDescription()))
    self._animations[os.path.basename(filename)[:-4]] = i
    return i
    
  def build_materials(self):
    cdef int              i, nb
    cdef CalCoreMaterial* material
    
    self._materials.__imul__(0)
    if self._core_model == NULL: return
    
    nb = CalCoreModel_GetCoreMaterialCount(self._core_model)
    for i from 0 <= i < nb:
      material = CalCoreModel_GetCoreMaterial(self._core_model, i)
      
      # It seems that the Cal3D C wrapper does not support yet the CalCoreMaterial_Get*Color functions
      self._materials.append(self._get_material_4_cal3d(CalCoreMaterial_GetMapFilename(material, 0), 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, CalCoreMaterial_GetShininess(material)))
      
      CalCoreModel_CreateCoreMaterialThread(self._core_model, i)
      CalCoreModel_SetCoreMaterialId(self._core_model, i, 0, i)
      CalCoreMaterial_SetUserData(material, <CalUserData> i)
      
  cdef _Material _get_material_4_cal3d(self, image_filename, float diffuse_r, float diffuse_g, float diffuse_b, float diffuse_a, float specular_r, float specular_g, float specular_b, float specular_a, float shininess):
    if isinstance(image_filename, bytes): image_filename = image_filename.decode("utf8")
    material_name = os.path.basename(image_filename)
    material_name = material_name[:material_name.find(".")]
    return Material.get(material_name)
    #if material_name in Material.availables(): return Material.get(material_name)
    #else: return self._create_material_4_cal3d(image_filename, diffuse_r, diffuse_g, diffuse_b, diffuse_a, specular_r, specular_g, specular_b, specular_a, shininess)
    
  cdef _Material _create_material_4_cal3d(self, image_filename, float diffuse_r, float diffuse_g, float diffuse_b, float diffuse_a, float specular_r, float specular_g, float specular_b, float specular_a, float shininess):
    material_name = "__cal3dmaterial_texture_%s_diffuse_%s_%s_%s_%s_specular_%s_%s_%s_%s_shininess_%s__" % (image_filename, diffuse_r , diffuse_g , diffuse_b , diffuse_a, specular_r, specular_g, specular_b, specular_a, shininess)
    if material_name in Material.availables(): return Material.get(material_name)
    
    cdef _Material material
    material = Material()
    material.filename  = material_name
    material.diffuse   = (diffuse_r , diffuse_g , diffuse_b , diffuse_a )
    material.specular  = (specular_r, specular_g, specular_b, specular_a)
    material.shininess = shininess
    
    if image_filename != "":
#      import soya3 as soya
      for path in soya.path:
        file = os.path.join(path, Image.DIRNAME, os.path.basename(image_filename))
        if os.path.exists(file):
          if   image_filename.endswith(".raw"): material.texture = load_raw_image(file)
          else:                                 material.texture = open_image    (file)
          break
      else:  self._set_texture_from_model(material, image_filename)
      
    return material
  
  cdef void _set_texture_from_model(self, _Material material, image_filename):
    image_filename = os.path.join(os.path.dirname(self._full_filename), image_filename)
    if   image_filename.endswith(".raw"): material.texture = load_raw_image(image_filename)
    else:                                 material.texture = open_image    (image_filename)
    

  
  
  
  
  cdef void _raypick(self, RaypickData data, CoordSyst raypickable):
    cdef _Body              body
    cdef _AnimatedModelData da
    body = <_Body> raypickable
    da   = body._data
    
    if da._bones_ok      == 0: da._build_bones()
    #if da._vertex_ok     == 0: da._build_vertices() # Done by da._build_face_planes() below
    if da._face_plane_ok == 0: da._build_face_planes()
    
    cdef float*        raydata
    cdef float*        coords
    cdef float*        plane
    cdef float         z, root_z
    cdef int           i, j, r
    cdef _Cal3dSubMesh submesh
    
    # XXX take into account the ray length ? e.g., if ray_length == 1.0, sphere_radius = 1.0 and (ray_origin >> self).length() > 2.0, no collision can occur
    raydata = body._raypick_data(data)
    if (self._sphere[3] > 0.0) and (sphere_raypick(raydata, self._sphere) == 0): return
    
    i = 0
    plane  = da._face_planes
    coords   = da._coords
    for submesh in self._submeshes:
      if da._attached_meshes[submesh._mesh]:
        for j from 0 <= j < submesh._nb_faces:
          r = triangle_raypick(raydata, coords + 3 * submesh._faces[3 * j], coords + 3 * submesh._faces[3 * j + 1], coords + 3 * submesh._faces[3 * j + 2], plane + 4 * j, data.option, &z)
          
          if r != 0:
            root_z = body._distance_out(z)
            if (data.result_coordsyst is None) or (fabs(root_z) < fabs(data.root_result)):
              data.result      = z
              data.root_result = root_z
              data.result_coordsyst = body
              if   r == RAYPICK_DIRECT: memcpy(&data.normal[0], plane + 4 * j, 3 * sizeof(float))
              elif r == RAYPICK_INDIRECT:
                if self._option & CAL3D_DOUBLE_SIDED:
                  data.normal[0] = -(plane + 4 * j)[0]
                  data.normal[1] = -(plane + 4 * j)[1]
                  data.normal[2] = -(plane + 4 * j)[2]
                else: memcpy(&data.normal[0], plane + 4 * j, 3 * sizeof(float))
              vector_normalize(data.normal)
              
      i = i + 1
      coords = coords + submesh._nb_vertices * 3
      plane  = plane  + submesh._nb_faces    * 4
  
  cdef int _raypick_b(self, RaypickData data, CoordSyst raypickable):
    cdef float*                     raydata
    cdef float*                     coords
    cdef float*                     plane
    cdef float                      z
    cdef int                        i, j
    cdef _Cal3dSubMesh              submesh
    cdef _Body                    body
    cdef _AnimatedModelData da
    body = <_Body> raypickable
    da     = body._data
    
    if da._bones_ok      == 0: da._build_bones()
    #if da._vertex_ok     == 0: da._build_vertices() # Done by da._build_face_planes() below
    if da._face_plane_ok == 0: da._build_face_planes()
    
    # XXX take into account the ray length ? e.g., if ray_length == 1.0, sphere_radius = 1.0 and (ray_origin >> self).length() > 2.0, no collision can occur
    raydata = body._raypick_data(data)
    if (self._sphere[3] > 0.0) and (sphere_raypick(raydata, self._sphere) == 0): return 0
    
    i = 0
    plane  = da._face_planes
    coords   = da._coords
    for submesh in self._submeshes:
      if da._attached_meshes[submesh._mesh]:
        for j from 0 <= j < submesh._nb_faces:
          if triangle_raypick(raydata, coords + 3 * submesh._faces[3 * j], coords + 3 * submesh._faces[3 * j + 1], coords + 3 * submesh._faces[3 * j + 2], plane + 4 * j, data.option, &z) != 0: return 1
          
    return 0
  
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, CoordSyst parent):
    if (self._sphere[3] < 0.0) or (sphere_distance_sphere(sphere, self._sphere) < 0.0):
      chunk_add_ptr(items, <void*> parent)





  
cdef class _AnimatedModelData(_ModelData):
  #cdef int            _option
  #cdef _Body          _body
  #cdef _AnimatedModel _model
  #cdef                _attached_meshes, _attached_coordsysts
  #cdef CalModel*      _cal_model
  #cdef float          _delta_time
  #cdef float*         _face_planes, *_coords, *_vnormals
  #cdef int            _face_plane_ok, _vertex_ok
  #cdef dict           _material_programs
  
  def __init__(self, _Body body, _AnimatedModel model, attached_meshes = None):
    self._body              = body
    self._model             = model
    self._material_programs = {}
    
    self._cal_model = CalModel_New(model._core_model)
    if self._cal_model == NULL:
      print "error CalModel_Create", CalError_GetLastErrorDescription()
      raise RuntimeError("CalModel_Create failed: %s" % CalError_GetLastErrorDescription())
    
    self._attached_meshes     = []
    self._attached_coordsysts = []
    nb = CalCoreModel_GetCoreMeshCount(model._core_model)
    for i from 0 <= i < nb: self._attached_meshes.append(0)
    if not attached_meshes is None: self._attach(attached_meshes)
    else:                           self._attach_all()
    
  def __dealloc__(self):
    CalModel_Delete (self._cal_model)
    if self._coords      != NULL: free(self._coords)
    if self._vnormals    != NULL: free(self._vnormals)
    if self._face_planes != NULL: free(self._face_planes)
    
  cdef __getcstate__(self):
    return (self._body, self._model, self._attached_meshes, self._attached_coordsysts)
  
  cdef void __setcstate__(self, cstate):
    self._body, self._model, self._attached_meshes, self._attached_coordsysts = cstate
    self._option            = 0
    self._material_programs = {}
    
    self._cal_model = CalModel_New(self._model._core_model)
    if self._cal_model == NULL:
      print "error CalModel_Create", CalError_GetLastErrorDescription()
      raise RuntimeError("CalModel_Create failed: %s" % CalError_GetLastErrorDescription())
    
    for i from 0 <= i < len(self._attached_meshes):
      if self._attached_meshes[i] == 1:
        if CalModel_AttachMesh(self._cal_model, i) == 0:
          print "error CalModel_AttachMesh", CalError_GetLastErrorDescription()
          raise RuntimeError("CalModel_AttachMesh failed: %s" % CalError_GetLastErrorDescription())
    self._build_submeshes()
    
  cdef void _build_submeshes(self):
    if not(self._model._option & CAL3D_INITED): self._model._build_submeshes()
    
    if self._coords  != NULL: free(self._coords)
    if self._vnormals != NULL: free(self._vnormals)
    if self._face_planes    != NULL: free(self._face_planes)
    
    self._coords      = <GLfloat*> malloc(self._model._nb_vertices * 3 * sizeof(GLfloat))
    self._vnormals    = <GLfloat*> malloc(self._model._nb_vertices * 3 * sizeof(GLfloat))
    self._face_planes = <GLfloat*> malloc(self._model._nb_faces    * 4 * sizeof(GLfloat))
    
  cdef void _attach(self, mesh_names):
    cdef int i
    for mesh_name in mesh_names:
      i = self._model.meshes[mesh_name]
      if self._attached_meshes[i] == 0:
        if CalModel_AttachMesh(self._cal_model, i) == 0:
          print "error CalModel_AttachMesh", CalError_GetLastErrorDescription()
          raise RuntimeError("CalModel_AttachMesh failed: %s" % CalError_GetLastErrorDescription())

        self._attached_meshes[i] = 1
    self._build_submeshes()
    
  cdef void _detach(self, mesh_names):
    cdef int i
    for mesh_name in mesh_names:
      i = self._model.meshes[mesh_name]
      if self._attached_meshes[i] == 1:
        if CalModel_DetachMesh(self._cal_model, i) == 0:
          print "error CalModel_DetachMesh", CalError_GetLastErrorDescription()
          raise RuntimeError("CalModel_DetachMesh failed: %s" % CalError_GetLastErrorDescription())
        self._attached_meshes[i] = 0
    self._build_submeshes()
    
  cdef void _attach_all(self):
    cdef int i
    for i from 0 <= i < len(self._attached_meshes):
      if self._attached_meshes[i] == 0:
        if CalModel_AttachMesh(self._cal_model, i) == 0:
          print "error CalModel_AttachMesh", CalError_GetLastErrorDescription()
          raise RuntimeError("CalModel_AttachMesh failed: %s" % CalError_GetLastErrorDescription())
        self._attached_meshes[i] = 1
    self._build_submeshes()
    
  cdef int _is_attached(self, mesh_name):
    return self._attached_meshes[self._model.meshes[mesh_name]]
    
  cdef void _attach_to_bone(self, CoordSyst coordsyst, bone_name):
    cdef int i
    i = CalCoreSkeleton_GetCoreBoneId(CalCoreModel_GetCoreSkeleton(self._model._core_model), python2cstring(bone_name))
    if i == -1: raise ValueError("No bone named %s !" % bone_name)
    self._attached_coordsysts.append((coordsyst, i, 1))
    
  cdef void _detach_from_bone(self, CoordSyst coordsyst):
    cdef int i
    for i from 0 <= i < len(self._attached_coordsysts):
      if self._attached_coordsysts[i][0] is coordsyst:
        del self._attached_coordsysts[i]
        break
      
  cdef _get_attached_meshes    (self): return self._attached_meshes
  cdef _get_attached_coordsysts(self): return self._attached_coordsysts
  
  cdef void _animate_blend_cycle(self, animation_name, float weight, float fade_in):
    CalMixer_BlendCycle(CalModel_GetMixer(self._cal_model), self._model._animations[animation_name], weight, fade_in)
    
  cdef void _animate_clear_cycle(self, animation_name, float fade_out):
    CalMixer_ClearCycle(CalModel_GetMixer(self._cal_model), self._model._animations[animation_name], fade_out)
    
  cdef void _animate_execute_action(self, animation_name, float fade_in, float fade_out):
    CalMixer_ExecuteAction(CalModel_GetMixer(self._cal_model), self._model._animations[animation_name], fade_in, fade_out)
    
  cdef void _animate_reset(self):
    # Calling CalMixer_UpdateAnimation with 0.0 has a resetting effect.
    # This is an undocumented feature i've discovered by reading sources.
    CalMixer_UpdateAnimation(CalModel_GetMixer(self._cal_model), 0.0)
    
  cdef void _set_lod_level(self, float lod_level): CalModel_SetLodLevel(self._cal_model, lod_level)
  
  cdef void _advance_time(self, float proportion):
#    import soya3 as soya # XXX optimizable! probably slow!
    self._delta_time = self._delta_time + proportion * soya.MAIN_LOOP.round_duration
    self._face_plane_ok = 0
    self._vertex_ok     = 0
    self._bones_ok      = 0
    
  cdef int _update(self):
    if self._delta_time == 0.0: return 0
    CalModel_Update(self._cal_model, self._delta_time)
    self._delta_time = 0.0
    return 1
  
  cdef void _build_bones(self):
    cdef int       bone_id, option
    cdef CalBone*  bone
    cdef CoordSyst csyst
    cdef float*    trans
    cdef float*    quat
    
    if self._attached_coordsysts:
      self._update()
      
      for csyst, bone_id, option in self._attached_coordsysts: # Updates coordsysts attached to a bone
        bone = CalSkeleton_GetBone(CalModel_GetSkeleton(self._cal_model), bone_id)
        quat = CalQuaternion_Get(CalBone_GetRotationAbsolute(bone))
        quat[3] = -quat[3] # Cal3D use indirect frame or what ???
        matrix_from_quaternion(csyst._matrix, quat)
        trans = CalVector_Get(CalBone_GetTranslationAbsolute(bone))
        csyst._matrix[12] = <GLfloat> trans[0]
        csyst._matrix[13] = <GLfloat> trans[1]
        csyst._matrix[14] = <GLfloat> trans[2]
        csyst._invalidate()
        
    self._bones_ok = 1
    
  cdef void _build_vertices(self):
    self._update()
    self._model._build_vertices(self)
    self._vertex_ok = 1
    
  cdef void _build_face_planes(self):
    cdef float*        coords
    cdef float*        plane
    cdef int           i, j
    cdef _Cal3dSubMesh submesh
    
    if self._vertex_ok == 0: self._build_vertices()
    
    i      = 0
    plane  = self._face_planes
    coords = self._coords
    for submesh in self._model._submeshes:
      if self._attached_meshes[submesh._mesh]:
        for j from 0 <= j < submesh._nb_faces:
          face_plane(plane + 4 * j, coords + 3 * submesh._faces[3 * j], coords + 3 * submesh._faces[3 * j + 1], coords + 3 * submesh._faces[3 * j + 2])
          # XXX normalize here (with plane_vector_normalize) or keep normalization in _raypick ?
          
      i = i + 1
      coords = coords + submesh._nb_vertices * 3
      plane  = plane  + submesh._nb_faces    * 4
      
    self._face_plane_ok = 1
    
  cdef list _get_materials(self): return self._model._get_materials()
  
  cdef void _invalidate_shaders(self):
    self._option = self._option & ~MODELDATA_SHADERS_VALID
    
  cdef void _batch(self, _Body body):
    cdef list mini_shaders
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
    if self._bones_ok == 0: self._build_bones()
    self._model._raypick  (raypick_data, raypickable)
    
  cdef int  _raypick_b           (self, RaypickData raypick_data, CoordSyst raypickable):
    if self._bones_ok == 0: self._build_bones()
    return self._model._raypick_b(raypick_data, raypickable)
  
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, CoordSyst parent):
    if self._bones_ok == 0: self._build_bones()
    self._model._collect_raypickables(items, rsphere, sphere, parent)
