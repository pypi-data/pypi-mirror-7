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


# This is only a PARTIAL definition file -- i've defined only the stuff i need

cdef extern from "SDL2/SDL_endian.h":
  pass

SDL_ALLEVENTS = 0xFFFFFFFF

cdef extern from "SDL2/SDL.h":
  ctypedef struct SDL_Rect:
    unsigned short      x, y
    unsigned short      w, h
    
  ctypedef struct SDL_RWops
  ctypedef struct SDL_Joystick
  ctypedef struct SDL_PixelFormat:
    #SDL_Palette *palette
    unsigned char BitsPerPixel
    unsigned char BytesPerPixel
    unsigned char Rloss
    unsigned char Gloss
    unsigned char Bloss
    unsigned char Aloss
    unsigned char Rshift
    unsigned char Gshift
    unsigned char Bshift
    unsigned char Ashift
    unsigned int  Rmask
    unsigned int  Gmask
    unsigned int  Bmask
    unsigned int  Amask
    unsigned int  colorkey # RGB color key information
    unsigned char alpha    # Alpha value information (per-surface alpha)
    
  ctypedef struct SDL_Surface:
    int flags
    SDL_PixelFormat* format
    int w
    int h
    short pitch
    void* pixels
    SDL_Rect clip_rect
    int refcount
    
  ctypedef struct SDL_Window:
    pass
    
  ctypedef struct SDL_GLContext:
    pass
  
  ctypedef struct SDL_Keysym:
    int    scancode
    int    sym
    short  mod

  ctypedef struct SDL_JoystickID:
    pass
    
  ctypedef struct SDL_KeyboardEvent:
    char       type
    int        timestamp
    int        windowID
    char       state
    char       repeat
    SDL_Keysym keysym
    
  ctypedef struct SDL_TextInputEvent:
    char       type
    int        timestamp
    int        windowID
    char*      text
    
  ctypedef struct SDL_MouseMotionEvent:
    char       type
    int        timestamp
    int        windowID
    int        which
    int        state
    short      x, y, xrel, yrel
    
  ctypedef struct SDL_MouseButtonEvent:
    char       type
    int        timestamp
    int        windowID
    int        which
    char       button
    char       state
    char       clicks
    short      x, y
    
  ctypedef struct SDL_JoyAxisEvent:
    char       type
    int        timestamp
    int        windowID
    SDL_JoystickID which
    char       axis
    short      value
    
  ctypedef struct SDL_JoyButtonEvent:
    char       type
    int        timestamp
    int        windowID
    SDL_JoystickID which
    char       button
    char       state
    
  ctypedef struct SDL_WindowEvent:
    char       type
    int        timestamp
    int        windowID
    int        event
    int        data1
    int        data2
    
  ctypedef struct SDL_QuitEvent:
    char       type
    int        timestamp
    int        windowID
    
  ctypedef union SDL_Event:
    char type
    SDL_KeyboardEvent    key
    SDL_MouseMotionEvent motion
    SDL_MouseButtonEvent button
    SDL_JoyAxisEvent     jaxis
    SDL_JoyButtonEvent   jbutton
    SDL_QuitEvent        quit
    SDL_TextInputEvent   text
    SDL_WindowEvent      window
    
  int SDL_INIT_VIDEO
  int SDL_INIT_JOYSTICK
  int SDL_INIT_AUDIO
  int SDL_INIT_EVENTS
  int SDL_INIT_NOPARACHUTE
  int SDL_ENABLE
  int SDL_DISABLE
  
  int SDL_WINDOW_FULLSCREEN
  int SDL_WINDOW_OPENGL
  int SDL_WINDOW_RESIZABLE
  int SDL_WINDOW_FOREIGN
  int SDL_WINDOWPOS_UNDEFINED  
  
  int SDL_NOEVENT
  int SDL_ACTIVEEVENT
  int SDL_KEYDOWN
  int SDL_KEYUP
  int SDL_TEXTINPUT
  int SDL_MOUSEMOTION
  int SDL_MOUSEBUTTONDOWN
  int SDL_MOUSEBUTTONUP
  int SDL_JOYAXISMOTION
  int SDL_JOYBALLMOTION
  int SDL_JOYHATMOTION
  int SDL_JOYBUTTONDOWN
  int SDL_JOYBUTTONUP
  int SDL_QUIT
  int SDL_SYSWMEVENT
  int SDL_EVENT_RESERVEDA
  int SDL_EVENT_RESERVEDB
  int SDL_USEREVENT
  int SDL_NUMEVENTS
  int SDL_WINDOWEVENT
  int SDL_WINDOWEVENT_RESIZED
  
  enum SDL_GLattr:
    SDL_GL_RED_SIZE,
    SDL_GL_GREEN_SIZE,
    SDL_GL_BLUE_SIZE,
    SDL_GL_ALPHA_SIZE,
    SDL_GL_BUFFER_SIZE,
    SDL_GL_DOUBLEBUFFER,
    SDL_GL_DEPTH_SIZE,
    SDL_GL_STENCIL_SIZE,
    SDL_GL_ACCUM_RED_SIZE,
    SDL_GL_ACCUM_GREEN_SIZE,
    SDL_GL_ACCUM_BLUE_SIZE,
    SDL_GL_ACCUM_ALPHA_SIZE,
    SDL_GL_STEREO
    SDL_GL_MULTISAMPLEBUFFERS
    SDL_GL_MULTISAMPLESAMPLES
    
  void            SDL_Quit           ()
  int             SDL_Init           (unsigned int flags)
  char*           SDL_GetError       ()
  SDL_Window*     SDL_CreateWindow   (char* title, int x, int y, int w, int h, int flags)
  void            SDL_SetWindowTitle (SDL_Window* window, char* title)
  SDL_GLContext   SDL_GL_CreateContext(SDL_Window* window)
  
  int             SDL_GL_SetAttribute(SDL_GLattr attr, int value)
  void            SDL_JoystickClose  (SDL_Joystick* joystick)
  int             SDL_NumJoysticks   ()
  SDL_Joystick*   SDL_JoystickOpen   (int device_index)
  void            SDL_GL_SwapWindow  (SDL_Window* window)
  int             SDL_PollEvent      (SDL_Event*)
  void            SDL_ShowCursor     (int)
  int             SDL_Swap32         (int)
  int             SDL_GetModState    ()
  void            SDL_JoystickEventState(int)
  int             SDL_GetRelativeMouseState(int *x, int *y)
  int             SDL_EnableUNICODE(int enable)
  int             SDL_BlitSurface(SDL_Surface* src, SDL_Rect* src_rect, SDL_Surface* dest, SDL_Rect* dest_rect)
  SDL_Surface*    SDL_DisplayFormat(SDL_Surface* src)
  SDL_Surface*    SDL_CreateRGBSurface(int flag, int width, int height, int bpp, int r, int g, int b, int a)
  void            SDL_FreeSurface(SDL_Surface* surface)
  SDL_RWops*      SDL_RWFromFile(char* file, char* mode)
  SDL_Surface*    IMG_LoadPNG_RW(SDL_RWops* src)
  SDL_Surface*    IMG_LoadJPG_RW(SDL_RWops* src)
  
  ctypedef enum SDL_eventaction:
    SDL_ADDEVENT
    SDL_PEEKEVENT
    SDL_GETEVENT

    
  void            SDL_PumpEvents()
 
  # Key and mod consts
  int KMOD_NONE
  int KMOD_LSHIFT
  int KMOD_RSHIFT
  int KMOD_LCTRL
  int KMOD_RCTRL
  int KMOD_LALT
  int KMOD_RALT
  int KMOD_LMETA
  int KMOD_RMETA
  int KMOD_NUM
  int KMOD_CAPS
  int KMOD_MODE
  int KMOD_RESERVED
  int SDLK_UNKNOWN
  int SDLK_FIRST
  int SDLK_BACKSPACE
  int SDLK_TAB
  int SDLK_CLEAR
  int SDLK_RETURN
  int SDLK_PAUSE
  int SDLK_ESCAPE
  int SDLK_SPACE
  int SDLK_EXCLAIM
  int SDLK_QUOTEDBL
  int SDLK_HASH
  int SDLK_DOLLAR
  int SDLK_AMPERSAND
  int SDLK_QUOTE
  int SDLK_LEFTPAREN
  int SDLK_RIGHTPAREN
  int SDLK_ASTERISK
  int SDLK_PLUS
  int SDLK_COMMA
  int SDLK_MINUS
  int SDLK_PERIOD
  int SDLK_SLASH
  int SDLK_0
  int SDLK_1
  int SDLK_2
  int SDLK_3
  int SDLK_4
  int SDLK_5
  int SDLK_6
  int SDLK_7
  int SDLK_8
  int SDLK_9
  int SDLK_COLON
  int SDLK_SEMICOLON
  int SDLK_LESS
  int SDLK_EQUALS
  int SDLK_GREATER
  int SDLK_QUESTION
  int SDLK_AT
  int SDLK_LEFTBRACKET
  int SDLK_BACKSLASH
  int SDLK_RIGHTBRACKET
  int SDLK_CARET
  int SDLK_UNDERSCORE
  int SDLK_BACKQUOTE
  int SDLK_a
  int SDLK_b
  int SDLK_c
  int SDLK_d
  int SDLK_e
  int SDLK_f
  int SDLK_g
  int SDLK_h
  int SDLK_i
  int SDLK_j
  int SDLK_k
  int SDLK_l
  int SDLK_m
  int SDLK_n
  int SDLK_o
  int SDLK_p
  int SDLK_q
  int SDLK_r
  int SDLK_s
  int SDLK_t
  int SDLK_u
  int SDLK_v
  int SDLK_w
  int SDLK_x
  int SDLK_y
  int SDLK_z
  int SDLK_DELETE
  int SDLK_WORLD_0
  int SDLK_WORLD_1
  int SDLK_WORLD_2
  int SDLK_WORLD_3
  int SDLK_WORLD_4
  int SDLK_WORLD_5
  int SDLK_WORLD_6
  int SDLK_WORLD_7
  int SDLK_WORLD_8
  int SDLK_WORLD_9
  int SDLK_WORLD_10
  int SDLK_WORLD_11
  int SDLK_WORLD_12
  int SDLK_WORLD_13
  int SDLK_WORLD_14
  int SDLK_WORLD_15
  int SDLK_WORLD_16
  int SDLK_WORLD_17
  int SDLK_WORLD_18
  int SDLK_WORLD_19
  int SDLK_WORLD_20
  int SDLK_WORLD_21
  int SDLK_WORLD_22
  int SDLK_WORLD_23
  int SDLK_WORLD_24
  int SDLK_WORLD_25
  int SDLK_WORLD_26
  int SDLK_WORLD_27
  int SDLK_WORLD_28
  int SDLK_WORLD_29
  int SDLK_WORLD_30
  int SDLK_WORLD_31
  int SDLK_WORLD_32
  int SDLK_WORLD_33
  int SDLK_WORLD_34
  int SDLK_WORLD_35
  int SDLK_WORLD_36
  int SDLK_WORLD_37
  int SDLK_WORLD_38
  int SDLK_WORLD_39
  int SDLK_WORLD_40
  int SDLK_WORLD_41
  int SDLK_WORLD_42
  int SDLK_WORLD_43
  int SDLK_WORLD_44
  int SDLK_WORLD_45
  int SDLK_WORLD_46
  int SDLK_WORLD_47
  int SDLK_WORLD_48
  int SDLK_WORLD_49
  int SDLK_WORLD_50
  int SDLK_WORLD_51
  int SDLK_WORLD_52
  int SDLK_WORLD_53
  int SDLK_WORLD_54
  int SDLK_WORLD_55
  int SDLK_WORLD_56
  int SDLK_WORLD_57
  int SDLK_WORLD_58
  int SDLK_WORLD_59
  int SDLK_WORLD_60
  int SDLK_WORLD_61
  int SDLK_WORLD_62
  int SDLK_WORLD_63
  int SDLK_WORLD_64
  int SDLK_WORLD_65
  int SDLK_WORLD_66
  int SDLK_WORLD_67
  int SDLK_WORLD_68
  int SDLK_WORLD_69
  int SDLK_WORLD_70
  int SDLK_WORLD_71
  int SDLK_WORLD_72
  int SDLK_WORLD_73
  int SDLK_WORLD_74
  int SDLK_WORLD_75
  int SDLK_WORLD_76
  int SDLK_WORLD_77
  int SDLK_WORLD_78
  int SDLK_WORLD_79
  int SDLK_WORLD_80
  int SDLK_WORLD_81
  int SDLK_WORLD_82
  int SDLK_WORLD_83
  int SDLK_WORLD_84
  int SDLK_WORLD_85
  int SDLK_WORLD_86
  int SDLK_WORLD_87
  int SDLK_WORLD_88
  int SDLK_WORLD_89
  int SDLK_WORLD_90
  int SDLK_WORLD_91
  int SDLK_WORLD_92
  int SDLK_WORLD_93
  int SDLK_WORLD_94
  int SDLK_WORLD_95
  int SDLK_KP0
  int SDLK_KP1
  int SDLK_KP2
  int SDLK_KP3
  int SDLK_KP4
  int SDLK_KP5
  int SDLK_KP6
  int SDLK_KP7
  int SDLK_KP8
  int SDLK_KP9
  int SDLK_KP_PERIOD
  int SDLK_KP_DIVIDE
  int SDLK_KP_MULTIPLY
  int SDLK_KP_MINUS
  int SDLK_KP_PLUS
  int SDLK_KP_ENTER
  int SDLK_KP_EQUALS
  int SDLK_UP
  int SDLK_DOWN
  int SDLK_RIGHT
  int SDLK_LEFT
  int SDLK_INSERT
  int SDLK_HOME
  int SDLK_END
  int SDLK_PAGEUP
  int SDLK_PAGEDOWN
  int SDLK_F1
  int SDLK_F2
  int SDLK_F3
  int SDLK_F4
  int SDLK_F5
  int SDLK_F6
  int SDLK_F7
  int SDLK_F8
  int SDLK_F9
  int SDLK_F10
  int SDLK_F11
  int SDLK_F12
  int SDLK_F13
  int SDLK_F14
  int SDLK_F15
  int SDLK_NUMLOCK
  int SDLK_CAPSLOCK
  int SDLK_SCROLLOCK
  int SDLK_RSHIFT
  int SDLK_LSHIFT
  int SDLK_RCTRL
  int SDLK_LCTRL
  int SDLK_RALT
  int SDLK_LALT
  int SDLK_RMETA
  int SDLK_LMETA
  int SDLK_LSUPER
  int SDLK_RSUPER
  int SDLK_MODE
  int SDLK_COMPOSE
  int SDLK_HELP
  int SDLK_PRINT
  int SDLK_SYSREQ
  int SDLK_BREAK
  int SDLK_MENU
  int SDLK_POWER
  int SDLK_EURO
  int SDLK_UNDO
  
  
