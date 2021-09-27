#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Weiguo Jing'
import spglib as spg
import numpy as np


def trans_pylada_stru_to_ase(structure):
    from ase import Atoms

    positions = [atom.pos for atom in structure]
    string = [atom.type for atom in structure]
    return Atoms(symbols=string, positions=positions, cell=structure.cell.T)


def get_symmetrical_operations(structure, symprec=0.01):
    cell = trans_pylada_stru_to_ase(structure)
    sym = spg.get_symmetry(cell, symprec=symprec)
    ops = [(r, t) for r, t in zip(sym['rotations'], sym['translations'])]
    return ops


def symmetrically_inequivalent_indices(structure, center=None, species=None, symprec=0.01):
    cell = trans_pylada_stru_to_ase(structure)
    symmetry = spg.get_symmetry(cell, symprec=symprec)
    equivalent_atoms = symmetry['equivalent_atoms']
    inequivalent_sites = np.unique(equivalent_atoms)
    if center is None:
        if species is None:
            return inequivalent_sites
        else:
            indices = []
            for index in inequivalent_sites:
                if structure[index].type in species:
                    print(structure[index].type)
                    indices.append(index)
            return np.array(indices)
    else:
        center = np.dot(center, structure.cell.T)
        indices = []
        equivalent = {}
        for index in inequivalent_sites:
            equivalent[index] = [index, 9999999]
        for i in range(len(equivalent_atoms)):
            index = equivalent_atoms[i]
            atom = structure[i]
            distance = np.linalg.norm(atom.pos - center)
            if equivalent[index][1] > distance:
                equivalent[index][0] = i
                equivalent[index][1] = distance
        for index in inequivalent_sites:
            if species is None:
                indices.append(equivalent[index][0])
            else:
                if structure[index].type in species:
                    indices.append(equivalent[index][0])
        return np.array(indices)


def vonoroi_cell_vertices(cell):
    return np.array(cell.vertices())


def vonoroi_face_center(cell):
    vertices_indices_of_faces = cell.face_vertices()
    cell_vertices = vonoroi_cell_vertices(cell)
    face_center = []
    for each_face in vertices_indices_of_faces:
        position = [cell_vertices[vertices_index] for vertices_index in each_face]
        face_center.append(np.mean(position, axis=0))
    return np.array(face_center)


def vonoroi_edge_center(cell):
    vertices_indices_of_faces = cell.face_vertices()
    cell_vertices = vonoroi_cell_vertices(cell)
    edge_center = []
    for each_face in vertices_indices_of_faces:
        for i in range(len(each_face)):
            position = np.mean([cell_vertices[each_face[i]], cell_vertices[each_face[(i+1) % len(each_face)]]], axis=0)
            edge_center.append(position)
    return np.array(edge_center)


def create_basic_cell_parameters(structure, index, n_shell=4, tolerance=1e-2):
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


def get_vonoroi_intersitial_sites(structure, index=0, symprec=0.01):
    import tess
    from method import utilities

    n_shell = 4
    vonoroi_points_number = 9999999
    while True:
        points, limits = create_basic_cell_parameters(structure, index, n_shell, symprec)
        vonoroi_cell = tess.Container(points, limits)
        cell = vonoroi_cell[0]
        cell_vertices = vonoroi_cell_vertices(cell)
        face_center = vonoroi_face_center(cell)
        edge_center = vonoroi_edge_center(cell)
        sites = np.row_stack((cell_vertices, face_center, edge_center))
        if len(sites) == vonoroi_points_number:
            break
        else:
            n_shell = n_shell * 2
            vonoroi_points_number = len(sites)
        if n_shell > 1024:
            # avoid some unknown problems
            break
    positions = []
    transform = structure[index].pos
    for site in sites:
        site = utilities.into_cell(site + transform, structure.cell)
        site = np.ndarray.tolist(site)
        positions.append(site)
    positions = sorted(positions)
    return positions


def remove_equivalent_sites(structure, positions, ops, center, tolerance):
    from numpy import dot
    from numpy.linalg import norm, inv
    from utilities import are_periodic_images

    result = []
    for i in range(len(positions)):
        if len(positions[i]) != 3:
            continue
        else:
            equivalent_sites = [positions[i]]
            for op in ops:
                rotation = op[0]
                translation = op[1]
                fraction = dot(positions[i], inv(structure.cell.T))
                transform = dot(rotation, fraction) + translation
                transform = dot(transform, structure.cell.T)

                for j in range(i + 1, len(positions)):
                    if len(positions[j]) != 3:
                        continue
                    if are_periodic_images(positions[j], transform, cell=structure.cell, tolerance=tolerance):
                        equivalent_sites.append(positions[j])
                        positions[j] = [0, ]
        result.append(equivalent_sites)
    positions = []
    if center is None:
        center = dot([0.5, 0.5, 0.5], structure.cell.T)
    else:
        center = dot(center, structure.cell.T)
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


def get_interstitial_positions(structure, center=None, tolerance=0.01):
    positions = []
    ops = get_symmetrical_operations(structure, symprec=tolerance)
    indices = symmetrically_inequivalent_indices(structure, center=center, species=None, symprec=tolerance)
    for index in indices:
        sites = get_vonoroi_intersitial_sites(structure, index=index)
        positions += sites
    positions = remove_equivalent_sites(structure, positions, ops, center, tolerance)
    return positions


def eta1(x):
    if x < 1:
        return pow(x, -11) - 1
    else:
        return 0


def eta2(x):
    from math import pow
    return pow(x, -12) - 2 * pow(x, -6)


def evaluate_interstitial_sites(structure, positions, insert, tolerance, radius=5):
    from method.coordination_shells import coordination_shells
    from method.plot_crystal import get_atom_detail

    result = []
    for pos in positions:
        n_shell = 1
        while True:
            neighs = coordination_shells(structure, n_shell, pos, tolerance)
            if neighs[-1][-1][2] > radius:
                break
            else:
                n_shell = n_shell * 2
        coeff1 = 0
        coeff2 = 0
        for shell in neighs:
            for neighbor in shell:
                if neighbor[2] <= radius:
                    r = neighbor[2] / (get_atom_detail(insert)[0] + get_atom_detail(neighbor[0].type)[0])
                    coeff1 = coeff1 + eta1(r)
                    coeff2 = coeff2 + eta2(r)
        result.append((coeff1, coeff2, pos))
    result = sorted(result, key=lambda x: (x[0], -x[1]))
    return result


def interstitial(structure, insert, position=None, center=None, tolerance=0.01, tag='F'):

    result = []
    if position is not None:
        doped_structure = structure.copy()
        doped_structure.add_atom(position, insert)
        doped_structure.name = 'interstitial_of_{0}_in_site0'.format(insert)
        result.append(doped_structure)

        view_structure = doped_structure
    else:
        positions = get_interstitial_positions(structure, center, tolerance)
        positions = evaluate_interstitial_sites(structure, positions, insert, tolerance)
        # need judgement
        view_structure = structure.copy()
        for i, position in enumerate(positions, start=1):
            if tag is 'F':
                if position[0] > 1e-12:
                    break
            doped_structure = structure.copy()
            doped_structure.add_atom(position[2], insert)
            doped_structure.name = 'interstitial_of_{0}_in_site{1}'.format(insert, i)
            result.append(doped_structure)
            view_structure.add_atom(position[2], insert)
    return result, view_structure


def specieset(structure):
    """ Returns ordered set of species.

        Especially usefull with VASP since we are sure what the list of species
        is always ordered the same way.
    """
    return sorted({a.type for a in structure})


def substitution(structure, types=None, subs=None, center=None, tolerance=0.01):
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

            :note:
            If you want to substitute more than one atomic specie in structure, you can input e.g. type=['Si','Al'].
            If type=None, all different kinds of species in structure will be doped.
            If subs is None, it will create vacancy.
            Of course, subs can also more than one atomic specie, you need to input as a list.
            The parameter of center *should* be fractional coordinates, i.e. if you want to make a point defect\
            at the center of host, that is center=[0.5, 0.5, 0.5]
            The smaller of tolerance makes symmetrical requires harder, and thus gives more *un-equivalent* sites \
            when structure keeps unchanged.
            The smaller of 'symprec' will give less allowable symmetrical operations because of the more strict \
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
        indices = symmetrically_inequivalent_indices(structure, center=center, species=specie, symprec=tolerance)
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


if __name__ == "__main__":
    from method.read import poscar
    structure1 = poscar('R-3c.vasp')
    # inequivalent = interstitial(structure1, 'O', center=[0.5, 0.5, 0.5])
    test = substitution(structure1)


