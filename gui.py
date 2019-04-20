#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'jingslaw'
__version__ = 1.0

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from resultgui import ResultPage


class MainPage(QWidget):
    def __init__(self):
        super().__init__()
        self.fuzzy = {'Alkali Metals': ['AM', 'dodgerblue'], 'Alkaline Earths': ['AE', 'cyan'],
                      'Transition Metals': ['TM', 'chartreuse'], 'Lanthanides': ['La', 'pink'],
                      'Other Metals': ['OM', 'lightgreen'], 'Group 3A': ['3A', 'yellow'], 'Group 4A': ['4A', 'gold'],
                      'Group 5A': ['5A', 'orange'], 'Chalcogens': ['Ch', 'orangered'], 'Halogens': ['Ha', 'red']}
        self.omtag = False
        self.searchline = QLineEdit()
        self.periodic_table = QGridLayout()
        self.periodic_table.setContentsMargins(20, 20, 20, 20)
        names = ['H', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'He',
                 'Li', 'Be', '', '', '', '', '', '', '', '', '', '', 'B', 'C', 'N', 'O', 'F', 'Ne',
                 'Na', 'Mg', '', '', '', '', '', '', '', '', '', '', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar',
                 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br',
                 'Kr',
                 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I',
                 'Xe',
                 'Cs', 'Ba', '', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', '', '', '',
                 '', '', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu']
        groups = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
                  'AM', 'AE', '', '', '', '', '', '', '', '', '', '', '3A', '4A', '5A', 'Ch', 'Ha', '',
                  'AM', 'AE', '', '', '', '', '', '', '', '', '', '', 'OM&3A', '4A', '5A', 'Ch', 'Ha', '',
                  'AM', 'AE', 'TM', 'TM', 'TM', 'TM', 'TM', 'TM', 'TM', 'TM', 'TM', 'TM', 'OM&3A', 'OM&4A', '5A', 'Ch',
                  'Ha', '',
                  'AM', 'AE', 'TM', 'TM', 'TM', 'TM', 'TM', 'TM', 'TM', 'TM', 'TM', 'TM', 'OM&3A', 'OM&4A', 'OM&5A',
                  'Ch', 'Ha', '',
                  'AM', 'AE', '', 'TM', 'TM', 'TM', 'TM', 'TM', 'TM', 'TM', 'TM', 'TM', 'OM&3A', 'OM&4A', 'OM&5A', '',
                  '', '',
                  '', '', 'La', 'La', 'La', 'La', 'La', 'La', 'La', 'La', 'La', 'La', 'La', 'La', 'La', 'La', 'La']
        positions = [(i, j) for i in range(7) for j in range(18)]
        for position, name, gname in zip(positions, names, groups):
            if name == '':
                continue
            button = QPushButton(name)
            button.setFont(QFont('Arial', 10, 80))
            button.setCheckable(True)
            button.gname = gname
            button.clicked[bool].connect(self.setSearch)
            self.periodic_table.addWidget(button, *position)
        self.periodic_table.setSpacing(0)

        self.n = QLineEdit('40')
        self.total = QLineEdit('1000')
        self.species = QLineEdit()

        self.initUI()

    def initUI(self):
        self.resize(1450, 620)
        self.setWindowTitle('Ab-crystallib')
        self.setWindowIcon(QIcon('ustclogo.jpg'))

        index = QHBoxLayout()
        main_page = QVBoxLayout()
        main_page.setContentsMargins(20, 20, 20, 20)

        srchnm = QLabel('Ab-crystallib')
        srchnm.setFont(QFont('Arial', 40, 75))
        title = QHBoxLayout()
        title.addStretch(1)
        title.addWidget(srchnm)
        title.addStretch(1)

        search = QHBoxLayout()
        searchbutton = QPushButton('Search', self)
        searchbutton.setFont(QFont('Arial', 15, 50))
        searchbutton.clicked.connect(self.doSearch)

        search.addWidget(self.searchline)
        search.addWidget(searchbutton)
        self.searchline.setFont(QFont('Arial', 15, 50))
        search.setContentsMargins(20, 20, 20, 20)

        extra_require = QHBoxLayout()
        extra_require.addStretch(1)
        extra_require.addWidget(QLabel('Results Per Page:'))
        extra_require.addWidget(self.n)
        extra_require.addStretch(1)
        extra_require.addWidget(QLabel('Total # of Results:'))
        extra_require.addWidget(self.total)
        extra_require.addStretch(1)
        extra_require.addWidget(QLabel('# of Species:'))
        extra_require.addWidget(self.species)
        extra_require.addStretch(1)
        extra_require.setContentsMargins(20, 20, 20, 20)
        extra = QGroupBox('Advanced')
        extra.setFont(QFont('Arial'))
        extra.setLayout(extra_require)

        extra_group = QHBoxLayout()
        group = QGridLayout()
        names = ['Alkali Metals', 'Alkaline Earths', 'Transition Metals', 'Lanthanides', 'Other Metals',
                 'Group 3A', 'Group 4A', 'Group 5A', 'Chalcogens', 'Halogens']
        positions = [(i, j) for i in range(2) for j in range(5)]
        for position, name in zip(positions, names):
            if name == '':
                continue
            button = QPushButton(name)
            button.setCheckable(True)
            button.clicked[bool].connect(self.setSearch)
            button.clicked[bool].connect(self.setColor)
            button.backgroundRole()
            group.addWidget(button, *position)
        extra_group.addStretch(1)
        extra_group.addLayout(group)
        extra_group.addStretch(1)
        extra_group.setContentsMargins(20, 20, 20, 20)
        fuzzy = QGroupBox('Fuzzy')
        fuzzy.setFont(QFont('Arial'))
        fuzzy.setLayout(extra_group)

        main_page.addLayout(title)
        main_page.addLayout(search)
        main_page.addLayout(self.periodic_table)
        main_page.addWidget(extra)
        main_page.addWidget(fuzzy)
        main_page.addStretch(1)

        index.addStretch(1)
        index.addLayout(main_page)
        index.addStretch(1)
        self.setLayout(index)

        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', "Do you want to quit?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def doSearch(self):
        text = self.searchline.text()
        if text is '':
            QMessageBox.information(self, 'Warning', 'Search line can not be None!')
            return
        n = int(self.n.text())
        total = int(self.total.text())
        if n > total:
            QMessageBox.information(self, 'Warning', 'Result per page should be smaller '
                                                     'than the number of total result!')
            return
        if self.species.text() is '':
            species = None
        else:
            species = int(self.species.text())
        result = ResultPage(text, n, total, species)
        self.hide()
        result.exec_()
        self.show()

    def setSearch(self, pressed):
        source = self.sender()
        if pressed:
            if len(self.searchline.text()) > 0:
                text = self.searchline.text() + ' & ' + source.text()
            else:
                text = source.text()
            self.searchline.setText(text)
        else:
            text = ''
            if len(self.searchline.text()) > 0:
                elements = self.searchline.text().split('&')
                for element in elements:
                    element = element.strip()
                    if element != source.text():
                        if len(text) > 0:
                            text = text + ' & ' + element
                        else:
                            text = element
                self.searchline.setText(text)

    def setColor(self, pressed):
        source = self.sender()
        text = source.text()
        if pressed:
            if text == 'Other Metals':
                self.omtag = True
            for i in range(self.periodic_table.count()):
                button = self.periodic_table.itemAt(i).widget()
                if len(button.gname.split('&')) > 1:
                    gname1 = button.gname.split('&')[0]
                    gname2 = button.gname.split('&')[1]
                    if gname1 == self.fuzzy[text][0]:
                        button.setStyleSheet("QWidget { background-color: %s }" % self.fuzzy[text][1])
                    elif gname2 == self.fuzzy[text][0]:
                        button.setStyleSheet("QWidget { background-color: %s }" % self.fuzzy[text][1])
                elif button.gname == self.fuzzy[text][0]:
                    button.setStyleSheet("QWidget { background-color: %s }" % self.fuzzy[text][1])
        else:
            for i in range(self.periodic_table.count()):
                button = self.periodic_table.itemAt(i).widget()
                if len(button.gname.split('&')) > 1:
                    gname1 = button.gname.split('&')[0]
                    gname2 = button.gname.split('&')[1]
                    if gname1 == self.fuzzy[text][0]:
                        button.setStyleSheet("QWidget { background-color: %s }" % 'light gray')
                        self.omtag = False
                    elif gname2 == self.fuzzy[text][0] and self.omtag is False:
                        button.setStyleSheet("QWidget { background-color: %s }" % 'light gray')
                elif button.gname == self.fuzzy[text][0]:
                    button.setStyleSheet("QWidget { background-color: %s }" % 'light gray')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainPage()
    sys.exit(app.exec_())

