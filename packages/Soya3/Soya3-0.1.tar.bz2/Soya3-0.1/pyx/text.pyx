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

# A big part of this file is heavily inspired by OGLFT (www.sf.net/project/oglft)
# We need to rewrite it because OGLFT is written in C++ :-(


cdef FT_Library library
cdef int library_inited
library_inited = 0

cdef class Glyph:
  #cdef readonly float _pixels_x1, _pixels_y1, _pixels_x2, _pixels_y2, width, height, y, x
  #cdef readonly unichar
  
  def __init__(self, unichar): self.unichar = unicode(unichar)
  def __repr__(self): return "<Glyph '%s' %s x %s>" % (self.unichar, self.width, self.height)
  
  
cdef class _Font:
  #cdef FT_Face      _face
  #cdef readonly     filename
  #cdef int          _width, _height
  #cdef              _glyphs
  
  #cdef GLubyte*     _pixels
  #cdef int          _current_x, _current_y
  #cdef readonly int _current_height, _pixels_height
  #cdef int          _rendering
  #cdef GLuint       _tex_id
  #cdef float        _ascender, _descender
  
  property height:
    def __get__(self): return self._height
    
  property width:
    def __get__(self): return self._width
    
  def __init__(self, filename, int width = 20, int height = 30):
    import os.path
    if not os.path.exists(filename): raise ValueError("Cannot open font file %s", filename)
    
    self._width         = width
    self._height        = height + 4
    # Needed, because if the first glyph generated is " " (with a height of 0),
    # the texture won't be resized, and OpenGL doesn't accept a texture with a
    # zero dimension.
    # /!\ this field is also used to check initialisation of the font
    #    -1 mean not uninitialized
    #     0 mean font inited but not pixel height
    self._pixels_height = -1
    self._glyphs        = {}
    self.filename       = filename
    
  cdef void _init(self):
    glGenTextures(1, &self._tex_id)
    glBindTexture(GL_TEXTURE_2D, self._tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glBindTexture(GL_TEXTURE_2D, 0)
    
    global library_inited
    if library_inited == 0:
      if FT_Init_FreeType(&library): raise ImportError("Cannot init FreeType")
      library_inited = 1
      
    # init FreeType face
    if FT_New_Face(library, python2cstring(self.filename), 0, &self._face): raise ValueError("Cannot open font file %s", self.filename)
    if FT_Set_Char_Size(self._face, 0, self._face.units_per_EM * 64, 0, 0): raise ValueError("Cannot set char size")
    
    if self._face.face_flags & FT_FACE_FLAG_SCALABLE: FT_Set_Pixel_Sizes(self._face, self._width, self._height)
    else:                                             FT_Set_Pixel_Sizes(self._face, 0, 0)
    
    # As of FreeType 2.1: only a UNICODE charmap is automatically activated.
    # If no charmap is activated automatically, just use the first one.
    # BUT I NEED A UNICODE CHARMAP !!!!!
    #if (self._face.charmap == 0) and (self._face.num_charmaps > 0):
    #  FT_Select_Charmap(self._face, self._face.charmaps[0].encoding)
    
    # XXX Why 64.0 ?
    self._ascender  = (<float> self._face.size.metrics.ascender ) / 64.0
    self._descender = (<float> self._face.size.metrics.descender) / 64.0
    
    if self._pixels_height <= -1: self._pixels_height = 0
    
  def __dealloc__(self):
    if self._pixels_height > -1:
      FT_Done_Face(self._face)
      glDeleteTextures(1, &self._tex_id)
      
  cdef Glyph _get_glyph(self, char_):
    cdef int   code
    cdef Glyph glyph
    code  = ord(char_)
    
    glyph = self._glyphs.get(code)
    if glyph is None: glyph = self._glyphs[code] = self._gen_glyph(char_, code)
    return glyph
  
  cdef Glyph _gen_glyph(self, char_, int code):
    cdef int             glyph_index, j
    cdef Glyph           glyph
    cdef FT_Bitmap       bitmap
    cdef int             g_height
    
    # Initialize if needed.
    if self._pixels_height <= 0: self._init()
    
    if self._rendering: glEnd(); self._rendering = 0
    
    glyph = Glyph(char_)
    glyph_index = FT_Get_Char_Index(self._face, code)
    
    if FT_Load_Glyph(self._face, glyph_index, FT_LOAD_DEFAULT) != 0: raise ValueError("Glyph %s does not exist !" % glyph_index)
    if self._face.glyph.format != FT_GLYPH_FORMAT_BITMAP: FT_Render_Glyph(self._face.glyph, FT_RENDER_MODE_NORMAL)
    
    bitmap = self._face.glyph.bitmap
    g_height = bitmap.rows
    
    if self._current_x + bitmap.width > MAX_TEXTURE_SIZE: # We need a new row in the texture
      self._current_x = 0
      self._current_y = self._current_y + self._current_height + 1
      self._current_height = 0
      
    if g_height > self._current_height: self._current_height = g_height
    
    if self._current_y + g_height > self._pixels_height: # We need to extend the texture
      self._sizeup_pixel(self._current_y + g_height)
      
    if char_ == " ": glyph.width = self._width / 2
    else:            glyph.width = bitmap.width
    glyph.height     = g_height
    glyph._pixels_x1 = (<float> self._current_x               ) / (<float> MAX_TEXTURE_SIZE)
    glyph._pixels_y1 = (<float> self._current_y               ) / (<float> self._pixels_height)
    glyph._pixels_x2 = (<float> self._current_x + glyph.width ) / (<float> MAX_TEXTURE_SIZE)
    glyph._pixels_y2 = (<float> self._current_y + glyph.height) / (<float> self._pixels_height)
    glyph.y          = self._height - self._face.glyph.bitmap_top
    glyph.x          = self._face.glyph.bitmap_left
    
    for j from 0 <= j < bitmap.rows: # get pixels
      memcpy(self._pixels + self._current_x + (self._current_y + j) * MAX_TEXTURE_SIZE, bitmap.buffer + bitmap.pitch * j, bitmap.pitch)
      
    self._current_x = self._current_x + (<int> glyph.width) + 5
    
    glBindTexture(GL_TEXTURE_2D, self._tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_ALPHA,
                 MAX_TEXTURE_SIZE, self._pixels_height, 0,
                 GL_ALPHA, GL_UNSIGNED_BYTE,
                 self._pixels,
                 )
    
    return glyph
  
  cdef void _sizeup_pixel(self, int height):
    if   height <   32: height =   32
    elif height <   64: height =   64
    elif height <  128: height =  128
    elif height <  256: height =  256
    elif height <  512: height =  512
    elif height < 1024: height = 1024
    elif height < 2048: height = 2048
    else: raise MemoryError("Too many characters in font %s -- no space left on texture." % self)
    
    cdef Glyph glyph
    for glyph in self._glyphs.values():
      glyph._pixels_y1 = glyph._pixels_y1 / height * self._pixels_height
      glyph._pixels_y2 = glyph._pixels_y2 / height * self._pixels_height 
      
    self._pixels = <GLubyte*> realloc(self._pixels, MAX_TEXTURE_SIZE * height * sizeof(GLubyte))
    
    cdef int i
    # 'max' because self._pixels_height is -1 at the beginning
    for i from MAX_TEXTURE_SIZE * max(self._pixels_height, 0) <= i < MAX_TEXTURE_SIZE * height:
      self._pixels[i] = 0
      
    self._pixels_height = height
    
  def __repr__(self):
    return "<Font '%s', width = %s, height = %s, %s characters loaded>" % (self.filename, self._width, self._height, len(self._glyphs))
  
  def get_glyph(self, chr):
    return self._get_glyph(chr)
  
  def create_glyphs(self, text):
    for char_ in text: self._get_glyph(char_)
    
  def get_print_size(self, text):
    cdef float width, height, line_width
    cdef Glyph glyph
    width      = 0.0
    height     = self._height
    line_width = 0.0
    
    for char_ in text:
      if char_ == "\n":
        height = height + self._height
        if width < line_width: width = line_width
        line_width = 0.0
      else:
        glyph = self._get_glyph(char_)
        line_width = line_width + glyph.x + glyph.width
    if width < line_width: width = line_width
    
    return width, height
    
  def wordwrap(self, text, float width):
    """wordwrap(self, text, float width) -> (max_line_width, total_height, wrapped_text)"""
    
    cdef float height, line_width, max_line_width, char_width
    cdef int   word_start, i, nb
    cdef Glyph glyph
    height         = self._height
    line_width     = 0.0
    line_width_at_word_start = 0.0
    max_line_width = 0.0
    word_start     = -1
    i              = 0
    nb             = len(text)
    text2          = u""
    while i < nb:
      char_ = text[i]
      if char_ == u"\n":
        height = height + self._height
        if line_width > max_line_width: max_line_width = line_width
        line_width = 0.0
        word_start = -1
      else:
        if char_ == u" ":
          word_start = i
          line_width_at_word_start = line_width
        glyph = self._get_glyph(char_)
        line_width = line_width + glyph.width + glyph.x
        if (line_width > width) and (word_start != -1):
          height = height + self._height
          if line_width_at_word_start > max_line_width: max_line_width = line_width_at_word_start
          line_width = 0.0
          text2      = text2 + text[len(text2):word_start] + u"\n"
          i          = word_start
          word_start = -1
      i = i + 1
    if line_width > max_line_width: max_line_width = line_width
    text2 = text2 + text[len(text2):]
    return max_line_width, height, text2
  
  def wordwrap_line(self, text, float width):
    """wordwrap_line(self, text, float width) -> (max_line_width, total_height, [ ("line1", line1width), ("line2", linewidth2) ... ]) 
    """
    cdef float height, line_width, max_line_width, char_width
    cdef int   word_start, i, nb, line_start
    cdef Glyph glyph
    height         = self._height
    line_width     = 0.0
    max_line_width = 0.0
    word_start     = -1
    i              = 0
    nb             = len(text)
    lines          = []
    line_start     = 0
    while i < nb:
      char_ = text[i]
      if char_ == u"\n":
        lines.append((text[line_start:i], line_width))
        height = height + self._height
        if line_width > max_line_width: max_line_width = line_width
        line_width = 0.0
        word_start = -1
        line_start = i + 1
      else:
        if char_ == u" ": word_start = i
        glyph = self._get_glyph(char_)
        char_width = glyph.width + glyph.x
        line_width = line_width + char_width
        if (line_width > width) and (word_start != -1):
          lines.append((text[line_start:word_start], line_width - char_width))
          height = height + self._height
          if line_width > max_line_width: max_line_width = line_width
          line_width = 0.0
          line_start = word_start + 1
          i = word_start
          word_start = -1
      i = i + 1
    if line_width > max_line_width: max_line_width = line_width
    lines.append((text[line_start:], line_width))
    return width, height, lines
    
  def draw(self, text, float x, float y, float z = 0.0, float width = 0.0, float box_height = 9999.0, int align = TEXT_ALIGN_LEFT, int cull_face = 0):
    cdef Glyph glyph
    cdef float w, h, x_orig
    cdef int   vertex_i, face_i
    cdef list  lines
    
    if cull_face == 0: glDisable(GL_CULL_FACE)
    glEnable (GL_TEXTURE_2D)
    glEnable (GL_BLEND)
    glBindTexture(GL_TEXTURE_2D, self._tex_id)
    
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, _tmp_face_buffer)
    glBindBuffer(GL_ARRAY_BUFFER        , _tmp_vertex_buffer)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    glVertexPointer  (3, GL_FLOAT, 0, BUFFER_OFFSET(0))
    glTexCoordPointer(2, GL_FLOAT, 0, BUFFER_OFFSET(128 * 3 * sizeof(float)))
    
    if not _CURRENT_PROGRAM is None: _CURRENT_PROGRAM._set_rendering_params() # For the texture
    
    if width > 0.0:
      if   align == TEXT_ALIGN_LEFT: width, h, text  = self.wordwrap     (text, width); lines = [text]
      else:                          width, h, lines = self.wordwrap_line(text, width)
    else:                                      lines = [text]
    
    x_orig     = x
    y          = y + self._descender
    box_height = box_height + y
    vertex_i   = face_i = 0
    for line in lines:
      if align == TEXT_ALIGN_CENTER:
        line, w = line
        x = x_orig + (width - w) / 2.0
        
      for char_ in line:
        if char_ == "\n":
          x = x_orig
          y = y + self._height
          if y >= box_height: break
        else:
          glyph = self._get_glyph(char_)
          
          x = x + glyph.x
          _tmp_vertices[vertex_i * 3     ] = x
          _tmp_vertices[vertex_i * 3 +  1] = y + glyph.y
          _tmp_vertices[vertex_i * 3 +  2] = z
          _tmp_vertices[vertex_i * 3 +  3] = x
          _tmp_vertices[vertex_i * 3 +  4] = y + glyph.y + glyph.height
          _tmp_vertices[vertex_i * 3 +  5] = z
          
          _tmp_vertices[128 * 3 + vertex_i * 2    ] = glyph._pixels_x1
          _tmp_vertices[128 * 3 + vertex_i * 2 + 1] = glyph._pixels_y1
          _tmp_vertices[128 * 3 + vertex_i * 2 + 2] = glyph._pixels_x1
          _tmp_vertices[128 * 3 + vertex_i * 2 + 3] = glyph._pixels_y2
          
          x = x + glyph.width
          _tmp_vertices[vertex_i * 3 +  6] = x
          _tmp_vertices[vertex_i * 3 +  7] = y + glyph.y + glyph.height
          _tmp_vertices[vertex_i * 3 +  8] = z
          _tmp_vertices[vertex_i * 3 +  9] = x
          _tmp_vertices[vertex_i * 3 + 10] = y + glyph.y
          _tmp_vertices[vertex_i * 3 + 11] = z
          
          _tmp_vertices[128 * 3 + vertex_i * 2 + 4] = glyph._pixels_x2
          _tmp_vertices[128 * 3 + vertex_i * 2 + 5] = glyph._pixels_y2
          _tmp_vertices[128 * 3 + vertex_i * 2 + 6] = glyph._pixels_x2
          _tmp_vertices[128 * 3 + vertex_i * 2 + 7] = glyph._pixels_y1
          
          _tmp_faces[face_i    ] = vertex_i
          _tmp_faces[face_i + 1] = vertex_i + 1
          _tmp_faces[face_i + 2] = vertex_i + 2
          _tmp_faces[face_i + 3] = vertex_i + 2
          _tmp_faces[face_i + 4] = vertex_i + 3
          _tmp_faces[face_i + 5] = vertex_i + 0
          
          face_i   = face_i   + 6
          vertex_i = vertex_i + 4
          
          if vertex_i >= 128:
            glBufferSubData(GL_ARRAY_BUFFER        , 0, 128 * (3 + 2) * sizeof(float), _tmp_vertices)
            glBufferSubData(GL_ELEMENT_ARRAY_BUFFER, 0, 192           * sizeof(short), _tmp_faces)
            glDrawElements(GL_TRIANGLES, 192, GL_UNSIGNED_SHORT, BUFFER_OFFSET(0))
            vertex_i = face_i = 0
            
      if align == TEXT_ALIGN_CENTER:
        y = y + self._height
        if y >= box_height: break
        
    if vertex_i > 0:
      glBufferSubData(GL_ARRAY_BUFFER        , 0, 128 * (3 + 2) * sizeof(float), _tmp_vertices)
      glBufferSubData(GL_ELEMENT_ARRAY_BUFFER, 0, face_i        * sizeof(short), _tmp_faces)
      glDrawElements(GL_TRIANGLES, face_i, GL_UNSIGNED_SHORT, BUFFER_OFFSET(0))
      
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ARRAY_BUFFER        , 0)
    
    if cull_face == 0: glEnable (GL_CULL_FACE)
    glDisable(GL_BLEND)
    glBindTexture(GL_TEXTURE_2D, 0)
    
  def _image(self):
    """Debugging stuff -- return the font loaded glyphs as a PIL image."""
    import PIL.Image
    cdef int i, size
    cdef GLubyte* pixels
    size   = MAX_TEXTURE_SIZE * self._pixels_height * 3 * sizeof(GLubyte)
    pixels = <GLubyte*> malloc(size)
    for i from 0 <= i < MAX_TEXTURE_SIZE * self._pixels_height:
      pixels[3 * i    ] = self._pixels[i]
      pixels[3 * i + 1] = self._pixels[i]
      pixels[3 * i + 2] = self._pixels[i]
      
    image = PIL.Image.new("RGB", (MAX_TEXTURE_SIZE, self._pixels_height))
    image.fromstring(PyString_FromStringAndSize(<char*> pixels, size))
    return image
    
  
