import sys
import random
import os
from functools import partial

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

from vcalc_ui import Ui_MainWindow


class BinLayout(QtWidgets.QGridLayout):
    def __init__(self, parent):
        super().__init__()
        self.mainWindow = parent
        self.bin_buttons = []
        self.layouts = []
        self.exponents = {}
        self.val = 0
        self.make_bins()

    def make_bins(self):
        row = 0
        col = 0
        for i in range(63, -1, -1):
            button = QtWidgets.QPushButton(self.mainWindow.centralwidget)
            button.setObjectName(f"binButton{i}")
            self.set_false(button)

            button.clicked.connect(partial(self.button_clicked, i))

            button.setFixedWidth(30)
            button.setFixedHeight(30)

            label = QtWidgets.QLabel(f"{i}")
            label.setObjectName(f"binLabel{i}")
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet("color: rgb(128, 128, 128);")

            label.setFixedWidth(30)
            label.setFixedHeight(10)

            vBinLayout = QtWidgets.QVBoxLayout()
            vBinLayout.setObjectName(f"vBinLayout{i}")

            vBinLayout.addWidget(button)
            vBinLayout.addWidget(label)

            self.layouts.append(label)
            self.bin_buttons.append(button)
            self.addLayout(vBinLayout, row, col, 1, 1)

            col = (col + 1) % 8
            if col == 0:
                row += 1

        self.layouts.reverse()
        self.bin_buttons.reverse()

    def show32(self, en):
        if en:
            for i in range(32):
                self.layouts[i].setVisible(True)
                self.bin_buttons[i].setVisible(True)

            for i in range(32, 64):
                self.layouts[i].setVisible(False)
                self.bin_buttons[i].setVisible(False)

    def show64(self, en):
        if en:
            for i in range(64):
                self.layouts[i].setVisible(True)
                self.bin_buttons[i].setVisible(True)

    def add_exp(self, i):
        self.exponents[i] = 1

    def remove_exp(self, i):
        if i in self.exponents:
            del self.exponents[i]

    def update_val(self):
        val = 0
        for bit in list(self.exponents.keys()):
            val += 2 ** bit
        self.val = val
        self.mainWindow.update_vals(val)

    def set_value(self, val):
        try:
            if val >= 0 and isinstance(val, int):
                bin_str = f"{val:b}"
                self.val = val
                self.clear()
                self.exponents.clear()

                j = 0
                for i in range(len(bin_str) - 1, -1, -1):
                    if bin_str[j] == "1":
                        self.set_button(i, 1)
                    else:
                        self.set_button(i, 0)
                    j += 1
        except:
            print(f"Cannot set bin value: {val}")

    def clear(self):
        while len(self.exponents) > 0:
            i, _ = self.exponents.popitem()
            self.set_button(i, 0)

    def set_true(self, button):
        button.setText("1")
        button.setStyleSheet("color: white;")

    def set_false(self, button):
        button.setText("0")
        button.setStyleSheet("color: rgb(50, 50, 50);")

    def set_button(self, i, val):
        button = self.bin_buttons[i]
        if val == 1:
            self.set_true(button)
            self.add_exp(i)
        else:
            self.set_false(button)
            self.remove_exp(i)

    def button_clicked(self, i):
        if self.bin_buttons[i].text() == "1":
            self.set_button(i, 0)
        else:
            self.set_button(i, 1)

        self.update_val()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.win_width = self.width()
        self.win_height = self.height()
        self.binLayout = BinLayout(self)
        self.bind()
        self.bind_shortcuts()
        self.binVerticalLayout.addLayout(self.binLayout)
        self.inputEdit.setFocus()
        self.bitRadioButton32.setChecked(True)

    def bind(self):
        self.inputEdit.textChanged.connect(self.input_changed)
        self.randomIntButton.clicked.connect(self.random_int)
        self.randomFloatButton.clicked.connect(self.random_float)
        self.bitRadioButton32.toggled.connect(self.show32)
        self.bitRadioButton64.toggled.connect(self.show64)
        self.clearButton.clicked.connect(lambda x: (self.inputEdit.clear(), self.inputEdit.setFocus()))
        self.clearLogButton.clicked.connect(self.logEdit.clear)

    def bind_shortcuts(self):
        esc = QtWidgets.QShortcut(QtGui.QKeySequence("Esc"), self)
        esc.activated.connect(self.clear_all)

        enter = QtWidgets.QShortcut(QtGui.QKeySequence("Enter"), self)
        enter.activated.connect(self.append_log)

    def clear_all(self):
        self.inputEdit.clear()
        self.clear_outs()
        self.binLayout.clear()
        self.inputEdit.setFocus()

    def clear_outs(self):
        self.decEdit.clear()
        self.binEdit.clear()
        self.hexEdit.clear()

    def input_changed(self, text):
        try:
            assert len(text) > 0
            val = eval(text)
            self.binLayout.set_value(val)
            self.update_vals(val)
        except:
            self.clear_outs()
            self.binLayout.clear()

    def update_vals(self, val):
        self.decEdit.setText(str(val))

        if val >= 0 and isinstance(val, int):
            bin_str = f"{val:b}"
            hex_str = f"{val:X}"
            self.binEdit.setText(bin_str)
            self.hexEdit.setText(hex_str)

    def random_int(self):
        low = eval(self.randomIntLowEdit.text())
        high = eval(self.randomIntHighEdit.text())
        val = random.randint(low, high)
        self.inputEdit.setText(str(val))

    def random_float(self):
        low = float(eval(self.randomFloatLowEdit.text()))
        high = float(eval(self.randomFloatHighEdit.text()))
        val = random.random() * (high - low) + low
        self.inputEdit.setText(str(val))

    def show32(self):
        self.binLayout.show32(True)

    def show64(self):
        self.binLayout.show64(True)

    def append_log(self):
        input_str = self.inputEdit.text()

        if len(input_str) != 0:
            dec_str = self.decEdit.text()
            bin_str = self.binEdit.text()
            hex_str = self.hexEdit.text()
            self.logEdit.appendPlainText(f"EXP = {input_str}\nDEC = {dec_str}\nBIN = {bin_str}\nHEX = {hex_str}\n")
            self.clear_all()


def dark_theme():
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(0, 128, 255))
    dark_palette.setColor(QPalette.HighlightedText, Qt.white)
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
    return dark_palette


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle('Fusion')
    app.setPalette(dark_theme())
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
