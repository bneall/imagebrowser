#
# IBView Mari Loader
#
# ------------------------------------------------------------------------------
# Subject to Licensing provided with this software

import mari
import imagebrowser
import imagebrowser.ui as ui

#---------------------------------------------
def mariMimePathHandeler(mimeData):
    mimeFormat = 'Mari/MriImagePath'
    pathList = []
    if mimeData.hasFormat(mimeFormat):
        data = mimeData.data(mimeFormat)
        path = data.data().split(';')[0]
        pathList.append(path)
    return pathList

#---------------------------------------------
def mariDropHandeler(mimeType, dropTarget, mimeData, contextualInfo):
    # Hard coded to only deliver a "tiled" node, this is consistent with native Mari behavior.
    nodeType = 'Procedural/Pattern/Tiled'
    
    # node graph handler
    if dropTarget == mari.app.NODE_GRAPH:

        nodegraph = contextualInfo['NodeGraph']
        dropPos = contextualInfo['Position']

        pathList = []
        for url in mimeData.urls():
            path = url.toLocalFile()
            pathList.append(path)

            node = nodegraph.createNode(nodeType)      
            node.setMetadata('TileImage', path)
            node.setNodeGraphPosition(dropPos)
    
    return True

#---------------------------------------------
def init():
    try:

        # Configure imagebrowser
        imagebrowser.IB_FORMATS = mari.images.supportedReadFormats()

        global ibviewwdg
        ibviewwdg = ui.IBView(mimeHandler=mariMimePathHandeler)

        # register callbacks
        mari.utils.ui.registerDropDataCallback(mariDropHandeler, 'text/uri-list', mari.app.NODE_GRAPH)

        # Setup Mari Tab
        tabName = 'Image Browser'

        # Clean Up Tab
        try:
            mari.app.removeTab(tabName)
        except:
            pass

        # Install Tab
        mari.app.addTab(tabName, ibviewwdg)

    except:
        print 'Image Browser Initialization failed.'
        raise

# Start
init()