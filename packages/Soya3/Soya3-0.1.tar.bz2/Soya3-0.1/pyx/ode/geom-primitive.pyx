# -*- coding: utf-8 -*-

# Soya 3D
# Copyright (C) 2001-2014 Jean-Baptiste LAMY
# Copyright (C) 2004-2012 Marmoute - Pierre-Yves David - marmoute@nekeme.net
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


#, land.x, land.y, land.z Geom objects

# GeomSphere

cdef class GeomSphere(_PrimitiveGeom):
    """Sphere geometry.

    This class represents a sphere centered at the origin.

    Constructor::
    
      GeomSphere(space=None, radius=1.0)
    """
    def __init__(self,_Body body=None,radius=1):
      _PlaceableGeom.__init__(self,body)
      self.radius = radius
    cdef _create(self):
      cdef dSpaceID sid
      if self._space is not None:
        sid = <dSpaceID>self._space._OdeGeomID
      else:
        sid = NULL
      self._OdeGeomID = dCreateSphere(sid,1)
        

    property radius:
      def __set__(self, dReal radius):
        dGeomSphereSetRadius(self._OdeGeomID, radius)

      def __get__(self):
        return dGeomSphereGetRadius(self._OdeGeomID)

    cdef float _point_depth(self, float x, float y, float z):
      """pointDepth(p) -> float

      Return the depth of the point p in the sphere. Points inside
      the geom will have positive depth, points outside it will have
      negative depth, and points on the surface will have zero
      depth.

      @param p: Point
      @type p: 3-sequence of floats
      """
      return dGeomSpherePointDepth(self._OdeGeomID, x, y, z)
      
# GeomBox
cdef class GeomBox(_PrimitiveGeom):
    """Box geometry.

    This class represents a box centered at the origin.

    Constructor::
    
      GeomBox(space=None, lengths=(1.0, 1.0, 1.0))
    """

    def __init__(self, _Body body, lengths=(1.0, 1.0, 1.0)):
      _PlaceableGeom.__init__(self,body)
      self.lengths = lengths
      
    cdef _create(self):
      cdef dSpaceID sid
      
      if self._space is not None:
          sid = <dSpaceID>self._space._OdeGeomID
      else:
          sid = NULL

      self._OdeGeomID = dCreateBox(sid, 1,1,1)

    property lengths:
      def __set__(self, lengths):
        dGeomBoxSetLengths(self._OdeGeomID, lengths[0], lengths[1], lengths[2])

      def __get__(self):
        cdef dVector3 res
        dGeomBoxGetLengths(self._OdeGeomID, res)
        return (res[0], res[1], res[2])

    cdef float _point_depth(self, float x, float y, float z):
        """pointDepth(p) -> float

        Return the depth of the point p in the box. Points inside the
        geom will have positive depth, points outside it will have
        negative depth, and points on the surface will have zero
        depth.

        @param p: Point
        @type p: 3-sequence of floats
        """
        return dGeomBoxPointDepth(self._OdeGeomID, x, y, z)

cdef class GeomCapsule(_PrimitiveGeom):
  """Capsule geometry.

  This class represents a capped cylinder (capsule) aligned
  along the local Z axis and centered at the origin.

  Constructor::
  
    GeomCapsule(space=None, radius=0.5, length=1.0)

  The length parameter does not include the caps.
  """

  def __init__(self, _Body body, radius=0.5, length=1.0):
    _PlaceableGeom.__init__(self,body)
    self.params = radius,length
    
  cdef _create(self):
      cdef dSpaceID sid
      if self._space is not None:
          sid = <dSpaceID>self._space._OdeGeomID
      else:
          sid = NULL

      self._OdeGeomID = dCreateCapsule(sid, 1,1)
    
  property radius:
    def __set__(self, radius):
      dGeomCapsuleSetParams(self._OdeGeomID, radius, self.length)
    def __get__(self):
      cdef dReal radius, length
      dGeomCapsuleGetParams(self._OdeGeomID, &radius, &length)
      return radius
  property length:
    def __set__(self, length):
      dGeomCapsuleSetParams(self._OdeGeomID, self.radius, length)
    def __get__(self):
      cdef dReal radius, length
      dGeomCapsuleGetParams(self._OdeGeomID, &radius, &length)
      return length
  property params:
    def __set__(self, params):
      dGeomCapsuleSetParams(self._OdeGeomID, params[0], params[1])

    def __get__(self):
      cdef dReal radius, length
      dGeomCapsuleGetParams(self._OdeGeomID, &radius, &length)
      return (radius, length)

  cdef float _point_depth(self, float x, float y, float z):
    """pointDepth(p) -> float

    Return the depth of the point p in the cylinder. Points inside the
    geom will have positive depth, points outside it will have
    negative depth, and points on the surface will have zero
    depth.

    @param p: Point
    @type p: 3-sequence of floats
    """
    return dGeomCapsulePointDepth(self._OdeGeomID, x, y, z)

cdef class GeomCylinder(_PrimitiveGeom):
  """Cylinder geometry.
  
  This class represents a cylinder aligned along the local Z axis
  and centered at the origin.
  
  Constructor::
  
    GeomCylinder(space=None, radius=0.5, length=1.0)
  """
  
  def __init__(self, _Body body, radius=0.5, length=1.0):
    _PlaceableGeom.__init__(self,body)
    self.params = radius,length
    
  cdef _create(self):
      cdef dSpaceID sid
      if self._space is not None:
          sid = <dSpaceID>self._space._OdeGeomID
      else:
          sid = NULL
  
      self._OdeGeomID = dCreateCylinder(sid, 1,1)
  
  property radius:
    def __set__(self, radius):
      dGeomCylinderSetParams(self._OdeGeomID, radius, self.length)
    def __get__(self):
      cdef dReal radius, length
      dGeomCylinderGetParams(self._OdeGeomID, &radius, &length)
      return radius
  property length:
    def __set__(self, length):
      dGeomCylinderSetParams(self._OdeGeomID, self.radius, length)
    def __get__(self):
      cdef dReal radius, length
      dGeomCylinderGetParams(self._OdeGeomID, &radius, &length)
      return length
  property params:
    def __set__(self, params):
      dGeomCylinderSetParams(self._OdeGeomID, params[0], params[1])
  
    def __get__(self):
      cdef dReal radius, length
      dGeomCylinderGetParams(self._OdeGeomID, &radius, &length)
      return (radius, length)
  
  #cdef float _point_depth(self, float x, float y, float z):
  #  """pointDepth(p) -> float
  #
  #  Return the depth of the point p in the cylinder. Points inside the
  #  geom will have positive depth, points outside it will have
  #  negative depth, and points on the surface will have zero
  #  depth.
  #
  #  @param p: Point
  #  @type p: 3-sequence of floats
  #  """
  #  return dGeomCylinderPointDepth(self._OdeGeomID, x, y, z)
