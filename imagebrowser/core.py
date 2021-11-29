#
# IBView Core
#
# ------------------------------------------------------------------------------
# Subject to Licensing provided with this software

from PySide2 import QtGui, QtSvg

import os
import threading
import hashlib
import shutil
import time

from imagebrowser import cfg, utils, IB_CONVERTERMAP, IB_FORMATS

#---------------------------------------------
def getThumbnails(inPaths, inType=None):
    '''Build a list of thumbnail property objects.
    '''
    if inType == 'dir':
        pathList = utils.getFilePaths(inPaths)
    elif inType == 'file':
        pathList = inPaths
    else:
        utils.warn("No path type specified")
        return

    # Build ThumbnailProperty object lists
    thumbnailPathList = []
    for path in pathList:
        try:
            tp = ThumbnailProperty(path, cfg.format, cfg.cache)
            if tp.sourceExt in IB_FORMATS:
                thumbnailPathList.append(tp)
        except Exception, e:
            raise
            if cfg.verbose:
                utils.warn(e)

    return thumbnailPathList


#---------------------------------------------
def startConvert(thumbnailToProcess):
    '''Start convert thread.
    '''
    th = threading.Thread(target=batchConvert, args=(thumbnailToProcess,)) 
    th.start()


#---------------------------------------------
def batchConvert(tpList, delay=0.1):
    '''Convert thumbnails, using tiered convert method.
    '''
    # Primary
    convert_primary = IB_CONVERTERMAP[cfg.convert_primary]

    # Secondary
    convert_secondary = None
    if cfg.convert_secondary and cfg.convert_secondary != 'None':
        convert_secondary = IB_CONVERTERMAP[cfg.convert_secondary]

    if utils.makeCachePath(cfg.cache):
        for tp in tpList:
            useError = False
            result = convert_primary.run(tp, cfg.max_size)
            if not result and convert_secondary:
                result = convert_secondary.run(tp, cfg.max_size)
                if not result:
                    useError = True
            elif not result and not convert_secondary:
                    useError = True

            # Render placeholder error thumbnail, SVG for max size flexibility
            if useError:
                utils.warn('Could not build thumbnail for: %s' % tp.sourcePath)
                
                svgRenderer = QtSvg.QSvgRenderer(utils.getCustomIconPath(cfg.resourcePath, 'error.svg'))
                svgImage = QtGui.QImage(cfg.max_size, cfg.max_size, QtGui.QImage.Format_ARGB32)
                painter = QtGui.QPainter(svgImage)
                svgRenderer.render(painter)
                svgImage.save(tp.thumbnailPath)
                painter.end()

            # Delay to for responsiveness
            time.sleep(delay)


#------------------------------------------------#
# Thumbnail Properties Object
#------------------------------------------------#
class ThumbnailProperty(object):
    def __init__(self, inPath, outFormat, cacheLocation):
        super(ThumbnailProperty, self).__init__()

        inPath = inPath.encode('utf-8')

        # Source
        self.sourcePath = os.path.normpath(inPath)
        self.sourceExt = self.sourcePath.split(os.extsep)[-1]
        self.sourceDir = os.path.dirname(self.sourcePath)
        self.sourceFile = os.path.basename(self.sourcePath)
        self.sourceName, self.sourceDotExt = os.path.splitext(self.sourceFile)

        # UUID
        self.uuid = hashlib.md5(self.sourcePath).hexdigest()

        # Thumbnail
        self.thumbnailExt = outFormat.lower()
        self.thumbnailFile = os.extsep.join([self.uuid, self.thumbnailExt])
        self.thumbnailPath = os.path.join(cacheLocation, self.thumbnailFile)

        self.sourcePath = self.sourcePath.decode('utf-8')
        self.sourceName = self.sourceName.decode('utf-8')

        # Check if file exists
        self.exists = False
        if os.path.exists(self.thumbnailPath):
            self.exists = True

        # Check is source has changed
        self.isCurrent = False
        if self.exists:
            inFileModified = os.path.getmtime(self.sourcePath)
            outFileModified = os.path.getmtime(self.thumbnailPath)
            if not inFileModified > outFileModified:
                self.isCurrent = True

        # File Resolution
        self.sourceResolution = None
        QtImgReader = QtGui.QImageReader()
        QtImgReader.setFileName(self.sourcePath)
        if QtImgReader.canRead():
            sourceSize = QtImgReader.size()
            self.sourceResolution = '%d x %d' % (sourceSize.width(), sourceSize.height())


    def clear(self):
        if self.exists:
            os.remove(self.thumbnailPath)
            self.exists = False
            self.isCurrent = False