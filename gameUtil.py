try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from shiboken6 import wrapInstance
except:
    from PySide2 import QtCore, QtGui, QtWidgets
    from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import os

def getMayaWindow():
    """Return Maya main window as QWidget"""
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)

# ----------------------------------------Path ของ resource (ภาพ / เสียง)----------------------------------------
RESOURCES_PATH = os.path.join(os.path.dirname(__file__), "resources").replace("\\", "/")

# ----------------------------------------ระดับความยาก----------------------------------------
DIFFICULT = ["Easy", "Normal", "Hard", "Goddamn"]
