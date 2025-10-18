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


RESOURCES_PATH = os.path.join(os.path.dirname(__file__), "resources").replace("\\", "/")
DIFFICULT = ["Easy", "Normal", "Hard", "Goddamn"]

# -------------------------------------------------------
# Game Object Classes (Use Images)
# -------------------------------------------------------
class Rocket(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, player_name="Player"):
        super().__init__()
        img_path = f"{RESOURCES_PATH}/images/rocket.png"
        pixmap = QtGui.QPixmap(img_path) if os.path.exists(img_path) else QtGui.QPixmap(40, 20)
        if pixmap.isNull():
            pixmap.fill(QtGui.QColor("cyan"))
        self.setPixmap(pixmap.scaled(40, 40, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        self.nameItem = QtWidgets.QGraphicsSimpleTextItem(player_name)
        self.nameItem.setBrush(QtGui.QBrush(QtCore.Qt.white))
        self.nameItem.setParentItem(self)
        self.nameItem.setPos(-10, -20)


class Enemy(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, x, y, hp=1, aggressive=False):
        super().__init__()
        img_path = f"{RESOURCES_PATH}/images/enemy.png"
        pixmap = QtGui.QPixmap(img_path) if os.path.exists(img_path) else QtGui.QPixmap(30, 30)
        if pixmap.isNull():
            pixmap.fill(QtGui.QColor("red"))
        self.setPixmap(pixmap.scaled(40, 40, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        self.setPos(x, y)
        self.hp = hp
        self.aggressive = aggressive

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


class Boss(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, x, y, hp=100):
        super().__init__()
        img_path = f"{RESOURCES_PATH}/images/boss.png"
        pixmap = QtGui.QPixmap(img_path) if os.path.exists(img_path) else QtGui.QPixmap(80, 50)
        if pixmap.isNull():
            pixmap.fill(QtGui.QColor("#FF007F"))
        self.setPixmap(pixmap.scaled(100, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

        self.setPos(x, y)
        self.hp = hp

        self.hpLabel = QtWidgets.QGraphicsSimpleTextItem(str(hp))
        self.hpLabel.setBrush(QtGui.QBrush(QtCore.Qt.yellow))
        self.hpLabel.setParentItem(self)
        self.hpLabel.setPos(30, -20)

    def hit(self):
        self.hp -= 1
        if self.hp > 0:
            self.hpLabel.setText(str(self.hp))
            return False
        return True


class Bullet(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, direction=QtCore.QPointF(0, -1), speed=10, color="green"):
        super().__init__(0, 0, 5, 15)
        self.setPos(x, y)
        self.direction = direction
        self.speed = speed
        self.setBrush(QtGui.QBrush(QtGui.QColor(color)))


# -------------------------------------------------------
# Game Window
# -------------------------------------------------------
class GameWindow(QtWidgets.QDialog):
    def __init__(self, player_name="Player", difficulty="Easy", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"SPACE INVADER: {difficulty}")
        self.resize(450, 600)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setStyleSheet("""
            QDialog {
                background-color: #000;
                color: #00FF99;
                font-family: 'Press Start 2P', 'VT323', monospace;
                font-size: 10px;
            }
            QLabel {
                color: #00FF99;
            }
        """)

        self.scene = QtWidgets.QGraphicsScene(0, 0, 400, 550)
        self.view = QtWidgets.QGraphicsView(self.scene, self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.view)

        labelLayout = QtWidgets.QHBoxLayout()
        self.scoreLabel = QtWidgets.QLabel("Score: 0")
        self.hpLabel = QtWidgets.QLabel("HP: 3")
        labelLayout.addWidget(self.scoreLabel)
        labelLayout.addStretch()
        labelLayout.addWidget(self.hpLabel)
        layout.addLayout(labelLayout)

        self.player_name = player_name
        self.rocket = Rocket(player_name)
        self.rocket.setPos(180, 500)
        self.scene.addItem(self.rocket)
        self.player_hp = 3

        self.setupDifficulty(difficulty)
        self.createEnemies()

        self.bullets = []
        self.enemy_bullets = []
        self.key_left = False
        self.key_right = False
        self.score = 0

        self.gameTimer = QtCore.QTimer()
        self.gameTimer.timeout.connect(self.updateGame)
        self.gameTimer.start(self.timer_interval)

        self.moveTimer = QtCore.QTimer()
        self.moveTimer.timeout.connect(self.moveRocket)
        self.moveTimer.start(16)

        self.enemyShootTimer = QtCore.QTimer()
        self.enemyShootTimer.timeout.connect(self.enemyShoot)
        self.enemyShootTimer.start(self.shoot_interval)

    def setupDifficulty(self, difficulty):
        if difficulty == "Easy":
            self.speed_enemy = 1
            self.timer_interval = 30
            self.enemy_hp = 1
            self.is_boss = False
            self.shoot_interval = 1000
        elif difficulty == "Normal":
            self.speed_enemy = 2
            self.timer_interval = 25
            self.enemy_hp = 2
            self.is_boss = False
            self.shoot_interval = 800
        elif difficulty == "Hard":
            self.speed_enemy = 3
            self.timer_interval = 20
            self.enemy_hp = 2
            self.is_boss = False
            self.shoot_interval = 600
        else:  # Goddamn
            self.speed_enemy = 3
            self.timer_interval = 20
            self.enemy_hp = 4
            self.is_boss = True
            self.shoot_interval = 200

    def createEnemies(self):
        self.enemies = []
        if self.is_boss:
            boss = Boss(150, 50, 100)
            self.scene.addItem(boss)
            self.enemies.append(boss)
        else:
            for i in range(6):
                e = Enemy(random.randint(0, 350), random.randint(0, 200), self.enemy_hp)
                self.scene.addItem(e)
                self.enemies.append(e)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Left:
            self.key_left = True
        elif event.key() == QtCore.Qt.Key_Right:
            self.key_right = True
        elif event.key() == QtCore.Qt.Key_Space:
            bullet = Bullet(self.rocket.x() + 17, self.rocket.y() - 15)
            self.scene.addItem(bullet)
            self.bullets.append(bullet)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Left:
            self.key_left = False
        elif event.key() == QtCore.Qt.Key_Right:
            self.key_right = False

    def moveRocket(self):
        if self.key_left:
            self.rocket.setX(max(0, self.rocket.x() - 5))
        if self.key_right:
            self.rocket.setX(min(360, self.rocket.x() + 5))

    def updateGame(self):
        for bullet in self.bullets[:]:
            bullet.setPos(bullet.x() + bullet.direction.x() * bullet.speed,
                           bullet.y() + bullet.direction.y() * bullet.speed)
            if bullet.y() < 0:
                self.scene.removeItem(bullet)
                self.bullets.remove(bullet)
                continue

            for enemy in self.enemies[:]:
                if bullet.collidesWithItem(enemy):
                    if enemy.hit():
                        self.scene.removeItem(enemy)
                        self.enemies.remove(enemy)
                        self.score += 20
                    else:
                        self.score += 5
                    self.scene.removeItem(bullet)
                    self.bullets.remove(bullet)
                    self.scoreLabel.setText(f"Score: {self.score}")
                    break

        # Boss movement
        if self.is_boss and self.enemies:
            boss = self.enemies[0]
            boss.setX(boss.x() + math.sin(QtCore.QTime.currentTime().msec() * 0.01) * 2)

        # Enemy bullets
        for b in self.enemy_bullets[:]:
            b.setPos(b.x() + b.direction.x() * b.speed, b.y() + b.direction.y() * b.speed)
            if b.y() > 550:
                self.scene.removeItem(b)
                self.enemy_bullets.remove(b)
                continue
            if b.collidesWithItem(self.rocket):
                self.scene.removeItem(b)
                self.enemy_bullets.remove(b)
                self.player_hp -= 1
                self.hpLabel.setText(f"HP: {self.player_hp}")
                if self.player_hp <= 0:
                    self.gameOver()
                    return

        if not self.enemies:
            self.winGame()

    def enemyShoot(self):
        for e in self.enemies:
            if self.is_boss:
                for angle in [-0.5, -0.25, 0, 0.25, 0.5]:
                    direction = QtCore.QPointF(angle, 1)
                    b = Bullet(e.x() + 40, e.y() + 80, direction, 8, "red")
                    self.scene.addItem(b)
                    self.enemy_bullets.append(b)
            else:
                if random.random() < 0.3:
                    b = Bullet(e.x() + 20, e.y() + 40, QtCore.QPointF(0, 1), 6, "red")
                    self.scene.addItem(b)
                    self.enemy_bullets.append(b)

    def winGame(self):
        self.stopAll()
        QtWidgets.QMessageBox.information(self, "Victory", f"You win, {self.player_name}! 🎉\nScore: {self.score}")
        self.close()
        showMainMenu()

    def gameOver(self):
        self.stopAll()
        QtWidgets.QMessageBox.warning(self, "Game Over", f"{self.player_name}, you lost!\nFinal Score: {self.score}")
        self.close()
        showMainMenu()

    def stopAll(self):
        self.gameTimer.stop()
        self.moveTimer.stop()
        self.enemyShootTimer.stop()


# -------------------------------------------------------
# Main Menu
# -------------------------------------------------------
class SpaceInvaderICT(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SPACE INVADER MENU")
        self.resize(500, 500)
        self.setStyleSheet("""
            QDialog { background-color: #000; }
            QLabel { color: #00FF99; font-family: 'Press Start 2P', monospace; font-size: 10px; }
            QLineEdit, QComboBox {
                background-color: black; color: #00FF99;
                border: 2px solid #00FF99; border-radius: 5px;
                font-family: 'Press Start 2P', monospace; font-size: 10px; padding: 6px;
            }
            QPushButton {
                background-color: #111; color: #00FF99; border: 2px solid #00FF99;
                border-radius: 5px; font-family: 'Press Start 2P', monospace; font-size: 10px; padding: 6px;
            }
            QPushButton:hover { background-color: #00FF99; color: #000; }
        """)

        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("SPACE INVADER")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 38px; color: #00FF99;")
        layout.addWidget(title)

        self.imageLabel = QtWidgets.QLabel()
        img = f"{RESOURCES_PATH}/images/MaysaGood.jpg"
        if os.path.exists(img):
            pix = QtGui.QPixmap(img)
            scaled = pix.scaled(QtCore.QSize(300, 300), QtCore.Qt.KeepAspectRatio)
            self.imageLabel.setPixmap(scaled)
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.imageLabel)

        self.nameLineEdit = QtWidgets.QLineEdit()
        self.nameLineEdit.setPlaceholderText("Enter your name...")
        layout.addWidget(self.nameLineEdit)

        h = QtWidgets.QHBoxLayout()
        self.diffCombo = QtWidgets.QComboBox()
        self.diffCombo.addItems(DIFFICULT)
        self.startButton = QtWidgets.QPushButton("START")
        self.startButton.clicked.connect(self.onStart)
        h.addWidget(self.diffCombo)
        h.addWidget(self.startButton)
        layout.addLayout(h)

        self.exitButton = QtWidgets.QPushButton("EXIT")
        self.exitButton.clicked.connect(self.close)
        layout.addWidget(self.exitButton)
        layout.addStretch()

    def onStart(self):
        name = self.nameLineEdit.text().strip() or "Player"
        diff = self.diffCombo.currentText()
        self.close()
        ptr = getMayaWindow()
        global gameui
        gameui = GameWindow(player_name=name, difficulty=diff, parent=ptr)
        gameui.show()
        gameui.setFocus()


def showMainMenu():
    global ui
    try:
        ui.close()
    except:
        pass
    ptr = getMayaWindow()
    ui = SpaceInvaderICT(parent=ptr)
    ui.show()


def run():
    showMainMenu()
