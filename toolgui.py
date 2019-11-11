#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'jingslaw'
__version__ = 1.2

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
from method import defects_int_donet


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
        self.start_tag = args[3]
        self.stop_tag = args[4]
        super(SupercellThread, self).__init__()

    def run(self):
        supercell_donet.exec(self.open_path, self.write_path, self.num, self.start_tag, self.stop_tag)

        self.trigger.emit()


class SupercellPage(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.figure = args[0]
        self.canvas = args[1]
        self.path = args[2]

        self.write_path = 'CONTCAR'
        self.num = 10
        self.start = 1
        self.stop = None

        self.factor_n = QLineEdit('10')
        self.factor_n.setFont(QFont('Arial'))
        self.start_tag = QLineEdit('1')
        self.start_tag.setFont(QFont('Arial'))
        self.stop_tag = QLineEdit('None')
        self.stop_tag.setFont(QFont('Arial'))
        self.output_filename = QLineEdit('CONTCAR')
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
        instruction.setPlainText('To transform a non-cubic primitive to a supercell as close to cube as possible. '
                                 'A geometric properties is used to judge whether a parallel hexahedron is close to a '
                                 'cubic that, in given volume of parallel hexahedron, cubic has the smallest surface '
                                 'area.\n\n'

                                 'The \'maximum multiple factor N\' decides the loop time of calculation. The elements '
                                 'in transform matrix are proportional to this parameter. The default value equals to '
                                 'the largest multiply times of supercell extended by primitive cell. However, '
                                 'sometimes this value causes considerable calculation, in this time, a small '
                                 '\'maximum multiple factor N\'\n\n and a small extend range is a good choice.\n\n'
                                 'The \'start\' and \'stop\' decide the range of expand times for supercell. If '
                                 '\'stop\' is *None*, the default value equals to \'maximum multiple factor N\'\n')
        instruction.setReadOnly(True)
        instruction.setFont(QFont('Arial'))
        layout = QVBoxLayout()
        layout.addWidget(instruction)
        ins_box.setLayout(layout)

        para_box = QGroupBox('Parameters')
        para_box.setFont(QFont('Arial'))
        para_layout = QFormLayout()
        para_layout.addRow('Maximum multiple factor N:', self.factor_n)
        para_layout.addRow('Start:', self.start_tag)
        para_layout.addRow('Stop:', self.stop_tag)
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
            self.start = int(self.start_tag.text())
            if self.stop_tag.text() != 'None':
                self.stop = int(self.stop_tag.text())
            else:
                self.stop = None

            self.timer.start(1000)
            self.work_thread = SupercellThread(self.path.open_path, self.write_path, self.num, self.start, self.stop)
            self.work_thread.start()
            self.work_thread.trigger.connect(self.time_stop)
        else:
            source.setText('Run')
            self.work_thread.terminate()
            self.work_thread.wait()
            self.status.setText('Ready')
            self.bar.setValue(0)
            self.timer.stop()

            with open('interstitial log.txt', 'w') as file:
                file.writelines('0%')

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

        with open('interstitial log.txt', 'w') as file:
            file.writelines('0%')

    def time_count(self):
        with open('log.txt', 'r') as file:
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
        self.tolerance = QLineEdit('0.01')
        self.tolerance.setFont(QFont('Arial'))

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
                                 'The \'tolerance\' judges how close of two atoms to treat them as equivalent atoms\n\n'

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
                                 '*un-equivalent* sites, when structure keeps unchanged.\n')
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
        view_result = defects_sub_donet.exec(self.path.open_path, self.path.save_path,
                                             types, subs, center, tolerance)

        self.figure.clear()
        ax = self.figure.add_subplot(111, projection='3d')
        draw_crystal_in_ax(ax, view_result)
        self.canvas.draw()


##########################################
class InterstitialThread(QThread):
    trigger = pyqtSignal()

    def __init__(self, *args):
        self.open_path = args[0]
        self.write_path = args[1]
        self.insert = args[2]
        self.position = args[3]
        self.center = args[4]
        self.tolerance = args[5]
        super(InterstitialThread, self).__init__()

    def run(self):
        self.view_structure = defects_int_donet.exec(self.open_path, self.write_path,
                                                     self.insert, self.center, self.position, self.tolerance)
        self.trigger.emit()


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
        self.tolerance = QLineEdit('0.01')
        self.tolerance.setFont(QFont('Arial'))

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
                                 'tolerance=0.1, is a good choice.\n'
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
        source = self.sender()
        if source.text() == 'Run':
            source.setText('Reset')
            self.status.setText('Calculating...')
            self.bar.setValue(0)
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

            self.timer.start(1000)
            self.work_thread = InterstitialThread(self.path.open_path, self.path.save_path,
                                                  insert, position, center, tolerance)
            self.work_thread.start()
            self.work_thread.trigger.connect(self.time_stop)
        else:
            source.setText('Run')
            self.work_thread.terminate()
            self.work_thread.wait()
            self.status.setText('Ready')
            self.bar.setValue(0)
            self.timer.stop()

            with open('interstitial log.txt', 'w') as file:
                file.writelines('0%')

    def time_stop(self):
        self.bar.setValue(100)
        self.timer.stop()
        self.status.setText('Finished.')
        self.run_btn.setText('Run')

        self.figure.clear()
        ax = self.figure.add_subplot(111, projection='3d')
        draw_crystal_in_ax(ax, self.work_thread.view_structure)
        self.canvas.draw()

        with open('interstitial log.txt', 'w') as file:
            file.writelines('0%')

    def time_count(self):
        with open('interstitial log.txt', 'r') as file:
            count = file.readline()
        n = count.split('%')[0]
        self.bar.setValue(int(n))
