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

cdef int            NB_JOYSTICK
cdef SDL_Joystick** JOYSTICKS

import sys
from warnings import warn

# GL initialization

def set_quality(int q):
  global quality
  quality = q
  if   q == QUALITY_LOW:
    glHint(GL_FOG_HINT                   , GL_FASTEST)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_FASTEST)
    glHint(GL_POINT_SMOOTH_HINT          , GL_FASTEST)
    glHint(GL_LINE_SMOOTH_HINT           , GL_FASTEST)
    IF OPENGL == "full":
      glHint(GL_POLYGON_SMOOTH_HINT        , GL_FASTEST)
    renderer.engine_option = renderer.engine_option & ~SHADOWS # Disable shadows
    
  elif q == QUALITY_MEDIUM:
    glHint(GL_FOG_HINT                   , GL_DONT_CARE)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_DONT_CARE)
    glHint(GL_POINT_SMOOTH_HINT          , GL_DONT_CARE)
    glHint(GL_LINE_SMOOTH_HINT           , GL_DONT_CARE)
    IF OPENGL == "full":
      glHint(GL_POLYGON_SMOOTH_HINT        , GL_DONT_CARE)
    if renderer.engine_option & HAS_STENCIL: renderer.engine_option = renderer.engine_option | SHADOWS # Enable shadows
    
  elif q == QUALITY_HIGH:
    glHint(GL_FOG_HINT                   , GL_NICEST)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    glHint(GL_POINT_SMOOTH_HINT          , GL_NICEST)
    glHint(GL_LINE_SMOOTH_HINT           , GL_NICEST)
    IF OPENGL == "full":
      glHint(GL_POLYGON_SMOOTH_HINT        , GL_NICEST)
    if renderer.engine_option & HAS_STENCIL: renderer.engine_option = renderer.engine_option | SHADOWS # Enable shadows


cdef void dump_info():
  s = PyString_FromString(<char*> glGetString(GL_VERSION))
  sys.stdout.write("""
* Soya * version %s
* Using OpenGL %s
*   - renderer   : %s
*   - vendor     : %s
*   - maximum number of lights        : %s
*   - maximum number of clip planes   : %s
*   - maximum number of texture units : %s
*   - maximum texture size            : %s pixels
""" % (
    VERSION,
    bytes(PyString_FromString(<char*> glGetString(GL_VERSION ))).decode("latin"),
    bytes(PyString_FromString(<char*> glGetString(GL_RENDERER))).decode("latin"),
    bytes(PyString_FromString(<char*> glGetString(GL_VENDOR  ))).decode("latin"),
    MAX_LIGHTS,
    MAX_CLIP_PLANES,
    MAX_TEXTURES,
    MAX_TEXTURE_SIZE,
    ))


cdef void init_gl():
  cdef int i
  
  glGetIntegerv(GL_MAX_LIGHTS,        &MAX_LIGHTS)
  glGetIntegerv(GL_MAX_CLIP_PLANES,   &MAX_CLIP_PLANES)
  glGetIntegerv(GL_MAX_TEXTURE_UNITS, &MAX_TEXTURES)
  glGetIntegerv(GL_MAX_TEXTURE_SIZE,  &MAX_TEXTURE_SIZE)
  
  for i from 0 <= i < MAX_LIGHTS:
    LIGHTS     .append(None)
    LAST_LIGHTS.append(None)
    
  glClearDepth(1.0)
  glDepthMask(GL_FALSE)
  glDisable(GL_DEPTH_TEST)
  
  glDepthFunc(GL_LESS)
  
  glDisable(GL_COLOR_MATERIAL)
  IF OPENGL == "full":
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
  glEnable(GL_COLOR_MATERIAL)
  
  cdef GLfloat black[4]
  black[3] = 1.0
  glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, black)
  glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_FALSE)
  glDisable(GL_LIGHTING)
  glDisable(GL_NORMALIZE)
    
  glDisable(GL_BLEND)
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
  glDisable(GL_ALPHA_TEST)
  glAlphaFunc(GL_NOTEQUAL, 0.0)
  
  glEnable(GL_CULL_FACE)
  glCullFace(GL_BACK)
  glFrontFace(GL_CCW)

  IF OPENGL == "full":
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glDisable(GL_POLYGON_SMOOTH)
  glEnable(GL_POINT_SMOOTH)
  glDisable(GL_LINE_SMOOTH)
  glShadeModel(GL_SMOOTH)

  glDisable(GL_DITHER)

  glPixelStorei(GL_PACK_ALIGNMENT  , 1)
  glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
  
  # 'activate' DEFAULT_MATERIAL
  glDisable(GL_TEXTURE_2D)
  glColor4f(1.0, 1.0, 1.0, 1.0)
  
  set_quality(quality)
  
  _init_tmp_buffer() # Init temporary vertex buffers
  
    
cdef void gl_resized(int quiet):
  # Wait until OpenGL is REALLY ready
  cdef int i
  from time import sleep
  if not quiet:
    sys.stdout.write("* Soya * OpenGL initialization ")
  for i from 0 <= i < 10:
    if glGetString(GL_RENDERER) != NULL: break
    if not quiet: sys.stdout.write(".")
    sleep(0.1)
  else: sys.stderr.write("\n* Soya * ERROR : OpenGL is not ready... Soya will crash soon i guess :-(\n")
  if not quiet: sys.stdout.write(" [OK]\n")
  
  glViewport(0, 0, renderer.screen_width, renderer.screen_height)
  glMatrixMode(GL_PROJECTION)
  glLoadIdentity()
  glOrtho(0.0, <GLfloat> renderer.screen_width, <GLfloat> renderer.screen_height, 0.0, -1.0, 1.0)
  glMatrixMode(GL_MODELVIEW)
  glLoadIdentity()
  
  global root_widget
  if not root_widget is None:
    root_widget.resize(0, 0, renderer.screen_width, renderer.screen_height)


IF OPENGL == "full": # SDL based video init
  def set_video(int width, int height, int fullscreen, int resizable, int antialiasing = True, int quiet = False, int sdl_blit = 0, int additional_flags = 0):
    cdef int stencil, bits_per_pixel
    cdef int flags
    cdef void* tmp
    renderer.screen_width  = width
    renderer.screen_height = height
    # Information about the current video settings
    
    flags = <int>SDL_WINDOW_OPENGL | additional_flags
    if fullscreen == 0: renderer.engine_option = renderer.engine_option & ~FULLSCREEN
    else:
      renderer.engine_option = renderer.engine_option | FULLSCREEN
      flags = flags | SDL_WINDOW_FULLSCREEN
    if antialiasing == 0: renderer.engine_option = renderer.engine_option & ~ANTIALIASING
    else:
      renderer.engine_option = renderer.engine_option | ANTIALIASING
      SDL_GL_SetAttribute(SDL_GL_MULTISAMPLEBUFFERS, 1)
      SDL_GL_SetAttribute(SDL_GL_MULTISAMPLESAMPLES, 4)
      
    if resizable == 1: flags = flags | SDL_WINDOW_RESIZABLE
      
    renderer.sdl_window = SDL_CreateWindow("", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, width, height, flags)
    if renderer.sdl_window == NULL:
      s = "Video mode set failed : %s" % SDL_GetError()
      sys.stderr.write(s + '\n')
      raise RuntimeError(s)
      
    renderer.sdl_gl_context = SDL_GL_CreateContext(renderer.sdl_window)
    
    gl_resized(quiet)

  cdef void init_video(char* title, int width, int height, int fullscreen, int resizable, int antialiasing, int quiet, int sdl_blit, int additional_flags):
    #if sys.platform == "darwin": import soya3.macosx
    
    # initialize SDL
    if SDL_Init(SDL_INIT_VIDEO | SDL_INIT_JOYSTICK | SDL_INIT_EVENTS | SDL_INIT_NOPARACHUTE) < 0:
      s = "Could not initialize SDL : %s" % SDL_GetError()
      sys.stderr.write(s + '\n')
      raise RuntimeError(s)
    set_video(width, height, fullscreen, resizable, antialiasing, quiet, sdl_blit, additional_flags)
    if title != NULL: SDL_SetWindowTitle(renderer.sdl_window, title)

  cdef void quit_video():
    pass # Everything is done by SDL


IF OPENGL == "es": # eGL based video init
  def set_video(int width, int height, int fullscreen, int resizable, int antialiasing = True, int quiet = False, int sdl_blit = 0, int additional_flags = 0):
    cdef int sdl_flags
    
    renderer.screen_width  = width
    renderer.screen_height = height
    
    sdl_flags = additional_flags
    renderer.screen = SDL_SetVideoMode(width, height, 16, sdl_flags)
    
    # Derived from :
    # Rikku2000's GL examples 
    # Adamant Armor Affection Adventure (GPL'ed) source's
    # http://code.google.com/p/cantuna/wiki/OpenglOnCaanoo
    
    cdef void* e_config
    cdef int   nc
    cdef int   egl_config_attr[20]
    egl_config_attr[0] = EGL_SURFACE_TYPE; egl_config_attr[1] = EGL_WINDOW_BIT
    egl_config_attr[2] = EGL_BUFFER_SIZE;  egl_config_attr[3] = 16
    egl_config_attr[4] = EGL_DEPTH_SIZE;   egl_config_attr[5] = 16
    egl_config_attr[6] = EGL_NONE
    #egl_config_attr[6] = EGL_RENDERABLE_TYPE; egl_config_attr[7] = EGL_OPENGL_ES_BIT
    
    
    renderer.egl_window  = OS_CreateWindow() #<void*> malloc(16 * 1024)
    
    renderer.egl_display = eglGetDisplay(EGL_DEFAULT_DISPLAY)
    
    print "egl_display", renderer.egl_display != NULL
    print eglGetError()
    
    eglInitialize  (renderer.egl_display, NULL, NULL)
    print eglGetError()
    
    eglChooseConfig(renderer.egl_display, egl_config_attr, &e_config, 1, &nc)
    print nc, "configs"
    print eglGetError()
    
    renderer.egl_surface = eglCreateWindowSurface(renderer.egl_display, e_config, renderer.egl_window, egl_config_attr)
    print "egl_surface", renderer.egl_surface != NULL
    print eglGetError()
    
    renderer.egl_context = eglCreateContext(renderer.egl_display, e_config, EGL_NO_CONTEXT, egl_config_attr)
    print "egl_context", renderer.egl_context != NULL
    print eglGetError()
    
    eglMakeCurrent(renderer.egl_display, renderer.egl_surface, renderer.egl_surface, renderer.egl_context)
    
    gl_resized(quiet)
    
  cdef void init_video(char* title, int width, int height, int fullscreen, int resizable, int antialiasing, int quiet, int sdl_blit, int additional_flags):
    # initialize SDL
    if SDL_Init(SDL_INIT_JOYSTICK  | SDL_INIT_NOPARACHUTE) < 0:
      s = "Could not initialize SDL : %s" % SDL_GetError()
      sys.stderr.write(s + '\n')
      raise RuntimeError(s)
    set_video(width, height, fullscreen, resizable, antialiasing, quiet, sdl_blit, additional_flags)

  cdef void quit_video():
    eglMakeCurrent   (renderer.egl_display, NULL, NULL, <void*> EGL_NO_CONTEXT)
    eglDestroySurface(renderer.egl_display, renderer.egl_surface)
    eglDestroyContext(renderer.egl_display, renderer.egl_context)
    eglTerminate     (renderer.egl_display)
    

# General init

cdef void base_init():
  global renderer
  clist_init()
  renderer = Renderer()

cdef void base_quit():
  cdef int i
  import soya3 as soya
  global JOYSTICKS, NB_JOYSTICK, renderer
  if not soya.quiet: sys.stdout.write("* Soya3D * Quit...\n")
  
  for i from 0 <= i < NB_JOYSTICK: SDL_JoystickClose(JOYSTICKS[i])
  SDL_Quit()
  
  quit_video()
  
  free(JOYSTICKS)
  renderer = None
  
def init(title = "Soya 3D", int width = 640, int height = 480, int fullscreen = 0, int resizeable = 1, int antialiasing = 1, int create_surface = 1, int sound = 1, sound_device = "", int sound_frequency = 44100, float sound_reference_distance = 1.0, float sound_doppler_factor = 0.01, int quiet=False, int sdl_blit = 0, int additional_flags = 0):
  """init(title = "Soya 3D", width = 640, height = 480, fullscreen = 0, resizeable = 1, create_surface = 1, sound = 1, sound_device = "", sound_frequency = 44100, sound_reference_distance = 1.0, sound_doppler_factor = 0.01, quiet=False)

Inits Soya 3D and display the 3D view.

TITLE is the title of the window.
WIDTH and HEIGHT the dimensions of the 3D view.
FULLSCREEN is true for fullscreen and false for windowed mode.
RESIZEABLE is true for a resizeable window.
ANTIALIASING is true for enabling full-screen antialiasing.
QUIET is true to hide the soya initialisation message.

Set SOUND to true to initialize 3D sound support (default to false for backward compatibility)
The following arguments are meaningful only if SOUND is true:
SOUND_DEVICE is the OpenAL device names, the default value should be nice.
SOUND_FREQUENCY is the sound frequency.
SOUND_REFERENCE_DISTANCE is the reference distance for sound attenuation.
SOUND_DOPPLER_FACTOR can be used to increase or decrease the Doppler effect."""
  global _DEFAULT_PROGRAM
  import soya3 as soya, atexit
  soya.quiet = quiet
  if renderer is None:
    base_init()
    
    # Deprecated
    #SDL_EnableUNICODE(1) # Do this BEFORE setting the window's title, because it can be in Unicode!
    
    #if create_surface: init_video(python2cstring(title), width, height, fullscreen, resizeable, quiet, sdl_blit, additional_flags)
    
    #title = title.encode("utf8")
    #if create_surface: init_video(title, width, height, fullscreen, resizeable, quiet, sdl_blit, additional_flags)
    
    #string2 = title.encode("utf8")
    #if create_surface: init_video(PyBytes_AS_STRING(string2), width, height, fullscreen, resizeable, quiet, sdl_blit, additional_flags)
    title = title.encode("utf8")
    if create_surface: init_video(title, width, height, fullscreen, resizeable, antialiasing, quiet, sdl_blit, additional_flags)
    
    IF OPENGL == "full":
      glewInit()
      
    init_joysticks()
    init_gl()
    
    IF HAS_ODE:
      dInitODE2(~0)
      geomterrain_init()
      
    if not root_widget is None: root_widget.resize(0, 0, width, height)
    
    atexit.register(quit)
    
    soya.inited = 1
    
  if not quiet: dump_info()
  
  IF HAS_SOUND:
    if sound: _init_sound(sound_device, sound_frequency, sound_reference_distance, sound_doppler_factor)
    
  if not quiet: sys.stdout.write('\n')
    
def quit():
  import soya3 as soya
  if soya.inited:
    soya.inited = 0
    base_quit()
    
    IF HAS_CAL3D:
      quit_cal3d()
      
    IF HAS_ODE:
      dCloseODE()





# SDL-related funcs, though not initialization-related

cdef void init_joysticks():
  cdef int i
  global JOYSTICKS, NB_JOYSTICK
  NB_JOYSTICK = SDL_NumJoysticks()
  
  if NB_JOYSTICK > 0:
    SDL_JoystickEventState(SDL_ENABLE)
    JOYSTICKS = <SDL_Joystick**> malloc(NB_JOYSTICK * sizeof(SDL_Joystick*))
    for i from 0 <= i < NB_JOYSTICK: JOYSTICKS[i] = SDL_JoystickOpen(i)

def coalesce_motion_event(events):
  """coalesce_motion_event(events) -> sequence

You should look the MainLoop.events property instead of using this function.

Prunes from EVENTS all mouse motion events except the last one.
This is usefull since only the last one is usually releavant. The relative
motion data is updated. The last mouse motion events is put at the very end of
the list.

In the process the last data event[5] about which button are pressed during the
event is **lost** as it could not be coalesced efficiently.

EVENTS should be a list of events, as returned by soya.process_event().
The returned list has the same structure except for the last data."""
  return _coalesce_motion_event(events)

cdef _coalesce_motion_event(events):
  cdef int first_motion = 1
  cdef int base_x, base_y
  
  last_motion   = None
  
  new_events = []
  events = list(events) # XXX Needed ?
  for event in events:
    if event[0] == SDL_MOUSEMOTION:
      last_motion = event
      if first_motion:
        first_motion = False
        base_x = event[1] - event[3]
        base_y = event[2] - event[4]
    else: new_events.append(event)
  if last_motion is not None:
    new_events.append((SDL_MOUSEMOTION,
                       last_motion[1], last_motion[2],
                       last_motion[1] - base_x, # relative x
                       last_motion[2] - base_y) # relative y
                      )
  return new_events

cdef int joy_x_pos = 0, joy_y_pos = 0
def emulate_keyboard_from_joystick_event(events, button1 = SDLK_RETURN, button2 = SDLK_ESCAPE, button3 = SDLK_LSHIFT, button4 = SDLK_LCTRL):
  global joy_x_pos, joy_y_pos
  cdef list new_events = []
  
  for event in events:
    if   event[0] == SDL_JOYBUTTONDOWN:
      if   event[1] == 0: new_events.append((SDL_KEYDOWN, button1, 0, 0))
      elif event[1] == 1: new_events.append((SDL_KEYDOWN, button2, 0, 0))
      elif event[1] == 2: new_events.append((SDL_KEYDOWN, button3, 0, 0))
      elif event[1] == 3: new_events.append((SDL_KEYDOWN, button4, 0, 0))
                                            
    elif event[0] == SDL_JOYBUTTONUP:
      if   event[1] == 0: new_events.append((SDL_KEYUP, button1, 0))
      elif event[1] == 1: new_events.append((SDL_KEYUP, button2, 0))
      elif event[1] == 2: new_events.append((SDL_KEYUP, button3, 0))
      elif event[1] == 3: new_events.append((SDL_KEYUP, button4, 0))
                                            
    elif event[0] == SDL_JOYAXISMOTION:
      if   event[1] == 0:
        if   event[2] < -1000:
          if joy_x_pos != -1: new_events.append((SDL_KEYDOWN, SDLK_LEFT , 0, 0)); joy_x_pos = -1
        elif event[2] >  1000:
          if joy_x_pos !=  1: new_events.append((SDL_KEYDOWN, SDLK_RIGHT, 0, 0)); joy_x_pos =  1
        elif joy_x_pos == -1: new_events.append((SDL_KEYUP  , SDLK_LEFT , 0   )); joy_x_pos =  0
        elif joy_x_pos ==  1: new_events.append((SDL_KEYUP  , SDLK_RIGHT, 0   )); joy_x_pos =  0
        
      if   event[1] == 1:
        if   event[2] < -1000:
          if joy_y_pos != -1: new_events.append((SDL_KEYDOWN, SDLK_UP   , 0, 0)); joy_y_pos = -1
        elif event[2] >  1000:
          if joy_y_pos !=  1: new_events.append((SDL_KEYDOWN, SDLK_DOWN , 0, 0)); joy_y_pos =  1
        elif joy_y_pos == -1: new_events.append((SDL_KEYUP  , SDLK_UP   , 0   )); joy_y_pos =  0
        elif joy_y_pos ==  1: new_events.append((SDL_KEYUP  , SDLK_DOWN , 0   )); joy_y_pos =  0
        
    else:  new_events.append(event)
  return new_events



cdef _process_event():
  cdef object    events
  cdef SDL_Event event
  events = []
  
  while SDL_PollEvent(&event):
    if   event.type == SDL_KEYDOWN:         events.append(( 1, event.key.keysym.scancode, event.key.keysym.mod))
    elif event.type == SDL_TEXTINPUT:       events.append(( 1, event.text.text.decode("utf8"), 0))
    elif event.type == SDL_KEYUP:           events.append(( 2, event.key.keysym.scancode, event.key.keysym.mod))
    elif event.type == SDL_MOUSEMOTION:     events.append(( 3, event.motion.x, event.motion.y, event.motion.xrel, event.motion.yrel, event.motion.state))
    elif event.type == SDL_MOUSEBUTTONDOWN: events.append(( 4, event.button.button, event.button.x, event.button.y))
    elif event.type == SDL_MOUSEBUTTONUP:   events.append(( 5, event.button.button, event.button.x, event.button.y))
    elif event.type == SDL_JOYAXISMOTION:   events.append(( 6, event.jaxis.axis, event.jaxis.value))
    elif event.type == SDL_JOYBUTTONDOWN:   events.append(( 9, event.jbutton.button))
    elif event.type == SDL_JOYBUTTONUP:     events.append((10, event.jbutton.button))
    elif event.type == SDL_QUIT:            events.append((13,))
    
    elif  event.type == SDL_WINDOWEVENT:
      if event.window.event == SDL_WINDOWEVENT_RESIZED:
        renderer.screen_width  = event.window.data1
        renderer.screen_height = event.window.data2
        gl_resized(0)
        events.append((11, event.window.data1, event.window.data2))
        
  return events

def get_mod(): return SDL_GetModState()

def cursor_set_visible(int visibility):
  if visibility == 0: SDL_ShowCursor(SDL_DISABLE)
  else:               SDL_ShowCursor(SDL_ENABLE)

# there are many more masks defined in SDL/SDL_event
# this is the mask for _all_ events 
SDL_ALLEVENTS=0xFFFFFFFF
ALL_EVENTS=SDL_ALLEVENTS

#def set_mouse_pos(int x,int y):
#  """ move the mouse cursor to x,y"""
#  SDL_WarpMouse(x,y)


def get_mouse_rel_pos():
  """ return the relative mouse position since the last call to this function"""
  cdef int x, y
  SDL_GetRelativeMouseState(&x,&y)
  return (x,y)

