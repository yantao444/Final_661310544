try:
	from PySide6 import QtCore, QtGui, QtWidgets
	from shiboken6 import wrapInstance
	from PySide6.QtGui import QIntValidator
except:
	from PySide2 import QtCore, QtGui, QtWidgets
	from shiboken2 import wrapInstance
	from PySide2.QtGui import QIntValidator
import importlib
import maya.OpenMayaUI as omui
import os 

from . import config
importlib.reload(config)
RESOURCES_PATH = os.path.join(os.path.dirname(__file__),'resources').replace("\\","/")

class SpaceInvaderICT(QtWidgets.QDialog):
	def __init__(self, parent = None):
		super().__init__(parent)

		self.setWindowTitle("SpaceInvaderICT")
		self.resize(300,300)

		self.mainLayout = QtWidgets.QVBoxLayout()
		self.setLayout(self.mainLayout)

		self.imageLabel = QtWidgets.QLabel()
		self.imagePixmap = QtGui.QPixmap(f"{RESOURCES_PATH}/images/MaysaGood.jpg")
		scaled_pixmap = self.imagePixmap.scaled(
			QtCore.QSize(300,300),
			QtCore.Qt.KeepAspectRatio,
			QtCore.Qt.SmoothTransformation
		)
		self.imageLabel.setPixmap(scaled_pixmap)
		self.imageLabel.setStyleSheet("background-color: 0;")
		self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
		self.mainLayout.addWidget(self.imageLabel)

		self.nameLineEdit = QtWidgets.QLineEdit()
		self.mainLayout.addWidget(self.nameLineEdit)

		self.difficultAndStartLayout = QtWidgets.QHBoxLayout()
		self.mainLayout.addLayout(self.difficultAndStartLayout)

		self.diffucultComboBox = QtWidgets.QComboBox()
		self.diffucultComboBox.addItems(config.DIFFICULT)

		self.startButton = QtWidgets.QPushButton("Start")
		self.startButton.clicked.connect(self.onStart)

		self.difficultAndStartLayout.addWidget(self.diffucultComboBox)
		self.difficultAndStartLayout.addWidget(self.startButton)

		self.closeButton = QtWidgets.QPushButton("Close")
		self.closeButton.clicked.connect(self.close)
		self.mainLayout.addWidget(self.closeButton)

	def onStart(self):
		self.close()

		global gameui
		try :
			gameui.close()
		except:
			pass

		ptr = wrapInstance(int(omui.MQtUtil.mainWindow()),QtWidgets.QWidget)
		
		gameui = GameWindow(parent = ptr)
		gameui.show()
		
class GameWindow(QtWidgets.QDialog):
	def __init__(self, parent = None):
		super().__init__(parent)

		self.setWindowTitle("SpaceInvaderICT")
		self.resize(300,300)

def run():
	global ui
	try :
		ui.close()
		gameui.close()
	except:
		pass

	ptr = wrapInstance(int(omui.MQtUtil.mainWindow()),QtWidgets.QWidget)
	ui = SpaceInvaderICT(parent = ptr)
	ui.show()