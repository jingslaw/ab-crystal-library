#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'jingslaw'
__version__ = 1.0

from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt
import numpy as np


def plot_cube(ax, cube_definition):
    cube_definition_array = [
        np.array(list(item))
        for item in cube_definition
    ]

    points = []
    points += cube_definition_array
    vectors = [
        cube_definition_array[1] - cube_definition_array[0],
        cube_definition_array[2] - cube_definition_array[0],
        cube_definition_array[3] - cube_definition_array[0]
    ]

    points += [cube_definition_array[0] + vectors[0] + vectors[1]]
    points += [cube_definition_array[0] + vectors[0] + vectors[2]]
    points += [cube_definition_array[0] + vectors[1] + vectors[2]]
    points += [cube_definition_array[0] + vectors[0] + vectors[1] + vectors[2]]

    points = np.array(points)

    edges = [
        [points[0], points[3], points[5], points[1]],
        [points[1], points[5], points[7], points[4]],
        [points[4], points[2], points[6], points[7]],
        [points[2], points[6], points[3], points[0]],
        [points[0], points[2], points[4], points[1]],
        [points[3], points[6], points[7], points[5]]
    ]

    faces = Poly3DCollection(edges, linewidths=1, edgecolors='k')
    faces.set_facecolor((0, 0, 1, 0.1))

    ax.add_collection3d(faces)

    # Plot the points themselves to force the scaling of the axes
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], s=0)

    ax.set_aspect('equal')


def get_atom_detail(atom_name):
    elements = {
        'H': (0.32, '#000000'), 'He': (0.31, '#D9FFFF'), 'Li': (1.23, '#CC80FF'), 'Be': (0.89, '#C2FF00'),
        'B': (0.82, '#FFB5B5'), 'C': (0.77, '#909090'), 'N': (0.74, '#3050F8'), 'O': (0.70, '#FF0D0D'),
        'F': (0.68, '#90E050'), 'Ne': (0.67, '#B3E3F5'), 'Na': (1.54, '#AB5CF2'), 'Mg': (1.36, '#8AFF00'),
        'Al': (1.18, '#BFA6A6'), 'Si': (1.11, '#F0C8A0'), 'P': (1.06, '#FF8000'), 'S': (1.02, '#FFFF30'),
        'Cl': (0.99, '#1FF01F'), 'Ar': (0.98, '#80D1E3'), 'K': (2.03, '#8F40D4'), 'Ca': (1.74, '#3DFF00'),
        'Sc': (1.44, '#E6E6E6'), 'Ti': (1.32, '#BFC2C7'), 'V': (1.22, '#A6A6AB'), 'Cr': (1.18, '#8A99C7'),
        'Mn': (1.17, '#9C7AC7'), 'Fe': (1.17, '#E06633'), 'Co': (1.16, '#F090A0'), 'Ni': (1.15, '#50D050'),
        'Cu': (1.17, '#C88033'), 'Zn': (1.25, '#7D80B0'), 'Ga': (1.26, '#C28F8F'), 'Ge': (1.22, '#668F8F'),
        'As': (1.20, '#BD80E3'), 'Se': (1.17, '#FFA100'), 'Br': (1.14, '#A62929'), 'Kr': (1.12, '#5CB8D1'),
        'Rb': (2.16, '#702EB0'), 'Sr': (1.91, '#00FF00'), 'Y': (1.62, '#94FFFF'), 'Zr': (1.45, '#94E0E0'),
        'Nb': (1.34, '#73C2C9'), 'Mo': (1.30, '#54B5B5'), 'Tc': (1.27, '#3B9E9E'), 'Ru': (1.25, '#248F8F'),
        'Rh': (1.25, '#0A7D8C'), 'Pd': (1.28, '#006985'), 'Ag': (1.34, '#C0C0C0'), 'Cd': (1.48, '#FFD98F'),
        'In': (1.44, '#A67573'), 'Sn': (1.40, '#668080'), 'Sb': (1.40, '#9E63B5'), 'Te': (1.36, '#D47A00'),
        'I': (1.33, '#940094'), 'Xe': (1.31, '#429EB0'), 'Cs': (2.35, '#57178F'), 'Ba': (1.98, '#00C900'),
        'La': (1.69, '#70D4FF'), 'Ce': (1.65, '#FFFFC7'), 'Pr': (1.64, '#D9FFC7'), 'Nd': (1.64, '#C7FFC7'),
        'Pm': (1.63, '#A3FFC7'), 'Sm': (1.62, '#8FFFC7'), 'Eu': (1.85, '#61FFC7'), 'Gd': (1.62, '#45FFC7'),
        'Tb': (1.61, '#30FFC7'), 'Dy': (1.60, '#1FFFC7'), 'Ho': (1.58, '#00FF9C'), 'Er': (1.58, '#00E675'),
        'Tm': (1.58, '#00D452'), 'Yb': (1.70, '#00BF38'), 'Lu': (1.56, '#00AB24'), 'Hf': (1.44, '#4DC2FF'),
        'Ta': (1.34, '#4DA6FF'), 'W': (1.30, '#2194D6'), 'Re': (1.28, '#267DAB'), 'Os': (1.26, '#266696'),
        'Ir': (1.27, '#175487'), 'Pt': (1.30, '#D0D0E0'), 'Au': (1.34, '#FFD123'), 'Hg': (1.49, '#B8B8D0'),
        'Tl': (1.48, '#A6544D'), 'Pb': (1.47, '#575961'), 'Bi': (1.46, '#9E4FB5'), 'Po': (1.46, '#AB5C00'),
        'At': (1.45, '#754F45'), 'Rn': (1.43, '#428296'), 'Fr': (2.60, '#420066'), 'Ra': (2.20, '#007D00'),
        'Ac': (2.00, '#70ABFA'), 'Th': (1.65, '#00BAFF'), 'Pa': (1.00, '#00A1FF'), 'U': (1.42, '#008FFF'),
        'Np': (1.00, '#0080FF'), 'Pu': (1.00, '#006BFF'), 'Am': (1.00, '#545CF2'), 'Cm': (1.00, '#785CE3'),
        'Bk': (1.00, '#8A4FE3'), 'Cf': (1.00, '#A136D4'), 'Es': (1.00, '#B31FD4'), 'Fm': (1.00, '#B31FBA'),
        'Md': (1.00, '#B30DA6'), 'No': (1.00, '#BD0D87'), 'Lr': (1.00, '#C70066'), 'Rf': (1.00, '#CC0059'),
        'Db': (1.00, '#D1004F'), 'Sg': (1.00, '#D90045'), 'Bh': (1.00, '#E00038'), 'Hs': (1.00, '#E6002E'),
        'Mt': (1.00, '#EB0026'), 'others': (1.00, '#FF1493'),
    }
    try:
        item = elements[atom_name]
    except KeyError:
        item = elements['others']
    atom_size = (item[0] * 10)**2
    atom_color = item[1]
    return atom_size, atom_color


def specieset(structure):
    """ Returns ordered set of species.

        Especially usefull with VASP since we are sure what the list of species
        is always ordered the same way.
    """
    return sorted({a.type for a in structure})


def plot_atoms(ax, structure):
    scatter = []
    species = specieset(structure)
    for s in species:
        xs = []
        ys = []
        zs = []
        for atom in structure:
            if atom.type != s:
                continue
            position = atom.pos
            xs.append(position[0])
            ys.append(position[1])
            zs.append(position[2])
        size, color = get_atom_detail(s)
        temp = ax.scatter(xs, ys, zs, s=size, c=color, marker='o', depthshade=False)
        scatter.append(temp)
    sub_scatter = (i for i in scatter)
    labels = (i for i in species)
    plt.legend(sub_scatter, labels)


def draw_crystal_in_ax(ax, structure):
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    cell = structure.cell.T
    cube_definition = [[0, 0, 0], cell[0], cell[1], cell[2]]
    plot_cube(ax, cube_definition)
    plot_atoms(ax, structure)
