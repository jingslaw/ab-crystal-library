#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'jingslaw'
__version__ = 1.0

import re
import sys
import platform
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import matplotlib.pyplot as plt
from method.plot_crystal import draw_crystal_in_ax
from method import supercell_donet


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


def read_poscar(raw):
    from method import read
    with open('POSCAR', 'w') as f:
        f.write(raw)
    structure = read.poscar('POSCAR', types=poscar_is_vasp5('POSCAR'))
    return structure


class FilePath(object):
    def __init__(self, *args):
        self._open_path = args[0]
        self._save_path = args[1]

    @property
    def open_path(self):
        return self._open_path

    @open_path.setter
    def open_path(self, open_path):
        self._open_path = open_path

    @property
    def save_path(self):
        return self._save_path

    @save_path.setter
    def save_path(self, save_path):
        self._save_path = save_path


class ToolPage(QWidget):
    def __init__(self, *args):
        super().__init__()
        default = args[0]
        self.structure = read_poscar(default)
        self.input_file = QLineEdit('POSCAR')
        self.output_file = QLineEdit()
        self.path = FilePath('POSCAR', '')

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        ax = self.figure.add_subplot(111, projection='3d')

        draw_crystal_in_ax(ax, self.structure)
        self.canvas.draw()
        self.mpl_ntb = NavigationToolbar(self.canvas, self)

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Ab-crystallib')
        self.setWindowIcon(QIcon('ustclogo.jpg'))
        self.resize(1500, 800)

        file_page = QGridLayout()
        input_label = QLabel('Input file name:')
        input_label.setFont(QFont('Arial', 10, 50))
        self.input_file.setFont(QFont('Arial', 10, 50))
        input_btn = QPushButton('View')
        input_btn.setFont(QFont('Arial', 10, 50))
        input_btn.clicked.connect(self.readpath)
        file_page.addWidget(input_label, 0, 0)
        file_page.addWidget(self.input_file, 0, 1)
        file_page.addWidget(input_btn, 0, 2)

        output_label = QLabel('Output folder :')
        output_label.setFont(QFont('Arial', 10, 50))
        self.output_file.setFont(QFont('Arial', 10, 50))
        output_btn = QPushButton('View')
        output_btn.setFont(QFont('Arial', 10, 50))
        output_btn.clicked.connect(self.writepath)
        file_page.addWidget(output_label, 1, 0)
        file_page.addWidget(self.output_file, 1, 1)
        file_page.addWidget(output_btn, 1, 2)

        method = QTabWidget()
        supercell = SupercellPage(self.figure, self.canvas, self.path)
        substitution = SubstitutionPage(self.figure, self.canvas, self.path)
        interstitial = InterstitialPage(self.figure, self.canvas, self.path)
        method.addTab(supercell, 'Supercell')
        method.addTab(substitution, 'Substitution and Vacancy')
        method.addTab(interstitial, 'Interstitial')
        method.setFont(QFont('Arial', 10, 50))

        image_page = QVBoxLayout()
        image_page.addWidget(self.canvas)
        image_page.addWidget(self.mpl_ntb)
        tool_page = QVBoxLayout()
        tool_page.addLayout(file_page)
        tool_page.addWidget(method)

        page = QGridLayout()
        page.addItem(image_page, 0, 0)
        page.addItem(tool_page, 0, 1)

        self.setLayout(page)
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def readpath(self):
        from method import read
        file_name, file_type = QFileDialog.getOpenFileName(None, 'Open', './', 'All Files (*)')
        self.path.open_path = file_name
        self.input_file.setText(file_name)

        self.figure.clear()
        self.structure = read.poscar(self.path.open_path, types=poscar_is_vasp5(self.path.open_path))
        ax = self.figure.add_subplot(111, projection='3d')
        draw_crystal_in_ax(ax, self.structure)
        self.canvas.draw()

    def writepath(self):
        path = QFileDialog.getExistingDirectory(None, 'Save', './')
        self.path.save_path = path
        self.output_file.setText(path)

##########################################
class SupercellThread(QThread):
    trigger = pyqtSignal()

    def __init__(self, *args):
        self.open_path = args[0]
        self.write_path = args[1]
        self.num = args[2]
        self.tolerance = args[3]
        super(SupercellThread, self).__init__()

    def run(self):
        supercell_donet.exec(self.open_path, self.write_path, self.num, self.tolerance)

        self.trigger.emit()


class SupercellPage(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.figure = args[0]
        self.canvas = args[1]
        self.path = args[2]
        self.write_path = 'CONTCAR'
        self.num = 10
        self.tolerance = 1e-3

        self.factor_n = QLineEdit('10')
        self.factor_n.setFont(QFont('Arial'))
        self.coefficient_ep = QLineEdit('1e-3')
        self.coefficient_ep.setFont(QFont('Arial'))
        self.output_filename = QLineEdit('CONTACR')
        self.output_filename.setFont(QFont('Arial'))
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.status = QLabel('Ready.')
        self.run_btn = QPushButton('Run')

        self.timer = QTimer()

        self.initUI()

    def initUI(self):
        ins_box = QGroupBox('Instruction')
        ins_box.setFont(QFont('Arial'))
        instruction = QTextEdit()
        instruction.setPlainText('To expand the given primitive cell to the smallest supercell which as close to a '
                                 'cubic as possible. The structure of primitive cell is from CONTCAR.relax.vasp by '
                                 'default, or you can choose a POSCAR-modal vasp file as primitive cell from '
                                 'local. Algorithm detail refers from *Phys. Rev. B 91, 165206* and an improvement for '
                                 'the definition of deviation coefficient, where the epsilon is the difference between '
                                 'sqrt(3) and the quotient of the longest body diagonal line and the shortest side '
                                 'length of supercell.\n\n'
                                 'The \'maximum multiple factor N\' restricts the largest size of supercell, which '
                                 'should be smaller than N times of primitive cell.\n\n'
                                 'The \'smallest deviation coefficient epsilon0\' judges the similarity between '
                                 'supercell and cubic, when deviation coefficient of one supercell is smaller than '
                                 'epsilon0, this supercell is considered to be a good cubic as output and stop the loop'
                                 ' directly.\n')
        instruction.setReadOnly(True)
        instruction.setFont(QFont('Arial'))
        layout = QVBoxLayout()
        layout.addWidget(instruction)
        ins_box.setLayout(layout)

        para_box = QGroupBox('Parameters')
        para_box.setFont(QFont('Arial'))
        para_layout = QFormLayout()
        para_layout.addRow('Maximum multiple factor N:', self.factor_n)
        para_layout.addRow('Smallest deviation coefficient epsilon0:', self.coefficient_ep)
        para_layout.addRow('Name of output supercell:', self.output_filename)
        para_box.setLayout(para_layout)

        run_layout = QHBoxLayout()
        self.run_btn.setFont(QFont('Arial', 10, 50))

        self.run_btn.clicked.connect(self.run_method)
        self.timer.timeout.connect(self.time_count)

        progress_box = QGroupBox('status')
        progress_box.setFont(QFont('Arial'))
        progress = QGridLayout()
        progress.addWidget(self.status, 0, 0)
        progress.addWidget(self.bar, 0, 2, 1, 2)
        progress_box.setLayout(progress)

        run_layout.addStretch(1)
        run_layout.addWidget(self.run_btn)
        run_layout.addStretch(1)

        page = QVBoxLayout()
        page.addWidget(ins_box)
        page.addWidget(para_box)
        page.addWidget(progress_box)
        page.addLayout(run_layout)

        self.setLayout(page)

    def run_method(self):
        import os
        source = self.sender()
        if source.text() == 'Run':
            source.setText('Reset')
            self.status.setText('Calculating...')
            self.bar.setValue(0)
            filename = self.output_filename.text()
            if self.path.save_path == '':
                self.write_path = filename
            else:
                self.write_path = os.path.join(self.path.save_path, filename)
            if platform.system() == 'Windows':
                self.write_path = self.write_path.replace('\\', '/')
            self.num = int(self.factor_n.text())
            self.tolerance = float(self.coefficient_ep.text())

            self.timer.start(1000)
            self.work_thread = SupercellThread(self.path.open_path, self.write_path, self.num, self.tolerance)
            self.work_thread.start()
            self.work_thread.trigger.connect(self.time_stop)
        else:
            source.setText('Run')
            self.work_thread.terminate()
            self.work_thread.wait()
            self.status.setText('Ready')
            self.bar.setValue(0)
            self.timer.stop()

    def time_stop(self):
        from method import read
        self.bar.setValue(100)
        self.timer.stop()
        self.status.setText('Finished.')
        self.run_btn.setText('Run')

        self.structure = read.poscar(self.write_path, types=poscar_is_vasp5(self.write_path))
        self.figure.clear()
        ax = self.figure.add_subplot(111, projection='3d')
        draw_crystal_in_ax(ax, self.structure)
        self.canvas.draw()

    def time_count(self):
        with open('log', 'r') as file:
            count = file.readline()
        n = count.split('%')[0]
        self.bar.setValue(int(n))


class SubstitutionPage(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.figure = args[0]
        self.canvas = args[1]
        self.path = args[2]

        self.types = QLineEdit('None')
        self.types.setFont(QFont('Arial'))
        self.subs = QLineEdit('None')
        self.subs.setFont(QFont('Arial'))
        self.center = QLineEdit('[0.5, 0.5, 0.5]')
        self.center.setFont(QFont('Arial'))
        self.tolerance = QLineEdit('1e-3')
        self.tolerance.setFont(QFont('Arial'))
        self.symprec = QLineEdit('0.1')
        self.symprec.setFont(QFont('Arial'))

        self.initUI()

    def initUI(self):
        ins_box = QGroupBox('Instruction')
        ins_box.setFont(QFont('Arial'))
        instruction = QTextEdit()
        instruction.setPlainText('To yield possible single-point substitution or vacancy in given structure, '
                                 'which is from CONTCAR.relax.vasp by default, or you can choose a POSCAR-modal vasp '
                                 'file from local. Algorithm detail refers from *Computational Material Science '
                                 '130(2017)1-9*.\n\n'
                                 'The \'species of substituted atoms\' decides which kinds of element will be '
                                 'substituted in given crystal.\n'
                                 'The \'species of substitution\' decides atoms to replace original structure.\n'
                                 'The \'doped center\' will affect the position of substitution. In practically doping,'
                                 ' point-defect prefers to be made at the center of the host. Thus, it will choose the '
                                 'nearest position of center to make point-defect when center is *not* None.\n'
                                 'The \'tolerance\' judges how close of two atoms to treat them as equivalent atoms\n'
                                 'The \'symmetrical precision\' is the tolerance to give proper symmetrical operation '
                                 'matrix for structure.\n\n'
                                 'HINTS\n'
                                 'If you want to substitute more than one atomic specie in structure, you can input '
                                 'e.g. Si, Al. Please use \',\' to split them.\n'
                                 'If \'species of substituted atoms\' input None, all different kinds of species in '
                                 'structure will be doped.\n'
                                 'If \'species of substitution\' is None, it will create vacancy. Of course, \'species '
                                 'of substitution\' can also more than one atomic specie, please use \',\' to split '
                                 'them.\n'
                                 'The parameter of \'doped center\' *should* be fractional coordinates, i.e. if you '
                                 'want to make a point defect close to the center of host, please input [0.5, 0.5, 0.5]'
                                 '.\n'
                                 'The smaller of \'tolerance\' makes symmetrical requires harder, and thus gives more '
                                 '*un-equivalent* sites, when structure keeps unchanged.\n'
                                 'The smaller of \'symmetrical precision\' will give less allowable symmetrical '
                                 'operations because of the more strict symmetrical requires.')
        instruction.setReadOnly(True)
        instruction.setFont(QFont('Arial'))
        layout = QVBoxLayout()
        layout.addWidget(instruction)
        ins_box.setLayout(layout)

        para_box = QGroupBox('Parameters')
        para_box.setFont(QFont('Arial'))
        para_layout = QFormLayout()
        para_layout.addRow('Species of substituted atoms:', self.types)
        para_layout.addRow('Species of substitution:', self.subs)
        para_layout.addRow('Doped center:', self.center)
        para_layout.addRow('Tolerance:', self.tolerance)
        para_layout.addRow('Symmetrical precision:', self.symprec)
        para_box.setLayout(para_layout)

        run_layout = QHBoxLayout()
        run_btn = QPushButton('Run')
        run_btn.setFont(QFont('Arial', 10, 50))
        run_btn.clicked.connect(self.run_method)
        run_layout.addStretch(1)
        run_layout.addWidget(run_btn)
        run_layout.addStretch(1)

        page = QVBoxLayout()
        page.addWidget(ins_box)
        page.addWidget(para_box)
        page.addLayout(run_layout)

        self.setLayout(page)

    def run_method(self):
        from method import defects_sub_donet

        temp = self.types.text()
        if re.match('None', temp):
            types = None
        else:
            types = [i.strip() for i in temp.split(',')]
        temp = self.subs.text()
        if re.match('None', temp):
            subs = None
        else:
            subs = [i.strip() for i in temp.split(',')]
        temp = self.center.text()
        if re.match('None', temp):
            center = None
        else:
            center = temp.split('[')[1].split(']')[0].split(',')
            center = [float(x) for x in center]
        tolerance = float(self.tolerance.text())
        symprec = float(self.symprec.text())
        view_result = defects_sub_donet.exec(self.path.open_path, self.path.save_path,
                                             types, subs, center, tolerance, symprec)

        self.figure.clear()
        ax = self.figure.add_subplot(111, projection='3d')
        draw_crystal_in_ax(ax, view_result)
        self.canvas.draw()


class InterstitialPage(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.figure = args[0]
        self.canvas = args[1]
        self.path = args[2]

        self.insert = QLineEdit('X')
        self.insert.setFont(QFont('Arial'))
        self.center = QLineEdit('[0.5, 0.5, 0.5]')
        self.center.setFont(QFont('Arial'))
        self.position = QLineEdit('None')
        self.position.setFont(QFont('Arial'))
        self.tolerance = QLineEdit('1.0')
        self.tolerance.setFont(QFont('Arial'))
        self.symprec = QLineEdit('0.1')
        self.symprec.setFont(QFont('Arial'))
        self.vnrprec = QLineEdit('0.1')
        self.vnrprec.setFont(QFont('Arial'))
        self.n_shell = QLineEdit('3')
        self.n_shell.setFont(QFont('Arial'))

        self.initUI()

    def initUI(self):
        ins_box = QGroupBox('Instruction')
        ins_box.setFont(QFont('Arial'))
        instruction = QTextEdit()
        instruction.setPlainText('Yields interstitial structure when interstitial atom specie and position is known or '
                                 'to find candidate interstitial structure when interstitial sites is unknown. The '
                                 'structure is from CONTCAR.relax.vasp by default, or you can choose a POSCAR-modal '
                                 'vasp file from local. The method to find candidate interstitial is referred as '
                                 '*Computational Material Science 130(2017)1-9*.\n\n'
                                 'The \'insert element\' gives the name of single-interstitial atom.\n'
                                 'The \'doped center\' will affect the position of substitution. In practically doping,'
                                 ' point-defect prefers to be made at the center of the host. Thus, it will choose the '
                                 'nearest position of center to make point-defect when center is *not* None.\n'
                                 'If the \'interstitial position\' is know, it will create this doped structure '
                                 'directly.\n'
                                 'The \'tolerance\' judges how close of two atoms to treat them as equivalent atoms. '
                                 'Needed in two place:\n'
                                 '1. to find symmetrically inequivalent sites.\n'
                                 '2. to remove equivalent sites in candidate interstitial sites.\n'
                                 'The \'symmetrical precision\' is the tolerance to give proper symmetrical operation '
                                 'matrix for structure.\n'
                                 'The \'vonoroi precision\' decides the number of neighbors for given symmetrical '
                                 'inequivalent sites. This will impact the shape of vonoroi cell.\n'
                                 'The \'number of shell\' decides how many shell of neighbors are considered for given '
                                 'symmetrical inequivalent sites. This will also impact the shape of vonoroi cell.\n\n'
                                 'HINTS\n'
                                 'The \'insert element\' should be only one specie of atom, if you want to interstitial'
                                 ' different atoms, loop this program or replace element name in output POSCAR '
                                 'directly.\n'
                                 'The parameter of \'doped center\' *should* be fractional coordinates, i.e. if you '
                                 'want to make a point defect close to the center of host, please input [0.5, 0.5, 0.5]'
                                 '.\n'
                                 'The smaller of \'tolerance\' makes symmetrical requires harder, and thus gives more '
                                 '*un-equivalent* sites when structure keeps unchanged. Meanwhile, the smaller '
                                 'tolerance will give more *un-equivalent* sites of candidate interstitial. Thus, if '
                                 'the result of candidate interstitial is too many, choose a bigger tolerance, e.g. '
                                 'tolerance=2.0, is a good choice.\n'
                                 'The smaller of \'symmetrical precision\' will give less allowable symmetrical '
                                 'operations because of the more strict symmetrical requires.\n'
                                 'The smaller of \'vonoroi precision\' will give fewer neighbors of each shell because '
                                 'of the more strict distance requirement.\n'
                                 )
        instruction.setReadOnly(True)
        instruction.setFont(QFont('Arial', 10, 50))
        layout = QVBoxLayout()
        layout.addWidget(instruction)
        ins_box.setLayout(layout)

        para_box = QGroupBox('Parameters')
        para_box.setFont(QFont('Arial'))
        para_layout = QFormLayout()
        para_layout.addRow('Insert element:', self.insert)
        para_layout.addRow('Doped center:', self.center)
        para_layout.addRow('Interstitial position:', self.position)
        para_layout.addRow('Tolerance:', self.tolerance)
        para_layout.addRow('Symmetrical precision:', self.symprec)
        para_layout.addRow('Vonoroi precision:', self.vnrprec)
        para_layout.addRow('Number of shell:', self.n_shell)
        para_box.setLayout(para_layout)

        run_layout = QHBoxLayout()
        run_btn = QPushButton('Run')
        run_btn.setFont(QFont('Arial', 10, 50))
        run_btn.clicked.connect(self.run_method)
        run_layout.addStretch(1)
        run_layout.addWidget(run_btn)
        run_layout.addStretch(1)

        page = QVBoxLayout()
        page.addWidget(ins_box)
        page.addWidget(para_box)
        page.addLayout(run_layout)

        self.setLayout(page)

    def run_method(self):
        from method import defects_int_donet

        insert = self.insert.text()
        temp = self.center.text()
        if re.match('None', temp):
            center = None
        else:
            center = temp.split('[')[1].split(']')[0].split(',')
            center = [float(x) for x in center]
        temp = self.position.text()
        if re.match('None', temp):
            position = None
        else:
            position = temp.split('[')[1].split(']')[0].split(',')
            position = [float(x) for x in position]
        tolerance = float(self.tolerance.text())
        symprec = float(self.symprec.text())
        vnrprec = float(self.vnrprec.text())
        n_shell = int(self.n_shell.text())
        view_result = defects_int_donet.exec(self.path.open_path, self.path.save_path, insert, center,
                                             position, tolerance, symprec, vnrprec, n_shell)

        self.figure.clear()
        ax = self.figure.add_subplot(111, projection='3d')
        draw_crystal_in_ax(ax, view_result)
        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    text = 'F & Alkaline Earths'
    ex = ToolPage()
    sys.exit(app.exec_())

