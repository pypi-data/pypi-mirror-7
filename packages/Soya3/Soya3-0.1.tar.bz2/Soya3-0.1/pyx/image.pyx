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

  
  
def open_image(filename):
  """open_image(filename) -> Image

Creates and returns a Soya image from file FILENAME.
The image is loaded with SDL_Image; the supported image formats are PNG and JPEG."""
  cdef _Image image
  
  #import PIL.Image
  #image = image_from_pil(PIL.Image.open(filename))
  
  #import pygame.image
  #image = image_from_pygame(pygame.image.load(filename))

  image = _image_from_sdl(filename)
  
  image._filename = filename
  return image

def image_from_pil(pil_image):
  """image_from_pil(pil_image) -> Image

Creates and returns a Soya image from PIL image PIL_IMAGE."""
  import PIL.Image
  cdef _Image image
  image = Image()
  image.width, image.height = pil_image.size
  if   pil_image.mode == "RGBA": image.nb_color = 4
  elif pil_image.mode == "RGB" : image.nb_color = 3
  elif pil_image.mode == "L"   : image.nb_color = 1
  elif pil_image.mode == "P"   : # XXX Palette may not be monochrome
    image.nb_color = 1 
    image.palette = pil_image.palette.palette
  else: raise ValueError("unknown image mode (%s)" % pil_image.mode)
  image.pixels = pil_image.tostring()
  return image

cdef _image_from_sdl(filename):
  cdef _Image       image
  cdef SDL_Surface* surface
  cdef SDL_RWops*   rwop
  
  if isinstance(filename, str): filename_b = bytes(filename, "utf8")
  rwop    = SDL_RWFromFile(filename_b, "rb");
  if   filename.endswith(".png"): surface = IMG_LoadPNG_RW(rwop)
  elif filename.endswith(".jpeg") or filename.endswith(".jpg"): surface = IMG_LoadJPG_RW(rwop)
  else: raise ValueError("Unsupported image format: %s" % filename)
  image = Image(None, surface.w, surface.h, surface.format.BytesPerPixel)
  #image.nb_color = surface.format.BytesPerPixel
  #image.width    = surface.w
  #image.height   = surface.h
  #image._pixels  = <GLubyte*> malloc(surface.w * surface.h * surface.format.BytesPerPixel * sizeof(GLubyte))
  memcpy(image._pixels, surface.pixels, surface.w * surface.h * surface.format.BytesPerPixel * sizeof(GLubyte))
  free(rwop)
  free(surface)
  return image
  
  
  
def image_from_pygame(surface):
  """image_from_pygame(surface) -> Image

Creates and returns a Soya image from pygame / SDL surface SURFACE."""
  import pygame.image
  cdef _Image image
  image = Image()
  image.width, image.height = surface.get_size()
  if   surface.get_bitsize() == 32:
    image.nb_color = 4
    image.pixels = pygame.image.tostring(surface, "RGBA")
  elif surface.get_bitsize() == 24:
    image.nb_color = 3
    image.pixels = pygame.image.tostring(surface, "RGB")
  else: raise ValueError("unknown image bitsize (%s), must be 24 or 32." % surface.get_bitsize())
  return image

def screenshot(filename = None, int x = 0, int y = 0, int width = 0, int height = 0, use_back_buffer = False):
  """screenshot(filename = None, x = 0, y = 0, width = soya.get_screen_width(), height = soya.get_screen_height(), use_back_buffer = False) -> PIL.Image.Image

Take a screenshot of the soya rendering screen, and return it as a PIL image object.
If given, the image is saved under FILENAME.
You must have rendered something before (e.g. by calling soya.render(), or by running
an MainLoop)."""
  cdef GLubyte* pixels
  cdef int      size
  cdef int      gl_buffer
  if use_back_buffer:
    gl_buffer = GL_BACK
  else:
    gl_buffer = GL_FRONT
  import PIL.Image
  width  = width  or renderer.screen_width
  height = height or renderer.screen_height
  size   = 3 * width * height
  pixels = <GLubyte*> malloc(size * sizeof(GLubyte))
  IF OPENGL == "full":
    glReadBuffer(gl_buffer)
  glReadPixels(x, y, width, height, GL_RGB, GL_UNSIGNED_BYTE, pixels)
  image = PIL.Image.fromstring("RGB", (width, height), PyString_FromStringAndSize(<char*> pixels, size))
  image = image.transpose(PIL.Image.FLIP_TOP_BOTTOM)
  free(pixels)
  if filename is not None: image.save(filename)
  return image


# XXX indexed images are not supported yet (not sure)

cdef class _Image(_CObj):
  """Image object, used in particular for texture."""

  #cdef readonly int nb_color, width, height
  #cdef GLubyte* _pixels
  #cdef public  _filename
  
  def __init__(self, pixels = None, int width = 0, int height = 0, int nb_color = 0):
    """Image(pixels = None, int width = 0, int height = 0, int nb_color = 0) -> Image

Creates a Soya image of dimension WIDTH and HEIGHT, with NB_COLOR color channels
(4 for RGBA), and with data PIXELS (a raw image in a string).

See Image.get(filename), open_image(filename) or image_from_pil(pil_image) for higher
level image loading functions."""
    if nb_color == 0:
      self._pixels = NULL
    else:
      if pixels is None:
        self._pixels  = <GLubyte*> malloc(width * height * nb_color * sizeof(GLubyte))
      else:
        self._pixels  = <GLubyte*> dup(PyString_AS_STRING(pixels), width * height * nb_color)
      self.width    = width
      self.height   = height
      self.nb_color = nb_color
      
  def __dealloc__(self):
    if self._pixels != NULL: free(self._pixels)
    
  cdef __getcstate__(self):
    cdef Chunk* chunk
    chunk = get_chunk()
    chunk_add_int_endian_safe  (chunk, self.nb_color)
    chunk_add_int_endian_safe  (chunk, self.width)
    chunk_add_int_endian_safe  (chunk, self.height)
    chunk_add_chars_endian_safe(chunk, <char*> self._pixels, self.nb_color * self.width * self.height)
    return drop_chunk_to_string(chunk), self._filename
  
  cdef void __setcstate__(self, cstate):
    if isinstance(cstate, tuple):
      self.filename  = cstate[1]
      cstate         = cstate[0]
    cdef Chunk* chunk
    chunk = string_to_chunk(cstate)
    chunk_get_int_endian_safe(chunk, &self.nb_color)
    chunk_get_int_endian_safe(chunk, &self.width)
    chunk_get_int_endian_safe(chunk, &self.height)
    self._pixels = <GLubyte*> malloc(self.nb_color * self.width * self.height * sizeof(GLubyte))
    chunk_get_chars_endian_safe(chunk, <char*> self._pixels, self.nb_color * self.width * self.height)
    drop_chunk(chunk)
    
  def __deepcopy__(self, memo):
    """Images are immutable."""
    return self
  
  property pixels:
    def __get__(self):
      return PyString_FromStringAndSize(<char*> self._pixels, self.nb_color * self.width * self.height)
    def __set__(self, string):
      self._pixels = <GLubyte*> dup(PyString_AS_STRING(string), self.nb_color * self.width * self.height)
      
  def has_border(self): return self.check_for_gl() == 2
  
  cdef int check_for_gl(self):
    """_Image.check_for_gl() -> int

Returns 1 if the image is suitable for OpenGL (=if both dimension are power of 2).
Returns 2 if the image is suitable for OpenGL, with a border (=if both dimension are power of 2 + 2 (for the border)).
Else returns 0."""
    if ( self.width      == power_of_2(self.width    )) and ( self.height      == power_of_2(self.height    )): return 1
    if ((self.width - 2) == power_of_2(self.width - 2)) and ((self.height - 2) == power_of_2(self.height - 2)): return 2
    return 0
    
    
  cdef GLuint typ(self):
    """_Image.typ() -> GLuint

Returns the image type, depending on the number of color channels,
i.e. either GL_LUMINANCE, GL_RGB or GL_RGBA."""
    if   self.nb_color == 1: return GL_LUMINANCE
    elif self.nb_color == 3: return GL_RGB
    elif self.nb_color == 4: return GL_RGBA
    raise ValueError("unknown image number of color (%s)" % self.nb_color)
  
  cdef GLuint internal_format(self):
    """_Image.internal_format() -> GLuint

Returns the image internal format, depending on the number of color channels and the
rendering quality."""
    IF OPENGL == "full":
      if   quality == QUALITY_LOW:
        if   self.nb_color == 1: return GL_LUMINANCE
        elif self.nb_color == 3: return GL_RGB
        elif self.nb_color == 4: return GL_RGBA
      elif quality == QUALITY_MEDIUM:
        if   self.nb_color == 1: return GL_LUMINANCE8
        elif self.nb_color == 3: return GL_RGB8
        elif self.nb_color == 4: return GL_RGBA8
      elif quality == QUALITY_HIGH:
        if   self.nb_color == 1: return GL_LUMINANCE16
        elif self.nb_color == 3: return GL_RGB16
        elif self.nb_color == 4: return GL_RGBA16
    ELSE:
      if   self.nb_color == 1: return GL_LUMINANCE
      elif self.nb_color == 3: return GL_RGB
      elif self.nb_color == 4: return GL_RGBA
      
    raise ValueError("unknown image number of color (%s)" % self.nb_color)
  
  def __repr__(self): return "<Image %s>" % self._filename
  
  def to_pil(self):
    import PIL.Image
    if   self.nb_color == 4: return PIL.Image.fromstring("RGBA", (self.width, self.height), self.pixels)
    elif self.nb_color == 3: return PIL.Image.fromstring("RGB" , (self.width, self.height), self.pixels)
    elif self.nb_color == 1: 
      if self.palette  == None: return PIL.Image.fromstring("L", (self.width, self.height), self.pixels)
      else :
        pimage = PIL.Image.fromstring("P", (self.width, self.height), self.pixels)
        pimage.putpalette(self.palette)
        return pimage

cdef int power_of_2(int i):
  if i <= 1   : return    1
  if i <= 2   : return    2
  if i <= 4   : return    4
  if i <= 8   : return    8
  if i <= 16  : return   16
  if i <= 32  : return   32
  if i <= 64  : return   64
  if i <= 128 : return  128
  if i <= 256 : return  256
  if i <= 512 : return  512
  if i <= 1024: return 1024
  if i <= 2048: return 2048
  return 4096
  
cdef GLubyte* pixels_scale_down_2(int nb_color, GLuint* w, GLuint* h, int border, GLubyte* pixels):
  """pixels_scale_down_2(int nb_color, GLuint* w, GLuint* h, int border, GLubyte* pixels) -> GLubyte*

Returns a reduced version of an image. Each dimension is divided by 2.
The image is given by PIXELS, NB_COLOR. W and H are pointers on the dimensions (i.e. the old image dimension at the beginning and then half of the image dimensions).
The returned image is malloc'ed, and must be free'd by the caller.
"""
  cdef int i, j, m, x, y
  cdef GLubyte* new_pixels

  if (w[0] == 1) or (h[0] == 1):
    if w[0] != 1: w[0] = w[0] >> 1
    if h[0] != 1: h[0] = h[0] >> 1
    new_pixels = <GLubyte*> malloc((h[0] + 2 * border) * (w[0] + 2 * border) * nb_color * sizeof(GLubyte))
    for j from 0 <= j < (h[0] + 2 * border):
      for i from 0 <= i < (w[0] + 2 * border):
        for m from 0 <= m < nb_color:
          new_pixels[(i + w[0] * j) * nb_color + m] = pixels[(i + w[0] * j) * nb_color * 2 + m]
  else:
    w[0] = w[0] >> 1
    h[0] = h[0] >> 1
    new_pixels = <GLubyte*> malloc((h[0] + 2 * border) * (w[0] + 2 * border) * nb_color * sizeof(GLubyte))
    #for i from 0 <= i < h[0] * w[0] * nb_color * sizeof(GLubyte):
    #  new_pixels[i] = 0
    for j from 0 <= j < (h[0] + 2 * border):
      y = 2 * j
      for i from 0 <= i < (w[0] + 2 * border):
        x = 2 * i
        for m from 0 <= m < nb_color:
          new_pixels[(i + w[0] * j) * nb_color + m] = <GLubyte> ((
            (<float> pixels[(x     + 2 * w[0] *  y)      * nb_color + m]) +
            (<float> pixels[(x + 1 + 2 * w[0] *  y)      * nb_color + m]) +
            (<float> pixels[(x     + 2 * w[0] * (y + 1)) * nb_color + m]) +
            (<float> pixels[(x + 1 + 2 * w[0] * (y + 1)) * nb_color + m])) / 4.0
            )
  return new_pixels


