# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'taxonome/gui/ui/csvimport_synonyms.ui'
#
# Created: Mon Oct 21 09:55:59 2013
#      by: PyQt4 UI code generator 4.10.2
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

class Ui_CsvSynonymsImportDialog(object):
    def setupUi(self, CsvSynonymsImportDialog):
        CsvSynonymsImportDialog.setObjectName(_fromUtf8("CsvSynonymsImportDialog"))
        CsvSynonymsImportDialog.resize(551, 647)
        self.verticalLayout_3 = QtGui.QVBoxLayout(CsvSynonymsImportDialog)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_3 = QtGui.QLabel(CsvSynonymsImportDialog)
        self.label_3.setTextFormat(QtCore.Qt.AutoText)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_3.addWidget(self.label_3)
        self.ds_name = QtGui.QLineEdit(CsvSynonymsImportDialog)
        self.ds_name.setObjectName(_fromUtf8("ds_name"))
        self.horizontalLayout_3.addWidget(self.ds_name)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.accepted_names = QtGui.QGroupBox(CsvSynonymsImportDialog)
        self.accepted_names.setFlat(False)
        self.accepted_names.setCheckable(False)
        self.accepted_names.setObjectName(_fromUtf8("accepted_names"))
        self.verticalLayout = QtGui.QVBoxLayout(self.accepted_names)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.accepted_names)
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.accnamefield = QtGui.QComboBox(self.accepted_names)
        self.accnamefield.setMinimumSize(QtCore.QSize(150, 0))
        self.accnamefield.setObjectName(_fromUtf8("accnamefield"))
        self.horizontalLayout.addWidget(self.accnamefield)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.groupBox = QtGui.QGroupBox(self.accepted_names)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.formLayout_2 = QtGui.QFormLayout(self.groupBox)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.accnoauth = QtGui.QRadioButton(self.groupBox)
        self.accnoauth.setObjectName(_fromUtf8("accnoauth"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.accnoauth)
        self.accauth_with_name = QtGui.QRadioButton(self.groupBox)
        self.accauth_with_name.setObjectName(_fromUtf8("accauth_with_name"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.accauth_with_name)
        self.accauth_separate = QtGui.QRadioButton(self.groupBox)
        self.accauth_separate.setChecked(True)
        self.accauth_separate.setObjectName(_fromUtf8("accauth_separate"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.LabelRole, self.accauth_separate)
        self.accauthfield = QtGui.QComboBox(self.groupBox)
        self.accauthfield.setEnabled(True)
        self.accauthfield.setObjectName(_fromUtf8("accauthfield"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.FieldRole, self.accauthfield)
        self.verticalLayout.addWidget(self.groupBox)
        self.verticalLayout_3.addWidget(self.accepted_names)
        self.synonyms_grp = QtGui.QGroupBox(CsvSynonymsImportDialog)
        self.synonyms_grp.setObjectName(_fromUtf8("synonyms_grp"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.synonyms_grp)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_4 = QtGui.QLabel(self.synonyms_grp)
        self.label_4.setTextFormat(QtCore.Qt.AutoText)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_2.addWidget(self.label_4)
        self.synnamefield = QtGui.QComboBox(self.synonyms_grp)
        self.synnamefield.setMinimumSize(QtCore.QSize(150, 0))
        self.synnamefield.setObjectName(_fromUtf8("synnamefield"))
        self.horizontalLayout_2.addWidget(self.synnamefield)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.groupBox_4 = QtGui.QGroupBox(self.synonyms_grp)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.formLayout_3 = QtGui.QFormLayout(self.groupBox_4)
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        self.synnoauth = QtGui.QRadioButton(self.groupBox_4)
        self.synnoauth.setObjectName(_fromUtf8("synnoauth"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.LabelRole, self.synnoauth)
        self.synauth_with_name = QtGui.QRadioButton(self.groupBox_4)
        self.synauth_with_name.setObjectName(_fromUtf8("synauth_with_name"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.LabelRole, self.synauth_with_name)
        self.synauth_separate = QtGui.QRadioButton(self.groupBox_4)
        self.synauth_separate.setChecked(True)
        self.synauth_separate.setObjectName(_fromUtf8("synauth_separate"))
        self.formLayout_3.setWidget(3, QtGui.QFormLayout.LabelRole, self.synauth_separate)
        self.synauthfield = QtGui.QComboBox(self.groupBox_4)
        self.synauthfield.setEnabled(True)
        self.synauthfield.setObjectName(_fromUtf8("synauthfield"))
        self.formLayout_3.setWidget(3, QtGui.QFormLayout.FieldRole, self.synauthfield)
        self.verticalLayout_2.addWidget(self.groupBox_4)
        self.verticalLayout_3.addWidget(self.synonyms_grp)
        self.label_2 = QtGui.QLabel(CsvSynonymsImportDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_3.addWidget(self.label_2)
        self.preview = QtGui.QTableWidget(CsvSynonymsImportDialog)
        self.preview.setObjectName(_fromUtf8("preview"))
        self.preview.setColumnCount(0)
        self.preview.setRowCount(0)
        self.verticalLayout_3.addWidget(self.preview)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_5 = QtGui.QLabel(CsvSynonymsImportDialog)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_4.addWidget(self.label_5)
        self.csv_encoding = QtGui.QComboBox(CsvSynonymsImportDialog)
        self.csv_encoding.setObjectName(_fromUtf8("csv_encoding"))
        self.horizontalLayout_4.addWidget(self.csv_encoding)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.buttonBox = QtGui.QDialogButtonBox(CsvSynonymsImportDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)
        self.label_3.setBuddy(self.ds_name)
        self.label.setBuddy(self.accnamefield)
        self.label_4.setBuddy(self.synnamefield)
        self.label_2.setBuddy(self.preview)

        self.retranslateUi(CsvSynonymsImportDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), CsvSynonymsImportDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), CsvSynonymsImportDialog.reject)
        QtCore.QObject.connect(self.accauth_separate, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.accauthfield.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(CsvSynonymsImportDialog)

    def retranslateUi(self, CsvSynonymsImportDialog):
        CsvSynonymsImportDialog.setWindowTitle(_translate("CsvSynonymsImportDialog", "Import CSV", None))
        self.label_3.setText(_translate("CsvSynonymsImportDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Dataset name:</span></p></body></html>", None))
        self.accepted_names.setTitle(_translate("CsvSynonymsImportDialog", "Accepted names", None))
        self.label.setText(_translate("CsvSynonymsImportDialog", "Name column:", None))
        self.groupBox.setTitle(_translate("CsvSynonymsImportDialog", "Authorities:", None))
        self.accnoauth.setText(_translate("CsvSynonymsImportDialog", "None", None))
        self.accauth_with_name.setText(_translate("CsvSynonymsImportDialog", "In column with species", None))
        self.accauth_separate.setText(_translate("CsvSynonymsImportDialog", "In separate column:", None))
        self.synonyms_grp.setTitle(_translate("CsvSynonymsImportDialog", "Synonyms", None))
        self.label_4.setText(_translate("CsvSynonymsImportDialog", "Name column:", None))
        self.groupBox_4.setTitle(_translate("CsvSynonymsImportDialog", "Authorities:", None))
        self.synnoauth.setText(_translate("CsvSynonymsImportDialog", "None", None))
        self.synauth_with_name.setText(_translate("CsvSynonymsImportDialog", "In column with species", None))
        self.synauth_separate.setText(_translate("CsvSynonymsImportDialog", "In separate column:", None))
        self.label_2.setText(_translate("CsvSynonymsImportDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Preview</span></p></body></html>", None))
        self.label_5.setText(_translate("CsvSynonymsImportDialog", "Character encoding", None))

