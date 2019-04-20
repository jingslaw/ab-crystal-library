#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = 'jingslaw'
__version__ = 1.0

import sys
import json
import re
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from toolgui import ToolPage


def get_the_detail(icsd_code):
    import sqlite3

    conn = sqlite3.connect('icsd.db')
    cursor = conn.cursor()
    sql = 'select * from item where ICSD_code = {0}'.format(icsd_code)
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result[0]


class LinkLabel(QLabel):
    clicked = pyqtSignal()

    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.clicked.emit()


class DetailPage(QWidget):
    def __init__(self, *args):
        super().__init__()
        icsd_code = args[0]
        self.result = get_the_detail(icsd_code)
        self.raw = ''
        self.windows = []

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Ab-crystallib')
        self.setWindowIcon(QIcon('ustclogo.jpg'))
        self.resize(800, 800)

        cal_label = QLabel('CALCULATION DETAIL')
        cal_label.setFont(QFont('Arial', 20, 50))
        calculation = json.loads(self.result[5])
        cal_layout = QGridLayout()
        for i in range(len(calculation)):
            temp = QVBoxLayout()
            item = calculation[i]
            title = QLabel(item['title'] + ':')
            title.setFont(QFont('Arial', 10, 50))
            title.setStyleSheet("QLabel { background-color : %s }" % "white")
            title.setContentsMargins(5, 5, 5, 5)
            value = QLabel(item['value'])
            value.setFont(QFont('Arial', 12, 70))
            value.setContentsMargins(5, 5, 5, 5)
            value.setStyleSheet("QLabel { background-color : %s }" % "white")
            temp.addWidget(title)
            temp.addWidget(value)
            temp.setContentsMargins(5, 5, 5, 5)
            position = (i // 3, i % 3)
            cal_layout.addItem(temp, *position)

        str_label = QLabel('RELAXED STRUCTURE')
        str_label.setFont(QFont('Arial', 20, 50))
        structure = json.loads(self.result[6])
        sub_label_1 = QLabel('Real Space Lattice')
        sub_label_1.setFont(QFont('Arial', 10, 50))
        tag = 0
        str_layout_1 = QGridLayout()
        for i in range(len(structure)):
            temp = QVBoxLayout()
            item = structure[i]
            if re.match('Space', item['title']):
                break
            title = QLabel(item['title'])
            title.setFont(QFont('Arial', 10, 50))
            title.setStyleSheet("QLabel { background-color : %s }" % "white")
            title.setContentsMargins(5, 5, 5, 5)
            if re.match('Lattice', item['title']):
                text = item['value']
                text = re.sub('&deg', '°', text)
                value = QLabel(text)
            else:
                value = QLabel(item['value'])
            value.setFont(QFont('Arial', 12, 70))
            value.setContentsMargins(5, 5, 5, 5)
            value.setStyleSheet("QLabel { background-color : %s }" % "white")
            temp.addWidget(title)
            temp.addWidget(value)
            temp.setContentsMargins(5, 5, 5, 5)
            position = (i // 3, i % 3)
            str_layout_1.addItem(temp, *position)
            tag = i + 1

        sub_label_2 = QLabel('Bravais Lattice of the Crystal')
        sub_label_2.setFont(QFont('Arial', 10, 50))
        str_layout_2 = QGridLayout()
        j = 0
        for i in range(tag, len(structure)):
            temp = QVBoxLayout()
            item = structure[i]
            if re.match('Crystal', item['title']):
                break
            title = QLabel(item['title'])
            title.setFont(QFont('Arial', 10, 50))
            title.setStyleSheet("QLabel { background-color : %s }" % "white")
            title.setContentsMargins(5, 5, 5, 5)
            value = QLabel(item['value'])
            value.setFont(QFont('Arial', 12, 70))
            value.setContentsMargins(5, 5, 5, 5)
            value.setStyleSheet("QLabel { background-color : %s }" % "white")
            temp.addWidget(title)
            temp.addWidget(value)
            temp.setContentsMargins(5, 5, 5, 5)
            position = (j // 3, j % 3)
            str_layout_2.addItem(temp, *position)
            tag = i + 1
            j += 1

        sub_label_3 = QLabel('Point Group of the Crystal')
        sub_label_3.setFont(QFont('Arial', 10, 50))
        str_layout_3 = QGridLayout()
        j = 0
        for i in range(tag, len(structure)):
            temp = QVBoxLayout()
            item = structure[i]
            if re.match('Bravais', item['title']):
                break
            title = QLabel(item['title'])
            title.setFont(QFont('Arial', 10, 50))
            title.setStyleSheet("QLabel { background-color : %s }" % "white")
            title.setContentsMargins(5, 5, 5, 5)
            value = QLabel(item['value'])
            value.setFont(QFont('Arial', 12, 70))
            value.setContentsMargins(5, 5, 5, 5)
            value.setStyleSheet("QLabel { background-color : %s }" % "white")
            temp.addWidget(title)
            temp.addWidget(value)
            temp.setContentsMargins(5, 5, 5, 5)
            position = (j // 3, j % 3)
            str_layout_3.addItem(temp, *position)
            tag = i + 1
            j += 1

        sub_label_4 = QLabel('Bravias Lattice of the Lattice')
        sub_label_4.setFont(QFont('Arial', 10, 50))
        str_layout_4 = QGridLayout()
        j = 0
        for i in range(tag, len(structure)):
            temp = QVBoxLayout()
            item = structure[i]
            if re.match('Superlattice', item['title']):
                break
            title = QLabel(item['title'])
            title.setFont(QFont('Arial', 10, 50))
            title.setStyleSheet("QLabel { background-color : %s }" % "white")
            title.setContentsMargins(5, 5, 5, 5)
            value = QLabel(item['value'])
            value.setFont(QFont('Arial', 12, 70))
            value.setContentsMargins(5, 5, 5, 5)
            value.setStyleSheet("QLabel { background-color : %s }" % "white")
            temp.addWidget(title)
            temp.addWidget(value)
            temp.setContentsMargins(5, 5, 5, 5)
            position = (j // 3, j % 3)
            str_layout_4.addItem(temp, *position)
            tag = i + 1
            j += 1

        sub_label_5 = QLabel('Superlattice')
        sub_label_5.setFont(QFont('Arial', 10, 50))
        str_layout_5 = QGridLayout()
        j = 0
        for i in range(tag, len(structure)):
            temp = QVBoxLayout()
            item = structure[i]
            if re.match('Reciprocal', item['title']):
                break
            title = QLabel(item['title'])
            title.setFont(QFont('Arial', 10, 50))
            title.setStyleSheet("QLabel { background-color : %s }" % "white")
            title.setContentsMargins(5, 5, 5, 5)
            value = QLabel(item['value'])
            value.setFont(QFont('Arial', 12, 70))
            value.setContentsMargins(5, 5, 5, 5)
            value.setStyleSheet("QLabel { background-color : %s }" % "white")
            temp.addWidget(title)
            temp.addWidget(value)
            temp.setContentsMargins(5, 5, 5, 5)
            position = (j // 3, j % 3)
            str_layout_5.addItem(temp, *position)
            tag = i + 1
            j += 1

        sub_label_6 = QLabel('Reciprocal Space Lattice')
        sub_label_6.setFont(QFont('Arial', 10, 50))
        str_layout_6 = QGridLayout()
        j = 0
        for i in range(tag, len(structure)):
            temp = QVBoxLayout()
            item = structure[i]
            title = QLabel(item['title'])
            title.setFont(QFont('Arial', 10, 50))
            title.setStyleSheet("QLabel { background-color : %s }" % "white")
            title.setContentsMargins(5, 5, 5, 5)
            value = QLabel(item['value'])
            value.setFont(QFont('Arial', 12, 70))
            value.setContentsMargins(5, 5, 5, 5)
            value.setStyleSheet("QLabel { background-color : %s }" % "white")
            temp.addWidget(title)
            temp.addWidget(value)
            temp.setContentsMargins(5, 5, 5, 5)
            position = (j // 3, j % 3)
            str_layout_6.addItem(temp, *position)
            j += 1

        thermo_label = QLabel('THERMODYNAMIC PROPERTIES')
        thermo_label.setFont(QFont('Arial', 20, 50))
        thermodynamic = json.loads(self.result[7])
        thermo_layout = QGridLayout()
        for i in range(len(thermodynamic)):
            temp = QVBoxLayout()
            item = thermodynamic[i]
            title = QLabel(item['title'])
            title.setFont(QFont('Arial', 10, 50))
            title.setStyleSheet("QLabel { background-color : %s }" % "white")
            title.setContentsMargins(5, 5, 5, 5)
            value = QLabel(item['value'])
            value.setFont(QFont('Arial', 12, 70))
            value.setContentsMargins(5, 5, 5, 5)
            value.setStyleSheet("QLabel { background-color : %s }" % "white")
            temp.addWidget(title)
            temp.addWidget(value)
            temp.setContentsMargins(5, 5, 5, 5)
            position = (i // 3, i % 3)
            thermo_layout.addItem(temp, *position)

        elec_label = QLabel('ELECTRONIC PROPERTIES')
        elec_label.setFont(QFont('Arial', 20, 50))
        electronic = json.loads(self.result[8])
        elec_layout = QGridLayout()
        for i in range(len(electronic)):
            temp = QVBoxLayout()
            item = electronic[i]
            title = QLabel(item['title'])
            title.setFont(QFont('Arial', 10, 50))
            title.setStyleSheet("QLabel { background-color : %s }" % "white")
            title.setContentsMargins(5, 5, 5, 5)
            value = QLabel(item['value'])
            value.setFont(QFont('Arial', 12, 70))
            value.setContentsMargins(5, 5, 5, 5)
            value.setStyleSheet("QLabel { background-color : %s }" % "white")
            temp.addWidget(title)
            temp.addWidget(value)
            temp.setContentsMargins(5, 5, 5, 5)
            position = (i // 3, i % 3)
            elec_layout.addItem(temp, *position)

        file_label = QLabel('DOWNLOAD FILES')
        file_label.setFont(QFont('Arial', 20, 50))
        files = json.loads(self.result[9])
        file_layout = QGridLayout()
        for i in range(len(files)):
            temp = QVBoxLayout()
            item = files[i]
            file_type = QLabel(item['type'] + ':')
            file_type.setFont(QFont('Arial', 10, 50))
            file_type.setStyleSheet("QLabel { background-color : %s }" % "white")
            file_type.setContentsMargins(5, 5, 5, 5)
            name = LinkLabel("<a href='#'>{0}</a>".format(item['name']))
            name.setOpenExternalLinks(True)
            name.setFont(QFont('Arial', 12, 70))
            name.setStyleSheet("QLabel { background-color : %s }" % "white")
            name.setContentsMargins(5, 5, 5, 5)
            name.content = item['content']
            name.clicked.connect(self.link_clicked)
            temp.addWidget(file_type)
            temp.addWidget(name)
            temp.setContentsMargins(5, 5, 5, 5)
            file_layout.addItem(temp, i, 0, 1, 3)

        self.raw = files[0]['content']
        toolpg = QHBoxLayout()
        toolbtn = QPushButton('Tools')
        toolbtn.setFont(QFont('Arial', 10, 50))
        toolbtn.setStyleSheet("QPushButton { background-color : %s }" % "white")
        toolbtn.clicked.connect(self.getmethod)
        toolpg.addStretch(1)
        toolpg.addWidget(toolbtn)

        page = QVBoxLayout()
        page.addLayout(toolpg)
        page.addWidget(cal_label)
        page.addLayout(cal_layout)
        page.addWidget(str_label)
        page.addWidget(sub_label_1)
        page.addLayout(str_layout_1)
        page.addWidget(sub_label_2)
        page.addLayout(str_layout_2)
        page.addWidget(sub_label_3)
        page.addLayout(str_layout_3)
        page.addWidget(sub_label_4)
        page.addLayout(str_layout_4)
        page.addWidget(sub_label_5)
        page.addLayout(str_layout_5)
        page.addWidget(sub_label_6)
        page.addLayout(str_layout_6)
        page.addWidget(thermo_label)
        page.addLayout(thermo_layout)
        page.addWidget(elec_label)
        page.addLayout(elec_layout)
        page.addWidget(file_label)
        page.addLayout(file_layout)

        w = QWidget()
        w.setLayout(page)
        scroll = QScrollArea()
        scroll.setWidget(w)
        scroll.setMinimumSize(800, 800)
        vbox = QVBoxLayout()
        vbox.addWidget(scroll)
        self.setLayout(vbox)
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def link_clicked(self):
        source = self.sender()
        content = source.content
        filename, ok = QFileDialog.getSaveFileName(None, 'Save As', './', "All Files (*)")
        if ok:
            with open(filename, 'w') as f:
                f.write(content)

    def getmethod(self):
        tool = ToolPage(self.raw)
        self.windows.append(tool)
        tool.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    text = 'F & Alkaline Earths'
    ex = DetailPage(52754)
    sys.exit(app.exec_())
