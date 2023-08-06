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

SHADER_TYPE_VERTEX = GL_VERTEX_SHADER
SHADER_TYPE_PIXEL  = GL_FRAGMENT_SHADER

cdef class _GLSLShader(_CObj):
  #cdef readonly GLuint shader_type
  #cdef readonly GLuint _id
  #cdef readonly object code

  def __init__(self, shader_type, code, uniforms):
    cdef int   compile_status, size
    cdef char* log
    
    self.shader_type = shader_type
    self._uniforms   = uniforms
    self._id         = glCreateShaderObjectARB(shader_type)
    
    compile_status = GL_TRUE
    
    self.code = code
    
    if hasattr(code, "encode"): code = code.encode("ascii")
    log = code
    glShaderSourceARB (self._id, 1, &log, NULL)
    glCompileShaderARB(self._id)
    glGetShaderiv     (self._id, GL_COMPILE_STATUS, &compile_status)
    if compile_status != GL_TRUE:
      glGetShaderiv(self._id, GL_INFO_LOG_LENGTH, &size)
      log = <char*> malloc(size + 1)
      glGetShaderInfoLog(self._id, size, &size, log)
      log2 = PyString_FromString(log)
      log2 = log2.decode("latin")
      print log2
      free(log)
      raise RuntimeError("Error while compiling GLSL shader!")
    
  def __dealloc__(self):
    glDeleteObjectARB(self._id)


cdef class _Program(_CObj):
  cdef void _set_rendering_params(self): pass
  
  cdef void _set_all_user_params(self, CoordSyst coord_syst, list model_mini_shaders, list material_mini_shaders): pass
  
  cdef void _set_user_params(self, dict params): pass
  
  cdef void _activate  (self): pass
  #cdef void _inactivate(self): pass

  def activate  (self): self._activate  ()
  #def inactivate(self): self._inactivate()


cdef class _GLSLProgram(_Program):
  #cdef readonly GLuint _id
  #cdef readonly _GLSLShader vertex_shader, pixel_shader
  #cdef int _time_uniform, _lighting_mode_uniform, _lights_enabled_uniform, _textures_enabled_uniform, _fog_type_uniform

  def __init__(self, _GLSLShader vertex_shader, _GLSLShader pixel_shader):
    cdef int   link_status, size
    cdef char* log
    
    self._param_2_uniform = {}
    self._id              = glCreateProgramObjectARB()
    self.vertex_shader    = vertex_shader
    self.pixel_shader     = pixel_shader
    glAttachObjectARB(self._id, vertex_shader._id)
    glAttachObjectARB(self._id, pixel_shader ._id)
    glLinkProgramARB (self._id)
    glGetProgramiv(self._id, GL_LINK_STATUS, &link_status)
    if link_status != GL_TRUE:
      glGetProgramiv(self._id, GL_INFO_LOG_LENGTH, &size)
      log = <char*> malloc(size + 1)
      glGetProgramInfoLog(self._id, size, &size, log)
      log2 = PyString_FromString(log)
      log2 = log2.decode("latin")
      print log2
      free(log)
      raise RuntimeError("Error while linking GLSL program")
      
    for uniform in vertex_shader._uniforms | pixel_shader._uniforms:
      self._param_2_uniform[uniform] = glGetUniformLocationARB(self._id, uniform)
      
  def __dealloc__(self):
    glDeleteObjectARB(self._id)
    
  cdef void _set_rendering_params(self):
    cdef int value = 0
    cdef int i
    
    if renderer.current_atmosphere:
      if renderer.current_atmosphere.fog: glUniform1iARB(self._param_2_uniform[b"fog_type"], renderer.current_atmosphere.fog_type)
      else:                               glUniform1iARB(self._param_2_uniform[b"fog_type"], -1)
    else:                                 glUniform1iARB(self._param_2_uniform[b"fog_type"], -1)
    
    if glIsEnabled(GL_LIGHTING): glUniform1iARB(self._param_2_uniform[b"lighting_mode"], 1)
    else:                        glUniform1iARB(self._param_2_uniform[b"lighting_mode"], 0)
    
    for i from 0 <= i < 8:
      if glIsEnabled(GL_LIGHT0 + i): value = value + (1 << i)
    glUniform1iARB(self._param_2_uniform[b"lights_enabled"], value)
    
    value = 0
    if glIsEnabled(GL_TEXTURE_2D): value += 1
    #glActiveTextureARB(GL_TEXTURE1)
    #if glIsEnabled(GL_TEXTURE_2D): value += 2
    #glActiveTextureARB(GL_TEXTURE0)
    glUniform1iARB(self._param_2_uniform[b"textures_enabled"], value)
    
  cdef void _set_all_user_params(self, CoordSyst coord_syst, list model_mini_shaders, list material_mini_shaders):
    #cdef dict params = {}
    while not coord_syst is None:
      for mini_shader in coord_syst.mini_shaders:
        if not mini_shader.params is None: self._set_user_params(mini_shader.params)
      coord_syst = coord_syst._parent

    for mini_shader in model_mini_shaders:
      if not mini_shader.params is None: self._set_user_params(mini_shader.params)
        
    for mini_shader in material_mini_shaders:
      if not mini_shader.params is None: self._set_user_params(mini_shader.params)
      
  cdef void _set_user_params(self, dict params):
    cdef int uniform
    for param in params:
      val     = params[param]
      uniform = self._param_2_uniform.get(param, -1)
      if uniform != -1: # uniform is -1 when using MiniShaderParameters to set inhirited parameters 
        if   isinstance(val   , float): glUniform1fARB(uniform, val)
        elif isinstance(val   , int  ): glUniform1iARB(uniform, val)
        elif len(val) == 2:
          if isinstance(val[0], float): glUniform2fARB(uniform, val[0], val[1])
          else:                         glUniform2iARB(uniform, val[0], val[1])
        elif len(val) == 3:
          if isinstance(val[0], float): glUniform3fARB(uniform, val[0], val[1], val[2])
          else:                         glUniform3iARB(uniform, val[0], val[1], val[2])
        elif len(val) == 4:
          if isinstance(val[0], float): glUniform4fARB(uniform, val[0], val[1], val[2], val[3])
          else:                         glUniform4iARB(uniform, val[0], val[1], val[2], val[3])
      
  cdef void _activate(self):
    global _CURRENT_PROGRAM
    if not _CURRENT_PROGRAM is self:
      glUseProgramObjectARB(self._id)
      _CURRENT_PROGRAM = self
    self._set_rendering_params()
    pass
    
  
cdef class _FixedPipelineProgram(_Program):
  cdef void _activate(self):
    global _CURRENT_PROGRAM
    if not _CURRENT_PROGRAM is self:
      glUseProgramObjectARB(0)
      _CURRENT_PROGRAM = self
    

# cdef class _MiniShader:
#   pass

# cdef class _MiniShaderWithParameters(_MiniShader):
#   def  
#   cdef void _advance_time(self, float proportion):
#     if self._option & MINI_SHADER_HAS_TIME:
#       self._params[] += proportion

