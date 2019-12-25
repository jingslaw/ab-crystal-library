import read
from method.compare_structure import structure_compare


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


def exec(outputPath, host_path, doped_path, tolerance, percent):
    host = read.poscar(host_path, types=poscar_is_vasp5(host_path))
    doped = read.poscar(doped_path, types=poscar_is_vasp5(doped_path))
    arrow_location, arrow = structure_compare(outputPath, host, doped, tolerance, percent)
    return arrow_location, arrow


if __name__ == "__main__":
    host_path = 'host'
    doped_path = 'defect'
    host = read.poscar(host_path, types=poscar_is_vasp5(host_path))
    doped = read.poscar(doped_path, types=poscar_is_vasp5(doped_path))
    save_path = ''
    result = structure_compare(save_path, host, doped)
    print(result)
