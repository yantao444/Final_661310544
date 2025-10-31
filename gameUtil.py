# space_invader_utils.py
try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from shiboken6 import wrapInstance
except:
    from PySide2 import QtCore, QtGui, QtWidgets
    from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import os, random, math


def getMayaWindow():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)


# --- Global paths ---
RESOURCES_PATH = os.path.join(os.path.dirname(__file__), "resources").replace("\\", "/")
DIFFICULT = ["Easy", "Normal", "Hard", "Goddamn"]


# -------------------------------------
# Game Objects
# -------------------------------------
class Rocket(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, player_name="Player"):
        super().__init__()
        img_path = os.path.join(RESOURCES_PATH, "rocket.png")
        if os.path.exists(img_path):
            self.setPixmap(QtGui.QPixmap(img_path).scaled(40, 40, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            self.setPixmap(QtGui.QPixmap(40, 40))
        self.nameItem = QtWidgets.QGraphicsSimpleTextItem(player_name)
        self.nameItem.setBrush(QtGui.QBrush(QtCore.Qt.white))
        self.nameItem.setParentItem(self)
        self.nameItem.setPos(0, -20)


class Enemy(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, x, y, hp=1, aggressive=False):
        super().__init__()
        self.hp = hp
        self.aggressive = aggressive
        img_path = os.path.join(RESOURCES_PATH, "enemy.png")
        if os.path.exists(img_path):
            self.setPixmap(QtGui.QPixmap(img_path).scaled(35, 35, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            self.setPixmap(QtGui.QPixmap(35, 35))
        self.setPos(x, y)
        self.hpLabel = QtWidgets.QGraphicsSimpleTextItem(str(hp))
        self.hpLabel.setBrush(QtGui.QBrush(QtCore.Qt.yellow))
        self.hpLabel.setParentItem(self)
        self.hpLabel.setPos(10, -15)

    def hit(self):
        self.hp -= 1
        if self.hp > 0:
            self.hpLabel.setText(str(self.hp))
            return False
        return True


class Boss(Enemy):
    def __init__(self, x, y, hp=100):
        super().__init__(x, y, hp)
        img_path = os.path.join(RESOURCES_PATH, "boss.png")
        if os.path.exists(img_path):
            self.setPixmap(QtGui.QPixmap(img_path).scaled(100, 60, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            self.setPixmap(QtGui.QPixmap(100, 60))
        self.hpLabel.setText(str(hp))


class Bullet(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, direction=QtCore.QPointF(0, -1), speed=10, color=QtCore.Qt.green):
        super().__init__(0, 0, 5, 15)
        self.setPos(x, y)
        self.direction = direction
        self.speed = speed
        self.setBrush(QtGui.QBrush(color))
