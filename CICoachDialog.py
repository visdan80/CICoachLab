from PyQt5 import QtWidgets

class CICoachDialog(QtWidgets.QMessageBox):
    """!
    CICoachDialog uses the QMessageBox dialog as base to display messages.
    The presented Dialog is raised in the stack of frames to ensure the visibility, epecially in the windows context.
    """
    def __init__(self, parHandle, title, text, mode='question', infoText='', detailedText=''):
        """!
        parHandle:  handle to CICoachLab
        title:      window title
        text:       question or informative text
        mode:       the mode defines if a question is asked, an information is provided
                    The mode defines which buttons are displayed and which icon is provided.
        infoText:   additional text which may be provided.
                    From QMessagebox documentation: "On the Mac, this text appears in small system
                    font below the text(). On other platforms, it is simply appended to the existing text."
        detailedText: the additional information may be seen by the user in the details area.

        Detailed information on the different modes:
            question:
                buttons:    yes, no, cancel
                icon:       question mark
            confirmation:
                buttons:    ok, cancel
                icon:       question mark
            information
                buttons:    ok
                icon:       none
            warning:
                buttons:    ok
                icon:       warning
            error:
                buttons:    ok
                icon:       error
        """

        super().__init__()
        self.title = title
        self.text = text
        self.mode = mode
        self.infoText = infoText
        self.detailedText = detailedText
        self.parHandle = parHandle
        self.initUI()


    def initUI(self):
        '''
        self.setWindowTitle(self.title)
        self.buttonReply = QtWidgets.QMessageBox.question(self, self.title, self.question,
                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        self.show()
        '''

        msg = QtWidgets.QMessageBox(self.parHandle)

        msg.setText(self.text)
        msg.setWindowTitle(self.title)
        msg.setSizeGripEnabled(True)

        if self.mode == 'question':
            msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
            msg.setIcon(QtWidgets.QMessageBox.Question)
        if self.mode == 'confirmation':
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            msg.setIcon(QtWidgets.QMessageBox.Question)
        if self.mode == 'confirmationNo':
            msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            msg.setIcon(QtWidgets.QMessageBox.Question)
        elif self.mode == 'information':
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        elif self.mode == 'warning':
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        elif self.mode == 'error':
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)

        if self.detailedText:
            msg.setDetailedText(self.detailedText)
        if self.infoText:
            msg.setInformativeText(self.infoText)

        msg.show()
        msg.raise_()

        self.buttonReply = msg.exec_()
        return self.buttonReply

    def returnButton(self):
        return self.buttonReply