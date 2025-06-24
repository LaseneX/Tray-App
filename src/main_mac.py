import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt, QTimer

class SystemTrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.icons = [
            QIcon("assets/CCTV-Camera-icon.png"),
            QIcon("assets/Bokehlicia-Captiva-Accessories-calculator.256.png"),
            QIcon("assets/Bokehlicia-Captiva-Accessories-text-editor.256.png"),
            QIcon("assets/Bokehlicia-Captiva-Bluetooth.256.png"),
        ]
        self.frame_index = 0

        self.trayIcon = QSystemTrayIcon(self.icons[0], parent=self.app)
        self.trayIcon.setToolTip('Check out my tray icon')

        self.menu = QMenu()

        self.gamesMenu = QMenu("Games")
        self.add_game("Pong", self.launch_pong)
        self.add_game("Connect Four", self.launch_connectFour)
        self.add_game("Snake Game", self.launch_snakegame)

        self.menu.addMenu(self.gamesMenu)

        exitAction = self.menu.addAction("Exit")
        exitAction.triggered.connect(self.app.quit)

        self.trayIcon.setContextMenu(self.menu)
        self.trayIcon.activated.connect(self.on_tray_activated)
        self.trayIcon.show()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_icon)
        self.timer.start(200)

    def add_game(self, name, callback):
        action = self.gamesMenu.addAction(name)
        action.triggered.connect(callback)

    def launch_pong(self):
        pong_path = os.path.join(os.path.dirname(__file__), "pong.py")

        if os.path.exists(pong_path):
            subprocess.Popen([sys.executable, pong_path])
        else:
            print("pong.py not found:", pong_path)

    def launch_connectFour(self):
        connectFour_path = os.path.join(os.path.dirname(__file__), "connectFour.py")

        if os.path.exists(connectFour_path):
            subprocess.Popen([sys.executable, connectFour_path])
        else:
            print("connectFour.py not found:", connectFour_path)

    def launch_snakegame(self):
        snake_path = os.path.join(os.path.dirname(__file__), "snake.py")

        if os.path.exists(snake_path):
            subprocess.Popen([sys.executable, snake_path])
        else:
            print("snake.py not found:", snake_path)

    def update_icon(self):
        self.frame_index = (self.frame_index + 1) % len(self.icons)
        self.trayIcon.setIcon(self.icons[self.frame_index])

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.menu.exec_(QCursor.pos())

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    trayApp = SystemTrayApp()
    trayApp.run()