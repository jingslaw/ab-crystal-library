import sys
from method import read
from method import write
from .supercell import build_supercell


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


def exec(inputPath, outputPath, num, start, stop):
    structure = read.poscar(inputPath, types=poscar_is_vasp5(inputPath))
    super_structure = build_supercell(structure, num=num, start=start, stop=stop)
    write.poscar(super_structure, file_name=outputPath, vasp5=True)


if __name__ == '__main__':
    inputPath = sys.argv[1]
    outputPath = sys.argv[2]
    num = int(sys.argv[3])
    tolerance = float(sys.argv[4])
    '''
    print("inputPath: {}".format(inputPath))
    print("outputOath: {}".format(outputPath))
    print("num: {} | type: {}".format(num, type(num)))
    print("tolerance: {} | type: {}".format(tolerance, type(tolerance)))
    '''
    exec(inputPath, outputPath, num, tolerance)
