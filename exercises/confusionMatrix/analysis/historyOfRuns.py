"""!
This function allows to slide through the valid results of the confusion matrix within one window.
"""


import copy
from numpy import ceil, floor
from PyQt5 import QtWidgets, QtCore

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

from DisplayResultsHistory import Ui_DisplayResultsHistory



# TODO: add filter for runs which have been successfully terminated?

class MplWidget(FigureCanvasQTAgg):
    """!
    This class generatess the QT5Widget inter face which can be added in the layout of the PyQt5 Application
    """
    def __init__(self, parent=None, width=5, height=4, dpi=300):
        fig = matplotlib.figure.Figure(figsize=(width, height), dpi=dpi)
        # TODO: check
        self.axes = []
        self.axes.append( fig.add_subplot(121) )
        self.axes.append( fig.add_subplot(122) )
        self.fig = fig
        super(MplWidget, self).__init__(fig)


class HistoryGuiCall(QtWidgets.QDialog):
    def __init__(self, parHandle=None):
        """Initializing the dialog window for the display of the history confusion matrix data. The selected run data
        in the run data list box can be displayed. The user can sweep through the different runs. If runs have been run
        with repetitions the average of the repetitions will be displayed.

        The selected data is subdivided into different subsets if the run data was measured with different numbers of
        phonemes. The subsets can be selected with the dynamically generated radio buttons.

        The gui is imported as Ui_DisplayResultsHistory which is defined in DisplayResultsHistory.py and
        DisplayResultsHistory.ui. DisplayResultsHistory.ui is converted into the pyhon file with the command line
        'pyuic5 DisplayResultsHistory.ui -o DisplayResultsHistory.py'.
        """

        self.parHandle = parHandle

        exerciseName = 'confusionMatrix'
        # get names of selected runs
        self.items = list(self.parHandle.runData[exerciseName])
        # getting data
        self.runData = self.parHandle.runData[exerciseName]

        self.runDataSubSelection = {}
        self.mergedItems = []
        self.subsetIDX = {}
        self.subsetLabels = {}
        self.numOfSubSetRunData = 0

        self.radioButtons = {}
        self.radioButtons['data'] = []
        self.radioButtons['subset'] = []
        self.uiDict = {}
        self.subsetLabels = {}
        self.sliderIdx = 0

        # getting index of selected runs
        self.selectedRuns = self.parHandle.curExercise['selectedRunData']

        # check if any runs were selected.
        if not(self.selectedRuns):
            msg = "No result data was selected for display. Please select data! "
            #msg = self._translate("confusionMatrix",
            #                 "No result data was selected for display. Please select data! ", None)
            self.parHandle.dPrint(msg, 2, guiMode = True)
            return

        # after check initialize gui
        QtWidgets.QDialog.__init__(self, parHandle)
        self.ui = Ui_DisplayResultsHistory()
        self.ui.setupUi(self)

        #generate the subset of all selected items to be able to check for all different subset regarding different
        # number of phonemes
        self.subsetIDX['all'] = self.selectedRuns
        self.setSubsets(mode='all')

        # getting all available settings of phonemes.
        columns = []
        nuOfItems = len(self.runDataSubSelection['all']['results']['confMat'])
        for idx in range(nuOfItems):
            columns.append(list(self.runDataSubSelection['all']['results']['confMat'][idx].columns))

        # getting the different sets of phonemes used along all selected rundata.
        # Different orders of the same phonemes within the settings may lead to a different subSets so far
        columnset = []
        for item in columns:
            if not (item in columnset):
                columnset.append(item)

        # number of sets aside the complete selection.
        numOfSubSets = len(columnset)
        self.subSetLabelVec = ['all'] + [str(len(columnset[x])) + ' Phon.s' for x in range(numOfSubSets)]

        for ii in range(len(columnset)):
            if self.subSetLabelVec[ii+1] != 'all':
                self.subsetIDX[self.subSetLabelVec[ii+1]] = []
                #self.subsetLabels[self.subSetLabelVec[ii + 1]] = []

        for idx in range(nuOfItems):
            for setIdx in range(len(columnset)):
                if list(self.runDataSubSelection['all']['results']['confMat'][idx].columns) == columnset[setIdx]:
                    # a new phoneme settings was found
                    self.subsetIDX[self.subSetLabelVec[setIdx+1]].append(idx)


        # generate subsets
        for item in self.subSetLabelVec:
            if item != 'all':
                self.setSubsets(mode=item)

        # generate radio buttons for selection of subsets
        rbItem = QtWidgets.QRadioButton('all', parent=parHandle)
        rbItem.setObjectName('all')
        rbItem.toggled.connect(self.selectSubSet)
        self.radioButtons['subset'].append(rbItem)
        self.ui.hl_radioButtons.addWidget(rbItem)
        for ii in range(numOfSubSets):
            rbItem = QtWidgets.QRadioButton(self.subSetLabelVec[ii+1], parent=parHandle)
            rbItem.setObjectName(self.subSetLabelVec[ii+1])
            rbItem.toggled.connect(self.selectSubSet)
            self.ui.hl_radioButtons.addWidget(rbItem)
            self.radioButtons['subset'].append(rbItem)

        # generate figure panel
        self.sc = MplWidget(self, width=5, height=4, dpi=100)
        self.toolbar = NavigationToolbar(self.sc, self)
        self.ui.vl_figureFrame.addWidget(self.toolbar)
        self.ui.vl_figureFrame.addWidget(self.sc)




        self.radioButtons['subset'][0].setChecked(True)
        self.radioButtons['data'][0].setChecked(True)

        #self.ui.horizontalSlider.valueChanged.connect(self.sliderChanged)


    def _translate(context, text, disambig):
        return QtCore.QCoreApplication.translate(context, text, disambig)


    def runDataChanged(self):
        """!
        """

        mode = self.subSetLabelVec[self.subsetIdx]
        radioButtonName = self.sender().text()
        self.sliderIdx = self.subsetLabels[mode].index(radioButtonName)

        self.imageUpdate()


    def setSubsets(self, mode=None):
        """!
        For the subsets the average over the repeatitions within one run are calculated.
        """

        self.subsetLabels[mode] = []
        ii = 0
        mergedData = copy.deepcopy(self.runData[self.subsetIDX[mode][0]])

        keys = list(self.runData.keys())

        for item in self.subsetIDX[mode]:
            '''
            import locale
            locale.setlocale(locale.LC_ALL, 'en_US.utf8')
            # locale.getlocale()
            #datetime.strptime looks at locale whereas asctime used in self.parHandle.saveRundData
            exerName = 'confusionMatrix'
            for ii in range(len(self.parHandle.runData[exerName])):
                # start time transformation
                date = self.parHandle.runData[exerName][ii]['time']['startASCII']
                datetimeObject = datetime.strptime(date, '%a %b %d %H:%M:%S %Y')
                dateTrans = datetimeObject.strftime('%H:%M:%S - %d.%m.%y')
                self.parHandle.runData[exerName][ii]['time']['startASCII'] = dateTrans
                # end time transformation
                date = self.parHandle.runData[exerName][ii]['time']['endASCII']
                datetimeObject = datetime.strptime(date, '%a %b %d %H:%M:%S %Y')
                dateTrans = datetimeObject.strftime('%H:%M:%S - %d.%m.%y')
                self.parHandle.runData[exerName][ii]['time']['endASCII'] = dateTrans
            #
            # date = 'Tue Oct 12 23:14:16 2021'
            locale.setlocale(locale.LC_ALL, 'de_De.utf8')
            '''
            # used as start-, end- time format
            # datetime.datetime.today().strftime('%H:%M:%S - %d.%m.%y')

            self.subsetLabels[mode].append(self.runData[keys[item]]['time']['endASCII'])
            meanConf = sum(self.runData[keys[item]]['results']['confMat']) / \
                       len(self.runData[keys[item]]['results']['confMat'])
            if ii == 0:
                mergedData['results']['confMat'] = []
            mergedData['results']['confMat'].append(meanConf)
            meanReact = sum(self.runData[keys[item]]['results']['reactMat']) / \
                        len(self.runData[keys[item]]['results']['reactMat'])
            if ii == 0:
                mergedData['results']['reactMat'] = []
            mergedData['results']['reactMat'].append(meanReact)

            #selectedItems.append(subItem)
            ii = ii + 1

        mergedData['time'] = dict()
        mergedData['statusMessage'] = 'Average of runs ' + str(self.subsetIDX[mode])


        self.runDataSubSelection[mode] = mergedData


    def selectSubSet(self):
        """!
        Selection of the subset according to the selected radio button.
        The slider maximum has to be reset according to the new subset. The slider will be set to zero.
        """

        # getting the object name of the radio button which is the same as its label
        radioButtonName = self.sender().text()
        self.subsetIdx = self.subSetLabelVec.index(radioButtonName)


        mode = self.subSetLabelVec[self.subsetIdx]

        numOfSubSetRunDataTemp = len(self.runDataSubSelection[mode]['results']['confMat'])

        # update labeling or number of shown radiobuttons
        noRadioButtons = len(self.radioButtons['data'])
        # I want to have 'numOfSubSetRunDataTemp' radio buttons
        for ii in range(max([numOfSubSetRunDataTemp, noRadioButtons])):
            if ii < noRadioButtons and ii < len(self.subsetLabels[mode]):
                # the radiobutton number (i+1) has been generated before. Just update data.
                rbItem = self.radioButtons['data'][ii]
                rbItem.setText(self.subsetLabels[mode][ii])
                rbItem.setObjectName(self.subsetLabels[mode][ii])
                rbItem.show()
            else:
                if ii >= noRadioButtons:
                    # the radiobutton has to be generated
                    rbItem = QtWidgets.QRadioButton(self.subsetLabels[mode][ii], parent=self.parHandle)
                    rbItem.setObjectName(self.subsetLabels[mode][ii])
                    rbItem.toggled.connect(self.runDataChanged)
                    self.ui.gl_sliderFrame.addWidget(rbItem, floor(ii/3), ii % 3 )
                    self.radioButtons['data'].append(rbItem)
                elif ii >= len(self.subsetLabels[mode]):
                    # the radio button has to be hidden because more radio buttons exist than data is present
                    self.radioButtons['data'][ii].hide()

        self.numOfSubSetRunData = numOfSubSetRunDataTemp
        self.radioButtons['data'][0].setChecked(True)

        '''
        # generate figure panel
        self.sc = MplWidget(self, width=5, height=4, dpi=100)
        self.toolbar = NavigationToolbar(self.sc, self)
        self.ui.vl_figureFrame.addWidget(self.toolbar)
        self.ui.vl_figureFrame.addWidget(self.sc)
        '''

        '''

        sliderMax = len(self.runDataSubSelection[self.subSetLabelVec[self.subsetIdx]]['results']['confMat'])
        if not('labeledSlider' in self.uiDict):
            self.uiDict['labeledSlider'] = LabeledSlider(minimum=0, maximum=sliderMax - 1, interval=1,
                                   labels=self.subsetLabels[self.subSetLabelVec[self.subsetIdx]])

            slLayout = self.uiDict['labeledSlider'].returnLayout()
            # If a slider is defined in ui file with the name horizontalSlider
            self.uiDict['sliderLayout'] = slLayout
            self.uiDict['sliderLayout'].setObjectName('slider')
            self.ui.vl_sliderFrame.addLayout(self.uiDict['sliderLayout'])

            self.uiDict['labeledSlider'].valueChanged.connect(self.sliderChanged)

            #self.uiDict['labeledSlider'].show()

        else:
            # temporarily blocking signals to prevent the calling of this function twice
            self.uiDict['labeledSlider'].blockSignals(True)
            self.sliderIdx = 0
            self.uiDict['labeledSlider'].setRange(self.sliderIdx, sliderMax-1)
            self.uiDict['labeledSlider'].blockSignals(False)

        if sliderMax <= 1:
            # no slider if just one item is available
            self.uiDict['labeledSlider'].setEnabled(False)
        else:
            self.uiDict['labeledSlider'].setEnabled(True)


        '''
        self.sliderIdx = 0

        self.imageUpdate()






    def imageUpdate(self):
        """!
        Show results of item with the index idx.
        """

        #self.sc.axes.cla(), does not remove the complete colorbar

        # removing all colorbars found in this figure, subplots, axes; May the brute force be with you.
        try:
            for ax in self.sc.axes:
                ax.images[-1].colorbar.remove()
        except:
            msg = "Could not remove colorbars from axes"
            self.parHandle.dPrint(msg, 2)

        '''
        for ax in self.sc.fig.axes:
            #ax.cla()
            try:
                ax.images[-1].colorbar.remove()
            except:
                msg = "Could not remove colorbars from axes within figure"
                self.parHandle.dPrint(msg, 2)
        '''
        data = copy.deepcopy(self.runDataSubSelection[self.subSetLabelVec[self.subsetIdx]])
        data['results']['confMat'] = [data['results']['confMat'][self.sliderIdx]]
        data['results']['reactMat'] = [data['results']['reactMat'][self.sliderIdx]]
        #self.sc.fig.clf(keep_observers=True) # clear
        self.parHandle.curExercise['functions']['displayResults'](data, self.sc.fig)

        self.sc.draw()


def historyOfRuns(parHandle):
    """!
    This function generates an gui object class.
    """

    temp = HistoryGuiCall(parHandle)
    #temp.setModal(False)
    try:
        temp.exec_()
    except:
        pass




'''
This code was published at
https://stackoverflow.com/questions/47494305/python-pyqt4-slider-with-tick-labels
on 22.03 2019 by Jason

CC-BY-SA-4.0





does not provide connect QSlider


class LabeledSlider(QtWidgets.QWidget):
    """!

    """

    def __init__(self, minimum, maximum, interval=1, orientation=QtCore.Qt.Horizontal,
            labels=None, parent=None):
        super(LabeledSlider, self).__init__(parent=parent)

        ticks = range(minimum, maximum + interval, interval)
        if labels is not None:
            if not isinstance(labels, (tuple, list)):
                raise Exception("<labels> is a list or tuple.")
            if len(labels) != len(ticks):
                raise Exception("Size of <labels> doesn't match ticks.")
            self.ticks = list(zip(ticks, labels))
        else:
            self.ticks = list(zip(ticks, map(str, ticks)))

        if orientation == QtCore.Qt.Horizontal:
            self.layout = QtWidgets.QVBoxLayout(self)
        elif orientation == QtCore.Qt.Vertical:
            self.layout = QtWidgets.QHBoxLayout(self)
        else:
            raise Exception("<orientation> wrong.")

        # gives some space to print labels
        self.leftMargin = 10
        self.topMargin = 10
        self.rightMargin = 10
        self.bottomMargin = 10

        self.layout.setContentsMargins(self.leftMargin, self.topMargin,
                self.rightMargin, self.bottomMargin)

        self.slider = QtWidgets.QSlider(orientation, self)
        self.slider.setMinimum(minimum)
        self.slider.setMaximum(maximum)
        self.slider.setValue(minimum)
        if orientation == QtCore.Qt.Horizontal:
            self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
            self.slider.setMinimumWidth(300) # just to make it easier to read
        else:
            self.slider.setTickPosition(QtWidgets.QSlider.TicksLeft)
            self.slider.setMinimumHeight(300) # just to make it easier to read
        self.slider.setTickInterval(interval)
        self.slider.setSingleStep(1)

        self.layout.addWidget(self.slider)

    def paintEvent(self, e):

        super(LabeledSlider,self).paintEvent(e)

        style = self.slider.style()
        painter = QPainter(self)
        stSlider = QtWidgets.QStyleOptionSlider()
        stSlider.initFrom(self.slider)
        stSlider.orientation = self.slider.orientation()

        length = style.pixelMetric(QtWidgets.QStyle.PM_SliderLength, stSlider, self.slider)
        available = style.pixelMetric(QtWidgets.QStyle.PM_SliderSpaceAvailable, stSlider, self.slider)

        for v, vStr in self.ticks:
            # get the size of the label
            rect = painter.drawText(QtCore.QRect(), QtCore.Qt.TextDontPrint, vStr)
            if self.slider.orientation() == QtCore.Qt.Horizontal:
                # I assume the offset is half the length of slider, therefore
                # + length//2
                xLoc = QtWidgets.QStyle.sliderPositionFromValue(self.slider.minimum(),
                        self.slider.maximum(), v, available) + length//2
                # left bound of the text = center - half of text width + L_margin
                left = xLoc - rect.width() // 2 + self.leftMargin
                bottom = self.rect().bottom()

                # enlarge margins if clipping
                if v == self.slider.minimum():
                    if left <= 0:
                        self.leftMargin = rect.width()// 2 - xLoc
                    if self.bottomMargin <= rect.height():
                        self.bottomMargin = rect.height()

                    self.layout.setContentsMargins(self.leftMargin,
                            self.topMargin, self.rightMargin,
                            self.bottomMargin)

                if v == self.slider.maximum() and rect.width()//2 >= self.rightMargin:
                    self.rightMargin = rect.width()//2
                    self.layout.setContentsMargins(self.leftMargin,
                            self.topMargin, self.rightMargin,
                            self.bottomMargin)

            else:
                yLoc = QtWidgets.QStyle.sliderPositionFromValue(self.slider.minimum(),
                        self.slider.maximum(), v, available, upsideDown=True)

                bottom = yLoc + length//2+rect.height()//2 + self.topMargin - 3
                # there is a 3 px offset that I can't attribute to any metric

                left = self.leftMargin - rect.width()
                if left <= 0:
                    self.leftMargin = rect.width()+2
                    self.layout.setContentsMargins(self.leftMargin,
                            self.topMargin, self.rightMargin,
                            self.bottomMargin)

            pos = QtCore.QPoint(left, bottom)
            painter.drawText(pos, vStr)

        return



'''


'''

# runs partially in ipython3 

import sys
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QStyle, QStyleOptionSlider, QSlider
from PyQt5.QtCore import QRect, QPoint, Qt


class LabeledSlider(QtWidgets.QSlider):
    def __init__(self, minimum, maximum, interval=1, orientation=Qt.Horizontal,
            labels=None, parent=None):
        super(QSlider, self).__init__(parent=parent)

        levels=range(minimum, maximum+interval, interval)
        if labels is not None:
            if not isinstance(labels, (tuple, list)):
                raise Exception("<labels> is a list or tuple.")
            if len(labels) != len(levels):
                raise Exception("Size of <labels> doesn't match levels.")
            self.levels=list(zip(levels,labels))
        else:
            self.levels=list(zip(levels,map(str,levels)))

        if orientation==Qt.Horizontal:
            self.layout=QtWidgets.QVBoxLayout(self)
        elif orientation==Qt.Vertical:
            self.layout=QtWidgets.QHBoxLayout(self)
        else:
            raise Exception("<orientation> wrong.")

        # gives some space to print labels
        self.leftMargin=10
        self.topMargin=10
        self.rightMargin=10
        self.bottomMargin=10

        self.layout.setContentsMargins(self.leftMargin,self.topMargin,
                self.rightMargin,self.bottomMargin)

        self.slider=QtWidgets.QSlider(orientation, self)
        self.slider.setMinimum(minimum)
        self.slider.setMaximum(maximum)
        self.slider.setValue(minimum)
        if orientation==Qt.Horizontal:
            self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
            self.slider.setMinimumWidth(300) # just to make it easier to read
        else:
            self.slider.setTickPosition(QtWidgets.QSlider.TicksLeft)
            self.slider.setMinimumHeight(300) # just to make it easier to read
        self.slider.setTickInterval(interval)
        self.slider.setSingleStep(1)

        self.layout.addWidget(self.slider)

    def paintEvent(self, e):

        super(QSlider, self).paintEvent(e)

        style=self.slider.style()
        painter=QPainter(self)
        stSlider=QStyleOptionSlider()
        stSlider.initFrom(self.slider)
        stSlider.orientation=self.slider.orientation()

        length=style.pixelMetric(QStyle.PM_SliderLength, stSlider, self.slider)
        available=style.pixelMetric(QStyle.PM_SliderSpaceAvailable, stSlider, self.slider)

        for v, vStr in self.levels:

            # get the size of the label
            rect=painter.drawText(QRect(), Qt.TextDontPrint, vStr)

            if self.slider.orientation()==Qt.Horizontal:
                # I assume the offset is half the length of slider, therefore
                # + length//2
                xLoc=QStyle.sliderPositionFromValue(self.slider.minimum(),
                        self.slider.maximum(), v, available)+length//2

                # left bound of the text = center - half of text width + L_margin
                left=xLoc-rect.width()//2+self.leftMargin
                bottom=self.rect().bottom()

                # enlarge margins if clipping
                if v==self.slider.minimum():
                    if left<=0:
                        self.leftMargin=rect.width()//2-xLoc
                    if self.bottomMargin<=rect.height():
                        self.bottomMargin=rect.height()

                    self.layout.setContentsMargins(self.leftMargin,
                            self.topMargin, self.rightMargin,
                            self.bottomMargin)

                if v==self.slider.maximum() and rect.width()//2>=self.rightMargin:
                    self.rightMargin=rect.width()//2
                    self.layout.setContentsMargins(self.leftMargin,
                            self.topMargin, self.rightMargin,
                            self.bottomMargin)

            else:
                yLoc=QStyle.sliderPositionFromValue(self.slider.minimum(),
                        self.slider.maximum(), v, available, upsideDown=True)

                bottom=yLoc+length//2+rect.height()//2+self.topMargin-3
                # there is a 3 px offset that I can't attribute to any metric

                left=self.leftMargin-rect.width()
                if left<=0:
                    self.leftMargin=rect.width()+2
                    self.layout.setContentsMargins(self.leftMargin,
                            self.topMargin, self.rightMargin,
                            self.bottomMargin)

            pos=QPoint(left, bottom)
            painter.drawText(pos, vStr)

        return


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    frame=QtWidgets.QWidget()
    ha=QtWidgets.QHBoxLayout()
    frame.setLayout(ha)

    w = LabeledSlider(1, 10 , 1, orientation=Qt.Horizontal)

    ha.addWidget(w)
    frame.show()
    sys.exit(app.exec_())
'''