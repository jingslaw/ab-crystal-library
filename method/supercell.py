#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

__author__ = 'Weiguo Jing'


def deviation(cell):
    from numpy.linalg import norm
    min_length = min(norm(cell[0]), norm(cell[1]), norm(cell[2]))
    diagonal1 = cell[0] + cell[1] + cell[2]
    diagonal2 = cell[0] + cell[1] - cell[2]
    diagonal3 = cell[0] - cell[1] + cell[2]
    diagonal4 = cell[0] - cell[1] - cell[2]
    max_diagonal = max(norm(diagonal1), norm(diagonal2), norm(diagonal3), norm(diagonal4))
    return max_diagonal/min_length - pow(3, 0.5)


# def deviation(super_cell, volume):
#    import numpy as np
#    from numpy.linalg import norm

#    unit = pow(volume, 1.0/3) * np.eye(3)
#    return norm(super_cell - unit, 2)/norm(unit, 2)


def find_transform_matrix(structure, num=10, tolerance=1e-5):
    import numpy as np
    from numpy import cross, dot
    from numpy.linalg import norm, det
    from math import ceil

    cell = structure.cell.T
    volume = structure.volume
    max_length = pow(num, 1.0 / 3) * max(norm(cell[0]), norm(cell[1]), norm(cell[2]))
    vector_projection1 = volume/norm(cross(cell[1], cell[2]))
    vector_projection2 = volume/norm(cross(cell[2], cell[0]))
    vector_projection3 = volume/norm(cross(cell[0], cell[1]))
    r1 = int(ceil(max_length/vector_projection1)+0.001)
    r2 = int(ceil(max_length/vector_projection2)+0.001)
    r3 = int(ceil(max_length/vector_projection3)+0.001)
    bias = [9999999.0 for i in range(num)]
    matrixes = [None for i in range(num)]
    i = 0
    tot = ((2*r1+1)**3)*((2*r2+1)**3)*((2*r3+1)**3)

    for P11 in range(-r1, r1+1):
        for P22 in range(-r2, r2+1):
            for P33 in range(-r3, r3+1):
                with open('log', 'w') as file:
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
                                        if n > num or n == 0:
                                            continue
                                        else:
                                            super_cell = dot(pmatrix, cell)
                                            result = deviation(super_cell)
                                            if result < tolerance:
                                                with open('log', 'w') as file:
                                                    file.writelines('{0}%'.format('100'))
                                                    file.close()
                                                return pmatrix
                                            elif result < bias[n-1]:
                                                bias[n-1] = result
                                                matrixes[n-1] = pmatrix
    index = bias.index(min(bias))
    file.close()
    return matrixes[index]


def is_in_cell(fractional):
    for i in range(3):
        if fractional[i] < 0 or fractional[i] >= 1:
            return False
    return True


def supercell(structure, transform):
    from method.structure import Structure
    import numpy as np
    from numpy import dot

    r = []
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
                    if is_in_cell(temp):
                        result.add_atom(dot(result.cell, temp), structure[i].type)
    return result


def build_supercell(structure, num=10, tolerance=1e-5):
    """
    To transform a non-cubic primitive to a supercell as close to cube as possible. Algorithm detail see \
    *Phys. Rev. B 91, 165206*.

    :param structure: 'Pylada.crystal.Structure'
    The structure of primitive cell.
    :param num: 'int'
    The maximum sizes of supercell to primitive cell.
    :param tolerance: 'float'
    The tolerance to stop the loop of find transform matrix. The supercell will be considered as cube when the \
    deviation is smaller than tolerance.
    :return: 'Pylada.crystal.Structure'
    The structure of supercell.
    """
    from numpy import dot
    from numpy.linalg import det

    transform = find_transform_matrix(structure, num, tolerance)
    result = dot(transform, structure.cell.T)
    if result[0][0] < 0:
        transform[0] = -1 * transform[0]
    if result[1][1] < 0:
        transform[1] = -1 * transform[1]
    if result[2][2] < 0:
        transform[2] = -1 * transform[2]
    result = supercell(structure, transform)
    result.name = "{0} times for original cell".format(int(0.01 + abs(det(transform))))
    return result
