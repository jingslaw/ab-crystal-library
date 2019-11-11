import os
import re
import sys
from method import read
from method.write import poscar
from method.defect import interstitial


def poscar_is_vasp5(path="POSCAR"):
    import re
    from os.path import join, exists, isdir

    if path is None:
        path = "POSCAR"
    if not hasattr(path, 'read'):
        assert exists(path), IOError("Could not find path %s." % (path))
        if isdir(path):
            assert exists(join(path, "POSCAR")), IOError("Could not find POSCAR in %s." % (path))
            path = join(path, "POSCAR")
    poscar = path if hasattr(path, "read") else open(path, 'r')
    for i in range(5):
        poscar.readline()
    is_vasp_5 = True
    line = poscar.readline().split()
    for i in line:
        if not re.match(r"[A-Z][a-z]?", i):
            is_vasp_5 = False
            break
    if is_vasp_5 is True:
        poscar.close()
        return None
    else:
        species = []
        nb_atoms = [int(u) for u in line]
        poscar.readline()
        for n in nb_atoms:
            flag = 0
            for i in range(n):
                line = poscar.readline().split()
                if flag is 0:
                    species.append(line[3])
                    flag = 1
        poscar.close()
        return species


def exec(inputPath, outputPath, insert, center, position, tolerance):
    import platform

    structure = read.poscar(inputPath, types=poscar_is_vasp5(inputPath))
    doped_result, view_result = interstitial(structure, insert, position=position, center=center, tolerance=tolerance)
    for doped_structure in doped_result:
        output_name = os.path.join(outputPath, doped_structure.name)
        if platform.system() == 'Windows':
            output_name = output_name.replace('\\', '/')
        poscar(doped_structure, file_name=output_name, vasp5=True)
    poscar(view_result, file_name='inequivalent interstitial sites.vasp', vasp5=True)
    return view_result


if __name__ == "__main__":
    inputPath = sys.argv[1]
    outputPath = sys.argv[2]
    insert = sys.argv[3]
    center = sys.argv[4]
    if re.match(r'None', center):
        center = None
    else:
        center = center.split('[')[1].split(']')[0].split(',')
        center = [float(x) for x in center]
    position = sys.argv[5]
    if re.match(r'None', position):
        position = None
    else:
        position = position.split('[')[1].split(']')[0].split(',')
        position = [float(x) for x in position]
    tolerance = float(sys.argv[6])
    symprec = float(sys.argv[7])
    vnrprec = float(sys.argv[8])
    n_shell = int(sys.argv[9])

    exec(inputPath, outputPath, insert, center, position, tolerance)
