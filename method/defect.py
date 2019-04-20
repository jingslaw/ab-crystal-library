#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

__author__ = 'Weiguo Jing'


def trans_pylada_stru_to_ase(structure):
    from ase import Atoms

    positions = [atom.pos for atom in structure]
    string = [atom.type for atom in structure]
    return Atoms(symbols=string, positions=positions, cell=structure.cell.T)


def get_symmetrical_operations(structure, symprec=0.1):
    import spglib as spg
    import numpy as np
    from numpy import dot

    structure = trans_pylada_stru_to_ase(structure)
    sym = spg.get_symmetry(structure, symprec=symprec)
    ops = []
    for i in range(len(sym['rotations'])):
        # Note: sym gives operations for fractional coordinate, however, we need operation for cartesain coordinate.
        #       Thus, rotation matrix is unchanged while translation matrix need transform as below.
        translation = dot(sym['translations'][i], structure.cell.T)
        op = np.row_stack((sym['rotations'][i], translation))
        ops.append(op)
    return ops


def symmetrically_inequivalent_sites(structure, specie=None, center=None, tolerance=1e-3, symprec=0.1):
    from method import error
    from method.atom import Atom
    from method.utilities import are_periodic_images
    from numpy import dot
    from numpy.linalg import norm

    if specie is None:
        raise error.RuntimeError("specie is None!")
    ops = get_symmetrical_operations(structure, symprec=symprec)
    temp = structure.copy()
    result = []
    for i in range(len(temp)):
        equivalent_sites = []
        if temp[i].type != specie:
            continue
        else:
            atom = Atom(temp[i].pos, type=temp[i].type, index=i)
            equivalent_sites.append(atom)
            for op in ops:
                rotation = op[:3]
                translation = op[3]
                transform = dot(rotation, temp[i].pos) + translation
                for j in range(i+1, len(temp)):
                    if temp[j].type != specie:
                        continue
                    if are_periodic_images(transform, temp[j].pos, cell=structure.cell, tolerance=tolerance):
                        atom = Atom(temp[j].pos, type=temp[j].type, index=j)
                        equivalent_sites.append(atom)
                        temp[j].type = 'Used'
        result.append(equivalent_sites)
    indices = []
    for equivalent in result:
        if center is None:
            indices.append(equivalent[0].index)
        else:
            center = dot(temp.cell, center)
            minimum = norm(equivalent[0].pos - center)
            index = equivalent[0].index
            for site in equivalent:
                if norm(site.pos - center) < minimum:
                    minimum = norm(site.pos - center)
                    index = site.index
            indices.append(index)
    return indices


def substitution(structure, types=None, subs=None, center=None, tolerance=1e-3, symprec=0.1):
    """Yields point-defects in given structure.
        One-point substitution or vacancy is decided by type and subs parameters.
        The result loops over all symmetrically un-equivalent sites in structure.
                :param structure: 'pylada.crystal.Structure'
                Structure which is interested for doping.
                :param types: list of 'str'
                Atomic specie for which to make one-point defect in given structure.
                :param subs: list of 'str'
                Atomic specie to substitute atoms in structure.
                :param center: a 'list' as 1*3 matrix
                In practically doping, point-defect prefers to be made at the center of the host.
                Thus, it will choose the nearest position of center to make point-defect when center is *not* None.
                :param tolerance: 'float'
                To judge how close of two atoms equals to treat as equivalence.
                :param symprec: 'float'
                The tolerance to give proper symmetrical operation matrix for structure.

                :note:
                If you want to substitute more than one atomic specie in structure, you can input e.g. type=['Si','Al'].
                If type=None, all different kinds of species in structure will be doped.
                If subs is None, it will create vacancy.
                Of course, subs can also more than one atomic specie, you need to input as a list.
                The parameter of center *should* be fractional coordinates, i.e. if you want to make a point defect\
                 at the center of host, that is center=[0.5, 0.5, 0.5]
                The smaller of tolerance makes symmetrical requires harder, and thus gives more *un-equivalent* sites\
                 when structure keeps unchanged.
                The smaller of 'symprec' will give less allowable symmetrical operations because of the more strict\
                 symmetrical requires.

                :return: 'pylada.crystal.Structure'
                A list of one-point substitution or vacancy structures.
    """
    from method import error

    result = []
    species = specieset(structure)
    if types is None:
        types = species
    else:
        types = [specie for specie in types if specie in species]
    if len(types) < 1:
        raise error.RuntimeError("Cannot find specie to substitute in structure!")
    view_structure = structure.copy()
    for specie in types:
        indices = symmetrically_inequivalent_sites(structure, specie, center, tolerance, symprec)
        for index in indices:
            if subs is None:
                doped_structure = structure.copy()
                del doped_structure[index]
                doped_structure.name = 'vacancy_of_{0}_in_site{1}'.format(specie, index+1)
                result.append(doped_structure)

                view_structure[index].type = 'Vac'
            else:
                for sub_specie in subs:
                    doped_structure = structure.copy()
                    doped_structure[index].type = sub_specie
                    doped_structure.name = 'substitution_{0}_in_site{1}'.format(sub_specie, index+1)
                    result.append(doped_structure)

                view_structure[index].type = 'Sub'
    return result, view_structure


def specieset(structure):
    """ Returns ordered set of species.

        Especially usefull with VASP since we are sure what the list of species
        is always ordered the same way.
    """
    return sorted({a.type for a in structure})


def vonoroi_cell_vertices(cell):
    import numpy as np

    return np.array(cell.vertices())


def vonoroi_face_center(cell):
    import numpy as np

    vertices_indices_of_faces = cell.face_vertices()
    cell_vertices = vonoroi_cell_vertices(cell)
    face_center = []
    for each_face in vertices_indices_of_faces:
        position = [cell_vertices[vertices_index] for vertices_index in each_face]
        face_center.append(np.mean(position, axis=0))
    return np.array(face_center)


def vonoroi_edge_center(cell):
    import numpy as np

    vertices_indices_of_faces = cell.face_vertices()
    cell_vertices = vonoroi_cell_vertices(cell)
    edge_center = []
    for each_face in vertices_indices_of_faces:
        for i in range(len(each_face)):
            position = np.mean([cell_vertices[each_face[i]], cell_vertices[each_face[(i+1) % len(each_face)]]], axis=0)
            edge_center.append(position)
    return np.array(edge_center)


def create_basic_cell_parameters(structure, index, n_shell=4, tolerance=1e-3):

    import numpy as np
    from numpy.linalg import norm
    from method.coordination_shells import coordination_shells

    neighs = coordination_shells(structure, n_shell, structure[index].pos, tolerance)
    points = np.array([[0, 0, 0], ])
    for shell in neighs:
        for neighbor in shell:
            points = np.row_stack((points, neighbor[1]))
    limit = round(10.0 * max([norm(vector) for vector in structure.cell.T]))
    limits = ((-limit, -limit, -limit), (limit, limit, limit))
    return points, limits


def remove_equivalent_sites(structure, index, positions, ops, tolerance):
    from numpy import dot
    from numpy.linalg import norm

    result = []
    for i in range(len(positions)):
        if len(positions[i]) != 3:
            continue
        else:
            equivalent_sites = [positions[i]]
            for op in ops:
                rotation = op[:3]
                translation = op[3]
                transform = dot(rotation, positions[i]) + translation
                for j in range(i + 1, len(positions)):
                    if len(positions[j]) != 3:
                        continue
                    if norm(transform - positions[j]) < tolerance:
                        equivalent_sites.append(positions[j])
                        positions[j] = [0, ]
        result.append(equivalent_sites)
    positions = []
    center = structure[index].pos
    for equivalent in result:
        minimum = norm(equivalent[0] - center)
        site = equivalent[0]
        for j in range(len(equivalent)):
            temp = norm(equivalent[j] - center)
            if minimum > temp:
                minimum = temp
                site = equivalent[j]
        positions.append(site)
    return positions


def inequivalent_intersitial_sites(structure, index=0, tolerance=1e-3, vnrprec=1e-3, symprec=0.1, n_shell=4):
    import tess
    import numpy as np
    from method import utilities

    points, limits = create_basic_cell_parameters(structure, index, n_shell, vnrprec)
    vonoroi_cell = tess.Container(points, limits)
    cell = vonoroi_cell[0]
    cell_vertices = vonoroi_cell_vertices(cell)
    face_center = vonoroi_face_center(cell)
    edge_center = vonoroi_edge_center(cell)
    sites = np.row_stack((cell_vertices, face_center, edge_center))
    positions = []
    transform = structure[index].pos
    for site in sites:
        site = utilities.into_cell(site+transform, structure.cell)
        site = np.ndarray.tolist(site)
        positions.append(site)
    positions = sorted(positions)
    ops = get_symmetrical_operations(structure, symprec=symprec)
    positions = remove_equivalent_sites(structure, index, positions, ops, tolerance)
    return positions


def get_interstitial_positions(structure, center=None, tolerance=1e-3, symprec=0.1, vnrprec=1e-3, n_shell=4):

    species = specieset(structure)
    positions = []
    for specie in species:
        indices = symmetrically_inequivalent_sites(structure, specie, center, tolerance, symprec)
        for index in indices:
            sites = inequivalent_intersitial_sites(structure, index, tolerance, vnrprec, symprec, n_shell)
            positions += sites
    return positions


def interstitial(structure, insert=None, center=None, position=None, tolerance=1e-3,
                 symprec=0.1, vnrprec=1e-3, n_shell=4):
    """Yields interstitial structure when interstitial atom specie and position is known or to find candidate\
     interstitial structure when interstitial sites is unknown. The method to find candidate interstitial is \
     referred as *Computational Material Science 130(2017)1-9*

            :param structure: pylada.crystal.Structure
            Structure which is interested for doping.
            :param insert: str
            Specie of interstitial atom.
            :param center: a 'list' as 1*3 matrix
            In practically doping, point-defect prefers to be made at the center of the host.
            Thus, it will choose the nearest position of center to make point-defect when center is *not* None.
            :param position: a 'list' as 1*3 matrix
            If the position of interstitial atom is know, it will create this doped structure directly.
            :param tolerance: float
            To judge how close of two atoms equals to treat as equivalence. Needed in two place:
            1. to find symmetrically inequivalent sites.
            2. to remove equivalent sites in candidate interstitial sites.
            :param symprec: float
            The tolerance to give proper symmetrical operation matrix for structure.
            :param vnrprec: float
            The tolerance decides the number of neighbors for given symmetrical inequivalent sites. This will impact\
             the shape of vonoroi cell.
            :param n_shell: int
            To decide how many shell of neighbors are considered for given symmetrical inequivalent sites. This will\
             also impact the shape of vonoroi cell.

            :note:
            insert should be only one specie of atom, if you want to interstitial different atoms, loop this program.
            The parameter of center *should* be fractional coordinates, i.e. if you want to make a point defect\
             at the center of host, that is center=[0.5, 0.5, 0.5]
            The smaller of tolerance makes symmetrical requires harder, and thus gives more *un-equivalent* sites\
             when structure keeps unchanged. Meanwhile, the smaller tolerance will give more *un-equivalent* sites\
             of candidate interstitial. Thus, if the result of candidate interstitial is too many, choose a bigger\
             tolerance, e.g. tolerance=0.5, is a good choice.
            The smaller of 'symprec' will give less allowable symmetrical operations because of the more strict\
             symmetrical requires.
            The smaller of 'vnrprec' will give fewer neighbors of each shell because of the more strict distance\
             require.
     """
    from method import error

    result = []
    if insert is None:
        raise error.RuntimeError("Interstitial atom specie should be known!")
    if position is not None:
        doped_structure = structure.copy()
        doped_structure.add_atom(position, insert)
        doped_structure.name = 'interstitial_of_{0}_in_site0'.format(insert)
        result.append(doped_structure)

        view_structure = doped_structure
    else:
        positions = get_interstitial_positions(structure, center, tolerance, symprec, vnrprec, n_shell)
        view_structure = structure.copy()
        for i, position in enumerate(positions, start=1):
            doped_structure = structure.copy()
            doped_structure.add_atom(position, insert)
            doped_structure.name = 'interstitial_of_{0}_in_site{1}'.format(insert, i)
            result.append(doped_structure)

            view_structure.add_atom(position, insert)
    return result, view_structure
