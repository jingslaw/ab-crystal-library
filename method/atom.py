###############################
#  This file is part of PyLaDa.
#
#  Copyright (C) 2013 National Renewable Energy Lab
#
#  PyLaDa is a high throughput computational platform for Physics. It aims to make it easier to submit
#  large numbers of jobs on supercomputers. It provides a python interface to physical input, such as
#  crystal structures, as well as to a number of DFT (VASP, CRYSTAL) and atomic potential programs. It
#  is able to organise and launch computational jobs on PBS and SLURM.
#
#  PyLaDa is free software: you can redistribute it and/or modify it under the terms of the GNU General
#  Public License as published by the Free Software Foundation, either version 3 of the License, or (at
#  your option) any later version.
#
#  PyLaDa is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
#  the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#  Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with PyLaDa.  If not, see
#  <http://www.gnu.org/licenses/>.
###############################

class Atom(object):
    """ Defines an atomic site

        __init__ accepts different kind of input.
          - The position can be given as:
              - the first *three* positional argument
              - as a keyword argument ``position``,
          - The type can be given as:
              - arguments listed after the first three giving the position. A
              list is created to hold references to these arguments.
              - as a keyword argument ``type``.
          - All other keyword arguments become attributes.
            In other words, one could add ``magnetic=0.5`` if one wanted to
            specify the magnetic moment of an atom.

        For instance, the following will create a silicon atom at the origin::

          atom = Atom(0, 0, 0, 'Si')

        Or we could place a iron atom with a magntic moment::

          atom = Atom(0.25, 0, 0.5, 'Si', moment=0.5)

        The ``moment`` keyword will create a corresponding ``atom.moment``
        keyword with a value of 0.5. There are strictly no limits on what kind
        of type to include as attributes. However, in order to work well with
        the rest of Pylada, it is best if extra attributes are pickle-able.

        .. note::

            the position is always owned by the object. Two atoms will not own
            the same position object.  The position given on input is *copied*,
            *not* referenced.  All other attributes behave like other python
            attributes: they are refence if complex objects and copies if a
            basic python type.
    """

    def __init__(self, *args, **kwargs):
        from numpy import array
        from method import error
        super(Atom, self).__init__()

        if len(args) >= 3 and 'pos' in kwargs:
            raise error.TypeError(
                "Position given through argument and keyword arguments both")
        if len(args) > 3 and 'type' in kwargs:
            raise error.TypeError(
                "Type given through argument and keyword arguments both")

        dtype = kwargs.pop('dtype', 'float64')
        if len(args) >= 3:
            self._pos = array(args[:3], dtype=dtype)
        elif len(args) == 2 or len(args) == 1:
            self._pos = array(args[0], dtype=dtype)
        elif 'pos' in kwargs:
            self._pos = array(kwargs.pop('pos'), dtype=dtype)
        else:
            self._pos = array([0., 0., 0.])
        if len(args) == 4:
            self.type = args[3]
        elif len(args) == 2:
            self.type = args[1]
        elif len(args) > 4:
            self.type = args[3:]
        else:
            self.type = kwargs.pop('type', None)
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        from numpy import require
        if not hasattr(value, 'dtype'):
            self._pos = require(value, dtype=self._pos.dtype)
        else:
            self._pos = value

    def __repr__(self):
        """ Dumps atom to string """
        args = [repr(u) for u in self.pos]
        args.append(repr(self.type))
        if self.pos.dtype != 'float64':
            args.append("dtype='%s'" % self._pos.dtype)
        for k, v in self.__dict__.items():
            if k != '_pos' and k != 'type':
                args.append(str(k) + "=" + repr(v))
        return self.__class__.__name__ + "(" + ", ".join(args) + ")"

    def to_dict(self):
        result = self.__dict__.copy()
        result['pos'] = result.pop('_pos')
        return result

    def copy(self):
        """ Deep copy of this object """
        from copy import deepcopy
        return deepcopy(self)
