# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/python-solar.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.setWindowModality(QtCore.Qt.WindowModal)
        MainWindow.resize(425, 570)
        MainWindow.setMaximumSize(QtCore.QSize(425, 570))
        MainWindow.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.output_source_button = QtGui.QPushButton(self.centralwidget)
        self.output_source_button.setGeometry(QtCore.QRect(20, 20, 131, 51))
        self.output_source_button.setObjectName(_fromUtf8("output_source_button"))
        self.output_source_combo = QtGui.QComboBox(self.centralwidget)
        self.output_source_combo.setGeometry(QtCore.QRect(180, 20, 191, 51))
        self.output_source_combo.setObjectName(_fromUtf8("output_source_combo"))
        self.output_source_combo.addItem(_fromUtf8(""))
        self.output_source_combo.addItem(_fromUtf8(""))
        self.output_source_combo.addItem(_fromUtf8(""))
        self.battery_recharge_v_button = QtGui.QPushButton(self.centralwidget)
        self.battery_recharge_v_button.setGeometry(QtCore.QRect(20, 90, 131, 51))
        self.battery_recharge_v_button.setObjectName(_fromUtf8("battery_recharge_v_button"))
        self.battery_recharge_v_edit = QtGui.QLineEdit(self.centralwidget)
        self.battery_recharge_v_edit.setGeometry(QtCore.QRect(180, 100, 101, 33))
        self.battery_recharge_v_edit.setMaxLength(4)
        self.battery_recharge_v_edit.setObjectName(_fromUtf8("battery_recharge_v_edit"))
        self.device_charge_combo = QtGui.QComboBox(self.centralwidget)
        self.device_charge_combo.setGeometry(QtCore.QRect(180, 170, 191, 51))
        self.device_charge_combo.setObjectName(_fromUtf8("device_charge_combo"))
        self.device_charge_combo.addItem(_fromUtf8(""))
        self.device_charge_combo.addItem(_fromUtf8(""))
        self.device_charge_combo.addItem(_fromUtf8(""))
        self.device_charge_combo.addItem(_fromUtf8(""))
        self.device_charge_button = QtGui.QPushButton(self.centralwidget)
        self.device_charge_button.setGeometry(QtCore.QRect(20, 170, 131, 51))
        self.device_charge_button.setObjectName(_fromUtf8("device_charge_button"))
        self.battery_cutoff_edit = QtGui.QLineEdit(self.centralwidget)
        self.battery_cutoff_edit.setGeometry(QtCore.QRect(180, 250, 101, 33))
        self.battery_cutoff_edit.setMaxLength(4)
        self.battery_cutoff_edit.setObjectName(_fromUtf8("battery_cutoff_edit"))
        self.battery_cutoff_button = QtGui.QPushButton(self.centralwidget)
        self.battery_cutoff_button.setGeometry(QtCore.QRect(20, 240, 131, 51))
        self.battery_cutoff_button.setObjectName(_fromUtf8("battery_cutoff_button"))
        self.battery_constant_v_button = QtGui.QPushButton(self.centralwidget)
        self.battery_constant_v_button.setGeometry(QtCore.QRect(20, 310, 131, 51))
        self.battery_constant_v_button.setObjectName(_fromUtf8("battery_constant_v_button"))
        self.battery_constant_v_edit = QtGui.QLineEdit(self.centralwidget)
        self.battery_constant_v_edit.setGeometry(QtCore.QRect(180, 320, 101, 33))
        self.battery_constant_v_edit.setMaxLength(4)
        self.battery_constant_v_edit.setObjectName(_fromUtf8("battery_constant_v_edit"))
        self.battery_floating_v_edit = QtGui.QLineEdit(self.centralwidget)
        self.battery_floating_v_edit.setGeometry(QtCore.QRect(180, 390, 101, 33))
        self.battery_floating_v_edit.setMaxLength(4)
        self.battery_floating_v_edit.setObjectName(_fromUtf8("battery_floating_v_edit"))
        self.battery_floating_v_button = QtGui.QPushButton(self.centralwidget)
        self.battery_floating_v_button.setGeometry(QtCore.QRect(20, 380, 131, 51))
        self.battery_floating_v_button.setObjectName(_fromUtf8("battery_floating_v_button"))
        self.generate_report_button = QtGui.QPushButton(self.centralwidget)
        self.generate_report_button.setGeometry(QtCore.QRect(20, 450, 131, 51))
        self.generate_report_button.setObjectName(_fromUtf8("generate_report_button"))
        self.report_from_edit = QtGui.QLineEdit(self.centralwidget)
        self.report_from_edit.setGeometry(QtCore.QRect(180, 460, 101, 33))
        self.report_from_edit.setMaxLength(10)
        self.report_from_edit.setObjectName(_fromUtf8("report_from_edit"))
        self.report_to_edit = QtGui.QLineEdit(self.centralwidget)
        self.report_to_edit.setGeometry(QtCore.QRect(310, 460, 101, 33))
        self.report_to_edit.setMaxLength(10)
        self.report_to_edit.setObjectName(_fromUtf8("report_to_edit"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 425, 27))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Inverter interface version 0.10", None))
        self.output_source_button.setText(_translate("MainWindow", "Output Source \n"
"Priority", None))
        self.output_source_combo.setItemText(0, _translate("MainWindow", "Utility first", None))
        self.output_source_combo.setItemText(1, _translate("MainWindow", "Solar first", None))
        self.output_source_combo.setItemText(2, _translate("MainWindow", "SBU priority", None))
        self.battery_recharge_v_button.setText(_translate("MainWindow", "Battery Recharge \n"
"Voltage", None))
        self.battery_recharge_v_edit.setToolTip(_translate("MainWindow", "<html><head/><body><p>12V unit: 11V/11.3V/11.5V/11.8V/12V/12.3V/12.5V/12.8V </p><p>24V unit: 22V/22.5V/23V/23.5V/24V/24.5V/25V/25.5V </p><p>48V unit: 44V/45V/46V/47V/48V/49V/50V/51V</p></body></html>", None))
        self.device_charge_combo.setItemText(0, _translate("MainWindow", "Utility first", None))
        self.device_charge_combo.setItemText(1, _translate("MainWindow", "Solar first", None))
        self.device_charge_combo.setItemText(2, _translate("MainWindow", "Solar and utility", None))
        self.device_charge_combo.setItemText(3, _translate("MainWindow", "Solar only", None))
        self.device_charge_button.setText(_translate("MainWindow", "Device Charge \n"
"Priority", None))
        self.battery_cutoff_edit.setToolTip(_translate("MainWindow", "<html><head/><body><p>40.0 to 48.0</p></body></html>", None))
        self.battery_cutoff_button.setText(_translate("MainWindow", "Battery Cutoff\n"
"Voltage", None))
        self.battery_constant_v_button.setText(_translate("MainWindow", "Battery Constant\n"
"Charge Voltage", None))
        self.battery_constant_v_edit.setToolTip(_translate("MainWindow", "<html><head/><body><p>48.0 to 58.4</p></body></html>", None))
        self.battery_floating_v_edit.setToolTip(_translate("MainWindow", "<html><head/><body><p>48.0 to 58.4</p></body></html>", None))
        self.battery_floating_v_button.setText(_translate("MainWindow", "Battery Floating\n"
"Charge Voltage", None))
        self.generate_report_button.setText(_translate("MainWindow", "Generate\n"
"Report", None))
        self.report_from_edit.setToolTip(_translate("MainWindow", "<html><head/><body><p>Format: yyyy/mm/dd</p></body></html>", None))
        self.report_to_edit.setToolTip(_translate("MainWindow", "<html><head/><body><p>Format: yyyy/mm/dd</p></body></html>", None))

