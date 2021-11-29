#
# IBView Maya Loader
#
# ------------------------------------------------------------------------------
# Subject to Licensing provided with this software

from PySide2 import QtWidgets, QtGui
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

#---------------------------------------------
def getMayaMainWindow():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QMainWindow)

#---------------------------------------------
def init():
    import imagebrowser
    import imagebrowser.ui as ui
    
    imagebrowser.IB_FORMATS = [str(f).lower() for f in QtGui.QImageReader.supportedImageFormats()]
    
    # Make dialog
    global ibdlg
    ibdlg = QtWidgets.QDialog(getMayaMainWindow())
    ibviewwdg = ui.IBView(parent=ibdlg)
    ibdlg.setWindowTitle('Image Browser')
    ibdlg.setMinimumSize(800,800)
    dlgLayout = QtWidgets.QHBoxLayout()
    ibdlg.setLayout(dlgLayout)
    dlgLayout.addWidget(ibviewwdg)
    ibdlg.show()