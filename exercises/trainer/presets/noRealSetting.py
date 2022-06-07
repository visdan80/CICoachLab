def defineSettings(parHandle):
    """
    This function is doing nothing but to show that a preset file can be defined.
    The informtion is provided in the status bar, although it may be overwritten by other messages quickly.
    The default settings will not be changed or extended by this function.
    """
    
    from PyQt5 import QtWidgets, QtCore
    
    
    def _translate(context, text, disambig):
        return QtCore.QCoreApplication.translate(context, text, disambig)

    msg = _translate("Trainer", 'The default settings of Trainer have been set and not been changed.', None)
    parHandle.showInformation(msg)
    title = _translate("Trainer", 'Information.', None)

    QtWidgets.QMessageBox.information(parHandle.ui.exerWidget, title , msg)
    
