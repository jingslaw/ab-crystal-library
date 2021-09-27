# ab-crystal-library
#############################################

INTRODUCTION

An offline crystal library, which includes about tens of thousand structure calculated by VASP, is provided. You can search the crystal in a friendly GUI page. The library will provide basic structure information such like space group, and basic electronic properties such like band gap calculated by VASP. When you are intrested to specific crystals, you can download their well-done VASP calculation files: INCAR, POSCAR, KPOINTS.

In addition, this library provides some practical tools for crystal doping. Fristly, there is a useful single-point doping program. When you choose a crystal as substrate, this program can find the most likely doping sites and give the structure(POSCAR). All of this candicates are found according to their geometric charecteristic. The algorithm detail of this program can be found in *Computational Material Science 130(2017)1-9*.
Secondly, there is a function to expand a unit cell to supercell which is as close as a cubic. When a crystal is charged during the calculation in VASP, cubic shap is better for charge correction. The algorithm detail can be read in the appendix of *Phys. Rev. B 91, 165206*, although the judgement whether a cell is cubic in this reference is not correct. As we known, the matrix discribe of a cubic is not always diagonal, the diagonal form depends on specific coordinate system. In our program, we use the geometry charecteristic to judge the cell, i.e. in given volume of parallel hexahedron, cubic has the smallest surface area. And there is also a useful tool to visualize the deformation, the movement of atoms before and after the doping relaxation, which compares the doped POSCAR and relaxed result CONTCAR files. 
Thirdly, we add a visualization tool to illustrate the structure relaxation between pristine bulk and doped structure. 

NOTE

The icsd.db only include about 2k crystals because of the upload limit. if you want to access a complete version for this database, please contact me. 
Thanks!

#############################################

INSTALL

Many external library are needed for this library. And few of them maybe a little bit hard to install. *Pylada* is the most important part in this program, however, it seems that this package could not install in WINDOWS system, so some needed methods from Pylada has been included in method folder.

Pylada (if you want to develop this program, this package might be needed):

The website: https://github.com/pylada/pylada-light

pip: pip install pylada

Pyqt5:

The website: https://pypi.org/project/PyQt5/#description

pip: pip install PyQt5

ase:

The website: https://pypi.org/project/ase/

pip: pip install ase

spglib:

The website: https://pypi.org/project/spglib/

pip: pip install spglib

matplotlib:

The website: https://pypi.org/project/matplotlib/

pip: pip install matplotlib

NOTE: python version higher than 3.7 will cause a problem that you can not see the 3D plot of crytall structure, which is plotted by mmatplotlib. 

tess:

The website: https://pypi.org/project/tess/

pip: pip install tess

NOTE: tess can not be installed directly in WINDOWS system. So you need download "tess-master.zip" file, or you can find this zip file in ab-crystal-library/method/ folder. Decompress this zip, and use cmd to install it:

Frist, find the location of setup.py of tess.

Then, input the command: python setup.py install

This method can help you install the tess successfully in WINDOWS system. If it still doesn't work, you need install Cpython, and do this process again.

Cython:

pip: pip install Cython.

#############################################

USAGE

Just use cmd and input:

python gui.py

Then you can use this library！

#############################################

UPDATE

Some changes in cystal-doped tools, which makes user more easier to handle.

2019-12-15
A new method: visulable structure compare between host and doped structure has been added to this project. And this function can analyze the defect location and type by comparing the host and doped structure.

2021-1-24
several bugs are fixed in tools.

2021-9-21
Now this program can used in Python3.8 version.
