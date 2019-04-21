# ab-crystal-library
#############################################

INTRODUCTION

An offline crystal library, which includes about tens of thousand structure calculated by VASP, is provided. You can search the crystal in a friendly GUI page. The library will provide basic structure information such like space group, and basic electronic properties such like band gap calculated by VASP. When you are intrested to specific crystals, you can download their well-done VASP calculation files: INCAR, POSCAR, KPOINTS.

In addition, this library provides some practical tools for crystal doping. Fristly, there is a useful single-point doping program. When you choose a crystal as substrate, this program can find the most likely doping sites and give the structure(POSCAR). All of this candicates are found according to their geometric charecteristic. The algorithm detail of this program can be found in *Computational Material Science 130(2017)1-9*. Secondly, there is a function to expand a unit cell to supercell which is as close as a cubic. When a crystal is charged during the calculation in VASP, cubic shap is better for charge correction. The algorithm detail can be read in the appendix of *Phys. Rev. B 91, 165206*, although the judgement whether a cell is cubic in this reference is not correct. As we known, the matrix discribe of a cubic is not always diagonal, the diagonal form depends on specific coordinate system. In our program, we use the geometry charecteristic to judge the cell, i.e. the longest body diagonal line/the shortest side lenth=sqrt(3).

#############################################

INSTALL

Many external library are needed for this library. And few of them maybe a little bit hard to install.

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

Cpython:

pip: pip install Cpython.

#############################################

USAGE

Just use cmd and input:

python gui.py

Then you can use this library！
