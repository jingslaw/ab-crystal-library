#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
__version__ = '1.1.0'
__author__ = 'Weiguo Jing'


def deviation(cell):
    import numpy as np
    from numpy.linalg import norm, det

    surface = 2*(norm(np.cross(cell[0], cell[1]))+norm(np.cross(cell[0], cell[2]))+norm(np.cross(cell[1], cell[2])))
    volume = abs(det(cell))
    return surface * np.sqrt(surface / 6) / (6 * volume) - 1


def find_transform_matrix(structure, num=10, start=1, stop=None, tolerance=1e-5, fast_search=False):
    import numpy as np
    from numpy import cross, dot
    from numpy.linalg import norm, det
    from math import ceil

    if stop is None:
        stop = num
    cell = structure.cell.T
    volume = structure.volume
    max_length = pow(num, 1.0 / 3) * max(norm(cell[0]), norm(cell[1]), norm(cell[2]))
    vector_projection1 = volume/norm(cross(cell[1], cell[2]))
    vector_projection2 = volume/norm(cross(cell[2], cell[0]))
    vector_projection3 = volume/norm(cross(cell[0], cell[1]))
    r1 = int(ceil(max_length/vector_projection1)+0.001)
    r2 = int(ceil(max_length/vector_projection2)+0.001)
    r3 = int(ceil(max_length/vector_projection3)+0.001)
    bias = [9999999.0 for i in range(start, stop+1)]
    matrixes = [None for i in range(start, stop+1)]
    i = 0
    tot = ((2*r1+1)**2)*((2*r2+1)**2)*((2*r3+1)**2)*(r1+1)*(r2+1)*(r3+1)

    for P11 in range(0, r1+1):
        for P22 in range(0, r2+1):
            for P33 in range(0, r3+1):
                with open('log.txt', 'w') as file:
                    file.writelines('{0}%\r'.format(round(i*100.0/tot)))
                for P21 in range(-r1, r1+1):
                    for P31 in range(-r1, r1+1):
                        for P12 in range(-r2, r2+1):
                            for P32 in range(-r2, r2+1):
                                for P13 in range(-r3, r3+1):
                                    for P23 in range(-r3, r3+1):
                                        i += 1
                                        pmatrix = [P11, P12, P13, P21, P22, P23, P31, P32, P33]
                                        pmatrix = np.reshape(pmatrix, (3, 3))
                                        n = int(abs(det(pmatrix))+0.001)
                                        if n > stop or n < start:
                                            continue
                                        else:
                                            super_cell = dot(pmatrix, cell)
                                            result = deviation(super_cell)
                                            if fast_search and result < tolerance:
                                                with open('log.txt', 'w') as file:
                                                    file.writelines('{0}%'.format('100'))
                                                return pmatrix
                                            if result < bias[n-start]:
                                                bias[n-start] = result
                                                matrixes[n-start] = pmatrix
    with open('log.txt', 'w') as file:
        file.writelines('{0}%'.format('100'))
    index = bias.index(min(bias))
    with open('p_matrix.txt', 'w') as file:
        file.writelines('{0} supercells are calculated.\n\n'.format(tot))
        for i in range(len(bias)):
            file.writelines('{0}\n'.format(i + start))
            file.writelines('\nbias:{0}\n'.format(bias[i]))
            file.writelines('\n{0}\n\n'.format(matrixes[i]))
        file.writelines('\ncell size and bias\n\n')
        for i in range(len(bias)):
            file.writelines('{0}'.format(i + start) + ' {:.7f}\n'.format(bias[i]))
    return matrixes[index]


def is_in_cell(fractional, tolerance=1e-3):
    for i in range(3):
        if fractional[i] < tolerance or fractional[i] > 1 - tolerance:
            return False
    return True


def is_in_surface(fractional, tolerance=1e-3):
    for i in range(3):
        if fractional[i] < -tolerance or fractional[i] > 1 + tolerance:
            return False
    return True


def remove_reduplicate(surface, cell, tolerance=1e-3):
    from numpy.linalg import inv
    from numpy import dot

    for i in range(3):
        up = []
        down = []
        for atom in surface:
            fraction = dot(inv(cell), atom.pos)
            if abs(fraction[i]) <= tolerance:
                down.append(atom)
            elif abs(fraction[i] - 1) <= tolerance:
                up.append(atom)
        for atom1 in up:
            for atom2 in down:
                if abs(dot(inv(cell), atom1.pos - atom2.pos)[i] - 1) <= 2 * tolerance:
                    atom1.flag = 1
    result = []
    for atom in surface:
        if atom.flag == 0:
            result.append(atom)
    return result


def supercell(structure, transform):
    from method.structure import Structure
    from method.atom import Atom
    import numpy as np
    from numpy import dot
    epsilon = 1e-3

    r = []
    surface = []
    for j in range(3):
        minimum = 0
        maximum = 0
        for i in range(3):
            if transform[i][j] <= 0:
                minimum += transform[i][j]
            else:
                maximum += transform[i][j]
        r.append([minimum, maximum])
    result = Structure(dot(structure.cell, transform.T), scale=structure.scale)
    inverse = np.linalg.inv(transform)
    inv_cell = np.linalg.inv(structure.cell)
    for i in range(len(structure)):
        fractional = dot(inv_cell, structure[i].pos)
        for a0 in range(r[0][0]-1, r[0][1]+1):
            for a1 in range(r[1][0]-1, r[1][1]+1):
                for a2 in range(r[2][0]-1, r[2][1]+1):
                    translation = np.array([a0, a1, a2])
                    temp = dot((translation + fractional), inverse)
                    if is_in_cell(temp, epsilon):
                        result.add_atom(dot(result.cell, temp), structure[i].type)
                    elif is_in_surface(temp, epsilon):
                        surface.append(Atom(dot(result.cell, temp), structure[i].type, flag=0))
    surface = remove_reduplicate(surface, dot(structure.cell, transform.T), epsilon)
    result.extend(surface)
    return result


def build_supercell(structure, num=10, start=1, stop=None, fast_search=False, tolerance=1e-5):
    """
    To transform a non-cubic primitive to a supercell as close to cube as possible. A geometric properties is used to \
    judge whether a parallel hexahedron is close to a cubic that, in given volume of parallel hexahedron, cubic has the\
     smallest surface area.

    :param structure: 'Pylada.crystal.Structure'
    The structure of primitive cell.
    :param num: 'int'
    It decides the element range in loop matrix, whose value is proportional to the maximum size of supercell. When \
    stop para is default, the maximum size of supercell will be chosen as the value of num para. It is extremly useful \
    when you want to search the supercell in a large range, because you can choose a smaller value of num for smaller \
    loop times.
    :param start: 'int'
    The minimun sizes of supercell to primitive, default is 1, i.e. same volume as primitive cell.
    :param stop: 'int'
    The maximum sizes of supercell to primitive cell. Default value is None. When this value is default, this program \
    will choose the value of num as the maximum size of primitive cell.
    :param fast_search: 'bool'
    When the switch of fast search scheme is on, the program will finish when find a cell satisfies the judge tolerance.
    :param tolerance: 'float'
    The tolerance to stop the loop of find transform matrix. The supercell will be considered as cube when the \
    deviation is smaller than tolerance.
    :return: 'Pylada.crystal.Structure'
    The structure of supercell.
    """
    from numpy import dot
    from numpy.linalg import det

    transform = find_transform_matrix(structure, num=num, start=start, stop=stop, tolerance=tolerance,
                                      fast_search=fast_search)
    result = dot(transform, structure.cell.T)
    if result[0][0] < 0:
        transform[0] = -1 * transform[0]
    if result[1][1] < 0:
        transform[1] = -1 * transform[1]
    if result[2][2] < 0:
        transform[2] = -1 * transform[2]
    result = supercell(structure, transform)
    result.name = "{0} times of the primitive cell".format(int(0.01 + abs(det(transform))))

    return result
