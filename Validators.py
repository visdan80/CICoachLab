from PyQt5 import QtWidgets, QtCore, QtGui
import locale






class NumberValidator(QtGui.QValidator):
    """!
    Validating gui input in SettingsDialogCall. Check if a single valid numeric value is provided.
    """
    validationChanged = QtCore.pyqtSignal(QtGui.QValidator.State)

    def __init__(self, inputRange, convertFunc, comboStyle, sysname=None):
        """!
        The init function defines the valid range which can be set.
        The conversion function can be the functions float or int.
        comboStyle defines if a inputRange with two elements defines the minimum and maximum (False)
        or the two possible values (True).
        """

        QtGui.QValidator.__init__(self)

        self.range = inputRange
        self.convertFunc = convertFunc
        if not (convertFunc == int or convertFunc == float):
            raise TypeError

        self.comboStyle = comboStyle
        self.sysname = sysname

    def setRange(self, inputRange):
        """!
        Setting range
        """

        self.range = inputRange


    def validate(self, string, index):
        """!
        Validates the input string and returns the state of the validation.
        The input may be a single number of type float or integer.

        The status may be be of type
            QtGui.QValidator.Intermediate if the input is not finished yet,
            QtGui.QValidator.Invalid if invalid or unparsable data has been entered or
            QtGui.QValidator.Acceptable if data is valid.

            The data is valid only if it is of type int or float, and if it lies within the defined range. The range
            may be a set of possible values (comboStyle == True) or the range of length two within the minimum and maximum
            (comboStyle == False).

        Alongside the state the input string and the cursor index within the string is passed without interference.

        returns state, string, index
        """

        # do we have to check a string?
        if string:
            try:
                # setting locale to the found locale, without this locale.localeconv()['decimal_point'] won't return the
                # separator
                if self.sysname == 'Windows':
                    locale.setlocale(locale.LC_ALL, locale.getlocale()[0])
                else:
                    locale.setlocale(locale.LC_ALL, locale.getlocale())
                if locale.localeconv()['decimal_point'] == ',':
                    string = string.replace(',', '.')

                self.convertFunc(string)
                # first check passed
                state = QtGui.QValidator.Intermediate
            except ValueError:
                if string in '-+':
                    if self.range:
                        if string == '-' and min(self.range) > 0:
                            state = QtGui.QValidator.Invalid
                        else:
                            state = QtGui.QValidator.Intermediate
                        if string == '+' and max(self.range) < 0:
                            state = QtGui.QValidator.Invalid
                        else:
                            state = QtGui.QValidator.Intermediate
                    else:
                        state = QtGui.QValidator.Intermediate
                else:
                    state = QtGui.QValidator.Invalid
            # if no input or wrong type: no further check necessary
            if not(state == QtGui.QValidator.Invalid):
                try:
                    # if int or float, for the check of the range, the type does not matter
                    entry = float(string)
                    # do we have to check the range?
                    if self.range:
                        if len(self.range) == 2 and self.comboStyle == False:
                            if entry >= min(self.range) and entry <= max(self.range):
                                state = QtGui.QValidator.Acceptable
                            else:
                                state = QtGui.QValidator.Invalid
                        elif len(self.range) < 2:
                            state = QtGui.QValidator.Invalid
                        else:
                            if entry in self.range:
                                state = QtGui.QValidator.Acceptable
                            else:
                                state = QtGui.QValidator.Invalid
                    else:
                        state = QtGui.QValidator.Acceptable
                except:
                    regexp = QtCore.QRegExp('[0-9\.+-]')
                    if regexp.exactMatch(string):
                        state = QtGui.QValidator.Intermediate
                    else:
                        state = QtGui.QValidator.Invalid
        else:
            state = QtGui.QValidator.Intermediate

        self.validationChanged.emit(state)

        return state, string, index


class NumberListValidator(NumberValidator):
    """!
    Validating gui input in SettingsDialogCall. Check if valid list of numeric value(s) is provided.
    """
    validationChanged = QtCore.pyqtSignal(QtGui.QValidator.State)

    def __init__(self, inputRange, convertFunc, comboStyle, sysname=None):
        """!
        inputRange:          defines the minimum and maximum number for the input value
        convertFunc:    defines the function int or float for the conversion from string to the number
        comboStyle:     defines if the range of length two defines a set of possible values (True)
                        or a minimum and a maximum (False)
        """
        QtGui.QValidator.__init__(self)

        self.range = inputRange
        self.convertFunc = convertFunc
        #QtGui.QValidator.__init__(self)

        if not (convertFunc == int or convertFunc == float):
            raise TypeError

        self.comboStyle = comboStyle
        self.sysname = sysname

    def setRange(self, inputRange):
        """!
        Setting the range. The range can define minimum and maximum or a set of possible values.
        """

        self.range = inputRange


    def validate(self, string, index):
        """!
        Validates the input and returns the state of the validation.
        The input may consist of a single string value or a list of strings devided by ','

        It may be of type
            QtGui.QValidator.Intermediate if the input is not finished yet,
            QtGui.QValidator.Invalid if invalid or unparsable data has been entered or
            QtGui.QValidator.Acceptable if data is valid.

            The data is valid only if it is of type int or float, and if it lies within the defined range. The range
            may be a set of possible values (comboStyle == True) or the range within the minimum and maximum.

        Alongside the state the input string and the cursor index within the string is passed without interference.

        returns state, string, index
        """

        stateList = []

        stringList = "".join(string.split()).split(',')

        itemValidator = NumberValidator(self.range, self.convertFunc, self.comboStyle)

        state = QtGui.QValidator.Invalid
        for itemString in stringList:
            state, string, index = itemValidator.validate(itemString, index)
            stateList.append(state)
        # take the least acceptable state after the sorting of the statelist by applying set
        stateOut = list(set(stateList))[0]

        self.validationChanged.emit(stateOut)

        return stateOut, string, index


class StringValidator(QtGui.QValidator):
    """!
    Validating gui input in SettingsDialogCall. Check if valid string value is provided.
    """
    validationChanged = QtCore.pyqtSignal(QtGui.QValidator.State)

    def __init__(self, inputRange, sysname=None):
        QtGui.QValidator.__init__(self)
        """!
        The init function defines the range which has to be fullfilled.
        # range can define a list of possible words or a string which defines the possible symbols.
        """

        self.range = inputRange
        self.sysname = sysname


    def validate(self, string, index):
        """!
        Validates the input and returns the state of the validation.
        The input may consist of a list of strings or a string value which defines True or False and which will be
        interpreted as a boolean value. A list of strings is separated by ','.

        It may be of type
            QtGui.QValidator.Intermediate if the input is not finished yet,
            QtGui.QValidator.Invalid if invalid or unparsable data has been entered or
            QtGui.QValidator.Acceptable if data is valid.

            The data is valid if any string is entered. The input can

        Alongside the state the input string and the cursor index within the string is passed without interference.

        returns state, string, index
        """

        stateList = []

        if string:
            if self.range:
                if isinstance(self.range, list):
                    # check if string is part of acceptable words
                    if string in self.range:
                        # exact match was found
                        state = QtGui.QValidator.Acceptable
                        stateList.append(state)
                    else:
                        for rangeItem in self.range:
                            if string in rangeItem:
                                # partial match was found
                                state = QtGui.QValidator.Intermediate
                            else:
                                state = QtGui.QValidator.Invalid
                            stateList.append(state)
                elif isinstance(self.range, string):
                    # check if string contains allowed words
                    setRange = set(self.range)
                    setString = set(string)
                    difference = setString - setRange
                    if difference:
                        state = QtGui.QValidator.Invalid
                    else:
                        state = QtGui.QValidator.Acceptable
                    stateList.append(state)
            else:
                # check if checker/input function exists

                # without range definition anything can be entered
                stateList.append(QtGui.QValidator.Acceptable)
        else:
            # empty strings are acceptable
            stateList.append(QtGui.QValidator.Acceptable)

        stateOut = list(set(stateList))[-1]

        self.validationChanged.emit(stateOut)

        return stateOut, string, index


class BoolValidator(StringValidator):
    """!
    Validating gui input in SettingsDialogCall. Check if a valid boolean value is provided.
    """
    validationChanged = QtCore.pyqtSignal(QtGui.QValidator.State)


    def __init__(self, sysname=None):
        """!
        The ini function defines the possible range of strings ['True', 'False']
        """
        super().__init__(inputRange=['True', 'False'], sysname=sysname)
        #self.range = ['True', 'False']


    def validate(self, string, index):
        """!
        Check if string contains the possible strings defined in self. range ['True' or 'False']
        """

        state, string, index = StringValidator.validate(self, string, index)

        #self.validationChanged.emit(state)

        return state, string, index


class StringListValidator(StringValidator):
    """!
    Validating gui input in SettingsDialogCall. Check if valid boolean value is provided.
    """
    validationChanged = QtCore.pyqtSignal(QtGui.QValidator.State)


    def __init__(self, inputRange, sysname=None):
        """!
        The init function defines the range which has to be fullfilled.
        range can define a list of possible words or a string which defines the possible symbols.
        """

        super().__init__(self, sysname=sysname)
        QtGui.QValidator.__init__(self)
        self.range = inputRange


    def validate(self, string, index):
        """!
        Validates the input and returns the state of the validation.
        The input may consist of a list of strings or a string value which defines True or False and which will be
        interpreted as a boolean value. A list of strings is separated by ','.

        It may be of type
            QtGui.QValidator.Intermediate if the input is not finished yet,
            QtGui.QValidator.Invalid if invalid or unparsable data has been entered or
            QtGui.QValidator.Acceptable if data is valid.

            The data is valid if any string is entered. The input can

        Alongside the state the input string and the cursor index within the string is passed without interference.

        returns state, string, index
        """

        itemValidator = StringValidator(self.range)
        stateList = []
        itemStateList = []
        if string:
            if self.range:
                stringList = "".join(string.split()).split(',')
                for itemString in stringList:
                    state, stringItem, indexItem = itemValidator.validate(itemString, index)
                    itemStateList.append(state)
                stateList.append(list(set(itemStateList))[0])
            else:
                # without range definition anything can be entered
                stateList.append(QtGui.QValidator.Acceptable)
        else:
            # empty strings are acceptable
            stateList.append(QtGui.QValidator.Acceptable)
        if len(stateList) > 1:
            stateOut = list(set(stateList))[-1]
        else:
            stateOut = stateList[0]

        self.validationChanged.emit(stateOut)

        return stateOut, string, index


class BoolListValidator(StringListValidator):
    """!
    Validating gui input in SettingsDialogCall. Check if a list of valid boolean value is provided.
    """
    validationChanged = QtCore.pyqtSignal(QtGui.QValidator.State)


    def __init__(self, sysname=None):
        """!
        The ini function defines the possible range of strings ['True', 'False']
        """
        super().__init__(inputRange=['True', 'False'], sysname=sysname)

        self.range = ['True', 'False']


    def validate(self, string, index):
        """!
        Validates the input and returns the state of the validation.
        The input may consist of a list of strings or a string value which defines True or False and which will be
        interpreted as a boolean value. A list of strings is separated by ','.

        It may be of type
            QtGui.QValidator.Intermediate if the input is not finished yet,
            QtGui.QValidator.Invalid if invalid or unparsable data has been entered or
            QtGui.QValidator.Acceptable if data is valid.

            The data is valid if any string is entered. The input can

        Alongside the state the input string and the cursor index within the string is passed without interference.

        returns state, string, index
        """

        state, string, index = StringListValidator.validate(self, string, index)

        self.validationChanged.emit(state)

        return state, string, index


class AnyValidator(NumberValidator, BoolValidator, StringValidator):
    validationChanged = QtCore.pyqtSignal(QtGui.QValidator.State)


    def __init__(self, type, listStyle=None, inputRange=None, convertFunc=None, comboStyle=None, sysname=None):
        """!
        type:                   defines the type of validator which has to be run.
                                tpye can be defined as a string or a list of strings as defined in settingsLimits.
                                If a list of types is provided the input can be any of the possible types.
                                possible types are:
                                'int', 'float', 'bool', 'string'
                                Example for a list of types:
                                phase of sinusoid: 'sin', 'cos', or any float as degree
        listStyle               defines if a list of entries can be entered (True)
                                or if a single entry is expected (False),
        inputRange [None]:           defines the minimum and maximum number for the input value or a set of possible values
                                if comboStyle is set to True.
        convertFunc [None]:     defines the function int or float for the conversion from string to the number
        comboStyle [None]:      defines if the range of length two defines a set of possible values (True)
                                or a minimum and a maximum (False)
        """

        QtGui.QValidator.__init__(self)
        self.type = type
        self.listStyle = listStyle
        # if isinstance(range,list) and not(isinstance(range[0],list)):
        self.rangeAny = inputRange
        self.convertFunc = convertFunc
        self.comboStyle = comboStyle
        self.sysname = sysname


    def validate(self, string, index):

        if isinstance(self.type, str):
            self.range = self.rangeAny

        stateList = []

        if self.listStyle:
            stringList = "".join(string.split()).split(',')
        else:
            stringList = [string]

        for stringItem in stringList:
            stateItemList = []
            if 'float' in self.type or 'int' in self.type:
                if isinstance(self.type, list):
                    if 'float' in self.type:
                        self.range = self.rangeAny[self.type.index('float')]
                        convertFucnt = float
                        comboStyle = False
                    else:
                        self.range = self.rangeAny[self.type.index('int')]
                        convertFucnt = int
                        comboStyle = False
                tempValidator = NumberValidator(self.range, convertFucnt, comboStyle)
                state, string1, index1 = tempValidator.validate(stringItem, index)
                stateItemList.append(state)
            if 'bool' in self.type:
                # if isinstance(self.type, list):
                # if 'bool' in self.type:
                #        self.range = self.rangeAny[self.type.index('bool')]
                tempValidator = BoolValidator()
                state, string3, index3 = tempValidator.validate(stringItem, index)

                stateItemList.append(state)
            if 'string' in self.type:
                if isinstance(self.type, list):
                    if 'string' in self.type:
                        self.range = self.rangeAny[self.type.index('string')]
                tempValidator = StringValidator(self.range)
                state, string3, index3 = tempValidator.validate(stringItem, index)
                stateItemList.append(state)

            stateList.append(list(set(stateItemList))[-1])
        stateOut = list(set(stateList))[0]

        self.validationChanged.emit(state)

        return stateOut, string, index