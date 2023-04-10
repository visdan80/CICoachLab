#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Sun May 24 21:18:52 2015

@author: Daniel Leander


"""
import os
from numpy.core.multiarray import zeros


def getListOfDirectories(searchPath='/', depthOfDir=1, fullPath=False):
    """!
    This function returns a list of directories and subdirectories that
    are found in 'searchPath'.


                default
    input
    searchPath   '/'      = string determines the path of directories
    depthOfDir   1        = provides the depth of the subdirectories that can be
                                checked
    fullPath     False    = The returned directories are provided with the full path

    output
    listOfDirs    []      = list of folders
    """

    listOfDirs = []

    if depthOfDir <= 0:
        return listOfDirs

    try:

        listOfDirs = [f for f in os.listdir(searchPath) if os.path.isdir(os.path.join(searchPath, f))]
        if fullPath:
            listOfDirs = [searchPath + os.path.sep + i for i in listOfDirs]
    except:
        # no files have been found
        listOfDirs = []
        return listOfDirs

    nextDepthOfDir = depthOfDir - 1
    if nextDepthOfDir > 0:
        listOfDirsThisLevel = list(listOfDirs)
        for directory in listOfDirsThisLevel:
            # print directory
            try:
                if fullPath:
                    nextLevel = getListOfDirectories(directory, nextDepthOfDir, fullPath)
                else:
                    nextLevel = getListOfDirectories(os.path.join(searchPath, directory), nextDepthOfDir, fullPath)
                if len(nextLevel) > 0:
                    for subDirs in nextLevel:
                        # print 'subdir:'+subDirs
                        listOfDirs.append(subDirs)
            except:
                print("Exception found")

    return listOfDirs


"""
Created on Mon May 25 21:41:30 2015
@author: Daniel Leander
"""


def getListOfFiles(searchPath='/', depthOfDir=2, namePart=[], nameIgnore=[], fullPath=False):
    """!
    This function returns the list of files that are found in 'search_path' and
    subdirectories of 'search_path'. To find all subdirectories the function
    GetListOfDirectories(searchPath, depthOfDir) is used.

    input  :        default
        searchPath   '/'        string that gives the path of files whose list will
                                be compiled
        depthOfDir              number of subdirectories, 1 means no
                      2         subdirectories
        namePart      []        list of strings or string that shall be part of the filename
        nameIgnore    []        list of strings or string that shall not be part of the filename
        fullPath      False     flag which defines if the returned file names should provide the full path

    output :
        listOfFiles      list of matching files in path.
    """

    if depthOfDir <= 0:
        listOfFiles = []
        return listOfFiles

    if isinstance(namePart, str):
        namePart = [namePart]

    if isinstance(nameIgnore, str) and nameIgnore:
        nameIgnore = [nameIgnore]
    else:
        # an empty string is passed, which will be interpreted as nothing to ignore
        nameIgnore = []



    # files that can be found in the current directory
    try:
        listOfFiles = [f for f in os.listdir(searchPath) if os.path.isfile(os.path.join(searchPath, f))]
    except:
        # no files have been found
        listOfFiles = []
        return listOfFiles

    # checking for 'namePart' in file_name if 'namePart' is known
    if len(namePart) > 0:
        loFilesStrIdx = []
        for fileCounter in range(0, len(listOfFiles)):
            # getting index of files with 'namePart' as part of files
            # names
            flag = zeros(len(namePart))
            for fc in range(0, len(namePart)):
                if listOfFiles[fileCounter].lower().find(namePart[fc].lower()) >= 0:
                    flag[fc] = 1
            if all(flag):
                loFilesStrIdx.append(fileCounter)

        listOfFiles = [listOfFiles[i] for i in loFilesStrIdx]

    # checking for names to be ignored: 'nameIgnore' in file_name if 'nameIgnore' is known
    if len(nameIgnore) > 0:
        loFilesStrIdx = []
        for fileCounter in range(0, len(listOfFiles)):
            # getting index of files with 'namePart' as part of files
            # names
            flag = zeros(len(nameIgnore))
            for fc in range(0, len(nameIgnore)):
                if listOfFiles[fileCounter].lower().find(nameIgnore[fc].lower()) >= 0:
                    flag[fc] = 1
            if not(any(flag)):
                loFilesStrIdx.append(fileCounter)

        listOfFiles = [listOfFiles[i] for i in loFilesStrIdx]

    # getting all subdirectories
    listOfSubdirs = []
    if depthOfDir > 1:
        listOfSubdirs = getListOfDirectories(searchPath, depthOfDir - 1, fullPath=True)

    # Searching the subdirectories for more files, corresponding to
    # 'depthOfDir' and 'namePart'
    # Since all directories are known from 'lo_subdir' the depth of
    # subdirectories will be set to '1'
    for subdir in listOfSubdirs:
        moreSubfiles = getListOfFiles(subdir, 1, namePart, nameIgnore, fullPath)
        for subfile in moreSubfiles:
            listOfFiles.append(subfile)

    # return filenames using fullpath
    if fullPath:
        listOfFiles = [os.path.join(searchPath, i) for i in listOfFiles]

    return listOfFiles


def humansize(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    if nbytes == 0:
        return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])
