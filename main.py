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

# -------------------------------------
# Game Objects
# -------------------------------------
class Rocket(QtWidgets.QGraphicsRectItem):
    def __init__(self, player_name="Player"):
        super().__init__(0, 0, 40, 20)
        self.setBrush(QtGui.QBrush(QtCore.Qt.blue))
        self.nameItem = QtWidgets.QGraphicsSimpleTextItem(player_name)
        self.nameItem.setBrush(QtGui.QBrush(QtCore.Qt.white))
        self.nameItem.setParentItem(self)
        self.nameItem.setPos(-5, -20)

class Enemy(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, hp=1, aggressive=False):
        super().__init__(0, 0, 30, 30)
        self.setPos(x, y)
        self.hp = hp
        self.aggressive = aggressive
        self.setBrush(QtGui.QBrush(QtCore.Qt.red))
        self.hpLabel = QtWidgets.QGraphicsSimpleTextItem(str(hp))
        self.hpLabel.setBrush(QtGui.QBrush(QtCore.Qt.yellow))
        self.hpLabel.setParentItem(self)
        self.hpLabel.setPos(7, -15)

    def hit(self):
        self.hp -= 1
        if self.hp > 0:
            self.hpLabel.setText(str(self.hp))
            color = QtGui.QColor(255, 100 + self.hp * 30, 100)
            self.setBrush(QtGui.QBrush(color))
            return False
        return True

class Bullet(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, direction=QtCore.QPointF(0, -1), speed=10):
        super().__init__(0, 0, 5, 15)
        self.setPos(x, y)
        self.direction = direction
        self.speed = speed
        self.setBrush(QtGui.QBrush(QtCore.Qt.green))

# -------------------------------------
# Game Window
# -------------------------------------
class GameWindow(QtWidgets.QDialog):
    def __init__(self, player_name="Player", difficulty="Easy", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Space Invader ICT - {difficulty}")
        self.resize(450, 600)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.scene = QtWidgets.QGraphicsScene(0, 0, 400, 550)
        self.view = QtWidgets.QGraphicsView(self.scene, self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.view)
        self.setStyleSheet('background-color: #18182E;')

        self.scoreLabel = QtWidgets.QLabel("Score: 0")
        layout.addWidget(self.scoreLabel)
        self.hpLabel = QtWidgets.QLabel("HP: 3")
        layout.addWidget(self.hpLabel)

        self.player_name = player_name
        self.rocket = Rocket(player_name)
        self.rocket.setPos(180, 500)
        self.scene.addItem(self.rocket)

        self.player_hp = 3

        # Difficulty setup
        self.speed_enemy = 1
        self.timer_interval = 30
        self.enemy_hp = 1
        self.enemy_aggressive = False
        self.is_boss_level = False

        if difficulty == "Normal":
            self.speed_enemy = 2
            self.timer_interval = 25
            self.enemy_hp = 2
        elif difficulty == "Hard":
            self.speed_enemy = 3
            self.timer_interval = 20
            self.enemy_hp = 2
        elif difficulty == "Goddamn":
            self.speed_enemy = 3
            self.timer_interval = 20
            self.enemy_hp = 4
            self.enemy_aggressive = True
            self.is_boss_level = True

        self.enemies = []
        self.bullets = []
        self.enemy_bullets = []
        self.direction = 1
        self.t = 0
        self.score = 0
        self.boss_direction = 1

        if self.is_boss_level:
            boss = Enemy(150, 50, hp=100, aggressive=False)
            boss.setRect(0, 0, 80, 50)
            self.scene.addItem(boss)
            self.enemies.append(boss)
        else:
            for i in range(6):
                enemy = Enemy(random.randint(0, 350), random.randint(0, 200), self.enemy_hp, self.enemy_aggressive)
                self.scene.addItem(enemy)
                self.enemies.append(enemy)

        # Timers
        self.gameTimer = QtCore.QTimer()
        self.gameTimer.timeout.connect(self.updateGame)
        self.gameTimer.start(self.timer_interval)

        self.moveTimer = QtCore.QTimer()
        self.moveTimer.timeout.connect(self.moveRocket)
        self.moveTimer.start(16)

        self.enemyShootTimer = QtCore.QTimer()
        self.enemyShootTimer.timeout.connect(self.enemyShoot)
        if self.is_boss_level:
            self.enemyShootTimer.setInterval(200)
        else:
            self.enemyShootTimer.setInterval(1000)
        self.enemyShootTimer.start()

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Left:
            self.key_left = True
        elif key == QtCore.Qt.Key_Right:
            self.key_right = True
        elif key == QtCore.Qt.Key_Space:
            bullet = Bullet(self.rocket.x() + 17, self.rocket.y() - 15)
            self.scene.addItem(bullet)
            self.bullets.append(bullet)

    def keyReleaseEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Left:
            self.key_left = False
        elif key == QtCore.Qt.Key_Right:
            self.key_right = False

    def moveRocket(self):
        if getattr(self, "key_left", False):
            self.rocket.setX(max(0, self.rocket.x() - 5))
        if getattr(self, "key_right", False):
            self.rocket.setX(min(360, self.rocket.x() + 5))

    def updateGame(self):
        self.t += 1
        # Update bullets
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

        # Enemy movement
        for e in self.enemies:
            if e.aggressive and not self.is_boss_level:
                x_move = math.sin(self.t * 0.05 + e.x()) * self.speed_enemy * 2
                e.setX(max(0, min(370, e.x() + x_move)))
                e.setY(e.y() + 0.5)
            elif not self.is_boss_level:
                e.setX(e.x() + self.direction * self.speed_enemy)

        # Boss movement ซ้ายขวา
        if self.is_boss_level and self.enemies:
            boss = self.enemies[0]
            new_x = boss.x() + self.boss_direction * 1
            if new_x <= 0 or new_x >= 320:
                self.boss_direction *= -1
            boss.setX(boss.x() + self.boss_direction)

        if not self.is_boss_level:
            if any(e.x() <= 0 or e.x() >= 370 for e in self.enemies):
                self.direction *= -1
                for e in self.enemies:
                    e.setY(e.y() + 20)
                    if e.y() > 500:
                        self.gameOver()
                        return

        # Enemy bullets
        for b in self.enemy_bullets[:]:
            b.setPos(b.x() + b.direction.x() * b.speed,
                     b.y() + b.direction.y() * b.speed)
            if b.y() > 550 or b.x() < 0 or b.x() > 400:
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

        # Win condition
        if not self.enemies:
            self.gameTimer.stop()
            self.moveTimer.stop()
            self.enemyShootTimer.stop()
            QtWidgets.QMessageBox.information(
                self, "Victory", f"You win, {self.player_name}! 🎉\nScore: {self.score}"
            )
            self.close()
            showMainMenu()

    def enemyShoot(self):
        for e in self.enemies:
            if self.is_boss_level:
                # Boss ยิงหลายทาง 5-way
                for angle in [-0.5, -0.25, 0, 0.25, 0.5]:
                    direction = QtCore.QPointF(angle, 1)
                    b = Bullet(e.x() + e.rect().width()/2, e.y() + e.rect().height(), direction, 8)
                    self.scene.addItem(b)
                    self.enemy_bullets.append(b)
            else:
                if random.random() < 0.3:
                    b = Bullet(e.x() + 12, e.y() + 30, QtCore.QPointF(0,1), 6)
                    self.scene.addItem(b)
                    self.enemy_bullets.append(b)

    def gameOver(self):
        self.gameTimer.stop()
        self.moveTimer.stop()
        self.enemyShootTimer.stop()
        QtWidgets.QMessageBox.warning(
            self, "Game Over", f"{self.player_name}, you lost!\nFinal Score: {self.score}"
        )
        self.close()
        showMainMenu()

# -------------------------------------
# Main Menu
# -------------------------------------
class SpaceInvaderICT(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Space Invader ICT")
        self.resize(500, 500)

        mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(mainLayout)
        self.setStyleSheet('background-color: #18182E;')

        self.imageLabel = QtWidgets.QLabel()
        image_path = f"{RESOURCES_PATH}/images/MaysaGood.jpg"
        if os.path.exists(image_path):
            pixmap = QtGui.QPixmap(image_path)
            scaled = pixmap.scaled(QtCore.QSize(300, 300),
                QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.imageLabel.setPixmap(scaled)
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        mainLayout.addWidget(self.imageLabel)

        self.nameLineEdit = QtWidgets.QLineEdit()
        self.nameLineEdit.setPlaceholderText("Enter your name...")
        mainLayout.addWidget(self.nameLineEdit)

        hLayout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(hLayout)

        self.diffCombo = QtWidgets.QComboBox()
        self.diffCombo.addItems(DIFFICULT)
        self.startButton = QtWidgets.QPushButton("Start")
        self.startButton.clicked.connect(self.onStart)
        hLayout.addWidget(self.diffCombo)
        hLayout.addWidget(self.startButton)

        self.closeButton = QtWidgets.QPushButton("Close")
        self.closeButton.clicked.connect(self.close)
        mainLayout.addWidget(self.closeButton)

    def onStart(self):
        player_name = self.nameLineEdit.text().strip() or "Player"
        self.close()
        global gameui
        try:
            gameui.close()
        except:
            pass
        ptr = getMayaWindow()
        diff = self.diffCombo.currentText()
        gameui = GameWindow(player_name=player_name, difficulty=diff, parent=ptr)
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
