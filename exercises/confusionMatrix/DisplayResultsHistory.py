# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DisplayResultsHistory.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DisplayResultsHistory(object):
    def setupUi(self, DisplayResultsHistory):
        DisplayResultsHistory.setObjectName("DisplayResultsHistory")
        DisplayResultsHistory.resize(942, 609)
        font = QtGui.QFont()
        font.setPointSize(10)
        DisplayResultsHistory.setFont(font)
        self.verticalLayout = QtWidgets.QVBoxLayout(DisplayResultsHistory)
        self.verticalLayout.setObjectName("verticalLayout")
        self.figureFrame = QtWidgets.QFrame(DisplayResultsHistory)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.figureFrame.sizePolicy().hasHeightForWidth())
        self.figureFrame.setSizePolicy(sizePolicy)
        self.figureFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.figureFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.figureFrame.setObjectName("figureFrame")
        self.vl_figureFrame = QtWidgets.QVBoxLayout(self.figureFrame)
        self.vl_figureFrame.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.vl_figureFrame.setObjectName("vl_figureFrame")
        self.verticalLayout.addWidget(self.figureFrame)
        self.radioButtons = QtWidgets.QFrame(DisplayResultsHistory)
        self.radioButtons.setMinimumSize(QtCore.QSize(0, 40))
        self.radioButtons.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.radioButtons.setFrameShadow(QtWidgets.QFrame.Raised)
        self.radioButtons.setObjectName("radioButtons")
        self.hl_radioButtons = QtWidgets.QHBoxLayout(self.radioButtons)
        self.hl_radioButtons.setObjectName("hl_radioButtons")
        self.verticalLayout.addWidget(self.radioButtons)
        self.sliderFrame = QtWidgets.QFrame(DisplayResultsHistory)
        self.sliderFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.sliderFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.sliderFrame.setObjectName("sliderFrame")
        self.gl_sliderFrame = QtWidgets.QGridLayout(self.sliderFrame)
        self.gl_sliderFrame.setObjectName("gl_sliderFrame")
        self.verticalLayout.addWidget(self.sliderFrame)

        self.retranslateUi(DisplayResultsHistory)
        QtCore.QMetaObject.connectSlotsByName(DisplayResultsHistory)

    def retranslateUi(self, DisplayResultsHistory):
        _translate = QtCore.QCoreApplication.translate
        DisplayResultsHistory.setWindowTitle(_translate("DisplayResultsHistory", "Results History"))
