#!/usr/bin/python
# -*- coding: utf-8 -*-

def main():

    from PySide2 import QtWidgets, QtGui
    import imagebrowser
    import imagebrowser.ui as ui

    imagebrowser.IB_FORMATS = [str(f).lower() for f in QtGui.QImageReader.supportedImageFormats()]

    global app
    app = QtWidgets.QApplication(sys.argv)

    # Make dialog
    ibdlg = QtWidgets.QDialog()
    ibviewwdg = ui.IBView(parent=ibdlg)
    ibdlg.setWindowTitle('Image Browser')
    ibdlg.setMinimumSize(800,800)
    dlgLayout = QtWidgets.QHBoxLayout()
    ibdlg.setLayout(dlgLayout)
    dlgLayout.addWidget(ibviewwdg)
    ibdlg.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()