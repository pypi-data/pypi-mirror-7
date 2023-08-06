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


# Callback function for the dSpaceCollide() call in the Space.collide() method
# The data parameter is a tuple (Python-Callback, Arguments).
# The function calls a Python callback function with 3 arguments:
# def callback(UserArg, Geom1, Geom2)
# Geom1 and Geom2 are instances of GeomXyz classes.

cdef void collide_callback(void* data, dGeomID o1, dGeomID o2):
  cdef void *gv1, *gv2
  cdef _JointGroup contact_group
  cdef _PlaceableGeom geom
  cdef _Body body
  cdef _World world
  space = <object>data
  if dGeomIsSpace(o1) or dGeomIsSpace(o2):
    dSpaceCollide2(o1, o2, data, collide_callback)
  else:
    gv1 = dGeomGetData(o1)
    g1  = <object>gv1
    gv2 = dGeomGetData(o2)
    g2  = <object>gv2
    contacts = collide(g1, g2)
    if len(contacts):
      if hasattr(g1.body,'ode_parent'):
        world = g1.body.ode_parent
      else:
        world = g2.body.ode_parent
        
      contact_group = world._contact_group
      if hasattr(g1.body,'hit'):
        g1.body.hit(g2.body,contacts)
      if hasattr(g2.body,'hit'):
        g2.body.hit(g1.body,contacts)
      if not (g1.body is None or g2.body is None):
        if not (g1.body.pushable or g2.body.pushable):
          return
        elif not g1.body.pushable:
          for contact in contacts:
            contact.erase_Geom1()
        elif not g2.body.pushable:
          for contact in contacts:
            contact.erase_Geom2()
        
      for contact in contacts:
        joint = ContactJoint(contact,contact_group)
      



def collide(_Geom geom1, _Geom geom2, int max_contacts=8):
  """Generate contact information for two objects.

  Given two geometry objects that potentially touch (geom1 and geom2),
  generate contact information for them. Internally, this just calls
  the correct class-specific collision functions for geom1 and geom2.

  [flags specifies how contacts should be generated if the objects
  touch. Currently the lower 16 bits of flags specifies the maximum
  number of contact points to generate. If this number is zero, this
  function just pretends that it is one - in other words you can not
  ask for zero contacts. All other bits in flags must be zero. In
  the future the other bits may be used to select other contact
  generation strategies.]

  If the objects touch, this returns a list of Contact objects,
  otherwise it returns an empty list.
  """
  
  cdef dContactGeom c[150]
  cdef int i, n
  cdef Contact cont
  
  cdef long nb_contact
  if max_contacts < 1 or max_contacts > 150:
      raise ValueError, "max_contacts must be between 1 and 150"
  # WTH is n ?
  nb_contact = dCollide(geom1._OdeGeomID, geom2._OdeGeomID,
                        max_contacts, c, sizeof(dContactGeom))
  res = []
  body = geom1.body
  if body is None:
    body = geom2.body
  root = body.ode_parent
  if nb_contact:
    bounce = (geom1._bounce + geom2._bounce)/2.
    grip = (geom1._grip * geom2._grip)
  for i from 0 <= i < nb_contact:
    cont = Contact(bounce=bounce,mu=grip, ode_root=root)
    cont._contact.geom = c[i]
    res.append(cont)

  # Set collision flag on trimeshes when they're colliding with one
  # another so that they don't update their last transformations
  # This could probably be done more genericly in a collision notification
  # method.
  #if n and isinstance(geom1, _TriMesh) and isinstance(geom2, _TriMesh):
  #  (<_TriMesh>geom1)._colliding = 1
  #  (<_TriMesh>geom2)._colliding = 1

  return res
