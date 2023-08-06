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


cdef class Context:
  cdef list         lights
  cdef _Atmosphere  atmosphere
  cdef _Portal      portal

    
    
cdef class Renderer:
  cdef int       engine_option
  cdef int       state
  cdef _World    root_object
  cdef _Camera   current_camera
  cdef _Material current_material
  
  cdef Frustum*  root_frustum
  cdef Chunk*    frustums
  cdef CoordSyst current_coordsyst
  
  # contexts
  cdef Context current_context
  cdef list contexts
  cdef int  nb_contexts
  cdef int  max_contexts
  cdef _Atmosphere root_atmosphere # root atmosphere (the one to clear the screen with)
  cdef _Atmosphere current_atmosphere
  
  # list of collected objects to render
  cdef CList* opaque
  cdef CList* secondpass
  cdef CList* alpha
  cdef CList* specials  # objects that are rendered after the shadows (= not shadowed)
  
  cdef list top_lights # contain top level activated lights
  cdef list worlds_made  # list of world whose context has been made (used by portals to determine if a world must be batched or not)
  cdef list portals  # a list of encountered portals to clear_part the atmosphere before any other rendering and to draw fog at the end
  
  # mesh renderer
  cdef CList*       data
  cdef CListHandle* current_data
  cdef CList       *used_opaque_packs
  cdef CList       *used_secondpass_packs
  cdef CList       *used_alpha_packs
  cdef float**      colors
  
  # screen
  #cdef SDL_Surface* screen
  cdef SDL_Window*    sdl_window
  cdef SDL_GLContext  sdl_gl_context

  IF OPENGL == "es":
    cdef void* egl_display
    cdef void* egl_context
    cdef void* egl_surface
    cdef void* egl_window
    
  cdef int screen_width, screen_height
  
  cdef float delta_time
  
  cdef Frustum* _frustum(self, CoordSyst coordsyst)
  cdef Context _context(self)
  cdef void _activate_context_over(self, Context old, Context new)
  cdef void _reset(self)
  cdef void _batch(self, CList* list, obj, CoordSyst coordsyst, CListHandle* data)
  cdef void _render(self)
  cdef void _render_list(self, CList* list)
  cdef void _clear_screen(self, float* color)


cdef class Position(_CObj):
  cdef CoordSyst _parent
  
  cdef void _into(self, CoordSyst coordsyst, float* result)
  cdef void _out(self, float* result)


cdef class _Point(Position):
  cdef float _matrix[3]
  
  cdef void _into(self, CoordSyst coordsyst, float* result)
  cdef void _out(self, float* result)
  cdef      __getcstate__(self)
  cdef void __setcstate__(self, object cstate)


cdef class _Vector(_Point):
  cdef void _into(self, CoordSyst coordsyst, float* result)
  cdef void _out(self, float* result)

cdef class _Plane(Position):
  cdef float _matrix[4]
  
  cdef void _into(self, CoordSyst coordsyst, float* result)
  cdef void _out(self, float* result)
  cdef void _init_from_equation(self, float a, float b, float c, float d)
  cdef void _init_from_point_and_normal(self, _Point point, _Vector normal)
  cdef void _init_from_3_points(self, _Point p1, _Point p2, _Point p3)


cdef class MainLoop:
  cdef list            _next_round_tasks
  cdef list            _round_tasks
  cdef                 _return_value
  cdef list            _scenes
  cdef list            _events
  cdef list            _raw_events
  cdef list            _queued_events
  cdef public   double round_duration, min_frame_duration
  cdef readonly double fps
  cdef public   int    running
  cdef public   int    will_render
  cdef double          _time, _time_since_last_round
  cdef          double _last_fps_computation_time
  cdef          int    _nb_frame


cdef class _Image(_CObj):
  cdef readonly int nb_color, width, height
  cdef GLubyte* _pixels
  cdef public object _filename # str or unicode
  
  cdef      __getcstate__(self)
  cdef void __setcstate__(self, object cstate)
  cdef int check_for_gl(self)
  cdef GLuint typ(self)
  cdef GLuint internal_format(self)


cdef class _Material(_CObj):
  cdef int     _option, _nb_packs
  cdef _Image  _texture
  cdef readonly GLuint _id # the OpenGL texture name
  cdef public float shininess
  cdef GLfloat _diffuse [4]
  cdef GLfloat _specular[4]
  cdef GLfloat _emissive[4]
  cdef Pack**  _packs # the list of packs which are based on this material
  cdef list _mini_shaders
  
  cdef public object _filename # str or unicode
  
  cdef      __getcstate__(self)
  cdef void __setcstate__(self, cstate)
  cdef Pack* _pack(self, int option)
  cdef void _init_texture(self)
  cdef void _build_2D_mipmaps(self, int border)
  cdef void _compute_alpha(self)
  cdef void _activate(self)
  cdef void _inactivate(self)


cdef class _PythonMaterial(_Material):
  cdef void _init_texture(self)
  cdef void _activate(self)
  cdef void _inactivate(self)


cdef class _Model(_CObj):
  cdef public object _filename # str or unicode
  
  cdef void _instanced(self, _Body body, opt)
  cdef void _batch(self, _Body body)
  cdef void _render(self, _Body body)
  cdef void _get_box(self, float* box, float* matrix)
  cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable)
  cdef int  _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable)
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, CoordSyst parent)
  
  cdef void _attach(self, mesh_names)
  cdef void _detach(self, mesh_names)
  cdef int  _is_attached(self, mesh_name)
  cdef void _attach_to_bone(self, CoordSyst coordsyst, bone_name)
  cdef void _detach_from_bone(self, CoordSyst coordsyst)
  cdef void _advance_time(self, float proportion)
  cdef      _get_attached_meshes    (self)
  cdef      _get_attached_coordsysts(self)
  cdef void _animate_blend_cycle   (self, animation_name, float weight, float fade_in)
  cdef void _animate_clear_cycle   (self, animation_name, float fade_out)
  cdef void _animate_execute_action(self, animation_name, float fade_in, float fade_out)
  cdef void _animate_reset(self)
  cdef void _set_lod_level(self, float lod_level)
  cdef void _begin_round  (self)
  cdef void _advance_time (self, float proportion)

  cdef list _get_materials     (self)
  cdef list _get_mini_shaders  (self)
  cdef void _invalidate_shaders(self)
  
ctypedef struct _VertexBufferModelFace:
  int      option
  Pack*    pack
  float    normal[4] # normal[3] is optional (for shadows)
  int      v[4]      # v[3]      is optional (only for quad, unused for triangle)

ctypedef struct _VertexBufferModelFaceGroup:
  int       option
  int       start, nb_triangles
  uintptr_t material_id
  
  
cdef class _VertexBufferedModel(_Model):
  cdef int           _option
  cdef list          _materials
  cdef float*        _sphere
  cdef int           _nb_faces, _nb_quads, _nb_vertices
  cdef float*        _coords
  cdef float*        _vnormals
  cdef float*        _diffuses
  cdef float*        _emissives
  cdef float*        _texcoords
  cdef float*        _texcoords2
  cdef int*          _vertexids
  cdef char*         _vertex_options
  cdef list          _mini_shaders
  
  cdef _VertexBufferModelFace* _faces
  cdef int*                    _neighbors
  cdef int*                    _simple_neighbors
  cdef signed char*            _neighbors_side
  cdef signed char*            _simple_neighbors_side
  
  cdef int                          _nb_opaque_face_groups
  cdef int                          _nb_face_groups
  cdef short*                       _face_group_vertices
  cdef _VertexBufferModelFaceGroup* _face_groups
  
  cdef GLuint        _vertex_buffer, _texcoords2_buffer, _face_buffer
  cdef int           _buffer_sizeof_vertex
  cdef int           _vnormal_offset, _diffuse_offset, _emissive_offset, _texcoord_offset, _texcoord2_offset

  cdef float     _outline_color[4]
  cdef float     _outline_width, _outline_attenuation
  
  cdef      __getcstate__(self)
  cdef void __setcstate__(self, cstate)
  cdef object _identify_vertices(self, faces, float angle)
  cdef void _compute_face_normals(self, faces)
  cdef void _compute_vertex_normals(self, faces, vertex2ivertex, ivertex2vertices)
  cdef void _compute_face_neighbors(self, faces, vertex2ivertex, ivertex2vertices, int* neighbor, signed char* neighbor_side)
  cdef void _init_vertex_buffers(self)
  cdef void _batch(self, _Body body)
  cdef void _render(self, _Body body)
  cdef void _raypick(self, RaypickData data, CoordSyst parent)
  cdef int _raypick_b(self, RaypickData data, CoordSyst parent)
  cdef void _face_raypick(self, _VertexBufferModelFace* face, float* raydata, RaypickData data, CoordSyst parent)
  cdef int _face_raypick_b(self, _VertexBufferModelFace* face, float* raydata, RaypickData data)
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, CoordSyst parent)
  cdef void _get_box(self, float* box, float* matrix)
  cdef void _render_outline(self, _VertexBufferedModelData data, Frustum* frustum)

cdef class _ModelData(_Model):
  pass

cdef class _VertexBufferedModelData(_ModelData):
  cdef int    _option
  cdef _Body  _body
  cdef _Model _model
  cdef dict   _material_programs
  
  cdef      __getcstate__(self)
  cdef void __setcstate__(self, cstate)
  
  cdef void _invalidate_shaders(self)
  


cdef class _LODModel(_Model):
  cdef _Model _render_model, _collision_model
  cdef object _low_quality_filename, _medium_quality_filename, _high_quality_filename, _collision_filename
  
  cdef void _init(self)
  cdef      __getcstate__(self)
  cdef void __setcstate__(self, cstate)
  

IF HAS_CAL3D:
  cdef class _Cal3dSubMesh:
    cdef int       _option, _mesh, _submesh
    cdef _Material _material

    cdef int       _nb_faces, _nb_vertices
    cdef short*    _faces
    cdef int*      _face_neighbors

    cdef GLuint    _face_buffer

    cdef _build(self, _AnimatedModel model, CalRenderer* cal_renderer, CalCoreModel* cal_core_model, CalCoreMesh* cal_core_mesh, int mesh, int submesh)
    cdef void _build_neighbors(self, full_filename, float* coords)
    cdef void _init_vertex_buffers(self)
    
  cdef class _AnimatedModel(_Model):
    cdef int    _option
    cdef int    _nb_faces, _nb_vertices
    cdef float  _sphere[4]
    cdef dict   _meshes, _animations
    cdef list   _materials, _submeshes
    cdef object _full_filename
    cdef list   _mini_shaders
    
    cdef CalCoreModel* _core_model
    
    cdef float     _outline_color[4]
    cdef float     _outline_width, _outline_attenuation
    
    cdef void _instanced(self, _Body body, opt)
    cdef void _build_submeshes(self)
    cdef void _batch (self, _Body body)
    cdef void _render(self, _Body body)
    cdef void _render_outline(self, _AnimatedModelData data, _Cal3dSubMesh submesh, Frustum* frustum, float* coords, float* vnormals, float* plane)
    cdef _Material _get_material_4_cal3d(self, image_filename, float diffuse_r, float diffuse_g, float diffuse_b, float diffuse_a, float specular_r, float specular_g, float specular_b, float specular_a, float shininess)
    cdef _Material _create_material_4_cal3d(self, image_filename, float diffuse_r, float diffuse_g, float diffuse_b, float diffuse_a, float specular_r, float specular_g, float specular_b, float specular_a, float shininess)
    cdef void _set_texture_from_model(self, _Material material, image_filename)
    cdef void _build_vertices(self, _AnimatedModelData data)
    
  cdef class _AnimatedModelData(_ModelData):
    cdef int            _option
    cdef _Body          _body
    cdef _AnimatedModel _model
    cdef list           _attached_meshes, _attached_coordsysts
    cdef CalModel*      _cal_model
    cdef float          _delta_time
    cdef float*         _face_planes
    cdef float*         _coords
    cdef float*         _vnormals
    cdef int            _face_plane_ok, _vertex_ok, _bones_ok
    cdef dict           _material_programs

    cdef      __getcstate__(self)
    cdef void __setcstate__(self, cstate)

    cdef void _attach(self, mesh_names)
    cdef void _detach(self, mesh_names)
    cdef int  _is_attached(self, mesh_name)
    cdef void _attach_to_bone(self, CoordSyst coordsyst, bone_name)
    cdef void _detach_from_bone(self, CoordSyst coordsyst)
    cdef void _advance_time(self, float proportion)
    cdef void _begin_round(self)
    cdef      _get_attached_meshes    (self)
    cdef      _get_attached_coordsysts(self)
    cdef void _animate_blend_cycle   (self, animation_name, float weight, float fade_in)
    cdef void _animate_clear_cycle   (self, animation_name, float fade_out)
    cdef void _animate_execute_action(self, animation_name, float fade_in, float fade_out)
    cdef void _animate_reset(self)
    cdef void _set_lod_level(self, float lod_level)
    cdef void _begin_round  (self)
    cdef void _advance_time (self, float proportion)

    cdef int  _update(self)
    cdef void _build_submeshes(self)
    cdef void _build_face_planes(self)
    cdef void _build_bones(self)
    cdef void _build_vertices(self)
    cdef void _attach_all(self)

    cdef void _invalidate_shaders(self)

    

cdef class _GLSLShader(_CObj):
  cdef readonly GLuint shader_type
  cdef readonly GLuint _id
  cdef readonly object code
  cdef public object _filename # str or unicode
  cdef object _uniforms


cdef class _Program(_CObj):
  cdef void _set_rendering_params(self)
  cdef void _set_all_user_params(self, CoordSyst coord_syst, list model_mini_shaders, list material_mini_shaders)
  cdef void _set_user_params(self, dict params)
  cdef void _activate(self)
  
cdef class _GLSLProgram(_Program):
  cdef readonly GLuint _id
  cdef readonly _GLSLShader vertex_shader, pixel_shader
  cdef int _time_uniform, _lighting_mode_uniform, _lights_enabled_uniform, _textures_enabled_uniform, _fog_type_uniform
  cdef public object _filename # tuple of two strs or unicodes
  
  cdef dict _param_2_uniform
  
  cdef void _activate  (self)
  #cdef void _inactivate(self)
  
  cdef void _set_rendering_params(self)
  cdef void _set_user_params     (self, dict params)
  cdef void _set_all_user_params (self, CoordSyst coord_syst, list model_mini_shaders, list material_mini_shaders)

cdef class _FixedPipelineProgam(_Program):
  cdef void _activate(self)
  




cdef class CoordSyst(Position):
  cdef float _matrix               [19]
  cdef float __root_matrix         [19]
  cdef float __inverted_root_matrix[19]
  cdef float _render_matrix        [19]
  cdef int _frustum_id
  cdef int _validity
  cdef int __raypick_data
  cdef int _option
  cdef int _category_bitfield
  cdef list _mini_shaders
  
  cdef      __getcstate__(self)
  cdef void __setcstate__(self, cstate)
  cdef void _batch(self, CoordSyst coord_syst)
  cdef void _render(self, CoordSyst coord_syst)
  cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category)
  cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category)
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category)
  cdef int _contains(self, _CObj obj)
  cdef float* _raypick_data(self, RaypickData data)
  cdef float _distance_out(self, float distance)
  cdef void _invalidate(self)
  cdef void _invalidate_shaders(self)
  cdef void _check_lefthanded(self)
  cdef float* _root_matrix(self)
  cdef float* _inverted_root_matrix(self)
  cdef _World _get_root(self)
  cdef void _get_box(self, float* box, float* matrix)
  cdef void _get_sphere(self, float* sphere)
  cdef void _matrix_into(self, CoordSyst coordsyst, float* result)
  
 
cdef class RaypickData:
  cdef int       option
  cdef Chunk*    raypicked
  cdef Chunk*    raypick_data
  cdef float     root_data[7]
  cdef float     normal   [3]
  cdef float     result, root_result
  cdef CoordSyst result_coordsyst
  

cdef class RaypickContext:
  cdef Chunk* _items
  cdef _World _root


cdef class PythonCoordSyst(CoordSyst):
  cdef void _batch (self, CoordSyst parent)
  cdef void _render(self, CoordSyst coordsyst)


cdef class _CoordSystState(CoordSyst):
  cdef float _quaternion[4]
  
  cdef void _check_state_validity(self)
  cdef void __setcstate__(self, object cstate)
  
cdef class _CoordSystSpeed(CoordSyst):
  cdef void _matrix_into(self, CoordSyst coordsyst, float* result)


cdef class _Vertex(_Point):
  cdef float   _tex_x, _tex_y
  cdef         _diffuse, _emissive
  cdef _Face   _face
  cdef _Vector _normal
  
  cdef __getcstate__(self)
  cdef void __setcstate__(self, object cstate)
  cdef void _render(self, CoordSyst coord_syst)
  cdef float _angle_at(self)


cdef class _Face(CoordSyst):
  cdef object     _vertices
  cdef _Material  _material
  cdef _Vector    _normal
  
  cdef __getcstate__(self)
  cdef void __setcstate__(self, object cstate)
  cdef void _compute_normal(self)
  cdef void _batch(self, CoordSyst coord_syst)
  cdef void _render(self, CoordSyst coord_syst)
  cdef void _get_box(self, float* box, float* matrix)
  cdef void _raypick(self, RaypickData data, CoordSyst parent, int category)
  cdef int _raypick_b(self, RaypickData data, CoordSyst parent, int category)
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category)


cdef class _Body(CoordSyst):
  cdef _Model _model
  cdef _Model _data
  
  cdef __getcstate__(self)
  cdef void __setcstate__(self, object cstate)
  cdef void _batch(self, CoordSyst coordsyst)
  cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category)
  cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category)
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category)
  cdef int _contains(self, _CObj obj)
  cdef void _get_box(self, float* box, float* matrix)
  
  IF HAS_ODE:
    cdef dBodyID _OdeBodyID
    cdef _World _ode_parent
    cdef readonly list joints
    cdef readonly __ode_data     #some data about ODE state load when deserealisation but not yet used
    cdef GLfloat _cm[3] # Centre of mass in local coordinates (Greg Ewing, Oct 2007)
    
    cdef GLfloat _q[4] # Previous quaternion (into ode_parent coord sys)
    cdef GLfloat _p[4] # Previous position   (into ode_parent coord sys)
    cdef float _t # Cumulative round time
    cdef int _valid # Is the previous quaternion/position valid?
    cdef _PlaceableGeom _geom
    
    cdef void _activate_ode_body(_Body self)
    cdef void _activate_ode_body_with(_Body self,_World world)
    cdef void _reactivate_ode_body(_Body self,_World world)
    cdef void _deactivate_ode_body(self)
    cdef _World _find_or_create_most_probable_ode_parent(self)
    cdef void _sync_ode_position(self)
    cdef void _add_joint(self, _Joint joint)
    cdef void _remove_joint(self, _Joint joint)
    
cdef class _World(_Body):
  cdef readonly         children
  cdef _Atmosphere      _atmosphere
  cdef object           _model_builder
  cdef public object    _filename # str or unicode
  
  cdef __getcstate__(self)
  cdef void __setcstate__(self, object cstate)
  cdef _World _get_root(self)
  cdef void _invalidate(self)
  cdef void _batch(self, CoordSyst coordsyst)
  cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category)
  cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category)
  cdef int _contains(self, _CObj obj)
  cdef void _get_box(self, float* box, float* matrix)
  cdef void _search_all(self, predicat, result)
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category)
  
  IF HAS_ODE:
    cdef dWorldID         _OdeWorldID
    cdef readonly         ode_children
    cdef _Space           _space
    cdef _JointGroup      _contact_group
  
    cdef void _activate_ode_world(self)
    cdef void _deactivate_ode_world(self)
    


cdef class _Camera(CoordSyst):
  cdef _World   _to_render
  cdef float    _front, _back, _fov
  cdef Frustum* _frustum
  cdef int      _viewport[4]
  
  cdef __getcstate__(self)
  cdef void __setcstate__(self, object cstate)
  cdef void _init_frustum(self)
  cdef void _subrender_scene(self)
  cdef void _render_scene(self)
  
cdef class _TravelingCamera(_Camera):
  cdef list      _travelings
  cdef Traveling _traveling
  cdef float     _speed_value, _proportion
  cdef _Vector   _speed
  
  cdef void _traveling_changed(self)
    
    
cdef class Traveling(_CObj):
  cdef CoordSyst _incline_as
  cdef int       _smooth_move, _smooth_rotation
  

cdef class _FixTraveling(Traveling):
  cdef Position _target, _direction
  

cdef class _ThirdPersonTraveling(Traveling):
  cdef Position       _target
  cdef _Point         __target, _best, _result, __direction
  cdef _Vector        _direction, __normal
  cdef float          _distance, _offset_y, _offset_y2, _lateral_angle, _top_view
  cdef float          _speed
  cdef RaypickContext _context
  
  cdef float _check(self, RaypickContext root, Position target, _Vector direction, _Point result)



cdef class _Light(CoordSyst):
  cdef public float radius
  cdef float _w, _constant, _linear, _quadratic, _angle, _exponent
  cdef float _colors[16] # ambient + diffuse + specular + shadow colors
  cdef float _data[3] # used by cell-shading and shadow
  cdef readonly int _id
  cdef int _gl_id_enabled
  
  cdef       __getcstate__(self)
  cdef void  __setcstate__(self, object cstate)
  cdef int   _shadow_at(self, float position[3])
  cdef float _spotlight_at(self, float position[3])
  cdef float _attenuation_at(self, float position[3])

  cdef void _static_light_at(self, float* position, float* normal, int shadow, float* result)
  cdef void _cast_into(self, CoordSyst coordsyst)
  cdef void _batch(self, CoordSyst coordsyst)
  cdef void _activate(self)
  cdef void _compute_radius(self)



cdef class _Atmosphere(_CObj):
  cdef int       _option, _fog_type
  cdef float     _fog_start, _fog_end, _fog_density
  cdef float     _ambient  [4]
  cdef float     _bg_color [4]
  cdef float     _fog_color[4]
  
  cdef      __getcstate__(self)
  cdef void __setcstate__(self, object cstate)
  cdef void _clear(self)
  cdef void _draw_bg(self)
  cdef void _render(self)
  cdef float _fog_factor_at(self, float p[3])

  cdef void _begin_round  (self)
  cdef void _advance_time (self, float proportion)
  cdef void _end_round    (self)


cdef class _NoBackgroundAtmosphere(_Atmosphere):
  cdef void _clear(self)
    
cdef class _NoBackgroundNoDepthCleanAtmosphere(_Atmosphere):
  cdef void _clear(self)
  
  
IF OPENGL == "full":
  cdef class _FixedBackgroundAtmosphere(_Atmosphere):
    cdef int x, y, width, height
    cdef GLuint _color_tex_id
    cdef GLuint _depth_tex_id
    
    cdef void _clear(self)
    

cdef class _SkyAtmosphere(_Atmosphere):
  cdef float     _sky_color[4]
  cdef float     _cloud_scale
  cdef _Material _cloud
  cdef           _sky_box
  cdef _Program  _cloud_program
  cdef list      _mini_shaders
  
  cdef      __getcstate__(self)
  cdef void __setcstate__(self, object cstate)
  cdef void _draw_bg(self)
  cdef void _draw_sky_plane(self)
  cdef void _draw_sky_box(self)
  cdef void _invalidate_shaders(self)


cdef class _Portal(CoordSyst):
  cdef _World  _beyond
  cdef object  _beyond_name
  cdef double* _equation  # Clip plane equations
  cdef Context _context
  
  cdef int     _nb_vertices # NB vertex and their coordinates for the portal quad ;
  cdef float*  _coords      # used to draw this quad (for bounds atmosphere or teleporter).
  
  cdef void _compute_clipping_planes(self)
  cdef void _compute_points(self)
  cdef void _batch(self, CoordSyst coordsyst)
  cdef void _atmosphere_clear_part(self)
  cdef void _draw_fog(self, _Atmosphere atmosphere)
  cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category)
  cdef int  _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category)
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category)
  cdef      __getcstate__(self)
  cdef void __setcstate__(self, object cstate)


cdef class _Sprite(CoordSyst):
  cdef float     _width, _height
  cdef float     _color[4]
  cdef _Material _material
  cdef _Program  _program
  
  cdef      __getcstate__(self)
  cdef void __setcstate__(self, object cstate)
  cdef void _batch(self, CoordSyst coordsyst)
  cdef void _render(self, CoordSyst coordsyst)
  cdef void _compute_alpha(self)
  
    
cdef class _CylinderSprite(_Sprite):
  cdef      __getcstate__(self)
  cdef void __setcstate__(self, object cstate)
  cdef void _render(self, CoordSyst coordsyst)


cdef class _Particles(CoordSyst):
  cdef _Material _material
  cdef CoordSyst _particle_coordsyst
  cdef int       _nb_particles, _nb_max_particles, _particle_size # range from 11 to 20 float
  cdef float*    _particles # life, max_life, position, speed, acceleration, [color], [size], [direction]
                            # life, max_life, x/y/z, u/v/w, a/b/c, [r/g/b/a], [w/h], [m/n/o]
  cdef float     _delta_time
  cdef int       _nb_colors, _nb_sizes
  cdef float*    _fading_colors
  cdef float*    _sizes # fading colors and size gain
  cdef int       _nb_creatable_particles, _max_particles_per_round
  cdef _Program  _program
  
  cdef      __getcstate__(self)
  cdef void __setcstate__(self, object cstate)
  cdef void _reinit(self)
  cdef void _advance(self, float proportion)
  cdef void _batch(self, CoordSyst coordsyst)
  cdef void _render(self, CoordSyst coordsyst)
  cdef void _compute_alpha(self)
  cdef void _get_fading_color(self, float life, float max_life, float* returned_color)
  cdef void _get_size(self, float life, float max_life, float* returned_size)
  cdef float* _generate(self, int index, float life)


cdef class Smoke(_Particles):
  cdef float  _life_base
  cdef object _life_function
  cdef float  _speed_factor
  cdef float  _acceleration


cdef class FlagFirework(_Particles):
  cdef _Particles _subgenerator
  cdef int        _nb_sub_particles
    
ctypedef struct TerrainVertex:
  float texcoord[2]
  float normal  [3]
  float coord   [3]
  Pack* pack

cdef struct _TerrainTri

cdef struct _TerrainPatch:
  float        sphere[4]
  char         level # precision level for rendering
  _TerrainTri* tri_top
  _TerrainTri* tri_left
  _TerrainTri* tri_right
  _TerrainTri* tri_bottom
  int          visible
ctypedef _TerrainPatch TerrainPatch

cdef struct _TerrainTri:
  char           level
  float          normal[3]
  float          sphere[4]
  # 3 vertices that determine the triangle. turn right to left (CCW)
  TerrainVertex* v1 # apex vertex
  TerrainVertex* v2 # right vertex for the apex
  TerrainVertex* v3 # left vertex for the apex
  _TerrainTri*   parent
  _TerrainTri*   left_child
  _TerrainTri*   right_child
  _TerrainTri*   left_neighbor
  _TerrainTri*   right_neighbor
  _TerrainTri*   base_neighbor
  Pack*          pack
  TerrainPatch*  patch
  int            texcoord_type # 0: use terrainvertex texcoord, 1, 2, 3, 4: the tri use a texture generated (from blend_material), and the texcoord are (0.0, 0.0) - (1.0, 1.0)
ctypedef _TerrainTri TerrainTri

cdef class _Terrain(CoordSyst):
  cdef list           _materials
  cdef dict           _material_programs
  cdef TerrainVertex* _vertices
  cdef char*          _vertex_options
  cdef int*           _vertex_colors
  cdef float*         _vertex_geos # Geomorph Y coordinate
  cdef float*         _normals # full LOD triangles normals
  cdef int            _nb_colors
  cdef int            _nb_vertex_width # size_width and size_depth must be (2^n) + 1
  cdef int            _nb_vertex_depth # or I don't know what happen (crash?)
  cdef int            _patch_size
  cdef int            _max_level
  cdef float          _texture_factor # a factor that multiply the texture coordinates
  cdef float          _scale_factor # a factor to decide when the triangle must split (higher value means more accuracy)
  cdef float          _split_factor
  cdef int            _nb_patchs
  cdef int            _nb_patch_width
  cdef int            _nb_patch_depth
  cdef TerrainPatch*  _patchs
  
  cdef GLuint         _vertex_buffer

  cdef TerrainVertex* _get_vertex(self, int x, int z)
  cdef void _check_size(self)
  cdef void _free_patchs(self)
  cdef void _add_material(self, _Material material)
  cdef float _get_height(self, int x, int z)
  cdef void _set_height (self, int x, int z, float height)
  cdef void _init(self)
  cdef void _compute_normal(self, int x, int y)
  cdef void _compute_normals(self)
  cdef void _compute_coords(self)
  cdef void _create_patch(self, TerrainPatch* patch, int x, int z, int patch_size)
  cdef void _create_patchs(self)
  cdef void _tri_split(self, TerrainTri* tri)
  cdef int _tri_merge_child(self, TerrainTri* tri)
  cdef void _tri_set_level(self, TerrainTri* tri, char level)
  cdef void _patch_set_level(self, TerrainPatch* patch, char level)
  cdef int _patch_update(self, TerrainPatch* patch, Frustum* frustum, float* frustum_box)
  cdef void _tri_force_presence(self, TerrainTri* tri, TerrainVertex* v)
  cdef void _force_presence(self)
  cdef void _tri_batch(self, TerrainTri* tri, Frustum* frustum)
  cdef void _patch_batch(self, TerrainPatch* patch, Frustum* frustum)
  cdef void _batch(self, CoordSyst coordsyst)
  cdef void _tri_render_middle(self, TerrainTri* tri, int vertex_i)
  cdef void _tri_render_secondpass(self, TerrainTri* tri, int vertex_i)
  cdef void _render(self, CoordSyst coordsyst)
  cdef void _tri_raypick(self, TerrainTri* tri, float* raydata, RaypickData data)
  cdef int _tri_raypick_b(self, TerrainTri* tri, float* raydata, int option)
  cdef void _full_raypick(self, TerrainVertex* v1, TerrainVertex* v2, TerrainVertex* v3, float* normal, float* raydata, RaypickData data)
  cdef void _full_raypick_rect(self, int x1, int z1, int x2, int z2, float* raydata, RaypickData data)
  cdef void _raypick(self, RaypickData raypick_data, CoordSyst raypickable, int category)
  cdef int _full_raypick_b(self, TerrainVertex* v1, TerrainVertex* v2, TerrainVertex* v3, float* normal, float* raydata, int option)
  cdef int _full_raypick_rect_b(self, int x1, int z1, int x2, int z2, float* raydata, int option)
  cdef int _raypick_b(self, RaypickData raypick_data, CoordSyst raypickable, int category)
  cdef void _collect_raypickables(self, Chunk* items, float* rsphere, float* sphere, int category)
  cdef      __getcstate__(self)
  cdef void __setcstate__(self, object cstate)
  cdef void _check_vertex_options(self)
  
  IF HAS_ODE:
    cdef _GeomTerrain _geom
    

IF HAS_TEXT:
  cdef class Glyph:
    cdef readonly float _pixels_x1, _pixels_y1, _pixels_x2, _pixels_y2, width, height, y, x
    cdef readonly unicode unichar

  cdef class _Font:
    cdef FT_Face      _face
    cdef readonly     filename
    cdef int          _width, _height
    cdef dict         _glyphs

    cdef GLubyte*     _pixels
    cdef int          _current_x, _current_y
    cdef readonly int _current_height, _pixels_height
    cdef int          _rendering
    cdef GLuint       _tex_id
    cdef float        _ascender, _descender

    cdef Glyph _get_glyph(self, char_)
    cdef Glyph _gen_glyph(self, char_, int code)
    cdef void _sizeup_pixel(self, int height)
    cdef void _init(self)
    
  
#cdef class _MiniShader:
#  pass

#cdef class _MiniShaderWithParameters(_MiniShader):
#  cdef int _option
#  cdef void _advance_time(self, float proportion)
