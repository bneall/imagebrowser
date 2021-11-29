#
# IBView Utils
#
# ------------------------------------------------------------------------------
# Subject to Licensing provided with this software

import os

#---------------------------------------------
def error(msg):
    logMessage = '[IBView][error]: %s' % msg
    print logMessage

#---------------------------------------------
def warn(msg):
    logMessage = '[IBView][warn]: %s' % msg
    print logMessage

#---------------------------------------------
def info(msg):
    logMessage = '[IBView][info]: %s' % msg
    print logMessage

#---------------------------------------------
def getHomePath():
    return os.path.expanduser('~')

#---------------------------------------------
def getCustomIconPath(resourcePath, name):
    return os.path.join(resourcePath, 'icons', name)

#---------------------------------------------
def getFilePaths(inPaths):
    '''Return list of files from given path
    '''
    fileList = []
    for path in inPaths:
        searchPath = os.path.normpath(path)
        for filename in os.listdir(searchPath):
            filepath = os.path.join(searchPath, filename)
            if not filename.startswith(".") and os.path.isfile(filepath):
                fileList.append(filepath)
    return sorted(fileList)

#---------------------------------------------
def makeCachePath(inPath):
    '''Makes directory for thumbnail if it doesnt already exist
    '''
    if os.path.exists(inPath):
        return True
    else:
        try:
            os.makedirs(inPath)
            return True

        # except IOError:
        except Exception, e:
            print e
            print "Could not create directory: ", inPath
            return False

#---------------------------------------------
def getStyleSheet(resourcePath):
    qssPath = os.path.join(resourcePath, 'stylesheets', 'ibStyle.qss')
    qss = open(qssPath, "r").read()
    return qss

#---------------------------------------------
def getConverterPlugins(inPath):
    '''Build Converter Plugin Map.
    '''
    import imp

    converters = {}
    for f in os.listdir(inPath):
        fileName, fileExt = os.path.splitext(f)
        if fileExt == '.py':
            filePath = os.path.join(inPath,f)
            mod = imp.load_source(fileName, filePath)
            converters[fileName]=mod
            
    return converters

#---------------------------------------------
def saveCollectionFile(presetName, presetValue, location):  
    import json
    with open(location, 'wb') as collectionFile:
        json.dump({presetName: presetValue}, collectionFile)

#---------------------------------------------
def loadCollectionsFile(location):
    import json
    with open(location) as collectionFile:
        collection = json.load(collectionFile)
        return collection.keys()[0], collection.values()[0]