#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'jingslaw'
__version__ = 1.0

import sys
import re
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from detailgui import DetailPage


def transfer_to_sql(text, species):
    temp = text.split('&')
    fuzzy = []
    elements = []
    for i in temp:
        i = i.strip()
        if re.match('Alkali Metals', i):
            fuzzy.append('AM')
        elif re.match('Alkaline', i):
            fuzzy.append('AE')
        elif re.match('Transition', i):
            fuzzy.append('TM')
        elif re.match('Lanthanides', i):
            fuzzy.append('La')
        elif re.match('Other', i):
            fuzzy.append('OM')
        elif re.match('Group 3A', i):
            fuzzy.append('3A')
        elif re.match('Group 4A', i):
            fuzzy.append('4A')
        elif re.match('Group 5A', i):
            fuzzy.append('5A')
        elif re.match('Chalcogens', i):
            fuzzy.append('Ch')
        elif re.match('Halogens', i):
            fuzzy.append('Ha')
        else:
            elements.append(i)
    sql = 'select ICSD_code, substance from item '
    text = ''
    n = 0
    for i in elements:
        if i == '':
            continue
        if n == 0:
            text = 'elements glob \'*{0}#*\' '.format(i)
            n = 1
        else:
            text += 'and elements glob \'*{0}#*\' '.format(i)
    text2 = ''
    m = 0
    for i in fuzzy:
        if m == 0:
            text2 = 'fuzzy glob \'*{0}*\' '.format(i)
            m = 1
        else:
            text2 += 'and fuzzy glob \'*{0}*\' '.format(i)
    text3 = ''
    if species is not None:
        text3 = 'species={0}'.format(species)
    flag = 0
    if text != '':
        sql += 'where ' + text
        flag = 1
    if text2 != '':
        if flag:
            sql += 'and ' + text2
        else:
            sql += 'where ' + text2
            flag = 1
    if text3 != '':
        if flag:
            sql += 'and ' + text3
        else:
            sql += 'where ' + text3
    return sql


def search_from_sql(sql):
    import sqlite3

    conn = sqlite3.connect('icsd.db')
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


class ResultPage(QDialog):
    def __init__(self, *args):
        super().__init__()
        crystal = args[0]
        self.n = args[1]
        self.total = args[2]
        species = args[3]
        sql = transfer_to_sql(crystal, species)
        self.result = search_from_sql(sql)

        self.flag = 0
        self.table = self.set_table(self.flag)
        self.windows = []

        self.initUI()

    def initUI(self):
        self.resize(1450, 620)
        self.setWindowTitle('Ab-crystallib')
        self.setWindowIcon(QIcon('ustclogo.jpg'))

        count = len(self.result)
        warning_label = QLabel('{0} possible results are found.'.format(count))
        if count > self.total:
            warning_label.setText('Only showing the first {0} of {1} possible results! '
                                  'You may wish to consider increasing the total result limit.'
                                  .format(self.total, count))
            warning_label.setStyleSheet('color: %s' % 'red')
        warning_label.setFont(QFont('Arial', 10, 50))

        page = QHBoxLayout()
        page.addStretch(1)
        page.addWidget(self.table)
        page.addStretch(1)

        backpg = QHBoxLayout()
        backpg.addStretch(1)
        backbtn = QPushButton('Reset Research')
        backbtn.clicked.connect(self.reset_research)
        backbtn.setFont(QFont('Arial', 15, 50))
        backbtn.setFixedSize(750, 50)
        backbtn.setStyleSheet("QPushButton { background-color : %s }" % "white")
        backpg.addWidget(backbtn)
        backpg.addStretch(1)

        previousbtn = QPushButton('Previous')
        previousbtn.setFixedSize(100, 25)
        previousbtn.setFont(QFont('Arial', 10, 50))
        previousbtn.clicked.connect(self.previous_page)
        nextbtn = QPushButton('Next')
        nextbtn.setFixedSize(100, 25)
        nextbtn.setFont(QFont('Arial', 10, 50))
        nextbtn.clicked.connect(self.next_page)

        change = QHBoxLayout()
        change.addWidget(previousbtn)
        change.addStretch(1)
        change.addWidget(nextbtn)

        main_page = QVBoxLayout()
        main_page.setContentsMargins(20, 20, 20, 20)
        main_page.addLayout(backpg)
        main_page.addWidget(warning_label)
        main_page.addWidget(self.table)
        main_page.addLayout(change)

        self.setLayout(main_page)
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def set_table(self, flag=0):
        table = QTableWidget()
        table.setColumnCount(3)
        table.setRowCount(self.n)
        table.setHorizontalHeaderLabels(['ICSD Collection Code', 'Substance', 'Data'])
        first = flag * self.n
        last = (flag + 1) * self.n
        table.setVerticalHeaderLabels([str(x) for x in range(first + 1, last + 1)])

        brush = QBrush(QColor('lightskyblue'))
        brush.setStyle(Qt.SolidPattern)

        for i in range(self.n):
            if i + first >= len(self.result):
                break
            for j in range(3):
                if j != 2:
                    table.setItem(i, j, QTableWidgetItem(str(self.result[i+first][j])))
                else:
                    table.setItem(i, j, QTableWidgetItem())
                    viewbtn = QPushButton('View')
                    viewbtn.code = self.result[i+first][0]
                    viewbtn.clicked.connect(self.view_detail)
                    viewbtn.setFixedSize(100, 25)
                    viewpg = QHBoxLayout()
                    viewpg.addStretch(1)
                    viewpg.addWidget(viewbtn)
                    viewpg.addStretch(1)
                    viewpg.setContentsMargins(0, 0, 0, 0)
                    widget = QWidget()
                    widget.setLayout(viewpg)
                    table.setCellWidget(i, j, widget)
                item = table.item(i, j)
                item.setTextAlignment(Qt.AlignCenter)
                if i % 2 == 0:
                    item.setBackground(brush)

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        return table

    def next_page(self):
        flag = self.flag + 1
        first = flag * self.n
        last = (flag + 1) * self.n
        if first + 1 > min(len(self.result), self.total):
            return
        self.table.setVerticalHeaderLabels([str(x) for x in range(first + 1, last + 1)])

        brush = QBrush(QColor('lightskyblue'))
        brush.setStyle(Qt.SolidPattern)

        for i in range(self.table.rowCount()):
            if i + first >= len(self.result):
                for j in range(3):
                    if j != 2:
                        self.table.setItem(i, j, QTableWidgetItem())
                        item = self.table.item(i, j)
                        if i % 2 == 0:
                            item.setBackground(brush)
                    else:
                        self.table.removeCellWidget(i, j)
            else:
                for j in range(3):
                    if j != 2:
                        self.table.setItem(i, j, QTableWidgetItem(str(self.result[i + first][j])))
                    else:
                        self.table.setItem(i, j, QTableWidgetItem())
                        viewbtn = QPushButton('View')
                        viewbtn.code = self.result[i + first][0]
                        viewbtn.clicked.connect(self.view_detail)
                        viewbtn.setFixedSize(100, 25)
                        viewpg = QHBoxLayout()
                        viewpg.addStretch(1)
                        viewpg.addWidget(viewbtn)
                        viewpg.addStretch(1)
                        viewpg.setContentsMargins(0, 0, 0, 0)
                        widget = QWidget()
                        widget.setLayout(viewpg)
                        self.table.setCellWidget(i, j, widget)
                    item = self.table.item(i, j)
                    item.setTextAlignment(Qt.AlignCenter)
                    if i % 2 == 0:
                        item.setBackground(brush)
        self.flag += 1

    def previous_page(self):
        flag = self.flag - 1
        if flag < 0:
            return
        first = flag * self.n
        last = (flag + 1) * self.n
        self.table.setVerticalHeaderLabels([str(x) for x in range(first + 1, last + 1)])

        brush = QBrush(QColor('lightskyblue'))
        brush.setStyle(Qt.SolidPattern)

        for i in range(self.table.rowCount()):
            for j in range(3):
                if j != 2:
                    self.table.setItem(i, j, QTableWidgetItem(str(self.result[i + first][j])))
                else:
                    self.table.setItem(i, j, QTableWidgetItem())
                    viewbtn = QPushButton('View')
                    viewbtn.code = self.result[i + first][0]
                    viewbtn.clicked.connect(self.view_detail)
                    viewbtn.setFixedSize(100, 25)
                    viewpg = QHBoxLayout()
                    viewpg.addStretch(1)
                    viewpg.addWidget(viewbtn)
                    viewpg.addStretch(1)
                    viewpg.setContentsMargins(0, 0, 0, 0)
                    widget = QWidget()
                    widget.setLayout(viewpg)
                    self.table.setCellWidget(i, j, widget)
                item = self.table.item(i, j)
                item.setTextAlignment(Qt.AlignCenter)
                if i % 2 == 0:
                    item.setBackground(brush)
        self.flag -= 1

    def reset_research(self):
        self.close()

    def view_detail(self):
        source = self.sender()
        detail = DetailPage(source.code)
        self.windows.append(detail)
        detail.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    text = 'F & Alkaline Earths'
    ex = ResultPage(text, 40, 1000, None)
    sys.exit(app.exec_())
