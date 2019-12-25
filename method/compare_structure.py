#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

__author__ = 'Weiguo Jing'

from method.atom import Atom
import numpy as np
from method.utilities import into_cell


def are_periodic(pos1, pos2, cell, tolerance=1.0):
    from numpy import dot
    from numpy.linalg import inv, norm
    invcell = inv(cell)
    result = dot(invcell, pos1 - pos2)
    frac = []
    for x in result:
        frac.append(min(abs(x), 1 - abs(x)))
    distance = norm(dot(cell, frac))
    if distance < tolerance:
        return True
    else:
        return False


class Element(object):
    def __init__(self, element, cell, host_list, doped_list, tolerance=1.0):
        self.type = element
        self.unchanged = []
        self.surface = []
        self.vac = []
        self.int = []
        self.sub = []
        if len(host_list) == 0:
            self.int.extend(doped_list)
        elif len(doped_list) == 0:
            self.vac.extend(host_list)
        else:
            used = []
            for atom1 in host_list:
                temp = [atom1, ]
                for atom2 in doped_list:
                    if are_periodic(atom1.pos, atom2.pos, cell, tolerance):
                        temp.append(atom2)
                        used.append(atom2)
                if len(temp) == 1:
                    self.vac.append(atom1)
                elif len(temp) > 2:
                    print('\nWARNING: atom {0} is not one to one mappping, tolerance is too large!\n\n'.format(atom1))
                    print(temp)
                    minimum = 9999999
                    atom = temp[0]
                    for i in range(1, len(temp)):
                        distance = np.linalg.norm(temp[0].pos - temp[i].pos)
                        if distance < minimum:
                            minimum = distance
                            atom = temp[i]
                    distance = np.linalg.norm(temp[0].pos - atom.pos)
                    if distance > tolerance:
                        self.surface.append([temp[0], atom])
                    else:
                        self.unchanged.append([temp[0], atom])
                else:
                    distance = np.linalg.norm(temp[0].pos - temp[1].pos)
                    if distance > tolerance:
                        self.surface.append(temp)
                    else:
                        self.unchanged.append(temp)
            for atom2 in doped_list:
                if atom2 not in used:
                    self.int.append(atom2)


def get_species(structure):
    species = {}
    i = 0
    for atom in structure:
        if species.get(atom.type):
            species[atom.type].append(Atom(atom.pos, atom.type, num=i))
        else:
            species[atom.type] = [Atom(atom.pos, atom.type, num=i), ]
        i = i + 1
    return species


def get_doped_type(host, doped, tolerance=1.0):
    host_species = get_species(host)
    doped_species = get_species(doped)
    result = []
    for key in host_species:
        element = Element(key, host.cell.T, host_species[key], doped_species.pop(key, []), tolerance=tolerance)
        result.append(element)
    for key in doped_species:
        element = Element(key, host.cell.T, host_species.pop(key, []), doped_species[key], tolerance=tolerance)
        result.append(element)
    for element in result:
        for temp in result:
            for interstitial in element.int:
                for vacancy in temp.vac:
                    if are_periodic(interstitial.pos, vacancy.pos, host.cell.T, tolerance=tolerance):
                        temp.vac.remove(vacancy)
                        element.int.remove(interstitial)
                        element.sub.append([interstitial, vacancy])
    return result


def get_atom_mass(name):
    elements = {
        'H': 1.008, 'He': 4.003, 'Li': 6.941, 'Be': 9.012, 'B': 10.812, 'C': 12.011, 'N': 14.007, 'O': 15.999,
        'F': 18.998, 'Ne': 20.180, 'Na': 22.990, 'Mg': 24.305, 'Al': 26.982, 'Si': 28.086, 'P': 30.974, 'S': 32.066,
        'Cl': 35.453, 'Ar': 39.948, 'K': 39.098, 'Ca': 40.078, 'Sc': 44.956, 'Ti': 47.867, 'V': 50.942, 'Cr': 51.996,
        'Mn': 54.938, 'Fe': 55.845, 'Co': 58.933, 'Ni': 58.693, 'Cu': 63.546, 'Zn': 65.382, 'Ga': 69.723, 'Ge': 72.641,
        'As': 74.922, 'Se': 78.972, 'Br': 79.904, 'Kr': 83.798, 'Rb': 85.468, 'Sr': 87.621, 'Y': 88.906, 'Zr': 91.224,
        'Nb': 92.906, 'Mo': 95.951, 'Tc': 98.907, 'Ru': 101.072, 'Rh': 102.906, 'Pd': 106.421, 'Ag': 107.868,
        'Cd': 112.414, 'In': 114.818, 'Sn': 118.711, 'Sb': 121.760, 'Te': 127.603, 'I': 126.904, 'Xe': 131.294,
        'Cs': 132.905, 'Ba': 137.328, 'La': 138.905, 'Ce': 140.116, 'Pr': 140.908, 'Nd': 144.242, 'Pm': 144.920,
        'Sm': 150.362, 'Eu': 151.964, 'Gd': 157.253, 'Tb': 158.925, 'Dy': 162.500, 'Ho': 164.930, 'Er': 167.259,
        'Tm': 168.934, 'Yb': 173.055, 'Lu': 174.967, 'Hf': 178.492, 'Ta': 180.948, 'W': 183.841, 'Re': 186.207,
        'Os': 190.233, 'Ir': 192.217, 'Pt': 195.085, 'Au': 196.967, 'Hg': 200.592, 'Tl': 204.383, 'Pb': 207.210,
        'Bi': 208.980, 'Po': 208.982, 'At': 209.987, 'Rn': 222.018, 'Fr': 223.020, 'Ra': 226.025, 'Ac': 227.028,
        'Th': 232.038, 'Pa': 231.036, 'U': 238.029, 'Np': 237.048, 'Pu': 239.064, 'Am': 243.061, 'Cm': 247.070,
        'Bk': 247.070, 'Cf': 251.080, 'Es': 252.083, 'Fm': 257.059, 'Md': 258.098, 'No': 259.101, 'Lr': 262.110,
        'Rf': 267.122, 'Db': 268.126, 'Sg': 269.129, 'Bh': 274.144, 'Hs': 277.152, 'Mt': 278, 'others': 281
    }
    try:
        return elements[name]
    except KeyError:
        return elements['others']


def mass_center_calculation(structure):
    total_mass = 0.0
    mass_center = np.array([0.0, 0.0, 0.0])
    for atom in structure:
        mass = get_atom_mass(atom.type)
        mass_center += mass * atom.pos
        total_mass += mass
    return mass_center / total_mass


def compare_structure(host, doped, tolerance=1.0, compare_type='M'):
    doped_type = get_doped_type(host, doped, tolerance)
    if compare_type == 'M':
        host_base = []
        doped_base = []
        for element in doped_type:
            for pair in element.unchanged:
                host_base.append(pair[0])
                doped_base.append(pair[1])
        distance = mass_center_calculation(host_base) - mass_center_calculation(doped_base)
        for atom in doped:
            atom.pos = into_cell(atom.pos + distance, cell=doped.cell)
        doped_type = get_doped_type(host, doped, tolerance)
    return doped_type


def write_compare_result(save_path, doped_type):
    import os
    import platform
    output_name = os.path.join(save_path, 'structure compare.txt')
    if platform.system() == 'Windows':
        output_name = output_name.replace('\\', '/')
    with open(output_name, 'w+') as fp:
        interstitial = []
        substitution = []
        vacancy = []
        unchanged = []
        surface = []
        for element in doped_type:
            interstitial += element.int
            substitution += element.sub
            vacancy += element.vac
            unchanged += element.unchanged
            surface += element.surface
        fp.writelines('*************************\n')
        fp.writelines('DOPED\n')
        if len(interstitial) > 0:
            fp.writelines('INTERSTITIAL\n')
            for atom in interstitial:
                fp.writelines('{0}  {1}\n'.format(atom.type, atom.pos))
        if len(substitution) > 0:
            fp.writelines('SUBSTITUTION\n')
            for pair in substitution:
                for atom in pair:
                    fp.writelines('{0}{1}   {2}\n'.format(atom.type, atom.num, atom.pos))
                fp.writelines('displacement: {0}\nnorm: {1}\n\n'.format(pair[1].pos - pair[0].pos,
                                                                        np.linalg.norm(pair[1].pos - pair[0].pos)))
        if len(vacancy) > 0:
            fp.writelines('VACANCY\n')
            for atom in vacancy:
                fp.writelines('{0}  {1}\n'.format(atom.type, atom.pos))
        if len(surface) > 0:
            fp.writelines('\nTHE SURFACE ATOMS:\n')
            for pair in surface:
                for atom in pair:
                    fp.writelines('{0}{1}   {2}\n'.format(atom.type, atom.num, atom.pos))
        fp.writelines('*************************\n')
        fp.writelines('\nTHE MOVEMENT:\n')
        for pair in unchanged:
            for atom in pair:
                fp.writelines('{0}{1}   {2}\n'.format(atom.type, atom.num, atom.pos))
            fp.writelines('displacement: {0}\nnorm: {1}\n\n'.format(pair[1].pos - pair[0].pos,
                                                                    np.linalg.norm(pair[1].pos - pair[0].pos)))


def structure_compare(save_path, host, doped, tolerance=1.0, percent=10):
    result = compare_structure(host, doped, tolerance)
    write_compare_result(save_path, result)
    temp = []
    for element in result:
        temp += element.unchanged + element.sub
    arrow_location = np.array([0, 0, 0])
    arrow = np.array([0, 0, 0])
    maximum = 0
    for pair in temp:
        postion = (pair[1].pos + pair[0].pos) / 2
        vector = pair[1].pos - pair[0].pos
        if np.linalg.norm(vector) > maximum:
            maximum = np.linalg.norm(vector)
        arrow_location = np.dstack((arrow_location, postion))
        arrow = np.dstack((arrow, vector))
    arrow_location = arrow_location[0]
    arrow = arrow[0] * percent
    return arrow_location, arrow
