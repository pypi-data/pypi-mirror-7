# -*- coding: utf-8 -*-

# Soya 3D
# Copyright (C) 2001-2014 Jean-Baptiste LAMY
#	Copyright (C) 2001-2012 Marmoute - Pierre-Yves David -- marmoute@nekeme.net
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


cdef enum:
  paramLoStop        = 0
  paramHiStop        = 1
  paramVel           = 2
  paramFMax          = 3
  paramFudgeFactor   = 4
  paramBounce        = 5
  paramCFM           = 6
  paramStopERP       = 7
  paramStopCFM       = 8
  paramSuspensionERP = 9
  paramSuspensionCFM = 10
  
  ParamLoStop        = 0
  ParamHiStop        = 1
  ParamVel           = 2
  ParamFMax          = 3
  ParamFudgeFactor   = 4
  ParamBounce        = 5
  ParamCFM           = 6
  ParamStopERP       = 7
  ParamStopCFM       = 8
  ParamSuspensionERP = 9
  ParamSuspensionCFM = 10
  
  ParamLoStop2        = 256+0
  ParamHiStop2        = 256+1
  ParamVel2           = 256+2
  ParamFMax2          = 256+3
  ParamFudgeFactor2   = 256+4
  ParamBounce2        = 256+5
  ParamCFM2           = 256+6
  ParamStopERP2       = 256+7
  ParamStopCFM2       = 256+8
  ParamSuspensionERP2 = 256+9
  ParamSuspensionCFM2 = 256+10
  
  ContactMu2  = 0x001
  ContactFDir1  = 0x002
  ContactBounce  = 0x004
  ContactSoftERP  = 0x008
  ContactSoftCFM  = 0x010
  ContactMotion1  = 0x020
  ContactMotion2  = 0x040
  ContactSlip1  = 0x080
  ContactSlip2  = 0x100
  
  ContactApprox0 = 0x0000
  ContactApprox1_1  = 0x1000
  ContactApprox1_2  = 0x2000
  ContactApprox1  = 0x3000


cdef class _Geom
cdef class _Space(_Geom)
cdef class _Geom:
  cdef dGeomID _OdeGeomID
  cdef _Space  _space
  #cdef _World  _ode_parent #XXX check it
  cdef float _bounce
  cdef float _grip
  
  cdef float _point_depth(self, float x, float y, float z)
  cdef _create(self)
  cdef dReal* _getAABB(self)
  
cdef class _PlaceableGeom(_Geom):
  cdef _Body  _body

cdef class _PrimitiveGeom(_PlaceableGeom):
  pass
cdef class GeomSphere(_PrimitiveGeom):
  pass
cdef class GeomBox(_PrimitiveGeom):
  pass
cdef class GeomCapsule(_PrimitiveGeom):
  pass
cdef class GeomCylinder(_PrimitiveGeom):
  pass

ctypedef dReal dGetDepthFn(dGeomID g, dReal x, dReal y, dReal z)

cdef class _GeomTerrain(_Geom):
    cdef _Terrain _terrain
    cdef CoordSyst _ode_root
    cdef float min_x, max_x, min_y, max_y, min_z, max_z

    cdef void _get_aabb(self, dReal aabb[6])
    #cdef int _collide_edge(self, GLfloat *A, GLfloat *B,
    #                       GLfloat *AB, GLfloat *normalA,
    #                       GLfloat *normalB, dGeomID o1, dGeomID o2, 
    #                       int max_contacts, int flags, dContactGeom *contact, 
    #                       dGetDepthFn *GetDepth)
    cdef int _collide_cell(self, int x, int z, dGeomID o1, 
                           dGeomID o2, int max_contacts, int flags, 
                           dContactGeom *contact, int skip)#,
                           #dGetDepthFn *GetDepth)
    cdef int _collide(self, dGeomID o1, dGeomID o2, int flags,
                      dContactGeom *contact, int skip)#, 
                      #dGetDepthFn *GetDepth)
    


cdef class _JointGroup:
  cdef dJointGroupID _OdeGroupJoinID
  # A list of Python joints that were added to the group
  cdef object jointlist
  
Joint = None
cdef class _Joint:
  """Base class for all joint classes."""

    
  # Joint id as returned by dJointCreateXxx()
  cdef dJointID _OdeJointID
  # A reference to the world so that the world won't be destroyed while
  # there are still joints using it.
  cdef object world
  # The feedback buffer
  cdef dJointFeedback* feedback

  cdef _Body _body1
  cdef _Body _body2
  
  cdef _destroy(self)
  cdef void _destroyed(self)
  cdef void _setParam(self, int param, dReal value)
  cdef dReal _getParam(self, int param)
  
  cdef __getcstate__(self)
  cdef void __setcstate__(self,cstate)


cdef class Contact:
  cdef dContact _contact
  cdef _World   _ode_root
cdef class ContactJoint(_Joint):
  cdef Contact _contact


cdef class _Mass:
  """Mass parameters of a rigid body.

  This class stores mass parameters of a rigid body which can be
  accessed through the following attributes:

   - mass: The total mass of the body (float)
   - c:    The center of gravity position in body frame (3-tuple of floats)
   - I:    The 3x3 inertia tensor in body frame (3-tuple of 3-tuples)

  This class wraps the dMass structure from the C API.

  @ivar mass: The total mass of the body
  @ivar c: The center of gravity position in body frame (cx, cy, cz)
  @ivar I: The 3x3 inertia tensor in body frame ((I11, I12, I13), (I12, I22, I23), (I13, I23, I33))
  @type mass: float
  @type c: 3-tuple of floats
  @type I: 3-tuple of 3-tuples of floats 
  """
  cdef dMass _mass
  
  cdef __getcstate__(self)
  cdef __setcstate__(self,cstate)


cdef class _Space(_Geom):
  cdef _World   _world
  cdef readonly geoms
  
cdef class SimpleSpace(_Space):
  pass
