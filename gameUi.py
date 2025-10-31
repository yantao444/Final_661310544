from spaceGame.gameUtil import getMayaWindow, RESOURCES_PATH, DIFFICULT
try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets

import os, random, math

# ----------------------------------------Global UI References----------------------------------------
ui = None
gameui = None

def showMainMenu():
    global ui
    try:
        if gameui:
            gameui.close()
    except Exception:
        pass
        
    try:
        if ui:
            ui.close()
    except Exception:
        pass
        
    ptr = getMayaWindow()
    ui = SpaceInvaderICT(parent=ptr)
    ui.show()

def run():
    showMainMenu()

# ----------------------------------------Game Objects----------------------------------------
class Rocket(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, player_name="Player"):
        super().__init__()
        self.setZValue(10)
        img_path = os.path.join(RESOURCES_PATH, "icons", "mc.png")
        if os.path.exists(img_path):
            self.setPixmap(QtGui.QPixmap(img_path).scaled(40, 40, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            self.setPixmap(QtGui.QPixmap(40, 40))
        self.nameItem = QtWidgets.QGraphicsSimpleTextItem(player_name)
        self.nameItem.setBrush(QtGui.QBrush(QtCore.Qt.white))
        self.nameItem.setParentItem(self)
        self.nameItem.setPos(0, -20)

class Enemy(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, x, y, hp=1, icon_filename="zombie.png"):
        super().__init__()
        self.hp = hp
        img_path = os.path.join(RESOURCES_PATH, "icons", icon_filename)
        if os.path.exists(img_path):
            self.setPixmap(QtGui.QPixmap(img_path).scaled(35, 35, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            self.setPixmap(QtGui.QPixmap(35, 35))
        self.setPos(x, y)
        self.hpLabel = QtWidgets.QGraphicsSimpleTextItem(str(hp))
        self.hpLabel.setBrush(QtGui.QBrush(QtCore.Qt.yellow))
        self.hpLabel.setParentItem(self)
        self.hpLabel.setPos(10, -15)
        self.setZValue(5)

    def hit(self):
        self.hp -= 1
        if self.hp > 0:
            self.hpLabel.setText(str(self.hp))
            return False
        return True

class Boss(Enemy):
    def __init__(self, x, y, hp=100, icon_filename="the witch.png"):
        super().__init__(x, y, hp, icon_filename)
        img_path = os.path.join(RESOURCES_PATH, "icons", icon_filename)
        if os.path.exists(img_path):
            self.setPixmap(QtGui.QPixmap(img_path).scaled(100, 100, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            self.setPixmap(QtGui.QPixmap(100, 100))
        self.hpLabel.setText(str(hp))
        self.setZValue(6)

class Bullet(QtWidgets.QGraphicsRectItem):
    def __init__(self, x, y, direction=QtCore.QPointF(0, -1), speed=10, color=QtCore.Qt.green):
        super().__init__(0, 0, 5, 15)
        self.setPos(x, y)
        self.direction = direction
        self.speed = speed
        self.setBrush(QtGui.QBrush(color))
        self.setZValue(2)

# ----------------------------------------Game Window----------------------------------------
class GameWindow(QtWidgets.QDialog):
    def __init__(self, player_name="Player", difficulty="Easy", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"SPACE INVADER: {difficulty}")
        self.resize(450, 600)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        self.enemy_icon = "zombie.png"
        self.enemies_per_wave = 6
        self.player_bullet_color = QtCore.Qt.green
        self.enemy_bullet_color = QtCore.Qt.red
        self.enemy_bullet_speed = 6
        self.player_hp = 3
        
        self.speed_enemy = 1
        self.timer_interval = 30
        self.enemy_hp = 1
        self.is_boss = False
        
        bg_filename = "easy_bg.jpg"
        opacity_level = 0.5
        
        if difficulty == "Easy":
            self.enemy_icon = "zombie.png"
            self.enemies_per_wave = 6
        elif difficulty == "Normal":
            bg_filename = "normal_bg.jpg"
            self.speed_enemy = 2
            self.enemy_hp = 2
            self.enemy_icon = "mummy.png"
            self.enemies_per_wave = 8
            self.enemy_bullet_speed = 7
        elif difficulty == "Hard":
            bg_filename = "hard_bg.jpg"
            self.speed_enemy = 3
            self.enemy_hp = 2
            self.enemy_icon = "vampire.png"
            self.enemies_per_wave = 10
            self.enemy_bullet_speed = 8
        elif difficulty == "Goddamn":
            bg_filename = "goddamn_bg.jpg"
            self.speed_enemy = 3
            self.enemy_hp = 100
            self.is_boss = True
            self.enemy_icon = "the witch.png"
            self.enemies_per_wave = 1
            opacity_level = 0.3
            self.player_hp = 2
            self.enemy_bullet_speed = 8
            self.enemy_bullet_color = QtCore.Qt.magenta

        # ----------------------------------------UI Setup (Style Sheet)----------------------------------------
        self.setStyleSheet("""
            QDialog {
                background-color: #2b003d;
                color: #ffb347;
                font-family: 'Press Start 2P', 'VT323', monospace;
                font-size: 10px;
                border: 2px solid #ff6600;
                border-radius: 8px;
            }

            QLabel {
                color: #ff7f50;
                font-weight: bold;
            }

            QLineEdit, QComboBox {
                background-color: #3d003d;
                border: 1px solid #ff7518;
                color: #ffd;
                padding: 5px;
                border-radius: 4px;
                selection-background-color: #ff6600;
            }

            QPushButton {
                background-color: #ff6600;
                border: 2px solid #ffb347;
                color: #2b003d;    
                padding: 6px 10px;
                border-radius: 6px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #9b30ff;
                color: #ffd700;
            }

            QPushButton:pressed {
                background-color: #ff4500;
                color: #fff;
            }

            QScrollBar:vertical {
                border: none;
                background: #3d003d;
                width: 8px;
            }

            QScrollBar::handle:vertical {
                background: #ff6600;
                min-height: 20px;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical:hover {
                background: #ff9933;
            }
        """)

        # ----------------------------------------Scene and View Setup----------------------------------------
        self.scene = QtWidgets.QGraphicsScene(0, 0, 400, 550)
        self.view = QtWidgets.QGraphicsView(self.scene, self)

        # ----------------------------------------Background Setup----------------------------------------
        bg_path = os.path.join(RESOURCES_PATH, "images", bg_filename)
        
        if os.path.exists(bg_path):
            pixmap = QtGui.QPixmap(bg_path)
            
            scaled_pixmap = pixmap.scaled(
                400, 
                550, 
                QtCore.Qt.IgnoreAspectRatio,  
                QtCore.Qt.SmoothTransformation
            )
            
            background_item = QtWidgets.QGraphicsPixmapItem(scaled_pixmap)
            background_item.setPos(0, 0)
            background_item.setOpacity(opacity_level)
            background_item.setZValue(-1)
            self.scene.addItem(background_item)
        else:
            self.scene.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(43, 0, 61)))

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.view)

        # ----------------------------------------Labels----------------------------------------
        labelLayout = QtWidgets.QHBoxLayout()
        self.scoreLabel = QtWidgets.QLabel("Score: 0")
        self.hpLabel = QtWidgets.QLabel(f"HP: {self.player_hp}")
        labelLayout.addWidget(self.scoreLabel)
        labelLayout.addStretch()
        labelLayout.addWidget(self.hpLabel)
        layout.addLayout(labelLayout)

        # ----------------------------------------Game Initialization----------------------------------------
        self.player_name = player_name
        self.rocket = Rocket(player_name)
        self.rocket.setPos(180, 500)
        self.scene.addItem(self.rocket)

        self.bullets = []
        self.enemy_bullets = []
        self.score = 0
        self.key_left = self.key_right = False

        self.createEnemies()

        # ----------------------------------------Timers----------------------------------------
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
            boss = Boss(150, 50, self.enemy_hp, icon_filename=self.enemy_icon)
            self.scene.addItem(boss)
            self.enemies.append(boss)
            if not hasattr(boss, "direction_x"):
                boss.direction_x = 1
        else:
            for i in range(self.enemies_per_wave):
                x = random.randint(0, 365)
                y = random.randint(0, 200)
                e = Enemy(x, y, self.enemy_hp, icon_filename=self.enemy_icon)
                self.scene.addItem(e)
                self.enemies.append(e)

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Left:
            self.key_left = True
        elif key == QtCore.Qt.Key_Right:
            self.key_right = True
        elif key == QtCore.Qt.Key_Space:
            # Bullet: ใช้สีจากตัวแปรที่ตั้งค่าไว้
            bullet = Bullet(self.rocket.x() + 17, self.rocket.y() - 15, color=self.player_bullet_color)
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
            self.rocket.setX(min(400 - self.rocket.pixmap().width(), self.rocket.x() + 5))

    def updateGame(self):
        # ----------------------------------------Bullet movement----------------------------------------
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
                        self.score += 20 if not self.is_boss else 100 # Boss score
                    else:
                        self.score += 5
                    self.scene.removeItem(bullet)
                    self.bullets.remove(bullet)
                    self.scoreLabel.setText(f"Score: {self.score}")
                    break

        # ----------------------------------------Enemy movement----------------------------------------
        if not self.enemies:
             self.winGame()
             return

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
                    if e.y() + e.pixmap().height() >= self.rocket.y():
                        self.gameOver()
                        return
        else:
            boss = self.enemies[0]
            speed = 3 # Boss side speed
            boss.setX(boss.x() + speed * boss.direction_x)

            if boss.x() <= 0 or boss.x() + boss.pixmap().width() >= 400:
                boss.direction_x *= -1

        # ----------------------------------------Enemy bullets----------------------------------------
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

    def enemyShoot(self):
        for e in self.enemies:
            if self.is_boss:
                for angle in [-0.5, -0.25, 0, 0.25, 0.5]:
                    direction = QtCore.QPointF(angle, 1)
                    b = Bullet(e.x() + 40, e.y() + 60, direction, self.enemy_bullet_speed, self.enemy_bullet_color)
                    self.scene.addItem(b)
                    self.enemy_bullets.append(b)
            else:
                if random.random() < 0.3:
                    # ใช้ self.enemy_bullet_speed และ self.enemy_bullet_color
                    b = Bullet(e.x() + 17, e.y() + 35, QtCore.QPointF(0,1), self.enemy_bullet_speed, self.enemy_bullet_color)
                    self.scene.addItem(b)
                    self.enemy_bullets.append(b)

    def winGame(self):
        self.stopTimers()
        QtWidgets.QMessageBox.information(self, "Victory", f"You win, {self.player_name}! 🎉\nScore: {self.score}")
        self.close()
        showMainMenu()

    def gameOver(self):
        self.stopTimers()
        QtWidgets.QMessageBox.warning(self, "Game Over", f"{self.player_name}, you lost!\nFinal Score: {self.score}")
        self.close()
        showMainMenu()

    def stopTimers(self):
        self.gameTimer.stop()
        self.moveTimer.stop()
        self.enemyShootTimer.stop()

# ----------------------------------------Main Menu----------------------------------------
class SpaceInvaderICT(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MAYSA HALLOWEEN GAME")
        self.resize(500, 500)

        # ----------------- Load custom font -----------------
        font_path = os.path.join(RESOURCES_PATH, "font", "FredokaOne-Regular.ttf")
        if os.path.exists(font_path):
             QtGui.QFontDatabase.addApplicationFont(font_path)
             self.customFont = QtGui.QFont("Fredoka One", 14)
        else:
            self.customFont = QtGui.QFont("Arial", 14)

        # ----------------- Background image -----------------
        self.bgLabel = QtWidgets.QLabel(self)
        bg_path = os.path.join(RESOURCES_PATH, "images", "halloween_bg.jpg")
        if os.path.exists(bg_path):
            pixmap = QtGui.QPixmap(bg_path)
            self.bgLabel.setPixmap(pixmap)
            self.bgLabel.setScaledContents(True)
        self.bgLabel.setGeometry(0, 0, self.width(), self.height())
        self.bgLabel.lower()
        self.resizeEvent = self._resizeEvent

        # ----------------- Layout -----------------
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setContentsMargins(30, 30, 30, 30)
        mainLayout.setSpacing(15)

        # Title
        title = QtWidgets.QLabel("MAYSA HALLOWEEN GAME")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setFont(QtGui.QFont("Fredoka One", 25))
        title.setStyleSheet("color: orange;")
        mainLayout.addWidget(title)

        # Player name
        self.nameLineEdit = QtWidgets.QLineEdit()
        self.nameLineEdit.setPlaceholderText("Enter your name...")
        self.nameLineEdit.setFont(self.customFont)
        self.nameLineEdit.setStyleSheet("""
            background-color: rgba(0,0,0,150);
            color: #FFAA00;
            border: 2px solid #AA00FF;
            border-radius: 6px;
            padding: 4px;
        """)
        mainLayout.addWidget(self.nameLineEdit)

        # Difficulty selection
        self.diffCombo = QtWidgets.QComboBox()
        self.diffCombo.addItems(DIFFICULT)
        self.diffCombo.setFont(self.customFont)
        self.diffCombo.setStyleSheet("""
            background-color: rgba(0,0,0,150);
            color: #FFAA00;
            border: 2px solid #AA00FF;
            border-radius: 6px;
            padding: 4px;
        """)
        mainLayout.addWidget(self.diffCombo)

        # Start button
        self.startButton = QtWidgets.QPushButton("START")
        self.startButton.setFont(self.customFont)
        self.startButton.setStyleSheet("""
            QPushButton {
                background-color: rgba(80,0,80,180);
                color: orange;
                border: 2px solid #FFAA00;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(255,165,0,200);
                color: #2b003d;
            }
            QPushButton:pressed {
                background-color: rgba(170,0,255,200);
                color: #fff;
            }
        """)

        self.startButton.clicked.connect(self.onStart)
        mainLayout.addWidget(self.startButton)

        # Exit button
        self.exitButton = QtWidgets.QPushButton("EXIT")
        self.exitButton.setFont(self.customFont)
        self.exitButton.setStyleSheet("""
            QPushButton {
                background-color: rgba(80,0,80,180);
                color: orange;
                border: 2px solid #FFAA00;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(255,165,0,200);
                color: #2b003d;
            }
            QPushButton:pressed {
                background-color: rgba(170,0,255,200);
                color: #fff;
            }
        """)
        self.exitButton.clicked.connect(self.close)
        mainLayout.addWidget(self.exitButton)

        mainLayout.addStretch()


    def _resizeEvent(self, event):
        self.bgLabel.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)
        
    def onStart(self):
        player_name = self.nameLineEdit.text().strip() or "Player"
        diff = self.diffCombo.currentText()
        self.close()
        
        ptr = getMayaWindow()
        from spaceGame.gameUi import GameWindow 
        global gameui
        
        try:
            if gameui:
                gameui.close()
        except Exception:
            pass
            
        gameui = GameWindow(player_name=player_name, difficulty=diff, parent=ptr)
        gameui.show()
        gameui.setFocus()