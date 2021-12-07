#
# IBView UI
#
# ------------------------------------------------------------------------------
# Subject to Licensing provided with this software

from PySide2 import QtCore, QtWidgets, QtGui
import os

from imagebrowser import cfg, core, utils, IB_STYLESHEET

#------------------------------------------------#
# Path Browse Widget
#------------------------------------------------#
class IBPathBrowse(QtWidgets.QWidget):
    def __init__(self, defaultPath, isfile=False):
        super(IBPathBrowse, self).__init__()
    
        mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(mainLayout)

        self.pathEdit = QtWidgets.QLineEdit(defaultPath)
        self.defaultPath = defaultPath
        self.isfile = isfile
        browseBtn = QtWidgets.QPushButton('Browse')

        mainLayout.addWidget(self.pathEdit)
        mainLayout.addWidget(browseBtn)

        browseBtn.clicked.connect(self.browse)

    #_____________________________________________
    def browse(self):

        if self.isfile:
            browseRes = QtWidgets.QFileDialog.getSaveFileName(self,
                                                            caption='Choose file',
                                                            dir=self.defaultPath)
            if browseRes[0]:
                self.pathEdit.setText(browseRes[0])
        
        else:
            browseRes = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                                caption='Choose directory',
                                                                dir=self.defaultPath)
            if browseRes:
                self.pathEdit.setText(browseRes)
        

#------------------------------------------------#
# Configuration Widget
#------------------------------------------------#
class IBConfigUI(QtWidgets.QDialog):
    '''IBView Configuration Widget
    '''
    def __init__(self, parent=None):
        super(IBConfigUI, self).__init__(parent)

        self.setMinimumSize(400,200)
        self.setWindowTitle('Image Browser Config')
        self.setStyleSheet(IB_STYLESHEET)

        self.settingsMap = {}

        mainLayout = QtWidgets.QVBoxLayout()
        buttonLayout = QtWidgets.QHBoxLayout()
        self.setLayout(mainLayout)

        for settingCategory in sorted(cfg.config.keys()):
            if settingCategory.startswith('settings'):
                settings = cfg.config[settingCategory]
                categoryName = settingCategory.split('_')[1].capitalize()
                categoryGroup = QtWidgets.QGroupBox(categoryName)
                categoryLayout = QtWidgets.QGridLayout()
                categoryGroup.setLayout(categoryLayout)
                mainLayout.addWidget(categoryGroup)
                row = 0
                for setting in sorted(settings.keys()):
                    settingDict = cfg.config[settingCategory][setting]
                    settingName = ' '.join([n.capitalize() for n in setting.split('_')])
                    label = QtWidgets.QLabel(settingName)
                    widget, func = self.buildConfigSetting(settingName, settingDict)
                    categoryLayout.addWidget(label, row, 0)
                    categoryLayout.addWidget(widget, row, 1)
                    row += 1
                    self.settingsMap[setting]=func

        okBtn = QtWidgets.QPushButton('Ok')
        cancelBtn = QtWidgets.QPushButton('Cancel')
        buttonLayout.addWidget(okBtn)
        buttonLayout.addWidget(cancelBtn)
        mainLayout.addLayout(buttonLayout)

        # Connections
        okBtn.clicked.connect(self.accept)
        cancelBtn.clicked.connect(self.reject)

    #_____________________________________________
    def accept(self):
        for setting, getFunc in self.settingsMap.iteritems():
            newValue = getFunc()
            setFunc = getattr(cfg, 'set_%s' % setting)
            setFunc(newValue)
        cfg.saveConfig()
        super(IBConfigUI,self).accept()

    #_____________________________________________
    def buildConfigSetting(self, name, settingDict):
        values = settingDict['values']
        settingType = settingDict['type']
        current = settingDict['current']

        if settingType == 'list':
            valueWidget = QtWidgets.QComboBox()
            valueWidget.addItems(values)
            valueWidget.setCurrentIndex(valueWidget.findText(current))
            getValueFunc = valueWidget.currentText
        if settingType == 'range':
            valueWidget = QtWidgets.QSpinBox()
            valueWidget.setRange(values[0],values[1])
            valueWidget.setValue(current)
            getValueFunc = valueWidget.value
        if settingType == 'path':
            valueWidget = IBPathBrowse(current)
            getValueFunc = valueWidget.pathEdit.text
        if settingType == 'filepath':
            valueWidget = IBPathBrowse(current, isfile=True)
            getValueFunc = valueWidget.pathEdit.text
        if settingType == 'bool':
            valueWidget = QtWidgets.QCheckBox()
            valueWidget.setChecked(current)
            getValueFunc = valueWidget.isChecked
        if valueWidget and getValueFunc:
            return valueWidget, getValueFunc


#------------------------------------------------#
# File Bookmark Widget
#------------------------------------------------#
class IBBookmarkList(QtWidgets.QListWidget):
    collectionUpdated = QtCore.Signal(QtWidgets.QListWidgetItem)
    presetRemoved = QtCore.Signal(str)
    '''IBView Custom Bookmark List Widget
    '''
    def __init__(self, mimeHandler=None, parent=None):
        super(IBBookmarkList, self).__init__(parent)

        self.setSelectionMode(self.NoSelection)
        self.setAcceptDrops(True)
        self.setDragDropMode(self.DropOnly)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setMouseTracking(True)
        self.setSpacing(1)

        # Local
        self.actionItem = None
        self.dropPaths = None
        self.mimeHandler = mimeHandler

        # Looks
        self.neutralBrush = QtGui.QBrush(QtGui.QColor(255,255,255,15))
        self.hoverBrush = QtGui.QBrush(QtGui.QColor(255,255,255,35))
        self.activeBrush = QtGui.QBrush(QtGui.QColor(80,180,50,80))          

        # Init
        homePreset = self.addPreset('Home', utils.getHomePath())
        # Override icon
        homePreset.setIcon(QtGui.QIcon(QtGui.QPixmap(utils.getCustomIconPath(cfg.resourcePath, 'home.png'))))

    #_____________________________________________
    def mouseMoveEvent(self, e):
        hoverItem = self.itemAt(e.pos())
        self.setHoverLook(hoverItem,'all', self.hoverBrush)

    #_____________________________________________
    def leaveEvent(self, e):
        self.setAllLook(self.neutralBrush)

    #_____________________________________________
    def dragEnterEvent(self, e):
        self.dropPaths = self.getPathsFromMime(e.mimeData())
        e.acceptProposedAction()

    #_____________________________________________
    def dragMoveEvent(self, e):
        hoverItem = self.itemAt(e.pos())
        if self.dropPaths and hoverItem:
            if os.path.isfile(self.dropPaths[0]):
                self.setHoverLook(hoverItem, 'collection', self.activeBrush)
        e.acceptProposedAction()

    #_____________________________________________
    def dropEvent(self, e):
        '''Handle the drop event.
        '''
        if self.dropPaths:
            # Assume presetType by first entry
            isBookmarkDrop = os.path.isdir(self.dropPaths[0])
            isCollectionDrop = os.path.isfile(self.dropPaths[0])

            # Handle Bookmark
            if isBookmarkDrop:
                for path in self.dropPaths:
                    bookmarkName = os.path.basename(path)
                    self.addPreset(bookmarkName, path, new=True)

            # Handle Collection
            if isCollectionDrop:
                try:
                    hoverItem = self.itemAt(e.pos())
                    bookmarkType = hoverItem.data(32)[0]
                    if bookmarkType == 'collection':
                        self.updatePreset(hoverItem, self.dropPaths)
                except Exception, e:
                    if cfg.verbose:
                        utils.error(e)

        # Set all neutral
        self.setAllLook(self.neutralBrush)

    #_____________________________________________
    def contextMenuEvent(self, event):
        self.actionItem = self.itemAt(event.pos())

        if self.actionItem:

            contextMenu = QtWidgets.QMenu()

            renamePreset = contextMenu.addAction("Rename")
            renamePreset.triggered.connect(self.renamePreset)
            removePreset = contextMenu.addAction("Remove")
            removePreset.triggered.connect(self.removePreset)

            contextMenu.exec_(event.globalPos())

    #_____________________________________________
    def getPathsFromMime(self, mimeData):
        '''Get pathlist from mime data
        '''
  
        pathList = []
        if self.mimeHandler:
            pathList = self.mimeHandler(mimeData)

        if mimeData.hasUrls():
            for url in mimeData.urls():
                path = os.path.normpath(url.toLocalFile())
                pathList.append(path)
        
        return pathList

    #_____________________________________________
    def setAllLook(self, brush, exclude=None):
        for item in self.getAllItems(exclude):
            item.setBackground(brush)

    #_____________________________________________
    def setHoverLook(self, hoverItem, presetType, brush):
        if hoverItem:
            if presetType == 'all':
                hoverItem.setBackground(brush)
            else:
                bookmarkType = hoverItem.data(32)[0]
                if bookmarkType == presetType:
                    hoverItem.setBackground(brush)
                else:
                    hoverItem.setBackground(self.neutralBrush)

            self.setAllLook(self.neutralBrush, exclude=self.row(hoverItem))
        else:
            self.setAllLook(self.neutralBrush)

    #_____________________________________________
    def sortPresetItems(self):
        allItems = self.getAllItems(exclude=0)
        bookmarks = {}
        collections = {}
        for item in allItems:
            presetType = item.data(32)[0]
            presetName = item.text()
            if presetType == 'bookmark':
                bookmarks[presetName]=item
            if presetType == 'collection':
                collections[presetName]=item
            self.takeItem(self.row(item))

        for collection in sorted(collections.keys()):
            self.addItem(collections[collection])
        for bookmark in sorted(bookmarks.keys()):
            self.addItem(bookmarks[bookmark])

    #_____________________________________________
    def getAllItems(self, exclude=None):
        allItems = []
        rows = range(self.count())
        if exclude is not None:
            rows.remove(exclude)
        for row in rows:
            allItems.append(self.item(row))
        return allItems

    #_____________________________________________
    def findPresetItem(self, name):
        for item in self.getAllItems():
            if item.text() == name:
                return item
        return None

    #_____________________________________________
    def createPresetItem(self, name, data, iconPath):
        icon = QtGui.QIcon(QtGui.QPixmap(iconPath))
        newItem = QtWidgets.QListWidgetItem()
        newItem.setIcon(icon)
        newItem.setText(name)
        newItem.setData(32, data)
        newItem.setSizeHint(QtCore.QSize(100,22))
        newItem.setBackground(self.neutralBrush)
        return newItem

    #_____________________________________________
    def renamePreset(self):
        presetItem = self.actionItem
        presetName = presetItem.text()

        inputDialog = QtWidgets.QInputDialog()
        newName, ok = inputDialog.getText(self,"IBView","Rename Preset:", text=presetName)
        if newName and ok:
            try:
                presets = cfg.presets.copy()
                presets[newName] = presets.pop(presetName)
                cfg.set_presets(presets)
                cfg.saveConfig()
                presetItem.setText(newName)
            except Exception, e:
                utils.error(e)

        self.sortPresetItems()

    #_____________________________________________
    def getPresetType(name, value):
        if isinstance(value, (str, unicode)):
            return 'bookmark'
        if isinstance(value, list):
            return 'collection'

    #_____________________________________________
    def addPreset(self, presetName, presetValue, new=False):
        if self.findPresetItem(presetName):
            QtWidgets.QMessageBox.warning(self, 'IBView Warning', 'Preset with that name already exists, skipping...')
            return
        presetType = self.getPresetType(presetValue)
        presetData = (presetType, presetValue)
        iconPath = utils.getCustomIconPath(cfg.resourcePath,'%s.png' % presetType)
        presetItem = self.createPresetItem(presetName, presetData, iconPath)
        self.addItem(presetItem)
        if new:
            self.updatePreset(presetItem, presetValue)
        self.sortPresetItems()
        return presetItem

    #_____________________________________________
    def updatePreset(self, presetItem, presetValue, remove=False):
        presets = cfg.presets.copy()
        presetName = presetItem.text()
        presetType = self.getPresetType(presetValue)

        # Update
        if presetName in presets:
            value = presets[presetName]
            # Handle Collection
            if presetType == 'collection':
                if remove:
                    value = list(set(value) - set(presetValue))
                else:
                    value = list(set(value).union(set(presetValue)))

            # Handle Bookmark
            elif presetType == 'bookmark':
                value = presetValue

            # Set
            presets[presetName]=value
            presetItem.setData(32, (presetType, value))
        else:
            presets[presetName]=presetValue
            presetItem.setData(32, (presetType, presetValue))

        # Save
        cfg.set_presets(presets)
        cfg.saveConfig()

        if presetType == 'collection':
            self.collectionUpdated.emit(presetItem)

    #_____________________________________________
    def removePreset(self):
        presetItem = self.actionItem
        presetName = presetItem.text()

        confirmDialog = QtWidgets.QMessageBox()
        result = confirmDialog.question(self,
                                        'IBView',
                                        'Delete "%s" Preset?' % presetName,
                                        buttons=confirmDialog.Yes | confirmDialog.No)
        if result == confirmDialog.Yes:
            try:
                presets = cfg.presets.copy()
                presets.pop(presetName)
                cfg.set_presets(presets)
                cfg.saveConfig()
                delItem = self.takeItem(self.row(presetItem))
                del delItem
                self.presetRemoved.emit(presetName)
            except Exception, e:
                utils.error(e)


#------------------------------------------------#
# File Browser Widget
#------------------------------------------------#
class IBFileBrowser(QtWidgets.QWidget):
    '''IBView Custom File Browser Widget
    '''
    directoryChanged = QtCore.Signal(str)
    def __init__(self, parent=None):
        super(IBFileBrowser, self).__init__(parent)

        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setStyleSheet(IB_STYLESHEET)

        # Layouts
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0,0,0,0)
        self.setLayout(mainLayout)

        # Widget -- FileSystem View/Model
        self.fileModel = QtWidgets.QFileSystemModel()
        self.fileModel.setRootPath(QtCore.QDir.rootPath())
        self.fileModel.setFilter( QtCore.QDir.Dirs | QtCore.QDir.NoDot )
        self.fileViewer = QtWidgets.QTreeView()
        self.fileViewer.setModel(self.fileModel)
        self.fileViewer.hideColumn(1)
        self.fileViewer.hideColumn(2)
        self.fileViewer.hideColumn(3)
        self.fileViewer.setHeaderHidden(True)
        self.fileViewer.setDragEnabled(True)

        # Populate Layouts
        mainLayout.addWidget(self.fileViewer)

        # Connections
        self.fileViewer.doubleClicked.connect(self.setDirFromIndex)

    #_____________________________________________
    def setDirFromPath(self, path):
        path = os.path.normpath(path)
        index = self.fileModel.index(path)
        self.fileViewer.setRootIndex(index)
        self.directoryChanged.emit(path)

    #_____________________________________________
    def setDirFromIndex(self, index):
        path = self.fileModel.filePath(index)
        path = os.path.normpath(path)
        index = self.fileModel.index(path)
        self.fileViewer.setRootIndex(index)
        self.directoryChanged.emit(path)


#------------------------------------------------#
# Image List Widget
#------------------------------------------------#
class IBImageList(QtWidgets.QListWidget):
    '''IBView Custom QListWidget for thumbnail layout
    '''
    #_____________________________________________
    def __init__(self):
        super(IBImageList, self).__init__()

        # Local
        self._itemCache = {}
        self._processed = set()
        self._seen = set()
        self.currentSize = cfg.max_size

        # Properties
        self.setViewMode(self.IconMode)
        self.setLayoutMode(self.Batched)
        self.setBatchSize(25)
        self.setFlow(self.LeftToRight)
        self.setSortingEnabled(True)
        self.setWrapping(True)
        self.setResizeMode(self.Adjust)
        self.setDragEnabled(True)
        self.setDragDropMode(self.DragOnly)
        self.setUniformItemSizes(True)
        self.setSelectionMode(self.ExtendedSelection)

        # Style
        self.setStyleSheet(IB_STYLESHEET)

        # Widgets
        self._vertScrollBar = self.verticalScrollBar()
        self._timer = QtCore.QTimer()

        # Connections
        self._timer.timeout.connect(self.updateVisibleItems)

    #_____________________________________________
    def startDrag(self, supportedActions):
        drag = QtGui.QDrag(self)

        # Gather items source urls
        imageUrls = []
        for item in self.selectedItems():
            tp = item.data(32)
            sourceUrl = QtCore.QUrl.fromLocalFile(tp.sourcePath)
            imageUrls.append(sourceUrl)

        # Configure mime data
        mimeData = QtCore.QMimeData()
        mimeData.setUrls(imageUrls)
        drag.setMimeData(mimeData)

        pixmap = QtGui.QPixmap(utils.getCustomIconPath(cfg.resourcePath,'dragImage.png'))
        drag.setPixmap(pixmap)
        drag.exec_(supportedActions, QtCore.Qt.CopyAction)

    #_____________________________________________
    def setIconSmall(self, nosave=False):
        self.currentSize = cfg.max_size/2
        self.setItemSize()
        cfg.set_size_mode(0)
        if not nosave:
            cfg.saveConfig()

    #_____________________________________________
    def setIconMedium(self, nosave=False):
        self.currentSize = cfg.max_size/1.5
        self.setItemSize()
        cfg.set_size_mode(1)
        if not nosave:
            cfg.saveConfig()

    #_____________________________________________
    def setIconLarge(self,nosave=False):
        self.currentSize = cfg.max_size
        self.setItemSize()
        cfg.set_size_mode(2)
        if not nosave:
            cfg.saveConfig()

    #_____________________________________________
    def setItemSize(self, item=None, size=None):
        '''Set Thumbnail and Grid size
        '''
        # Read Config
        if not size:
            size = self.currentSize

        # Icon
        iconSize = QtCore.QSize(size,size)
        self.setIconSize(iconSize)

        # Grid
        hSize = size + 14
        vSize = size + 14 + 20 # last digit is size of text
        self.setSpacing(5)

        # Size Hint
        if not item:
            for uuid, item in self._itemCache.iteritems():
                item.setSizeHint(QtCore.QSize(hSize, vSize))
        else:
            item.setSizeHint(QtCore.QSize(hSize, vSize))

    #_____________________________________________
    def createItem(self, tp):
        '''Create new thumbnail item
        '''
        newItem = QtWidgets.QListWidgetItem(tp.sourceName)
        newItem.setData(32, tp)
        newItem.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)
        newItem.setIcon(QtGui.QIcon(QtGui.QPixmap(utils.getCustomIconPath(cfg.resourcePath,'default.png'))))
        newItem.setToolTip('Path: %s\nResolution: %s' % (tp.sourcePath, tp.sourceResolution))
        self.setItemSize(newItem)
        self.addItem(newItem)

        #cache and map
        self._itemCache[tp.uuid]=newItem

    #_____________________________________________
    def stop(self):
        '''Stops update state.
        '''
        self._vertScrollBar.valueChanged.disconnect(self.startThumbnailGen)
        self._timer.stop()

        if cfg.verbose:
            utils.info('Updating Completed')

    #_____________________________________________
    def start(self):
        '''Starts update state.
        '''
        self._vertScrollBar.valueChanged.connect(self.startThumbnailGen)
        self._timer.start(15)

        if cfg.verbose:
            utils.info('Updating Started')

    #_____________________________________________
    def resetAll(self):
        '''Resets image list.
        '''
        if self._timer.isActive():
            self.stop()

        self.clear()
        self._processed.clear()
        self._seen.clear()
        self._itemCache = {}

    #_____________________________________________
    def createItems(self, tpList):
        '''Create items from list of thumbnail property.
        '''
        self.resetAll()

        if tpList:
            for tp in tpList:
                self.createItem(tp)

            if cfg.verbose:
                utils.info('Found %d viable items' % len(tpList))

            self.start()

    #_____________________________________________
    def getVisibleItems(self):
        '''Finds visible qlistwidget items.
        '''
        visibleItems = {}
        viewportRect = self.frameRect()
        for uuid, item in self._itemCache.iteritems():
            itemVisRect = self.visualItemRect(item)
            if viewportRect.intersects(itemVisRect):
                visibleItems[self.row(item)]=item
        return visibleItems

    #_____________________________________________
    @QtCore.Slot()
    def startThumbnailGen(self):
        '''Starts updating visible qlistwidget items.
        '''   
        visibleItems = self.getVisibleItems()
        thumbnailToProcess = []

        for row in sorted(visibleItems.keys()):
            item = visibleItems[row]
            tp = item.data(32)
            if not tp.isCurrent and row not in self._seen:
                thumbnailToProcess.append(tp)
                self._seen.add(row)

        # Start conversion thread
        if thumbnailToProcess:
            core.startConvert(thumbnailToProcess)

            if cfg.verbose:
                utils.info('Processing %d items' % len(thumbnailToProcess))

    #_____________________________________________
    @QtCore.Slot()
    def updateVisibleItems(self):
        '''Refreshes the list and trys to update items icons
        for thumbnails that exist.
        '''
        # Stop updating if all items have been processed.
        if len(self._processed) == len(self._itemCache):
            self.stop()
            return

        # Process all visible items
        visibleItems = self.getVisibleItems()         
        for row in sorted(visibleItems.keys()):

            if row not in self._processed:
                item = visibleItems[row]
                tp = item.data(32)

                thumbnailPixmap = QtGui.QPixmap()
                thumbnailPixmap.load(tp.thumbnailPath)

                if not thumbnailPixmap.isNull():

                    # Composite background on images with alphas
                    if thumbnailPixmap.hasAlphaChannel():

                        bgBrush = QtGui.QBrush()
                        bgBrush.setTexture(QtGui.QPixmap(utils.getCustomIconPath(cfg.resourcePath,'checker.png')))
                        bgPen = QtGui.QPen()
                        bgPen.setColor(QtCore.Qt.transparent)
                        bgPen.setWidth(0)
                        thumbnailPixmapWithBg = QtGui.QPixmap(cfg.max_size, cfg.max_size)
                        thumbnailPixmapWithBg.fill(QtCore.Qt.transparent)

                        painter = QtGui.QPainter()
                        painter.begin(thumbnailPixmapWithBg)
                        painter.setBrush(bgBrush)
                        painter.setPen(bgPen)
                        painter.setOpacity(0.2)
                        painter.drawRect(QtCore.QRectF(0.0,0.0, float(cfg.max_size), float(cfg.max_size)))
                        painter.setOpacity(1.0)
                        painter.drawPixmap((cfg.max_size/2)-(thumbnailPixmap.width()/2), 0, thumbnailPixmap)
                        painter.end()
                        thumbnailPixmap = thumbnailPixmapWithBg

                    # Set Icon
                    item.setIcon(QtGui.QIcon(thumbnailPixmap))
                    self._processed.add(row)

                    if cfg.verbose:
                        utils.info('Completed Update for %s' % tp.sourceName)


#------------------------------------------------#
# Viewer Widget
#------------------------------------------------#
class IBView(QtWidgets.QWidget):
    '''Central Custom Widget for IBView, handles
    layout and communication between all UI widgets'''
    def __init__(self, mimeHandler=None, parent=None):
        super(IBView, self).__init__(parent)

        mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(mainLayout)

        self.activeCollectionItem = None

        # Viewers
        self.bookmarkView = IBBookmarkList(mimeHandler=mimeHandler)
        self.browserView = IBFileBrowser()
        self.imageView = IBImageList()

        # Toolbar
        self.toolbar = QtWidgets.QToolBar()

        # Toolbar Actions
        spacerWidget = QtWidgets.QWidget()
        spacerWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        addBookmarkIcon = QtGui.QIcon(utils.getCustomIconPath(cfg.resourcePath,'addBookmark.png'))
        addCollectionIcon = QtGui.QIcon(utils.getCustomIconPath(cfg.resourcePath,'addCollection.png'))
        importCollectionIcon = QtGui.QIcon(utils.getCustomIconPath(cfg.resourcePath,'importCollection.png'))
        exportCollectionIcon = QtGui.QIcon(utils.getCustomIconPath(cfg.resourcePath,'exportCollection.png'))
        refreshCurrentIcon = QtGui.QIcon(utils.getCustomIconPath(cfg.resourcePath,'refresh.png'))
        smallIconSizeIcon = QtGui.QIcon(utils.getCustomIconPath(cfg.resourcePath,'small.png'))
        mediumIconSizeIcon = QtGui.QIcon(utils.getCustomIconPath(cfg.resourcePath,'medium.png'))
        largeIconSizeIcon = QtGui.QIcon(utils.getCustomIconPath(cfg.resourcePath,'large.png'))
        configIcon = QtGui.QIcon(utils.getCustomIconPath(cfg.resourcePath,'config.png'))
        self.toolbar.addAction(addBookmarkIcon, "Bookmark Current", self.addBookmark)
        self.toolbar.addAction(addCollectionIcon, "New Collection", self.addCollection)
        self.toolbar.addAction(importCollectionIcon, "Import Collection", self.importCollection)
        self.exportCollectionAction = self.toolbar.addAction(exportCollectionIcon, "Export Collection", self.exportCollection)
        self.toolbar.addWidget(spacerWidget)
        self.smallIconSizeAction = self.toolbar.addAction(smallIconSizeIcon, "Small Icons", self.imageView.setIconSmall)
        self.mediumIconSizeAction = self.toolbar.addAction(mediumIconSizeIcon, "Medium Icons", self.imageView.setIconMedium)
        self.largeIconSizeAction = self.toolbar.addAction(largeIconSizeIcon, "Large Icons", self.imageView.setIconLarge)
        self.smallIconSizeAction.setCheckable(True)
        self.mediumIconSizeAction.setCheckable(True)
        self.largeIconSizeAction.setCheckable(True)
        iconSizeActionGroup = QtWidgets.QActionGroup(self.toolbar)
        iconSizeActionGroup.addAction(self.smallIconSizeAction)
        iconSizeActionGroup.addAction(self.mediumIconSizeAction)
        iconSizeActionGroup.addAction(self.largeIconSizeAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(refreshCurrentIcon, "Refresh Thumbnails", lambda: self.refreshThumbnails(True))
        self.toolbar.addAction(configIcon, "Configure", self.showConfig)

        # File Path Edit
        completer = QtWidgets.QCompleter()
        completer.setModel(self.browserView.fileModel)
        self.pathEdit = QtWidgets.QLineEdit()
        self.pathEdit.setCompleter(completer)

        # Splitters
        browserSplitter = QtWidgets.QSplitter()
        browserSplitter.addWidget(self.bookmarkView)
        browserSplitter.addWidget(self.browserView)
        browserSplitter.setOrientation(QtCore.Qt.Vertical)
        browserSplitter.setSizes([300,800])

        viewSplitter = QtWidgets.QSplitter()
        viewSplitter.addWidget(browserSplitter)
        viewSplitter.addWidget(self.imageView)
        viewSplitter.setSizes([220, 800])
        viewSplitter.setHandleWidth(6)

        # Layout
        mainLayout.addWidget(self.pathEdit)
        mainLayout.addWidget(self.toolbar)
        mainLayout.addWidget(viewSplitter)

        # Connections
        self.browserView.directoryChanged.connect(self.loadThumbnailsFromPath)
        self.browserView.directoryChanged.connect(self.setPathFromBrowser)
        self.pathEdit.returnPressed.connect(self.setPathFromEdit)
        self.bookmarkView.itemDoubleClicked.connect(self.setPreset)
        self.bookmarkView.collectionUpdated.connect(self.updateCollection)
        self.bookmarkView.presetRemoved.connect(self.cleanupCollectionView)

        # Init
        self.setSizeMode()
        self.browserView.setDirFromPath(utils.getHomePath())
        self.loadPresets()

    #_____________________________________________
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            selectedItems = self.imageView.selectedItems()
            if selectedItems:
                self.removeFromCollection(selectedItems)

    #_____________________________________________
    def addBookmark(self):
        bookmarkPath = self.pathEdit.text()
        if not bookmarkPath.startswith('COLLECTION:'):
            bookmarkName = os.path.basename(bookmarkPath)
            self.bookmarkView.addPreset(bookmarkName, bookmarkPath, new=True)

    #_____________________________________________
    def addCollection(self):
        collectionName, ok = QtWidgets.QInputDialog().getText(self,
                                                       "Create Collection",
                                                       "Name:",
                                                        QtWidgets.QLineEdit.Normal)
        if collectionName and ok:
            self.bookmarkView.addPreset(collectionName, [], new=True)

    #_____________________________________________
    def removeFromCollection(self, itemsToRemove):
        if not self.activeCollectionItem:
            return

        confirmDialog = QtWidgets.QMessageBox()
        result = confirmDialog.warning(self,
                                       "IBView",
                                       "Remove Selected Items from Collection?",
                                       buttons = confirmDialog.Yes | confirmDialog.No)
        if result == confirmDialog.Yes:
            try:
                pathsToRemove = [item.data(32).sourcePath for item in itemsToRemove]
                self.bookmarkView.updatePreset(self.activeCollectionItem, pathsToRemove, remove=True)
            except:
                raise
    
    #_____________________________________________
    def exportCollection(self):
        if self.activeCollectionItem:
            presetValue = self.activeCollectionItem.data(32)[1]
            presetName = self.activeCollectionItem.text()

            saveLocation = QtWidgets.QFileDialog.getSaveFileName(self,
                                                                caption='Choose Collection to Export',
                                                                dir=os.path.expanduser('~'),
                                                                filter="Json (*.json)")
            if saveLocation[0]:
                utils.saveCollectionFile(presetName, presetValue, saveLocation[0])

    #_____________________________________________
    def importCollection(self):
        loadLocation = QtWidgets.QFileDialog.getOpenFileName(self,
                                                            caption='Choose Collection to Import',
                                                            dir=os.path.expanduser('~'),
                                                            filter="Json (*.json)")
        if loadLocation[0]:
            presetName, presetValue = utils.loadCollectionsFile(loadLocation[0])
            self.bookmarkView.addPreset(presetName, presetValue, new=True)

    #_____________________________________________
    def setSizeMode(self):
        if cfg.size_mode == 0:
            self.imageView.setIconSmall(nosave=True)
            self.smallIconSizeAction.setChecked(True)
        if cfg.size_mode == 1:
            self.imageView.setIconMedium(nosave=True)
            self.mediumIconSizeAction.setChecked(True)
        if cfg.size_mode == 2:
            self.imageView.setIconLarge(nosave=True)
            self.largeIconSizeAction.setChecked(True)

    #_____________________________________________
    def cleanupCollectionView(self, presetName):
        presetPath = '%s:%s' % ('COLLECTION', presetName)
        if presetPath == self.pathEdit.text():
            self.browserView.setDirFromPath(utils.getHomePath())

    #_____________________________________________
    def updateCollection(self, item):
        if self.activeCollectionItem is item:
            presetValue = item.data(32)[1]
            self.loadThumbnailsFromCollection(presetValue)

    #_____________________________________________
    def showConfig(self):
        configUI = IBConfigUI()
        if configUI.exec_():
            self.setSizeMode()

    #_____________________________________________
    def setPreset(self, item):
        presetType = item.data(32)[0]
        presetValue = item.data(32)[1]
        presetName = item.text()

        # Handle Bookmark
        if presetType == 'bookmark':
            if not presetValue == self.pathEdit.text():
                self.browserView.setDirFromPath(presetValue)
                self.activeCollectionItem = None

        # Handle Collection
        if presetType == 'collection':
            presetPath = '%s:%s' % (presetType.upper(), presetName)
            if not presetPath == self.pathEdit.text():
                self.pathEdit.setText(presetPath)
                self.loadThumbnailsFromCollection(presetValue)
                self.activeCollectionItem = item

    #_____________________________________________
    def setPathFromBrowser(self, path):
        self.pathEdit.setText(path)
        self.activeCollectionItem = None

    #_____________________________________________
    def setPathFromEdit(self):
        self.browserView.setDirFromPath(self.pathEdit.text())

    #_____________________________________________
    def loadPresets(self):
        for name, value in cfg.presets.iteritems():
            self.bookmarkView.addPreset(name, value)

    #_____________________________________________
    def refreshThumbnails(self, force=False):
        # Refresh Collection
        if self.activeCollectionItem:
            paths = self.activeCollectionItem.data(32)[1]
            self.loadThumbnailsFromCollection(paths, force)
        # Refresh Bookmark Location
        else:
            path = self.pathEdit.text()
            self.loadThumbnailsFromPath(path, force)

    #_____________________________________________
    def loadThumbnailsFromCollection(self, inPaths, force=False):
        '''Loads new items and from path or list of paths given
        '''
        # Build items
        thumbnails = core.getThumbnails(inPaths, inType='file')

        # Remove existing if force enabled
        if force:
            for tp in thumbnails:
                if tp.exists:
                    tp.clear()

        # if thumbnails:
        self.imageView.createItems(thumbnails)

        # For initial view
        self.imageView.startThumbnailGen()

    #_____________________________________________
    def loadThumbnailsFromPath(self, inPath, force=False):
        '''Loads new items and from path or list of paths given
        '''
        # Build items
        thumbnails = core.getThumbnails([inPath], inType='dir')

        # Remove existing if force enabled
        if force:
            for tp in thumbnails:
                if tp.exists:
                    tp.clear()

        # if thumbnails:
        self.imageView.createItems(thumbnails)

        # For initial view
        self.imageView.startThumbnailGen()