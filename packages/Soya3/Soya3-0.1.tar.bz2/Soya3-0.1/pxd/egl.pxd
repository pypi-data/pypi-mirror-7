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



cdef extern from "EGL/egl.h":
  ctypedef unsigned int EGLBoolean
  ctypedef unsigned int EGLenum
  ctypedef int EGLint
  ctypedef void* EGLConfig
  ctypedef void* EGLContext
  ctypedef void* EGLDisplay
  ctypedef void* EGLSurface
  ctypedef void* EGLClientBuffer
  

  
  int EGL_VERSION_1_0
  int EGL_VERSION_1_1
  int EGL_VERSION_1_2
  int EGL_VERSION_1_3
  int EGL_VERSION_1_4
  int EGL_FALSE
  int EGL_TRUE
  int EGL_DEFAULT_DISPLAY
  int EGL_NO_CONTEXT
  int EGL_NO_DISPLAY
  int EGL_NO_SURFACE
  int EGL_DONT_CARE
  int EGL_SUCCESS
  int EGL_NOT_INITIALIZED
  int EGL_BAD_ACCESS
  int EGL_BAD_ALLOC
  int EGL_BAD_ATTRIBUTE
  int EGL_BAD_CONFIG
  int EGL_BAD_CONTEXT
  int EGL_BAD_CURRENT_SURFACE
  int EGL_BAD_DISPLAY
  int EGL_BAD_MATCH
  int EGL_BAD_NATIVE_PIXMAP
  int EGL_BAD_NATIVE_WINDOW
  int EGL_BAD_PARAMETER
  int EGL_BAD_SURFACE
  int EGL_CONTEXT_LOST
  int EGL_BUFFER_SIZE
  int EGL_ALPHA_SIZE
  int EGL_BLUE_SIZE
  int EGL_GREEN_SIZE
  int EGL_RED_SIZE
  int EGL_DEPTH_SIZE
  int EGL_STENCIL_SIZE
  int EGL_CONFIG_CAVEAT
  int EGL_CONFIG_ID
  int EGL_LEVEL
  int EGL_MAX_PBUFFER_HEIGHT
  int EGL_MAX_PBUFFER_PIXELS
  int EGL_MAX_PBUFFER_WIDTH
  int EGL_NATIVE_RENDERABLE
  int EGL_NATIVE_VISUAL_ID
  int EGL_NATIVE_VISUAL_TYPE
  int EGL_SAMPLES
  int EGL_SAMPLE_BUFFERS
  int EGL_SURFACE_TYPE
  int EGL_TRANSPARENT_TYPE
  int EGL_TRANSPARENT_BLUE_VALUE
  int EGL_TRANSPARENT_GREEN_VALUE
  int EGL_TRANSPARENT_RED_VALUE
  int EGL_NONE
  int EGL_BIND_TO_TEXTURE_RGB
  int EGL_BIND_TO_TEXTURE_RGBA
  int EGL_MIN_SWAP_INTERVAL
  int EGL_MAX_SWAP_INTERVAL
  int EGL_LUMINANCE_SIZE
  int EGL_ALPHA_MASK_SIZE
  int EGL_COLOR_BUFFER_TYPE
  int EGL_RENDERABLE_TYPE
  int EGL_MATCH_NATIVE_PIXMAP
  int EGL_CONFORMANT
  int EGL_SLOW_CONFIG
  int EGL_NON_CONFORMANT_CONFIG
  int EGL_TRANSPARENT_RGB
  int EGL_RGB_BUFFER
  int EGL_LUMINANCE_BUFFER
  int EGL_NO_TEXTURE
  int EGL_TEXTURE_RGB
  int EGL_TEXTURE_RGBA
  int EGL_TEXTURE_2D
  int EGL_PBUFFER_BIT
  int EGL_PIXMAP_BIT
  int EGL_WINDOW_BIT
  int EGL_VG_COLORSPACE_LINEAR_BIT
  int EGL_VG_ALPHA_FORMAT_PRE_BIT
  int EGL_MULTISAMPLE_RESOLVE_BOX_BIT
  int EGL_SWAP_BEHAVIOR_PRESERVED_BIT
  int EGL_OPENGL_ES_BIT
  int EGL_OPENVG_BIT
  int EGL_OPENGL_ES2_BIT
  int EGL_OPENGL_BIT
  int EGL_VENDOR
  int EGL_VERSION
  int EGL_EXTENSIONS
  int EGL_CLIENT_APIS
  int EGL_HEIGHT
  int EGL_WIDTH
  int EGL_LARGEST_PBUFFER
  int EGL_TEXTURE_FORMAT
  int EGL_TEXTURE_TARGET
  int EGL_MIPMAP_TEXTURE
  int EGL_MIPMAP_LEVEL
  int EGL_RENDER_BUFFER
  int EGL_VG_COLORSPACE
  int EGL_VG_ALPHA_FORMAT
  int EGL_HORIZONTAL_RESOLUTION
  int EGL_VERTICAL_RESOLUTION
  int EGL_PIXEL_ASPECT_RATIO
  int EGL_SWAP_BEHAVIOR
  int EGL_MULTISAMPLE_RESOLVE
  int EGL_BACK_BUFFER
  int EGL_SINGLE_BUFFER
  int EGL_VG_COLORSPACE_sRGB
  int EGL_VG_COLORSPACE_LINEAR
  int EGL_VG_ALPHA_FORMAT_NONPRE
  int EGL_VG_ALPHA_FORMAT_PRE
  int EGL_DISPLAY_SCALING
  int EGL_UNKNOWN
  int EGL_BUFFER_PRESERVED
  int EGL_BUFFER_DESTROYED
  int EGL_OPENVG_IMAGE
  int EGL_CONTEXT_CLIENT_TYPE
  int EGL_CONTEXT_CLIENT_VERSION
  int EGL_MULTISAMPLE_RESOLVE_DEFAULT
  int EGL_MULTISAMPLE_RESOLVE_BOX
  int EGL_OPENGL_ES_API
  int EGL_OPENVG_API
  int EGL_OPENGL_API
  int EGL_DRAW
  int EGL_READ
  int EGL_CORE_NATIVE_ENGINE
  int EGL_COLORSPACE
  int EGL_ALPHA_FORMAT
  int EGL_COLORSPACE_sRGB
  int EGL_COLORSPACE_LINEAR
  int EGL_ALPHA_FORMAT_NONPRE
  int EGL_ALPHA_FORMAT_PRE

  cdef EGLint  eglGetError()

  cdef EGLDisplay    eglGetDisplay(int display_id)
  cdef EGLBoolean    eglInitialize(EGLDisplay dpy, EGLint *major, EGLint *minor)
  cdef EGLBoolean    eglTerminate(EGLDisplay dpy)

  cdef  char *    eglQueryString(EGLDisplay dpy, EGLint name)

  cdef EGLBoolean    eglGetConfigs(EGLDisplay dpy, EGLConfig *configs, EGLint config_size, EGLint *num_config)
  cdef EGLBoolean    eglChooseConfig(EGLDisplay dpy,  EGLint *attrib_list, EGLConfig *configs, EGLint config_size, EGLint *num_config)
  cdef EGLBoolean    eglGetConfigAttrib(EGLDisplay dpy, EGLConfig config, EGLint attribute, EGLint *value)

  cdef EGLSurface    eglCreateWindowSurface(EGLDisplay dpy, EGLConfig config, void* win,  EGLint *attrib_list)
  cdef EGLSurface    eglCreatePbufferSurface(EGLDisplay dpy, EGLConfig config,  EGLint *attrib_list)
  cdef EGLSurface    eglCreatePixmapSurface(EGLDisplay dpy, EGLConfig config, void* pixmap,  EGLint *attrib_list)
  cdef EGLBoolean    eglDestroySurface(EGLDisplay dpy, EGLSurface surface)
  cdef EGLBoolean    eglQuerySurface(EGLDisplay dpy, EGLSurface surface, EGLint attribute, EGLint *value)

  cdef EGLBoolean    eglBindAPI(EGLenum api)
  cdef EGLenum    eglQueryAPI()

  cdef EGLBoolean    eglWaitClient()

  cdef EGLBoolean    eglReleaseThread()

  cdef EGLSurface    eglCreatePbufferFromClientBuffer( EGLDisplay dpy, EGLenum buftype, EGLClientBuffer buffer, EGLConfig config,  EGLint *attrib_list)

  cdef EGLBoolean    eglSurfaceAttrib(EGLDisplay dpy, EGLSurface surface, EGLint attribute, EGLint value)
  cdef EGLBoolean    eglBindTexImage(EGLDisplay dpy, EGLSurface surface, EGLint buffer)
  cdef EGLBoolean    eglReleaseTexImage(EGLDisplay dpy, EGLSurface surface, EGLint buffer)


  cdef EGLBoolean    eglSwapInterval(EGLDisplay dpy, EGLint interval)


  cdef EGLContext    eglCreateContext(EGLDisplay dpy, EGLConfig config, int share_context,  EGLint *attrib_list)
  cdef EGLBoolean    eglDestroyContext(EGLDisplay dpy, EGLContext ctx)
  cdef EGLBoolean    eglMakeCurrent(EGLDisplay dpy, EGLSurface draw, EGLSurface read, EGLContext ctx)

  cdef EGLContext    eglGetCurrentContext()
  cdef EGLSurface    eglGetCurrentSurface(EGLint readdraw)
  cdef EGLDisplay    eglGetCurrentDisplay()
  cdef EGLBoolean    eglQueryContext(EGLDisplay dpy, EGLContext ctx, EGLint attribute, EGLint *value)

  cdef EGLBoolean    eglWaitGL()
  cdef EGLBoolean    eglWaitNative(EGLint engine)
  cdef EGLBoolean    eglSwapBuffers(EGLDisplay dpy, EGLSurface surface)
  cdef EGLBoolean    eglCopyBuffers(EGLDisplay dpy, EGLSurface surface, void* target)

