# space_invader_ui.py
try:
    from PySide6 import QtCore, QtGui, QtWidgets
except:
    from PySide2 import QtCore, QtGui, QtWidgets

import os, random, math
from space_invader_utils import (
    getMayaWindow,
    Rocket, Enemy, Boss, Bullet,
    RESOURCES_PATH, DIFFICULT
)


# -------------------------------------
# Game Window
# -------------------------------------
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
            QLabel { color: #00FF99; }
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

        # Difficulty setup
        self.speed_enemy = 1
        self.timer_interval = 30
        self.enemy_hp = 1
        self.is_boss = False

        if difficulty == "Normal":
            self.speed_enemy = 2
            self.enemy_hp = 2
        elif difficulty == "Hard":
            self.speed_enemy = 3
            self.enemy_hp = 2
        elif difficulty == "Goddamn":
            self.speed_enemy = 3
            self.enemy_hp = 4
            self.is_boss = True

        self.bullets = []
        self.enemy_bullets = []
        self.score = 0
        self.key_left = self.key_right = False

        self.createEnemies()

        # Timers
        self.gameTimer = QtCore.QTimer()
        self.gameTimer.timeout.connect(self.updateGame)
        self.gameTimer.start(self.timer_interval)

        self.moveTimer = QtCore.QTimer()
        self.moveTimer.timeout.connect(self.moveRocket)
        self.moveTimer.start(16)

        self.enemyShootTimer = QtCore.QTimer()
        self.enemyShootTimer.timeout.connect(self.enemyShoot)
        self.enemyShootTimer.setInterval(250 if self.is_boss else 1000)
        self.enemyShootTimer.start()

    def createEnemies(self):
        self.enemies = []
        self.enemy_direction = 1
        self.enemy_step_down = 10

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
        if self.key_left:
            self.rocket.setX(max(0, self.rocket.x() - 5))
        if self.key_right:
            self.rocket.setX(min(360, self.rocket.x() + 5))

    def updateGame(self):
        # Bullet
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

        # Enemy move
        if not self.is_boss:
            move_down = False
            for e in self.enemies:
                e.setX(e.x() + self.speed_enemy * self.enemy_direction)
                if e.x() <= 0 or e.x() + 40 >= 400:
                    move_down = True
            if move_down:
                self.enemy_direction *= -1
                for e in self.enemies:
                    e.setY(e.y() + self.enemy_step_down)
        else:
            if self.enemies:
                boss = self.enemies[0]
                boss.setX(boss.x() + math.sin(QtCore.QTime.currentTime().msec() * 0.01) * 3)

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
                    b = Bullet(e.x() + 40, e.y() + 60, direction, 8, QtCore.Qt.red)
                    self.scene.addItem(b)
                    self.enemy_bullets.append(b)
            else:
                if random.random() < 0.3:
                    b = Bullet(e.x() + 17, e.y() + 35, QtCore.QPointF(0, 1), 6, QtCore.Qt.red)
                    self.scene.addItem(b)
                    self.enemy_bullets.append(b)

    def winGame(self):
        self.stopTimers()
        QtWidgets.QMessageBox.information(self, "Victory",
                                          f"You win, {self.player_name}! 🎉\nScore: {self.score}")
        self.close()
        showMainMenu()

    def gameOver(self):
        self.stopTimers()
        QtWidgets.QMessageBox.warning(self, "Game Over",
                                      f"{self.player_name}, you lost!\nFinal Score: {self.score}")
        self.close()
        showMainMenu()

    def stopTimers(self):
        self.gameTimer.stop()
        self.moveTimer.stop()
        self.enemyShootTimer.stop()


# -------------------------------------
# Main Menu
# -------------------------------------
class SpaceInvaderICT(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SPACE INVADER MENU")
        self.resize(500, 500)
        self.setStyleSheet("""
            QDialog { background-color: #000; }
            QLabel, QPushButton, QLineEdit, QComboBox {
                color: #00FF99;
                font-family: 'Press Start 2P', 'VT323', monospace;
                font-size: 10px;
            }
            QPushButton {
                background-color: #111;
                border: 2px solid #00FF99;
                border-radius: 5px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #00FF99;
                color: #000;
            }
        """)

        mainLayout = QtWidgets.QVBoxLayout(self)
        title = QtWidgets.QLabel("SPACE INVADER")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 38px; color: #00FF99;")
        mainLayout.addWidget(title)

        # image
        self.imageLabel = QtWidgets.QLabel()
        img_path = f"{RESOURCES_PATH}/images/MaysaGood.jpg"
        if os.path.exists(img_path):
            pixmap = QtGui.QPixmap(img_path).scaled(300, 300, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        mainLayout.addWidget(self.imageLabel)

        self.nameLineEdit = QtWidgets.QLineEdit()
        self.nameLineEdit.setPlaceholderText("Enter your name...")
        mainLayout.addWidget(self.nameLineEdit)

        hLayout = QtWidgets.QHBoxLayout()
        self.diffCombo = QtWidgets.QComboBox()
        self.diffCombo.addItems(DIFFICULT)
        self.startButton = QtWidgets.QPushButton("START")
        self.startButton.clicked.connect(self.onStart)
        hLayout.addWidget(self.diffCombo)
        hLayout.addWidget(self.startButton)
        mainLayout.addLayout(hLayout)

        self.closeButton = QtWidgets.QPushButton("EXIT")
        self.closeButton.clicked.connect(self.close)
        mainLayout.addWidget(self.closeButton)
        mainLayout.addStretch()

    def onStart(self):
        player_name = self.nameLineEdit.text().strip() or "Player"
        diff = self.diffCombo.currentText()
        self.close()
        ptr = getMayaWindow()
        global gameui
        try:
            gameui.close()
        except:
            pass
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
