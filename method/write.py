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

""" Methods to write structures from file. """


def poscar(structure, file_name='POSCAR', vasp5=None, substitute=None, direct=True):
    """ Writes a poscar to file.

        :param structure:
            The structure to print out.
        :type structure:
            :py:class:`Structure`
        :param file:
            Object with a ''write'' method. If a string, then a file object is
            opened with that filename. The file is overwritten. If None, then
            writes to POSCAR in current working directory.
        :type file: str, stream, or None.
        :param bool vasp5:
            If true, include species in poscar, vasp-5 style.  Otherwise, looks
            for :py:data:`is_vasp_4 <pylada.is_vasp_4>` global config variable.
            Defaults to False, in which case, does not print specie types.
        :param substitute:
            If present, will substitute the atom type in the structure. Can be
            incomplete. Only works with vasp5 = True (or :py:data:`is_vasp_4
            <pylada.is_vasp_4>` = True).
        :type substitute:
            dict or None

        # >>> with open("POSCAR", "w") as file: write.poscar(structure, file, vasp5=True)

        Species in structures can be substituted for others (when using vasp5 format).
        Below, aluminum atoms are replaced by cadmium atoms. Other atoms are left unchanged.

        # >>> with open("POSCAR", "w") as file:
        # >>>   write.poscar(structure, file, vasp5=True, substitute={"Al":"Cd"})

        Selective dynamics are added to the POSCAR file if an atom in the
        structure has a freeze attribute (of non-zero length). It is expected
        that this attribute is a string and that it contains one of "x", "y",
        "z", corresponding to freezing the first, second, or third fractional
        coordinates. Combinations of these are also allowed.
    """
    from quantities import angstrom
    if file_name is None:
        with open('POSCAR', 'w') as fileobj:
            return poscar(structure, fileobj, vasp5, substitute, direct)
    elif not hasattr(file_name, 'write'):
        with open(file_name, 'w') as fileobj:
            return poscar(structure, fileobj, vasp5, substitute, direct)

    from numpy import matrix, dot, identity

    if vasp5 is None:
        import pylada
        vasp5 = not getattr(pylada, 'is_vasp_4', True)

    string = "{0}\n{1}\n".format(getattr(structure, 'name', ''),
                                 float(structure.scale.rescale(angstrom)))
    for i in range(3):
        string += "  {0[0]} {0[1]} {0[2]}\n".format(structure.cell[:, i])
    species = specieset(structure)
    if vasp5:
        if substitute is None:
            substitute = {}
        for s in species:
            string += " {0} ".format(substitute.get(s, s))
        string += "\n"
    for s in species:
        string += "{0} ".format(len([0 for atom in structure if atom.type == s]))
    if direct:
        inv_cell = matrix(structure.cell).I
        d_or_c = '\ndirect\n'
    else:
        inv_cell = matrix(identity(3))
        d_or_c = '\ncartesian\n'
    selective_dynamics =\
        any([len(getattr(atom, 'freeze', '')) != 0 for atom in structure])
    if selective_dynamics:
        string += "\nselective dynamics" + d_or_c
    else:
        string += d_or_c
    for s in species:
        for atom in structure:
            if atom.type != s:
                continue
            string += "  {0[0]:20.16f} {0[1]:20.16f} {0[2]:20.16f}"\
                      .format(dot(inv_cell, atom.pos).tolist()[0])
            freeze = getattr(atom, 'freeze', '')
            if selective_dynamics:
                string += "  {0} {1} {2}\n"\
                    .format('T' if 'x' in freeze != 0 else 'F',
                            'T' if 'y' in freeze != 0 else 'F',
                            'T' if 'z' in freeze != 0 else 'F')
            else:
                string += '\n'
    if file_name == None:
        return string
    elif isinstance(file_name, str):
        with open(file_name, 'w') as file:
            file.write(string)
    else:
        file_name.write(string)


def specieset(structure):
    """ Returns ordered set of species.

        Especially usefull with VASP since we are sure what the list of species
        is always ordered the same way.
    """
    return sorted({a.type for a in structure})
