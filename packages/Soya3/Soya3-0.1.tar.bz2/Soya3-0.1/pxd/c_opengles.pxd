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


ctypedef double GLdouble

cdef extern from "libogl.h":
  void OS_InitFakeOS()
  void* OS_CreateWindow()
  unsigned int OS_GetTickCount()
  void OS_GetWindowSize(void* hNativeWnd, int* width, int* height)
  void OS_Sleep(unsigned int milliseconds)
  
cdef extern from "GLES/gl.h":
  ctypedef unsigned int    GLenum
  ctypedef unsigned char  GLboolean
  ctypedef unsigned int    GLbitfield
  ctypedef void            GLvoid
  ctypedef signed char    GLbyte
  ctypedef short          GLshort
  ctypedef int            GLint
  ctypedef unsigned char  GLubyte
  ctypedef unsigned short  GLushort
  ctypedef unsigned int    GLuint
  ctypedef int            GLsizei
  ctypedef float          GLfloat
  ctypedef float          GLclampf
  ctypedef double          GLclampd
  ctypedef char           GLchar
  ctypedef unsigned int   GLhandleARB
  ctypedef int             GLfixed
  ctypedef int             GLclampx
  ctypedef long int        GLintptr
  ctypedef long int        GLsizeiptr

  int GL_FALSE
  int GL_TRUE
  
  int GL_ZERO
  int GL_ONE
  
  int GL_NEVER
  int GL_LESS
  int GL_EQUAL
  int GL_LEQUAL
  int GL_GREATER
  int GL_NOTEQUAL
  int GL_GEQUAL
  int GL_ALWAYS
  
  int GL_BYTE
  int GL_UNSIGNED_BYTE
  int GL_SHORT
  int GL_UNSIGNED_SHORT
  int GL_FLOAT
  int GL_FIXED
  
  int GL_POINTS
  int GL_LINES
  int GL_LINE_LOOP
  int GL_LINE_STRIP
  int GL_TRIANGLES
  int GL_TRIANGLE_STRIP
  int GL_TRIANGLE_FAN
  
  int GL_VERTEX_ARRAY
  int GL_NORMAL_ARRAY
  int GL_COLOR_ARRAY
  int GL_TEXTURE_COORD_ARRAY
  int GL_MATRIX_INDEX_ARRAY_OES
  int GL_WEIGHT_ARRAY_OES
  int GL_POINT_SIZE_ARRAY_OES
  
  int GL_ARRAY_BUFFER
  int GL_ELEMENT_ARRAY_BUFFER
  int GL_STREAM_DRAW
  int GL_STATIC_DRAW
  int GL_DYNAMIC_DRAW
  int GL_BUFFER_SIZE
  int GL_BUFFER_USAGE
  int GL_BUFFER_ACCESS
  int GL_WRITE_ONLY
  
  int GL_MODELVIEW
  int GL_PROJECTION
  int GL_TEXTURE
  
  int GL_MATRIX_PALETTE_OES
  
  int GL_POINT_SMOOTH
  int GL_LINE_SMOOTH
  
  int GL_CW
  int GL_CCW
  int GL_FRONT
  int GL_BACK
  int GL_CULL_FACE
  int GL_POLYGON_OFFSET_FILL
  
  int GL_LIGHTING
  int GL_LIGHT0
  int GL_LIGHT1
  int GL_LIGHT2
  int GL_LIGHT3
  int GL_LIGHT4
  int GL_LIGHT5
  int GL_LIGHT6
  int GL_LIGHT7
  int GL_SPOT_EXPONENT
  int GL_SPOT_CUTOFF
  int GL_CONSTANT_ATTENUATION
  int GL_LINEAR_ATTENUATION
  int GL_QUADRATIC_ATTENUATION
  int GL_AMBIENT
  int GL_DIFFUSE
  int GL_SPECULAR
  int GL_EMISSION
  int GL_SHININESS
  int GL_POSITION
  int GL_SPOT_DIRECTION
  int GL_AMBIENT_AND_DIFFUSE
  int GL_LIGHT_MODEL_TWO_SIDE
  int GL_LIGHT_MODEL_AMBIENT
  int GL_FRONT_AND_BACK
  int GL_FLAT
  int GL_SMOOTH
  int GL_COLOR_MATERIAL
  int GL_NORMALIZE
  int GL_ADD
  int GL_BLEND
  int GL_SRC_COLOR
  int GL_ONE_MINUS_SRC_COLOR
  int GL_SRC_ALPHA
  int GL_ONE_MINUS_SRC_ALPHA
  int GL_DST_ALPHA
  int GL_ONE_MINUS_DST_ALPHA
  int GL_DST_COLOR
  int GL_ONE_MINUS_DST_COLOR
  int GL_SRC_ALPHA_SATURATE
  
  int GL_FOG
  int GL_FOG_DENSITY
  int GL_FOG_START
  int GL_FOG_END
  int GL_FOG_MODE
  int GL_FOG_COLOR
  int GL_EXP
  int GL_EXP2
  
  int GL_CLEAR
  int GL_AND
  int GL_AND_REVERSE
  int GL_COPY
  int GL_AND_INVERTED
  int GL_NOOP
  int GL_XOR
  int GL_OR
  int GL_NOR
  int GL_EQUIV
  int GL_INVERT
  int GL_OR_REVERSE
  int GL_COPY_INVERTED
  int GL_OR_INVERTED
  int GL_NAND
  int GL_SET
  
  int GL_DEPTH_TEST
  int GL_STENCIL_TEST
  int GL_ALPHA_TEST
  int GL_DITHER
  int GL_COLOR_LOGIC_OP
  int GL_SCISSOR_TEST
  int GL_RESCALE_NORMAL
  
  int GL_POINT_SPRITE_OES
  
  int GL_KEEP
  int GL_REPLACE
  int GL_INCR
  int GL_DECR
  
  int GL_ALPHA
  int GL_RGB
  int GL_RGBA
  int GL_LUMINANCE
  int GL_LUMINANCE_ALPHA
  
  int GL_SMOOTH_POINT_SIZE_RANGE
  int GL_SMOOTH_LINE_WIDTH_RANGE
  int GL_ALIASED_POINT_SIZE_RANGE
  int GL_ALIASED_LINE_WIDTH_RANGE
  int GL_MAX_LIGHTS
  int GL_MAX_TEXTURE_SIZE
  int GL_MAX_MODELVIEW_STACK_DEPTH
  int GL_MAX_PROJECTION_STACK_DEPTH
  int GL_MAX_TEXTURE_STACK_DEPTH
  int GL_MAX_VIEWPORT_DIMS
  int GL_SUBPIXEL_BITS
  int GL_RED_BITS
  int GL_GREEN_BITS
  int GL_BLUE_BITS
  int GL_ALPHA_BITS
  int GL_DEPTH_BITS
  int GL_STENCIL_BITS
  int GL_MAX_ELEMENTS_VERTICES
  int GL_MAX_ELEMENTS_INDICES
  int GL_MAX_TEXTURE_UNITS
  int GL_NUM_COMPRESSED_TEXTURE_FORMATS
  int GL_COMPRESSED_TEXTURE_FORMATS
  int GL_IMPLEMENTATION_COLOR_READ_TYPE_OES
  int GL_IMPLEMENTATION_COLOR_READ_FORMAT_OES
  
  int GL_MAX_PALETTE_MATRICES_OES
  int GL_MAX_VERTEX_UNITS_OES
  int GL_MAX_CLIP_PLANES
  
  int GL_CLIENT_ACTIVE_TEXTURE
  int GL_VERTEX_ARRAY_SIZE
  int GL_VERTEX_ARRAY_TYPE
  int GL_VERTEX_ARRAY_POINTER
  int GL_VERTEX_ARRAY_STRIDE
  int GL_NORMAL_ARRAY_TYPE
  int GL_NORMAL_ARRAY_STRIDE
  int GL_NORMAL_ARRAY_POINTER
  int GL_COLOR_ARRAY_SIZE
  int GL_COLOR_ARRAY_TYPE
  int GL_COLOR_ARRAY_STRIDE
  int GL_COLOR_ARRAY_POINTER
  int GL_TEXTURE_COORD_ARRAY_SIZE
  int GL_TEXTURE_COORD_ARRAY_TYPE
  int GL_TEXTURE_COORD_ARRAY_STRIDE
  int GL_TEXTURE_COORD_ARRAY_POINTER
  int GL_ARRAY_BUFFER_BINDING
  int GL_VERTEX_ARRAY_BUFFER_BINDING
  int GL_NORMAL_ARRAY_BUFFER_BINDING
  int GL_COLOR_ARRAY_BUFFER_BINDING
  int GL_TEXTURE_COORD_ARRAY_BUFFER_BINDING
  int GL_ELEMENT_ARRAY_BUFFER_BINDING
  int GL_VIEWPORT
  int GL_DEPTH_RANGE
  int GL_MATRIX_MODE
  int GL_SHADE_MODEL
  int GL_POINT_SIZE
  int GL_LINE_WIDTH
  int GL_CULL_FACE_MODE
  int GL_FRONT_FACE
  int GL_POLYGON_OFFSET_FACTOR
  int GL_POLYGON_OFFSET_UNITS
  int GL_TEXTURE_BINDING_2D
  int GL_ACTIVE_TEXTURE
  int GL_SCISSOR_BOX
  int GL_ALPHA_TEST_FUNC
  int GL_ALPHA_TEST_REF
  int GL_STENCIL_FUNC
  int GL_STENCIL_VALUE_MASK
  int GL_STENCIL_REF
  int GL_STENCIL_FAIL
  int GL_STENCIL_PASS_DEPTH_FAIL
  int GL_STENCIL_PASS_DEPTH_PASS
  int GL_DEPTH_FUNC
  int GL_BLEND_SRC
  int GL_BLEND_DST
  int GL_LOGIC_OP_MODE
  int GL_COLOR_WRITEMASK
  int GL_DEPTH_WRITEMASK
  int GL_STENCIL_WRITEMASK
  int GL_COLOR_CLEAR_VALUE
  int GL_DEPTH_CLEAR_VALUE
  int GL_STENCIL_CLEAR_VALUE
  int GL_MODELVIEW_MATRIX
  int GL_PROJECTION_MATRIX
  int GL_TEXTURE_MATRIX
  int GL_MODELVIEW_STACK_DEPTH
  int GL_PROJECTION_STACK_DEPTH
  int GL_TEXTURE_STACK_DEPTH
  int GL_MATRIX_INDEX_ARRAY_SIZE_OES
  int GL_MATRIX_INDEX_ARRAY_TYPE_OES
  int GL_MATRIX_INDEX_ARRAY_STRIDE_OES
  int GL_MATRIX_INDEX_ARRAY_POINTER_OES
  int GL_MATRIX_INDEX_ARRAY_BUFFER_BINDING_OES
  int GL_WEIGHT_ARRAY_SIZE_OES
  int GL_WEIGHT_ARRAY_TYPE_OES
  int GL_WEIGHT_ARRAY_STRIDE_OES
  int GL_WEIGHT_ARRAY_POINTER_OES
  int GL_WEIGHT_ARRAY_BUFFER_BINDING_OES
  int GL_POINT_SIZE_ARRAY_TYPE_OES
  int GL_POINT_SIZE_ARRAY_STRIDE_OES
  int GL_POINT_SIZE_ARRAY_POINTER_OES
  int GL_POINT_SIZE_ARRAY_BUFFER_BINDING_OES
  int GL_SAMPLE_COVERAGE_INVERT
  int GL_SAMPLE_COVERAGE_VALUE
  int GL_POINT_SIZE_MIN
  int GL_POINT_SIZE_MAX
  int GL_POINT_FADE_THRESHOLD_SIZE
  int GL_POINT_DISTANCE_ATTENUATION
  int GL_CURRENT_COLOR
  int GL_CURRENT_NORMAL
  int GL_CURRENT_TEXTURE_COORDS
  int GL_MODELVIEW_MATRIX_FLOAT_AS_INT_BITS_OES
  int GL_PROJECTION_MATRIX_FLOAT_AS_INT_BITS_OES
  int GL_TEXTURE_MATRIX_FLOAT_AS_INT_BITS_OES
  
  int GL_CLIP_PLANE0
  int GL_CLIP_PLANE1
  int GL_CLIP_PLANE2
  int GL_CLIP_PLANE3
  int GL_CLIP_PLANE4
  int GL_CLIP_PLANE5
  
  int GL_PERSPECTIVE_CORRECTION_HINT
  int GL_LINE_SMOOTH_HINT
  int GL_POINT_SMOOTH_HINT
  int GL_FOG_HINT
  int GL_DONT_CARE
  int GL_FASTEST
  int GL_NICEST
  
  int GL_GENERATE_MIPMAP_HINT
  
  int GL_UNPACK_ALIGNMENT
  int GL_PACK_ALIGNMENT
  
  int GL_MULTISAMPLE
  int GL_SAMPLE_ALPHA_TO_COVERAGE
  int GL_SAMPLE_ALPHA_TO_ONE
  int GL_SAMPLE_COVERAGE
  int GL_SAMPLE_BUFFERS
  int GL_SAMPLES
  
  int GL_TEXTURE_2D
  int GL_TEXTURE_ENV
  int GL_TEXTURE_ENV_MODE
  int GL_TEXTURE_MAG_FILTER
  int GL_TEXTURE_MIN_FILTER
  int GL_TEXTURE_WRAP_S
  int GL_TEXTURE_WRAP_T
  int GL_TEXTURE_ENV_COLOR
  int GL_MODULATE
  int GL_DECAL
  int GL_NEAREST
  int GL_LINEAR
  int GL_NEAREST_MIPMAP_NEAREST
  int GL_LINEAR_MIPMAP_NEAREST
  int GL_NEAREST_MIPMAP_LINEAR
  int GL_LINEAR_MIPMAP_LINEAR
  int GL_REPEAT
  int GL_CLAMP_TO_EDGE
  
  int GL_GENERATE_MIPMAP
  int GL_COORD_REPLACE_OES
  int GL_TEXTURE_CROP_RECT_OES
  
  int GL_COMBINE
  int GL_COMBINE_RGB
  int GL_COMBINE_ALPHA
  int GL_SOURCE0_RGB
  int GL_SOURCE1_RGB
  int GL_SOURCE2_RGB
  int GL_SOURCE0_ALPHA
  int GL_SOURCE1_ALPHA
  int GL_SOURCE2_ALPHA
  int GL_SRC0_RGB
  int GL_SRC1_RGB
  int GL_SRC2_RGB
  int GL_SRC0_ALPHA
  int GL_SRC1_ALPHA
  int GL_SRC2_ALPHA
  int GL_OPERAND0_RGB
  int GL_OPERAND1_RGB
  int GL_OPERAND2_RGB
  int GL_OPERAND0_ALPHA
  int GL_OPERAND1_ALPHA
  int GL_OPERAND2_ALPHA
  int GL_RGB_SCALE
  int GL_ALPHA_SCALE
  int GL_ADD_SIGNED
  int GL_INTERPOLATE
  int GL_SUBTRACT
  int GL_DOT3_RGB
  int GL_DOT3_RGBA
  int GL_CONSTANT
  int GL_PRIMARY_COLOR
  int GL_PREVIOUS
  
  int GL_PALETTE4_RGB8_OES
  int GL_PALETTE4_RGBA8_OES
  int GL_PALETTE4_R5_G6_B5_OES
  int GL_PALETTE4_RGBA4_OES
  int GL_PALETTE4_RGB5_A1_OES
  int GL_PALETTE8_RGB8_OES
  int GL_PALETTE8_RGBA8_OES
  int GL_PALETTE8_R5_G6_B5_OES
  int GL_PALETTE8_RGBA4_OES
  int GL_PALETTE8_RGB5_A1_OES
  
  int GL_VENDOR
  int GL_RENDERER
  int GL_VERSION
  int GL_EXTENSIONS
  
  int GL_NO_ERROR
  int GL_INVALID_ENUM
  int GL_INVALID_VALUE
  int GL_INVALID_OPERATION
  int GL_STACK_OVERFLOW
  int GL_STACK_UNDERFLOW
  int GL_OUT_OF_MEMORY
  
  int GL_UNSIGNED_SHORT_5_6_5
  int GL_UNSIGNED_SHORT_4_4_4_4
  int GL_UNSIGNED_SHORT_5_5_5_1
  
  int GL_DEPTH_BUFFER_BIT
  int GL_STENCIL_BUFFER_BIT
  int GL_COLOR_BUFFER_BIT
  
  int GL_TEXTURE0
  int GL_TEXTURE1
  int GL_TEXTURE2
  int GL_TEXTURE3
  int GL_TEXTURE4
  int GL_TEXTURE5
  int GL_TEXTURE6
  int GL_TEXTURE7
  int GL_TEXTURE8
  int GL_TEXTURE9
  int GL_TEXTURE10
  int GL_TEXTURE11
  int GL_TEXTURE12
  int GL_TEXTURE13
  int GL_TEXTURE14
  int GL_TEXTURE15
  int GL_TEXTURE16
  int GL_TEXTURE17
  int GL_TEXTURE18
  int GL_TEXTURE19
  int GL_TEXTURE20
  int GL_TEXTURE21
  int GL_TEXTURE22
  int GL_TEXTURE23
  int GL_TEXTURE24
  int GL_TEXTURE25
  int GL_TEXTURE26
  int GL_TEXTURE27
  int GL_TEXTURE28
  int GL_TEXTURE29
  int GL_TEXTURE30
  int GL_TEXTURE31


  cdef void             glActiveTexture         (GLenum texture)
  cdef void             glAlphaFunc             (GLenum func, GLclampf ref)
  cdef void             glAlphaFuncx            (GLenum func, GLclampx ref)
  cdef void             glBindTexture           (GLenum target, GLuint texture)
  cdef void             glBlendFunc             (GLenum sfactor, GLenum dfactor)
  cdef void             glClear                 (GLbitfield mask)
  cdef void             glClearColor            (GLclampf red, GLclampf green, GLclampf blue, GLclampf alpha)
  cdef void             glClearColorx           (GLclampx red, GLclampx green, GLclampx blue, GLclampx alpha)
  cdef void             glClearDepthf           (GLclampf depth)
  cdef void             glClearDepthx           (GLclampx depth)
  cdef void             glClearStencil          (GLint s)
  cdef void             glClientActiveTexture   (GLenum texture)
  cdef void             glColor4f               (GLfloat red, GLfloat green, GLfloat blue, GLfloat alpha)
  cdef void             glColor4x               (GLfixed red, GLfixed green, GLfixed blue, GLfixed alpha)
  cdef void             glColorMask             (GLboolean red, GLboolean green, GLboolean blue, GLboolean alpha)
  cdef void             glColorPointer          (GLint size, GLenum type, GLsizei stride,  GLvoid* ptr)
  cdef void             glCompressedTexImage2D  (GLenum target, GLint level, GLenum internalformat, GLsizei width, GLsizei height, GLint border, GLsizei imageSize,  GLvoid* data)
  cdef void             glCompressedTexSubImage2D(GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width, GLsizei height, GLenum format, GLsizei imageSize,  GLvoid* data)
  cdef void             glCopyTexImage2D        (GLenum target, GLint level, GLenum internalformat, GLint x, GLint y, GLsizei width, GLsizei height, GLint border)
  cdef void             glCopyTexSubImage2D     (GLenum target, GLint level, GLint xoffset, GLint yoffset, GLint x, GLint y, GLsizei width, GLsizei height)
  cdef void             glCullFace              (GLenum mode)
  cdef void             glDeleteTextures        (GLsizei n,  GLuint* textures)
  cdef void             glDepthFunc             (GLenum func)
  cdef void             glDepthMask             (GLboolean flag)
  cdef void             glDepthRangef           (GLclampf nearValue, GLclampf farValue)
  cdef void             glDepthRangex           (GLclampx nearValue, GLclampx farValue)
  cdef void             glDisable               (GLenum cap)
  cdef void             glDisableClientState    (GLenum cap)
  cdef void             glDrawArrays            (GLenum mode, GLint first, GLsizei count)
  cdef void             glDrawElements          (GLenum mode, GLsizei count, GLenum type,  GLvoid* indices)
  cdef void             glEnable                (GLenum cap)
  cdef void             glEnableClientState     (GLenum cap)
  cdef void             glFinish                ()
  cdef void             glFlush                 ()
  cdef void             glFogf                  (GLenum pname, GLfloat param)
  cdef void             glFogfv                 (GLenum pname,  GLfloat* params)
  cdef void             glFogx                  (GLenum pname, GLfixed param)
  cdef void             glFogxv                 (GLenum pname,  GLfixed* params)
  cdef void             glFrontFace             (GLenum mode)
  cdef void             glFrustumf              (GLfloat left, GLfloat right, GLfloat bottom, GLfloat top, GLfloat near_val, GLfloat far_val)
  cdef void             glFrustumx              (GLfixed left, GLfixed right, GLfixed bottom, GLfixed top, GLfixed near_val, GLfixed far_val)
  cdef void             glGenTextures           (GLsizei n, GLuint* textures)
  cdef GLenum           glGetError              ()
  cdef void             glGetIntegerv           (GLenum pname, GLint* params)
  cdef  GLubyte*   glGetString             (GLenum name)
  cdef void             glHint                  (GLenum target, GLenum mode)
  cdef void             glLightf                (GLenum light, GLenum pname, GLfloat param)
  cdef void             glLightfv               (GLenum light, GLenum pname,  GLfloat* params)
  cdef void             glLightx                (GLenum light, GLenum pname, GLfixed param)
  cdef void             glLightxv               (GLenum light, GLenum pname,  GLfixed* params)
  cdef void             glLightModelf           (GLenum pname, GLfloat param)
  cdef void             glLightModelfv          (GLenum pname,  GLfloat* params)
  cdef void             glLightModelx           (GLenum pname, GLfixed param)
  cdef void             glLightModelxv          (GLenum pname,  GLfixed* params)
  cdef void             glLineWidth             (GLfloat width)
  cdef void             glLineWidthx            (GLfixed width)
  cdef void             glLoadIdentity          ()
  cdef void             glLoadMatrixf           ( GLfloat* m)
  cdef void             glLoadMatrixx           ( GLfixed* m)
  cdef void             glLogicOp               (GLenum opcode)
  cdef void             glMaterialf             (GLenum face, GLenum pname, GLfloat param)
  cdef void             glMaterialfv            (GLenum face, GLenum pname,  GLfloat* params)
  cdef void             glMaterialx             (GLenum face, GLenum pname, GLfixed param)
  cdef void             glMaterialxv            (GLenum face, GLenum pname,  GLfixed* params)
  cdef void             glMatrixMode            (GLenum mode)
  cdef void             glMultiTexCoord4f       (GLenum target, GLfloat s, GLfloat t, GLfloat r, GLfloat q)
  cdef void             glMultiTexCoord4x       (GLenum target, GLfixed s, GLfixed t, GLfixed r, GLfixed q)
  cdef void             glMultMatrixf           ( GLfloat* m)
  cdef void             glMultMatrixx           ( GLfixed* m)
  cdef void             glNormal3f              (GLfloat nx, GLfloat ny, GLfloat nz)
  cdef void             glNormal3x              (GLfixed nx, GLfixed ny, GLfixed nz)
  cdef void             glNormalPointer         (GLenum type, GLsizei stride,  GLvoid* ptr)
  cdef void             glOrthof                (GLfloat left, GLfloat right, GLfloat bottom, GLfloat top, GLfloat near_val, GLfloat far_val)
  cdef void             glOrthox                (GLfixed left, GLfixed right, GLfixed bottom, GLfixed top, GLfixed near_val, GLfixed far_val)
  cdef void             glPixelStorei           (GLenum pname, GLint param)
  cdef void             glPointSize             (GLfloat size)
  cdef void             glPointSizex            (GLfixed size)
  cdef void             glPolygonOffset         (GLfloat factor, GLfloat units)
  cdef void             glPolygonOffsetx        (GLfixed factor, GLfixed units)
  cdef void             glPopMatrix             ()
  cdef void             glPushMatrix            ()
  cdef void             glReadPixels            (GLint x, GLint y, GLsizei width, GLsizei height, GLenum format, GLenum type, GLvoid* pixels)
  cdef void             glRotatef               (GLfloat angle, GLfloat x, GLfloat y, GLfloat z)
  cdef void             glRotatex               (GLfixed angle, GLfixed x, GLfixed y, GLfixed z)
  cdef void             glSampleCoverage        (GLclampf value, GLboolean invert)
  cdef void             glSampleCoveragex       (GLclampx value, GLboolean invert)
  cdef void             glScalef                (GLfloat x, GLfloat y, GLfloat z)
  cdef void             glScalex                (GLfixed x, GLfixed y, GLfixed z)
  cdef void             glScissor               (GLint x, GLint y, GLsizei width, GLsizei height)
  cdef void             glShadeModel            (GLenum mode)
  cdef void             glStencilFunc           (GLenum func, GLint ref, GLuint mask)
  cdef void             glStencilMask           (GLuint mask)
  cdef void             glStencilOp             (GLenum fail, GLenum zfail, GLenum zpass)
  cdef void             glTexCoordPointer       (GLint size, GLenum type, GLsizei stride,  GLvoid* ptr)
  cdef void             glTexEnvf               (GLenum target, GLenum pname, GLfloat param)
  cdef void             glTexEnvfv              (GLenum target, GLenum pname,  GLfloat* params)
  cdef void             glTexEnvx               (GLenum target, GLenum pname, GLfixed param)
  cdef void             glTexEnvxv              (GLenum target, GLenum pname,  GLfixed* params)
  cdef void             glTexImage2D            (GLenum target, GLint level, GLint internalFormat, GLsizei width, GLsizei height, GLint border, GLenum format, GLenum type,  GLvoid* pixels)
  cdef void             glTexParameterf         (GLenum target, GLenum pname, GLfloat param)
  cdef void             glTexParameterx         (GLenum target, GLenum pname, GLfixed param)
  cdef void             glTexSubImage2D         (GLenum target, GLint level, GLint xoffset, GLint yoffset, GLsizei width, GLsizei height, GLenum format, GLenum type,  GLvoid* pixels)
  cdef void             glTranslatef            (GLfloat x, GLfloat y, GLfloat z)
  cdef void             glTranslatex            (GLfixed x, GLfixed y, GLfixed z)
  cdef void             glVertexPointer         (GLint size, GLenum type, GLsizei stride,  GLvoid* ptr)
  cdef void             glViewport              (GLint x, GLint y, GLsizei width, GLsizei height)
  
  # 1.1
  cdef void             glBindBuffer                            (GLenum target, GLuint buffer)
  cdef void             glBufferData                            (GLenum target, GLsizeiptr size,  GLvoid* data, GLenum usage)
  cdef void             glBufferSubData                         (GLenum target, GLintptr offset, GLsizeiptr size,  GLvoid* data)
  cdef void             glColor4ub                              (GLubyte red, GLubyte green, GLubyte blue, GLubyte alpha)
  cdef void             glCurrentPaletteMatrixOES               (GLuint matrix)
  cdef void             glDeleteBuffers                         (GLsizei n,  GLuint* buffers)
  cdef void             glGenBuffers                            (GLsizei n, GLuint* buffers)
  cdef void             glGetBooleanv                           (GLenum pname, GLboolean* params)
  cdef void             glGetBufferParameteriv                  (GLenum target, GLenum pname, GLint* params)
  cdef void             glGetClipPlanef                         (GLenum plane, GLfloat* equation)
  cdef void             glGetClipPlanex                         (GLenum plane, GLfixed* equation)
  cdef void             glGetFloatv                             (GLenum pname, GLfloat* params)
  cdef void             glGetFixedv                             (GLenum pname, GLfixed* params)
  cdef void             glGetLightfv                            (GLenum light, GLenum pname, GLfloat* params)
  cdef void             glGetLightxv                            (GLenum light, GLenum pname, GLfixed* params)
  cdef void             glGetMaterialfv                         (GLenum face, GLenum pname, GLfloat* params)
  cdef void             glGetMaterialxv                         (GLenum face, GLenum pname, GLfixed* params)
  cdef void             glGetPointerv                           (GLenum pname, GLvoid** params)
  cdef void             glGetTexEnvfv                           (GLenum target, GLenum pname, GLfloat* params)
  cdef void             glGetTexEnviv                           (GLenum target, GLenum pname, GLint* params)
  cdef void             glGetTexEnvxv                           (GLenum target, GLenum pname, GLfixed* params)
  cdef void             glGetTexParameteriv                     (GLenum target, GLenum pname, GLint* params)
  cdef void             glGetTexParameterfv                     (GLenum target, GLenum pname, GLfloat* params)
  cdef void             glGetTexParameterxv                     (GLenum target, GLenum pname, GLfixed* params)
  cdef GLboolean        glIsEnabled                             (GLenum cap)
  cdef GLboolean        glIsTexture                             (GLuint texture)
  cdef GLboolean        glIsBuffer                              (GLuint buffer)
  cdef void             glLoadPaletteFromModelViewMatrixOES     ()
  cdef void             glMatrixIndexPointerOES                 (GLint size, GLenum type, GLsizei stride,  GLvoid* pointer)
  cdef void             glWeightPointerOES                      (GLint size, GLenum type, GLsizei stride,  GLvoid* pointer)
  cdef void             glClipPlanef                            (GLenum plane,  GLfloat* equation)
  cdef void             glClipPlanex                            (GLenum plane,  GLfixed* equation)
  cdef void             glPointSizePointerOES                   (GLenum type, GLsizei stride,  GLvoid* pointer)
  cdef void             glPointParameterfv                      (GLenum pname,  GLfloat* params)
  cdef void             glPointParameterxv                      (GLenum pname,  GLfixed* params)
  cdef void             glPointParameterf                       (GLenum pname, GLfloat params)
  cdef void             glPointParameterx                       (GLenum pname, GLfixed params)
  cdef void             glDrawTexfOES                           (GLfloat sx, GLfloat sy, GLfloat sz, GLfloat sw, GLfloat sh)
  cdef void             glDrawTexxOES                           (GLfixed sx, GLfixed sy, GLfixed sz, GLfixed sw, GLfixed sh)
  cdef void             glDrawTexiOES                           (GLint sx, GLint sy, GLint sz, GLint sw, GLint sh)
  cdef void             glDrawTexsOES                           (GLshort sx, GLshort sy, GLshort sz, GLshort sw, GLshort sh)
  cdef void             glDrawTexfvOES                          (GLfloat* params)
  cdef void             glDrawTexxvOES                          (GLfixed* params)
  cdef void             glDrawTexivOES                          (GLint* params)
  cdef void             glDrawTexsvOES                          (GLshort* params)
  cdef void             glTexParameteri                         (GLenum target, GLenum pname, GLint param)
  cdef void             glTexParameterfv                        (GLenum target, GLenum pname,  GLfloat* param)
  cdef void             glTexParameterxv                        (GLenum target, GLenum pname,  GLfixed* param)
  cdef void             glTexParameteriv                        (GLenum target, GLenum pname,  GLint* param)
  
  
  # Shaders
  int GL_PROGRAM_STRING_ARB
  int GL_PROGRAM_ERROR_STRING_ARB
  int GL_PROGRAM_ERROR_POSITION_ARB
  int GL_PROGRAM_FORMAT_ASCII_ARB
  int GL_PROGRAM_OBJECT_ARB
  int GL_SHADER_OBJECT_ARB
  int GL_OBJECT_TYPE_ARB
  int GL_OBJECT_SUBTYPE_ARB
  int GL_FLOAT_VEC2_ARB
  int GL_FLOAT_VEC3_ARB
  int GL_FLOAT_VEC4_ARB
  int GL_INT_VEC2_ARB
  int GL_INT_VEC3_ARB
  int GL_INT_VEC4_ARB
  int GL_BOOL_ARB
  int GL_BOOL_VEC2_ARB
  int GL_BOOL_VEC3_ARB
  int GL_BOOL_VEC4_ARB
  int GL_FLOAT_MAT2_ARB
  int GL_FLOAT_MAT3_ARB
  int GL_FLOAT_MAT4_ARB
  int GL_SAMPLER_1D_ARB
  int GL_SAMPLER_2D_ARB
  int GL_SAMPLER_3D_ARB
  int GL_SAMPLER_CUBE_ARB
  int GL_SAMPLER_1D_SHADOW_ARB
  int GL_SAMPLER_2D_SHADOW_ARB
  int GL_SAMPLER_2D_RECT_ARB
  int GL_SAMPLER_2D_RECT_SHADOW_ARB
  int GL_OBJECT_DELETE_STATUS_ARB
  int GL_OBJECT_COMPILE_STATUS_ARB
  int GL_OBJECT_LINK_STATUS_ARB
  int GL_OBJECT_VALIDATE_STATUS_ARB
  int GL_OBJECT_INFO_LOG_LENGTH_ARB
  int GL_OBJECT_ATTACHED_OBJECTS_ARB
  int GL_OBJECT_ACTIVE_UNIFORMS_ARB
  int GL_OBJECT_ACTIVE_UNIFORM_MAX_LENGTH_ARB
  int GL_OBJECT_SHADER_SOURCE_LENGTH_ARB
  int GL_VERTEX_SHADER_ARB
  int GL_MAX_VERTEX_UNIFORM_COMPONENTS_ARB
  int GL_MAX_VARYING_FLOATS_ARB
  int GL_MAX_VERTEX_TEXTURE_IMAGE_UNITS_ARB
  int GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS_ARB
  int GL_OBJECT_ACTIVE_ATTRIBUTES_ARB
  int GL_OBJECT_ACTIVE_ATTRIBUTE_MAX_LENGTH_ARB
  int GL_VERTEX_PROGRAM_ARB
  int GL_FRAGMENT_PROGRAM_ARB
  int GL_PROGRAM_ALU_INSTRUCTIONS_ARB
  int GL_PROGRAM_TEX_INSTRUCTIONS_ARB
  int GL_PROGRAM_TEX_INDIRECTIONS_ARB
  int GL_PROGRAM_NATIVE_ALU_INSTRUCTIONS_ARB
  int GL_PROGRAM_NATIVE_TEX_INSTRUCTIONS_ARB
  int GL_PROGRAM_NATIVE_TEX_INDIRECTIONS_ARB
  int GL_MAX_PROGRAM_ALU_INSTRUCTIONS_ARB
  int GL_MAX_PROGRAM_TEX_INSTRUCTIONS_ARB
  int GL_MAX_PROGRAM_TEX_INDIRECTIONS_ARB
  int GL_MAX_PROGRAM_NATIVE_ALU_INSTRUCTIONS_ARB
  int GL_MAX_PROGRAM_NATIVE_TEX_INSTRUCTIONS_ARB
  int GL_MAX_PROGRAM_NATIVE_TEX_INDIRECTIONS_ARB
  int GL_MAX_TEXTURE_COORDS_ARB
  int GL_MAX_TEXTURE_IMAGE_UNITS_ARB
  
  cdef void glGenProgramsARB(GLsizei n, GLuint* ids)
  cdef void glBindProgramARB(GLenum target, GLuint id)
  cdef void glProgramStringARB(GLenum target, GLenum format, GLsizei len, char* string)
  cdef void glDeleteProgramsARB(GLsizei n, GLuint* ids)
  cdef void glProgramEnvParameter4fARB(GLenum target, GLuint index, GLfloat v0, GLfloat v1, GLfloat v2, GLfloat v3)
  cdef void glProgramLocalParameter4fARB(GLenum target, GLuint index, GLfloat v0, GLfloat v1, GLfloat v2, GLfloat v3)
  cdef void glGetProgramStringARB(GLenum target, GLenum pname, void* string)
  
  cdef GLvoid* BUFFER_OFFSET(int offset)
