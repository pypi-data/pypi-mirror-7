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

# XXX does not allows None/NULL as a valid context, use a default context instead

cdef class Context:
  #cdef                      lights
  #cdef _Atmosphere          atmosphere
  #cdef _Portal              portal
  
  def __init__(self):
    self.lights = []
    
    
cdef class Renderer:
  #cdef int       engine_option
  #cdef int       state
  #cdef _World    root_object
  #cdef _Camera   current_camera
  #cdef _Material current_material
  
  #cdef Frustum*  root_frustum
  #cdef Chunk*    frustums
  #cdef CoordSyst current_coordsyst
  
  # contexts
  #cdef Context current_context
  #cdef contexts
  #cdef int nb_contexts
  #cdef int max_contexts
  #cdef _Atmosphere root_atmosphere # root atmosphere (the one to clear the screen with)
  #cdef _Atmosphere current_atmosphere
  
  # list of collected objects to render
  #cdef Chunk* opaque
  #cdef Chunk* secondpass
  #cdef Chunk* alpha
  #cdef Chunk* specials  # objects that are rendered after the shadows (= not shadowed)
  
  #cdef top_lights # contain top level activated lights
  #cdef worlds_made  # list of world whose context has been made (used by portals to determine if a world must be batched or not)
  #cdef portals  # a list of encountered portals to clear_part the atmosphere before any other rendering and to draw fog at the end
  
  # mesh renderer
  #cdef Chunk* data
  #cdef Chunk* used_opaque_packs, *used_secondpass_packs, *used_alpha_packs
  #cdef float** colors
  
  # screen
  #cdef SDL_Surface* screen
  #cdef int screen_width, screen_height
  
  #cdef float delta_time
  
  def __init__(self):
    self.engine_option = USE_MIPMAP | SHADOWS
    self.root_frustum  = <Frustum*> malloc(sizeof(Frustum))
    self.top_lights    = []
    self.worlds_made   = []
    self.portals       = []
    self.contexts      = []

    self.opaque        = get_clist()
    self.secondpass    = get_clist()
    self.alpha         = get_clist()
    self.specials      = get_clist()
    
    self.data                  = get_clist()
    self.frustums              = get_chunk()
    self.used_opaque_packs     = get_clist()
    self.used_secondpass_packs = get_clist()
    self.used_alpha_packs      = get_clist()
    
    self.current_material = _DEFAULT_MATERIAL
    
  def __dealloc__(self):
    pass
    """
    print "renderer dealloc"
    free(self.root_frustum)
    drop_clist(self.data)
    drop_clist(self.opaque)
    drop_clist(self.secondpass)
    drop_clist(self.alpha)
    drop_clist(self.specials)
    drop_clist(self.used_opaque_packs)
    drop_clist(self.used_secondpass_packs)
    drop_clist(self.used_alpha_packs)
    chunk_dealloc(self.frustums)
    """
  
  cdef Frustum* _frustum(self, CoordSyst coordsyst):
    if coordsyst is None: return self.root_frustum
    if coordsyst._frustum_id == -1:
      coordsyst._frustum_id = chunk_register(self.frustums, sizeof(Frustum))
      frustum_by_matrix(<Frustum*> (self.frustums.content + coordsyst._frustum_id), self.root_frustum, coordsyst._inverted_root_matrix())
    return <Frustum*> (self.frustums.content + coordsyst._frustum_id)
  
  cdef Context _context(self):
    cdef Context context
    context = Context()
    self.contexts.append(context)
    return context
    
  cdef void _activate_context_over(self, Context old, Context new):
    # XXX TODO activate / inactivate light only if necessary ?
    cdef _Light light
    if not old is None:
      # inactivate previous lights
      for light in old.lights:
        if light._id != -1:
          light._gl_id_enabled = 0
          glDisable(GL_LIGHT0 + light._id)
      if (not old.portal is None) and (old.portal._option & (PORTAL_USE_4_CLIP_PLANES | PORTAL_USE_5_CLIP_PLANES)):
        glDisable(GL_CLIP_PLANE0)
        glDisable(GL_CLIP_PLANE1)
        glDisable(GL_CLIP_PLANE2)
        glDisable(GL_CLIP_PLANE3)
        if old.portal._option & PORTAL_USE_5_CLIP_PLANES: glDisable(GL_CLIP_PLANE4)
        
    # activate new context
    if not new is None:
      if (not new.atmosphere is None) and ((old is None) or (not new.atmosphere is old.atmosphere)):
        new.atmosphere._render()
        self.current_atmosphere = new.atmosphere
      for light in new.lights: light._activate()
      
    # re-activate top level lights that may have been inactivated due to too many lights
    for light in renderer.top_lights:
      if light._id == -1: light.render(None)
      
    # active portal clip plane
    if (not new is None) and (not new.portal is None) and (new.portal._option & (PORTAL_USE_4_CLIP_PLANES | PORTAL_USE_5_CLIP_PLANES)):
      glLoadIdentity()  # the clip planes must be defined in the camera coordsys... so identity
      glClipPlane(GL_CLIP_PLANE0, new.portal._equation)
      glClipPlane(GL_CLIP_PLANE1, new.portal._equation + 4)
      glClipPlane(GL_CLIP_PLANE2, new.portal._equation + 8)
      glClipPlane(GL_CLIP_PLANE3, new.portal._equation + 12)
      glEnable(GL_CLIP_PLANE0)
      glEnable(GL_CLIP_PLANE1)
      glEnable(GL_CLIP_PLANE2)
      glEnable(GL_CLIP_PLANE3)
      if new.portal._option & PORTAL_USE_5_CLIP_PLANES:
        glClipPlane(GL_CLIP_PLANE4, new.portal._equation + 16)
        glEnable(GL_CLIP_PLANE4)
        
  cdef void _reset(self):
    cdef _World world
    self.root_atmosphere    = None
    self.current_atmosphere = None
    disable_all_lights()
    for world in self.worlds_made: world._option = world._option - WORLD_BATCHED
    self.contexts   .__imul__(0)
    self.top_lights .__imul__(0)
    self.worlds_made.__imul__(0)
    self.portals    .__imul__(0)
    clist_flush(self.opaque)
    clist_flush(self.secondpass)
    clist_flush(self.alpha)
    clist_flush(self.specials)
    clist_flush(self.data)
    self.delta_time = 0.0
    
  cdef void _batch(self, CList* list, obj, CoordSyst coordsyst, CListHandle* data):
    clist_add(list, <void*> obj)
    clist_add(list, <void*> coordsyst)
    clist_add(list, <void*> renderer.current_context)
    clist_add(list, <void*> data)
  
  cdef void _render(self):
    cdef Context ctxt
    cdef _Portal portal
    cdef _World  world
    cdef _Light  light
    
    renderer.frustums.nb = 0
    
    # RENDERING STEP 1 : BATCH
    ctxt = self.current_context = self._context()
    self.root_object._batch(self.current_camera)
    
    # RENDERING STEP 2 : RENDER
    # clear
    if not self.root_atmosphere is None: self.root_atmosphere._clear()
    else: self._clear_screen(NULL)
    # draw the atmosphere of the worlds that are seen through portals
    self.portals.reverse()
    for portal in self.portals:
      if portal._option & PORTAL_BOUND_ATMOSPHERE: portal._atmosphere_clear_part()
    # activate top lights
    for light in self.top_lights: light._activate()
    # current context have been changed during batching -> reinitialize
    self.current_context = None
    
    # render collected objects
    # draw opaque stuff first
    self.state = RENDERER_STATE_OPAQUE
    self._render_list(self.opaque)
    
    # then draw secondpass
    self.state = RENDERER_STATE_SECONDPASS
    self._render_list(self.secondpass)
    # finally draw alpha
    self.state = RENDERER_STATE_ALPHA
    glEnable(GL_BLEND)
    glDepthMask(GL_FALSE)
    self._render_list(self.alpha)
    # reset a part of the renderer here cause it's needed for rendering the portal fog
    _DEFAULT_MATERIAL._activate()
    self._activate_context_over(self.current_context, None)
    self.current_context = None
    
    # draw fog for portal if necessary
    for portal in self.portals:
      if portal._option & PORTAL_BOUND_ATMOSPHERE:
        # get previous/parent atmosphere
        world = <_World> portal._parent
        while (not world is None) and (world._atmosphere is None): world = <_World> world._parent
        if (not world._atmosphere is None) and (world._atmosphere._option & ATMOSPHERE_FOG):
          portal._draw_fog(world._atmosphere)
    # render shadow
    # render specials: objects that are not shadowed (sprite, particules)
    self.state = RENDERER_STATE_SPECIAL
    self._render_list (self.specials)
      
    # end of OpenGL rendering
    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)
    # auto-reset renderer
    self._reset()
    
    #drop_chunk(self.frustums)
    
  cdef void _render_list(self, CList* list):
    cdef CoordSyst    coordsyst
    cdef Context      context
    cdef CListHandle* handle
    cdef int          i, nb
    cdef _CObj        obj
    
    handle = list.begin
    while handle:
      obj               = <_CObj>        handle.data
      handle            =                handle.next
      coordsyst         = <CoordSyst>    handle.data
      handle            =                handle.next
      context           = <Context>      handle.data
      handle            =                handle.next
      self.current_data = <CListHandle*> handle.data
      
      # context
      if not context is self.current_context:
        self._activate_context_over(self.current_context, context)
        self.current_context = context
        
      # coordsyst
      self.current_coordsyst = coordsyst
      if not coordsyst is None:
        glLoadMatrixf(coordsyst._render_matrix)
        if coordsyst._render_matrix[17] != 1.0: glEnable(GL_NORMALIZE)
        
      if isinstance(obj, _Model): (<_Model>    obj)._render(coordsyst)
      else:                       (<CoordSyst> obj)._render(coordsyst)
      
      if (not coordsyst is None) and (coordsyst._render_matrix[17] != 1.0): glDisable(GL_NORMALIZE)
      
      handle = handle.next
  
  cdef void _clear_screen(self, float* color):
    cdef int* size
    cdef GLboolean lighting, fog, cullface, tex
    if (self.current_camera._option & CAMERA_PARTIAL):
      size = self.current_camera._viewport

      #glPushAttrib(GL_ENABLE_BIT)
      lighting = glIsEnabled(GL_LIGHTING)
      fog      = glIsEnabled(GL_FOG)
      cullface = glIsEnabled(GL_CULL_FACE)
      tex      = glIsEnabled(GL_TEXTURE_2D)
      
      glDisable(GL_LIGHTING)
      glDisable(GL_FOG)
      glDisable(GL_CULL_FACE)
      glDisable(GL_TEXTURE_2D)
      
      glDepthMask (GL_FALSE)
      if (color == NULL): glColor4f (0.0, 0.0, 0.0, 1.0)
      else:               glColor4fv(color)
      glLoadIdentity()
      glMatrixMode(GL_PROJECTION)
      glPushMatrix()
      glLoadIdentity()
      glOrtho(0.0, <GLfloat> size[2], <GLfloat> size[3], 0.0, -1.0, 1.0)
      
      #if not _CURRENT_PROGRAM is None: _CURRENT_PROGRAM._inactivate()
      _DEFAULT_PROGRAM._activate()
      
      # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, _tmp_face_buffer)
      # glBindBuffer(GL_ARRAY_BUFFER        , _tmp_vertex_buffer)
      # glEnableClientState(GL_VERTEX_ARRAY)
      # glVertexPointer(2, GL_FLOAT, 0, BUFFER_OFFSET(0))
      
      # _tmp_vertices[ 0] = 0
      # _tmp_vertices[ 1] = 0
      # _tmp_vertices[ 2] = size[2]
      # _tmp_vertices[ 3] = 0
      # _tmp_vertices[ 4] = size[2]
      # _tmp_vertices[ 5] = size[3]
      # _tmp_vertices[ 6] = 0
      # _tmp_vertices[ 7] = size[3]
      
      # _tmp_faces[0] = 0
      # _tmp_faces[1] = 1
      # _tmp_faces[2] = 2
      # _tmp_faces[3] = 2
      # _tmp_faces[4] = 3
      # _tmp_faces[5] = 0
      
      # glBufferSubData(GL_ARRAY_BUFFER        , 0, 8 * sizeof(float), _tmp_vertices)
      # glBufferSubData(GL_ELEMENT_ARRAY_BUFFER, 0, 6 * sizeof(short), _tmp_faces)
      # glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_SHORT, BUFFER_OFFSET(0))
      
      # glDisableClientState(GL_VERTEX_ARRAY)
      # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
      # glBindBuffer(GL_ARRAY_BUFFER        , 0)
      
      glBegin(GL_QUADS)
      glVertex2i(0, 0)
      glVertex2i(size[2], 0)
      glVertex2i(size[2], size[3])
      glVertex2i(0, size[3])
      glEnd()
      
      glMatrixMode(GL_PROJECTION)
      glPopMatrix()
      glMatrixMode(GL_MODELVIEW)
      
      #glPopAttrib()
      if lighting: glEnable(GL_LIGHTING)
      if fog:      glEnable(GL_FOG)
      if cullface: glEnable(GL_CULL_FACE)
      if tex:      glEnable(GL_TEXTURE_2D)
      
      glDepthMask(GL_TRUE)
      glClear(GL_DEPTH_BUFFER_BIT)
      
    else:
      if color == NULL: glClearColor(0.0, 0.0, 0.0, 1.0)
      else:             glClearColor(color[0], color[1], color[2], color[3])
      glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
      
    
def get_renderer(): return renderer

root_widget = None


class GLError(Exception): pass


def check_error(): return check_gl_error()

cdef int check_gl_error() except -1:
  cdef GLenum error
  error = glGetError()
  if error != GL_NO_ERROR:
    if   error == GL_INVALID_ENUM     : print "GL_INVALID_ENUM"     ; raise GLError, "GL_INVALID_ENUM"
    elif error == GL_INVALID_VALUE    : print "GL_INVALID_VALUE"    ; raise GLError, "GL_INVALID_VALUE"
    elif error == GL_INVALID_OPERATION: print "GL_INVALID_OPERATION"; raise GLError, "GL_INVALID_OPERATION"
    elif error == GL_STACK_OVERFLOW   : print "GL_STACK_OVERFLOW"   ; raise GLError, "GL_STACK_OVERFLOW"
    elif error == GL_STACK_UNDERFLOW  : print "GL_STACK_UNDERFLOW"  ; raise GLError, "GL_STACK_UNDERFLOW"
    elif error == GL_OUT_OF_MEMORY    : print "GL_OUT_OF_MEMORY"    ; raise GLError, "GL_OUT_OF_MEMORY"
    else:                               print "Unknown GL_ERROR 0x%X" % error    ; raise GLError, "Unknown GL_Error 0x%X" % error


def set_root_widget(widget):
  """set_root_widget(widget)

Sets the root widget of Soya3D. The root widget is the one used for rendering.
It is typically a camera, or a group of widget (soya.widget.Group) which includes
a camera."""
  global root_widget
  root_widget = widget
  if root_widget:
    root_widget.resize(0, 0, renderer.screen_width, renderer.screen_height)
    
def render(int swap_buffer = 1):
  """render()

Renders the 3D scene. Use set_root_widget() to choose which camera is used."""
  if root_widget and (not renderer is None):
    root_widget.render()
    check_gl_error()
    if swap_buffer:
      IF OPENGL == "full":
        SDL_GL_SwapWindow(renderer.sdl_window)
        
      IF OPENGL == "es":
        eglSwapBuffers(renderer.egl_display, renderer.egl_surface)
        
        
def get_screen_width (): return renderer.screen_width
def get_screen_height(): return renderer.screen_height


