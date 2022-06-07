#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 09:27:13 2020

@author: Daniel Leander
"""

import scipy as scp
import scipy.signal
import numpy as np

def normalizePeak(signalIn):
    signalOut = signalIn
    fac = 0
    for chIdx in range(signalIn['audio'].shape[1]):
        fac = max([fac,max(abs(signalIn['audio'][:, chIdx]))])

    for chIdx in range(signalIn['audio'].shape[1]):
        signalOut['audio'][:, chIdx] = signalIn['audio'][:, chIdx]/fac

    return signalOut