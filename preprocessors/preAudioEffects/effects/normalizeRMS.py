#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 09:27:13 2020

@author: Daniel Leander
"""
import numpy as np

def normalize(signalIn):

   signalOut = signalIn
   signalOut['audio'] = signalOut['audio']/np.mean(signalOut['audio']**2)**(1/2)
   return signalOut